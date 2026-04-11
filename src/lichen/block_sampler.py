"""Shot-level sampler for the blockwise hidden-memory env construction.

This module turns the blockwise conditional Pauli channels into a simulator-
facing sampled process: one hidden-memory value per shot, one Pauli fault
sampled after each ideal block.

The first `ultra` implementation materialized the full block Pauli channel for
every block. That is still available as the oracle path, but the sampler now
consumes a sparse exported distribution instead. This keeps the interface
compatible with notebook inspection while making it possible to truncate and
cache the simulator-facing block alphabet.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .hidden_memory import HiddenMemorySample, sample_hidden_memory
from .model import SharedQuasiStaticModel
from .frame_tracker import build_clifford_frame_history
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
    """One sampled block fault from a conditional block Pauli channel."""

    block_index: int
    pauli_string: str | None
    probability: float


@dataclass(frozen=True)
class BlockwiseHiddenMemoryProcess:
    """One full-shot blockwise hidden-memory sampled process."""

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

    generator = rng if rng is not None else np.random.default_rng()
    active_memory = memory if memory is not None else sample_hidden_memory(model, rng=generator)
    active_export_config = export_config if export_config is not None else SparseExportConfig()
    blocks = build_fixed_window_blocks(circuit, window_size=window_size)
    frame_history = build_clifford_frame_history(circuit, model.num_qubits)
    segment_generators = build_segment_generators(model, frame_history)
    cache = UltraBlockTemplateCache()

    block_channels: list[SparseBlockFaultDistribution] = []
    block_faults: list[BlockFaultChoice] = []
    for block in blocks:
        block_signature = build_block_signature(
            block=block,
            segment_generators=segment_generators,
        )
        block_channel = cache.get(
            signature=block_signature,
            xi_value=active_memory.xi,
            export_config=active_export_config,
        )
        if block_channel is None:
            supported_search = build_supported_block_probability_search(
                block=block,
                xi_value=active_memory.xi,
                segment_generators=segment_generators,
            )
            block_channel = export_sparse_probabilities(
                block=block,
                xi=active_memory.xi,
                probabilities=supported_search.probabilities,
                config=active_export_config,
                source_support_size=supported_search.candidate_support_size,
            )
            cache.put(
                signature=block_signature,
                xi_value=active_memory.xi,
                export_config=active_export_config,
                distribution=block_channel,
            )
        block_channels.append(block_channel)
        block_faults.append(_sample_block_fault(block_channel, rng=generator))

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
) -> BlockwiseHiddenMemoryProcessBatch:
    """Sample a Monte Carlo batch of blockwise hidden-memory shot processes."""

    if num_shots < 1:
        raise ValueError("num_shots must be positive.")

    generator = rng if rng is not None else np.random.default_rng()
    processes = tuple(
        build_blockwise_hidden_memory_process(
            model,
            circuit,
            window_size=window_size,
            export_config=export_config,
            rng=generator,
        )
        for _ in range(num_shots)
    )
    return BlockwiseHiddenMemoryProcessBatch(processes=processes)


def _sample_block_fault(
    block_channel: SparseBlockFaultDistribution,
    *,
    rng: np.random.Generator,
) -> BlockFaultChoice:
    """Sample one Pauli fault from a conditional block Pauli channel.

    The identity Pauli `I...I` is represented as `None` in the sampled process,
    because assembly only needs to insert explicit nontrivial faults.
    """

    random_value = float(rng.random())
    cumulative = 0.0
    identity_label = "I" * len(next(iter(block_channel.probabilities)))

    for pauli_string, probability in block_channel.probabilities.items():
        cumulative += probability
        if random_value < cumulative:
            return BlockFaultChoice(
                block_index=block_channel.block.block_index,
                pauli_string=None if pauli_string == identity_label else pauli_string,
                probability=probability,
            )

    last_pauli_string = next(reversed(block_channel.probabilities))
    return BlockFaultChoice(
        block_index=block_channel.block.block_index,
        pauli_string=None if last_pauli_string == identity_label else last_pauli_string,
        probability=block_channel.probabilities[last_pauli_string],
    )
