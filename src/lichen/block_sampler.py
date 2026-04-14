"""Shot-level sampler for the blockwise hidden-memory env construction.

This module turns the blockwise conditional Pauli channels into a simulator-
facing sampled process: one hidden-memory value per shot, one toggling-frame
Pauli fault sampled per block, and one corresponding physical inserted fault
obtained by conjugating that sampled fault by the block-end Clifford frame.

The first `ultra` implementation materialized the full block Pauli channel for
every block. That is still available as the oracle path, but the sampler now
consumes a sparse exported distribution instead. This keeps the interface
compatible with notebook inspection while making it possible to truncate and
cache the simulator-facing block alphabet.
"""

from __future__ import annotations

import os
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field
from multiprocessing import get_context
from time import perf_counter

import numpy as np

from .hidden_memory import HiddenMemorySample, sample_hidden_memory
from .model import SharedQuasiStaticModel
from .frame_tracker import CliffordFrameHistory, build_clifford_frame_history
from .segment_generators import build_segment_generators
from .block_fault_export import (
    SparseBlockFaultDistribution,
    SparseExportConfig,
    export_sparse_probabilities,
)
from .block_partition import BlockDescriptor, build_fixed_window_blocks
from .block_probability_search import build_supported_block_probability_search
from .block_template_cache import UltraBlockTemplateCache, build_block_signature
from .circuit import CircuitDescription


@dataclass(frozen=True)
class BlockFaultChoice:
    """One sampled block fault with both toggling-frame and physical labels.

    Attributes
    ----------
    block_index:
        Zero-based block index.
    toggling_frame_pauli_string:
        Sampled block fault ``Q_b`` in the toggling frame. The identity is
        represented as ``None``.
    physical_pauli_string:
        Physical inserted fault ``F_b = G_{e_b} Q_b G_{e_b}^dagger``. The
        identity is represented as ``None``.
    probability:
        Conditional probability of the sampled toggling-frame fault under the
        block's Pauli distribution.
    """

    block_index: int
    toggling_frame_pauli_string: str | None
    physical_pauli_string: str | None
    probability: float

    @property
    def pauli_string(self) -> str | None:
        """Return the physical inserted fault label.

        This preserves the old ``fault.pauli_string`` access pattern while
        making the returned label match the simulator-facing physical circuit.
        """

        return self.physical_pauli_string


@dataclass(frozen=True)
class BlockwiseHiddenMemoryProcess:
    """One full-shot blockwise hidden-memory sampled process.

    ``block_channels`` remain conditional toggling-frame block distributions.
    ``block_faults`` expose both the sampled toggling-frame fault and the
    physical inserted fault for each block.
    """

    hidden_memory: HiddenMemorySample
    block_channels: tuple[SparseBlockFaultDistribution, ...]
    block_faults: tuple[BlockFaultChoice, ...]


@dataclass(frozen=True)
class BlockwiseHiddenMemoryProcessBatch:
    """A collection of sampled blockwise hidden-memory shot processes."""

    processes: tuple[BlockwiseHiddenMemoryProcess, ...]

    @property
    def num_shots(self) -> int:
        """Return the number of sampled shot processes in the batch."""

        return len(self.processes)


@dataclass
class PreparedBlockwiseHiddenMemorySimulation:
    """Reusable per-circuit state for repeated hidden-memory sampling.

    This object holds the circuit-dependent preprocessing that does not change
    from shot to shot:

    - the fixed block partition,
    - the cumulative Clifford frame history,
    - the raw segment generators,
    - block signatures for template lookup,
    - and a persistent per-configuration cache.

    The optional profiling fields provide lightweight visibility into where the
    exact block-probability work is going during repeated sampling.
    """

    model: SharedQuasiStaticModel
    circuit: CircuitDescription
    window_size: int
    export_config: SparseExportConfig
    blocks: tuple[BlockDescriptor, ...]
    frame_history: CliffordFrameHistory
    segment_generators: tuple
    block_signatures: tuple
    cache: UltraBlockTemplateCache = field(default_factory=UltraBlockTemplateCache)
    block_candidate_support_sizes: dict[int, int] = field(default_factory=dict)
    block_compute_seconds: dict[int, float] = field(default_factory=dict)


@dataclass(frozen=True)
class _ParallelWorkerResult:
    """One worker-local Monte Carlo chunk result."""

    processes: tuple[BlockwiseHiddenMemoryProcess, ...]
    block_candidate_support_sizes: dict[int, int]
    block_compute_seconds: dict[int, float]


