"""Blockwise Pauli projection for the hidden-memory env construction.

This module supports two paths:

- a dense fallback, which projects the full block unitary directly,
- a structure-aware path, which exactly factors the block into independent
  support-disjoint anticommutation components when available.

The second path is the first serious reduction for the `ultra` construction.
It does not change the approximation; it only exploits algebraic structure that
the initial dense implementation ignored.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

import numpy as np

from .pauli import SignedPauliTerm, enumerate_pauli_basis, pauli_commutation_sign, pauli_string_to_matrix
from .segment_generators import SegmentGenerator
from .block_partition import BlockDescriptor
from .block_propagator import exact_block_unitary_from_segment_generators
from .block_structure_analyzer import TwoSegmentBlockStructure, _analyze_one_block


@dataclass(frozen=True)
class BlockPauliChannel:
    """Conditional Pauli channel exported for one block.

    Attributes
    ----------
    block:
        Block descriptor used to define the exact conditional block unitary.
    xi:
        Hidden-memory value used for the conditional block channel.
    diagonal_spectrum:
        Retained Pauli-transfer diagonal ``B -> d_{b,B}(xi)``.
    probabilities:
        Reconstructed Pauli-channel probabilities ``P -> q_{b,P}(xi)``.
    """

    block: BlockDescriptor
    xi: float
    diagonal_spectrum: dict[str, float]
    probabilities: dict[str, float]


def build_block_pauli_channel(
    *,
    block: BlockDescriptor,
    xi_value: float,
    block_unitary: np.ndarray,
) -> BlockPauliChannel:
    """Compute the conditional block Pauli channel from an exact block unitary."""

    num_qubits = int(np.log2(block_unitary.shape[0]))
    basis = enumerate_pauli_basis(num_qubits)
    diagonal_spectrum = {
        pauli_string: retained_block_diagonal_entry(
            pauli_string=pauli_string,
            block_unitary=block_unitary,
        )
        for pauli_string in basis
    }
    probabilities = reconstruct_pauli_probabilities(diagonal_spectrum)
    return BlockPauliChannel(
        block=block,
        xi=xi_value,
        diagonal_spectrum=diagonal_spectrum,
        probabilities=probabilities,
    )


def build_block_pauli_channel_from_segment_generators(
    *,
    block: BlockDescriptor,
    xi_value: float,
    segment_generators: tuple[SegmentGenerator, ...],
) -> BlockPauliChannel:
    """Build a conditional block Pauli channel from raw segment generators.

    This entry point can exploit structure of the two-segment block before
    falling back to full dense projection.
    """

    if block.num_segments != 2:
        block_unitary = exact_block_unitary_from_segment_generators(
            segment_generators=segment_generators,
            block=block,
            xi_value=xi_value,
        )
        return build_block_pauli_channel(
            block=block,
            xi_value=xi_value,
            block_unitary=block_unitary,
        )

    structure = _analyze_one_block(block, segment_generators)
    if _has_support_disjoint_components(structure):
        probabilities = _factorized_block_probabilities(
            structure=structure,
            segment_generators=segment_generators,
            xi_value=xi_value,
        )
        diagonal_spectrum = reconstruct_block_diagonal_from_probabilities(probabilities)
        return BlockPauliChannel(
            block=block,
            xi=xi_value,
            diagonal_spectrum=diagonal_spectrum,
            probabilities=probabilities,
        )

    block_unitary = exact_block_unitary_from_segment_generators(
        segment_generators=segment_generators,
        block=block,
        xi_value=xi_value,
    )
    return build_block_pauli_channel(
        block=block,
        xi_value=xi_value,
        block_unitary=block_unitary,
    )


def retained_block_diagonal_entry(*, pauli_string: str, block_unitary: np.ndarray) -> float:
    """Evaluate ``2^-n Tr(B U_b B U_b^dagger)`` for one Pauli basis element."""

    pauli_matrix = pauli_string_to_matrix(pauli_string)
    dimension = block_unitary.shape[0]
    overlap = np.trace(
        pauli_matrix @ block_unitary @ pauli_matrix @ block_unitary.conj().T
    ) / dimension
    return float(np.real_if_close(overlap))


def reconstruct_pauli_probabilities(diagonal_spectrum: dict[str, float]) -> dict[str, float]:
    """Recover Pauli-channel probabilities from block retained-diagonal values."""

    if not diagonal_spectrum:
        raise ValueError("diagonal_spectrum must not be empty.")
    any_label = next(iter(diagonal_spectrum))
    num_qubits = len(any_label)
    basis = enumerate_pauli_basis(num_qubits)
    missing = [pauli for pauli in basis if pauli not in diagonal_spectrum]
    if missing:
        raise ValueError("diagonal_spectrum must contain the full Pauli basis.")

    normalization = 4**num_qubits
    probabilities: dict[str, float] = {}
    for pauli_string in basis:
        probability = 0.0
        for basis_pauli in basis:
            probability += (
                pauli_commutation_sign(pauli_string, basis_pauli)
                * diagonal_spectrum[basis_pauli]
            )
        probabilities[pauli_string] = probability / normalization
    return _normalize_and_clip_probabilities(probabilities)


def reconstruct_block_diagonal_from_probabilities(probabilities: dict[str, float]) -> dict[str, float]:
    """Recover the retained diagonal from a Pauli-channel probability map."""

    if not probabilities:
        raise ValueError("probabilities must not be empty.")
    any_label = next(iter(probabilities))
    num_qubits = len(any_label)
    basis = enumerate_pauli_basis(num_qubits)
    missing = [pauli for pauli in basis if pauli not in probabilities]
    if missing:
        raise ValueError("probabilities must contain the full Pauli basis.")

    diagonal_spectrum: dict[str, float] = {}
    for basis_pauli in basis:
        retained = 0.0
        for pauli_string, probability in probabilities.items():
            retained += pauli_commutation_sign(pauli_string, basis_pauli) * probability
        diagonal_spectrum[basis_pauli] = retained
    return diagonal_spectrum


def _has_support_disjoint_components(structure: TwoSegmentBlockStructure) -> bool:
    """Return whether all anticommutation components act on disjoint qubit sets."""

    seen: set[int] = set()
    for component in structure.components:
        support = set(component.support_qubits)
        if seen & support:
            return False
        seen |= support
    return True


def _factorized_block_probabilities(
    *,
    structure: TwoSegmentBlockStructure,
    segment_generators: tuple[SegmentGenerator, ...],
    xi_value: float,
) -> dict[str, float]:
    """Exactly combine support-disjoint component channels into the full block channel."""

    num_qubits = len(segment_generators[0].terms[0].pauli_string)
    component_probabilities: list[tuple[tuple[int, ...], dict[str, float]]] = []

    for component in structure.components:
        support = component.support_qubits
        local_segment_generators = _restrict_block_generators_to_support(
            segment_generators=segment_generators,
            block=structure.block,
            support_qubits=support,
        )
        local_block = BlockDescriptor(
            block_index=structure.block.block_index,
            start_segment=0,
            end_segment=1,
        )
        local_unitary = exact_block_unitary_from_segment_generators(
            segment_generators=local_segment_generators,
            block=local_block,
            xi_value=xi_value,
        )
        local_channel = build_block_pauli_channel(
            block=local_block,
            xi_value=xi_value,
            block_unitary=local_unitary,
        )
        component_probabilities.append((support, local_channel.probabilities))

    full_probabilities = {"I" * num_qubits: 1.0}
    for support, local_probabilities in component_probabilities:
        updated: defaultdict[str, float] = defaultdict(float)
        for global_label, global_probability in full_probabilities.items():
            for local_label, local_probability in local_probabilities.items():
                lifted = _lift_local_pauli_to_global(
                    local_label=local_label,
                    support_qubits=support,
                    num_qubits=num_qubits,
                )
                merged = _merge_pauli_labels(global_label, lifted)
                updated[merged] += global_probability * local_probability
        full_probabilities = dict(updated)

    full_basis = enumerate_pauli_basis(num_qubits)
    return {pauli_string: full_probabilities.get(pauli_string, 0.0) for pauli_string in full_basis}


def _restrict_block_generators_to_support(
    *,
    segment_generators: tuple[SegmentGenerator, ...],
    block: BlockDescriptor,
    support_qubits: tuple[int, ...],
) -> tuple[SegmentGenerator, ...]:
    """Restrict the two raw segment generators of a block to one support component."""

    restricted_segments: list[SegmentGenerator] = []
    for offset, segment_index in enumerate(range(block.start_segment, block.end_segment + 1)):
        segment = segment_generators[segment_index]
        restricted_terms = []
        for term in segment.terms:
            local_label = "".join(term.pauli_string[qubit] for qubit in support_qubits)
            if local_label != "I" * len(support_qubits):
                restricted_terms.append(type(term)(sign=term.sign, pauli_string=local_label))
        if not restricted_terms:
            restricted_terms.append(
                SignedPauliTerm(sign=1, pauli_string="I" * len(support_qubits))
            )
        restricted_segments.append(
            SegmentGenerator(
                segment_index=offset,
                duration=segment.duration,
                terms=tuple(restricted_terms),
            )
        )
    return tuple(restricted_segments)


def _lift_local_pauli_to_global(
    *,
    local_label: str,
    support_qubits: tuple[int, ...],
    num_qubits: int,
) -> str:
    """Embed a local Pauli label on its component support into the full system."""

    letters = ["I"] * num_qubits
    for local_index, qubit in enumerate(support_qubits):
        letters[qubit] = local_label[local_index]
    return "".join(letters)


def _merge_pauli_labels(left: str, right: str) -> str:
    """Merge two support-disjoint Pauli labels."""

    merged: list[str] = []
    for left_letter, right_letter in zip(left, right):
        if left_letter != "I" and right_letter != "I":
            raise ValueError("Component supports are not disjoint; cannot merge Pauli labels.")
        merged.append(right_letter if left_letter == "I" else left_letter)
    return "".join(merged)


def _normalize_and_clip_probabilities(probabilities: dict[str, float]) -> dict[str, float]:
    """Clip tiny numerical negatives and renormalize the block channel."""

    cleaned: dict[str, float] = {}
    for pauli_string, probability in probabilities.items():
        if abs(probability) < 1e-12:
            probability = 0.0
        if probability < -1e-10:
            raise ValueError(
                "Recovered block Pauli probability is significantly negative. "
                "This indicates either numerical instability or an inconsistent block spectrum."
            )
        cleaned[pauli_string] = max(probability, 0.0)

    total_probability = sum(cleaned.values())
    if total_probability <= 0.0:
        raise ValueError("Recovered block Pauli probabilities have non-positive total weight.")

    return {
        pauli_string: probability / total_probability
        for pauli_string, probability in cleaned.items()
    }
