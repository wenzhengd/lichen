"""Exact short-block propagator for the blockwise hidden-memory env model.

This module implements the "keep coherence inside a short block, then project"
part of ``thought-2-Ultra.md``.  The first implementation uses dense matrices,
which is acceptable because blocks are intended to stay short and are mainly a
correctness-oriented starting point.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .hidden_memory import HiddenMemorySample
from .model import SharedQuasiStaticModel
from .pauli import SignedPauliTerm, pauli_string_to_matrix
from .segment_generators import SegmentGenerator, build_segment_generators
from .block_partition import BlockDescriptor
from .circuit import CircuitDescription
from .frame_tracker import build_clifford_frame_history


@dataclass(frozen=True)
class ExactBlockUnitary:
    """One exact conditional env unitary for a block and hidden-memory value."""

    block: BlockDescriptor
    xi: float
    unitary: np.ndarray


def build_exact_block_unitary(
    *,
    model: SharedQuasiStaticModel,
    circuit: CircuitDescription,
    block: BlockDescriptor,
    memory: HiddenMemorySample,
) -> ExactBlockUnitary:
    """Build the exact conditional env unitary for one block.

    The unitary is

        U_b(xi) = prod_{j=e_b}^{s_b} exp(-i xi Delta_j A_j),

    exactly as written in ``thought-2-Ultra.md``.
    """

    segment_generators = _build_segment_generators(model, circuit)
    unitary = exact_block_unitary_from_segment_generators(
        segment_generators=segment_generators,
        block=block,
        xi_value=memory.xi,
    )
    return ExactBlockUnitary(block=block, xi=memory.xi, unitary=unitary)


def exact_block_unitary_from_segment_generators(
    *,
    segment_generators: tuple[SegmentGenerator, ...],
    block: BlockDescriptor,
    xi_value: float,
) -> np.ndarray:
    """Construct ``U_b(xi)`` directly from segment generators.

    The segment generators already include the signed toggling-frame Paulis
    `A_j = sum_a sign_{a,j} P_{a,j}`.  The block unitary multiplies the segment
    unitaries in circuit order.
    """

    if not segment_generators:
        raise ValueError("segment_generators must not be empty.")

    num_qubits = len(segment_generators[0].terms[0].pauli_string)
    dimension = 2**num_qubits
    unitary = np.eye(dimension, dtype=complex)

    for segment_index in range(block.start_segment, block.end_segment + 1):
        segment = segment_generators[segment_index]
        generator_matrix = _segment_generator_to_matrix(segment.terms)
        segment_unitary = _matrix_exponential_from_hermitian(
            scale=-1.0j * xi_value * segment.duration,
            hermitian_matrix=generator_matrix,
        )
        unitary = segment_unitary @ unitary
    return unitary


def _build_segment_generators(
    model: SharedQuasiStaticModel,
    circuit: CircuitDescription,
) -> tuple[SegmentGenerator, ...]:
    """Build segment generators once for the full circuit."""

    frame_history = build_clifford_frame_history(circuit, model.num_qubits)
    return build_segment_generators(model, frame_history)


def _segment_generator_to_matrix(terms: tuple[SignedPauliTerm, ...]) -> np.ndarray:
    """Convert a signed-Pauli segment generator into its dense matrix."""

    dimension = 2 ** len(terms[0].pauli_string)
    generator = np.zeros((dimension, dimension), dtype=complex)
    for term in terms:
        generator = generator + term.sign * pauli_string_to_matrix(term.pauli_string)
    return generator


def _matrix_exponential_from_hermitian(*, scale: complex, hermitian_matrix: np.ndarray) -> np.ndarray:
    """Exponentiate a Hermitian matrix by eigendecomposition."""

    eigenvalues, eigenvectors = np.linalg.eigh(hermitian_matrix)
    phase_factors = np.exp(scale * eigenvalues)
    return eigenvectors @ np.diag(phase_factors) @ eigenvectors.conj().T