def prepare_blockwise_hidden_memory_simulation(
    model: SharedQuasiStaticModel,
    circuit: CircuitDescription,
    *,
    window_size: int,
    export_config: SparseExportConfig | None = None,
) -> PreparedBlockwiseHiddenMemorySimulation:
    """Prepare reusable circuit-side state for repeated shot sampling."""

    active_export_config = export_config if export_config is not None else SparseExportConfig()
    blocks = build_fixed_window_blocks(circuit, window_size=window_size)
    frame_history = build_clifford_frame_history(circuit, model.num_qubits)
    segment_generators = build_segment_generators(model, frame_history)
    block_signatures = tuple(
        build_block_signature(
            block=block,
            segment_generators=segment_generators,
        )
        for block in blocks
    )
    return PreparedBlockwiseHiddenMemorySimulation(
        model=model,
        circuit=circuit,
        window_size=window_size,
        export_config=active_export_config,
        blocks=blocks,
        frame_history=frame_history,
        segment_generators=segment_generators,
        block_signatures=block_signatures,
    )


def build_blockwise_hidden_memory_process(
    model: SharedQuasiStaticModel,
    circuit: CircuitDescription,
    *,
    window_size: int,
    export_config: SparseExportConfig | None = None,
    memory: HiddenMemorySample | None = None,
    rng: np.random.Generator | None = None,
) -> BlockwiseHiddenMemoryProcess:
    """Build one sampled blockwise hidden-memory process.

    The first implementation uses fixed-width contiguous blocks.  This is enough
    to realize the canonical sanity checks from ``thought-2-Ultra.md``.
    """

    prepared = prepare_blockwise_hidden_memory_simulation(
        model,
        circuit,
        window_size=window_size,
        export_config=export_config,
    )
    return build_prepared_blockwise_hidden_memory_process(
        prepared,
        memory=memory,
        rng=rng,
    )


def build_prepared_blockwise_hidden_memory_process(
    prepared: PreparedBlockwiseHiddenMemorySimulation,
    *,
    memory: HiddenMemorySample | None = None,
    rng: np.random.Generator | None = None,
) -> BlockwiseHiddenMemoryProcess:
    """Build one sampled process from precomputed circuit-side state."""

    generator = rng if rng is not None else np.random.default_rng()
    active_memory = memory if memory is not None else sample_hidden_memory(prepared.model, rng=generator)

    block_channels: list[SparseBlockFaultDistribution] = []
    block_faults: list[BlockFaultChoice] = []
    for block, block_signature in zip(prepared.blocks, prepared.block_signatures):
        block_channel = prepared.cache.get(
            signature=block_signature,
            xi_value=active_memory.xi,
            export_config=prepared.export_config,
        )
        if block_channel is None:
            start = perf_counter()
            supported_search = build_supported_block_probability_search(
                block=block,
                xi_value=active_memory.xi,
                segment_generators=prepared.segment_generators,
            )
            block_channel = export_sparse_probabilities(
                block=block,
                xi=active_memory.xi,
                probabilities=supported_search.probabilities,
                config=prepared.export_config,
                source_support_size=supported_search.candidate_support_size,
            )
            prepared.cache.put(
                signature=block_signature,
                xi_value=active_memory.xi,
                export_config=prepared.export_config,
                distribution=block_channel,
            )
            prepared.block_candidate_support_sizes[block.block_index] = max(
                prepared.block_candidate_support_sizes.get(block.block_index, 0),
                supported_search.candidate_support_size,
            )
            prepared.block_compute_seconds[block.block_index] = (
                prepared.block_compute_seconds.get(block.block_index, 0.0)
                + (perf_counter() - start)
            )
        block_channels.append(block_channel)
        block_faults.append(
            _sample_block_fault(
                block_channel,
                frame_history=prepared.frame_history,
                rng=generator,
            )
        )

    return BlockwiseHiddenMemoryProcess(
        hidden_memory=active_memory,
        block_channels=tuple(block_channels),
        block_faults=tuple(block_faults),
    )


def sample_blockwise_hidden_memory_processes(
    model: SharedQuasiStaticModel,
    circuit: CircuitDescription,
    *,
    window_size: int,
    num_shots: int,
    export_config: SparseExportConfig | None = None,
    rng: np.random.Generator | None = None,
    num_workers: int | None = None,
) -> BlockwiseHiddenMemoryProcessBatch:
    """Sample a Monte Carlo batch of blockwise hidden-memory shot processes.

    When ``num_workers`` is greater than one, trajectories are split into
    worker-local chunks and sampled in parallel across processes. Each worker
    prepares its own circuit-side state once, then samples its assigned chunk
    serially with an independent RNG stream.
    """

    if num_shots < 1:
        raise ValueError("num_shots must be positive.")
    if num_workers is not None and num_workers < 1:
        raise ValueError("num_workers must be positive when provided.")

    generator = rng if rng is not None else np.random.default_rng()
    active_num_workers = 1 if num_workers is None else num_workers
    if active_num_workers == 1 or num_shots == 1:
        prepared = prepare_blockwise_hidden_memory_simulation(
            model,
            circuit,
            window_size=window_size,
            export_config=export_config,
        )
        processes = tuple(
            build_prepared_blockwise_hidden_memory_process(
                prepared,
                rng=generator,
            )
            for _ in range(num_shots)
        )
        return BlockwiseHiddenMemoryProcessBatch(processes=processes)

    capped_num_workers = min(active_num_workers, num_shots, os.cpu_count() or 1)
    worker_shot_counts = _build_worker_shot_counts(
        num_shots=num_shots,
        num_workers=capped_num_workers,
    )
    root_seed_sequence = np.random.SeedSequence(int(generator.integers(0, 2**63)))
    worker_inputs = tuple(
        (
            model,
            circuit,
            window_size,
            export_config,
            shot_count,
            worker_seed_sequence,
        )
        for shot_count, worker_seed_sequence in zip(
            worker_shot_counts,
            root_seed_sequence.spawn(len(worker_shot_counts)),
        )
    )

    worker_results: list[_ParallelWorkerResult] = []
    with ProcessPoolExecutor(
        max_workers=capped_num_workers,
        mp_context=get_context("spawn"),
    ) as executor:
        for worker_result in executor.map(_sample_process_chunk_in_worker, worker_inputs):
            worker_results.append(worker_result)

    merged_processes: list[BlockwiseHiddenMemoryProcess] = []
    for worker_result in worker_results:
        merged_processes.extend(worker_result.processes)
    return BlockwiseHiddenMemoryProcessBatch(processes=tuple(merged_processes))


def _build_worker_shot_counts(*, num_shots: int, num_workers: int) -> tuple[int, ...]:
    """Split ``num_shots`` into near-equal positive worker chunk sizes."""

    base_count, remainder = divmod(num_shots, num_workers)
    return tuple(
        base_count + (1 if worker_index < remainder else 0)
        for worker_index in range(num_workers)
        if base_count + (1 if worker_index < remainder else 0) > 0
    )


def _sample_process_chunk_in_worker(
    worker_input: tuple[
        SharedQuasiStaticModel,
        CircuitDescription,
        int,
        SparseExportConfig | None,
        int,
        np.random.SeedSequence,
    ],
) -> _ParallelWorkerResult:
    """Worker entrypoint for one Monte Carlo chunk."""

    model, circuit, window_size, export_config, num_shots, worker_seed_sequence = worker_input
    prepared = prepare_blockwise_hidden_memory_simulation(
        model,
        circuit,
        window_size=window_size,
        export_config=export_config,
    )
    generator = np.random.default_rng(worker_seed_sequence)
    processes = tuple(
        build_prepared_blockwise_hidden_memory_process(
            prepared,
            rng=generator,
        )
        for _ in range(num_shots)
    )
    return _ParallelWorkerResult(
        processes=processes,
        block_candidate_support_sizes=dict(prepared.block_candidate_support_sizes),
        block_compute_seconds=dict(prepared.block_compute_seconds),
    )


def _sample_block_fault(
    block_channel: SparseBlockFaultDistribution,
    *,
    frame_history: CliffordFrameHistory,
    rng: np.random.Generator,
) -> BlockFaultChoice:
    """Sample one block fault from a conditional toggling-frame Pauli channel.

    The returned object carries both the toggling-frame sampled fault and the
    corresponding physical inserted fault after the ideal block.
    """

    random_value = float(rng.random())
    cumulative = 0.0
    identity_label = "I" * len(next(iter(block_channel.probabilities)))

    for pauli_string, probability in block_channel.probabilities.items():
        cumulative += probability
        if random_value < cumulative:
            toggling_frame_pauli_string = (
                None if pauli_string == identity_label else pauli_string
            )
            return BlockFaultChoice(
                block_index=block_channel.block.block_index,
                toggling_frame_pauli_string=toggling_frame_pauli_string,
                physical_pauli_string=_map_toggling_fault_to_physical(
                    toggling_frame_pauli_string=toggling_frame_pauli_string,
                    segment_index=block_channel.block.end_segment,
                    frame_history=frame_history,
                ),
                probability=probability,
            )

    last_pauli_string = next(reversed(block_channel.probabilities))
    toggling_frame_pauli_string = (
        None if last_pauli_string == identity_label else last_pauli_string
    )
    return BlockFaultChoice(
        block_index=block_channel.block.block_index,
        toggling_frame_pauli_string=toggling_frame_pauli_string,
        physical_pauli_string=_map_toggling_fault_to_physical(
            toggling_frame_pauli_string=toggling_frame_pauli_string,
            segment_index=block_channel.block.end_segment,
            frame_history=frame_history,
        ),
        probability=block_channel.probabilities[last_pauli_string],
    )


def _map_toggling_fault_to_physical(
    *,
    toggling_frame_pauli_string: str | None,
    segment_index: int,
    frame_history: CliffordFrameHistory,
) -> str | None:
    """Map a toggling-frame block fault to the physical inserted fault."""

    if toggling_frame_pauli_string is None:
        return None
    return frame_history.propagate_pauli_to_segment(
        toggling_frame_pauli_string,
        segment_index,
    )
