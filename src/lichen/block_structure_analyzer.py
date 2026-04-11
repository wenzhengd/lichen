"""Structural analysis tools for `window_size = 2` blockwise env construction.

The first `ultra` implementation uses dense exact block propagation. That is a
useful correctness baseline, but it does not answer the more important scaling
question:

    is the cost fundamental, or did we fail to exploit obvious block structure?

This module inspects two-segment blocks directly in the signed-Pauli generator
representation. The goal is to identify algebraic reductions before paying for
full dense block projection.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from .circuit import CircuitDescription
from .frame_tracker import build_clifford_frame_history
from .model import SharedQuasiStaticModel
from .pauli import SignedPauliTerm, pauli_commutation_sign
from .segment_generators import SegmentGenerator, build_segment_generators
from .block_partition import BlockDescriptor, build_fixed_window_blocks, validate_blocks_against_circuit


@dataclass(frozen=True)
class GeneratorMultiplicitySummary:
    """Compressed signed-Pauli summary of one segment generator."""

    signed_counts: dict[str, int]
    distinct_labels: tuple[str, ...]


@dataclass(frozen=True)
class AnticommutationComponent:
    """One connected component of the term anticommutation graph."""

    labels: tuple[str, ...]
    size: int
    support_width: int
    support_qubits: tuple[int, ...]


@dataclass(frozen=True)
class TwoSegmentBlockStructure:
    """Structural summary for one `window_size = 2` block."""

    block: BlockDescriptor
    generator_1: GeneratorMultiplicitySummary
    generator_2: GeneratorMultiplicitySummary
    generators_equal: bool
    generators_negatives: bool
    all_cross_terms_commute: bool
    num_components: int
    max_component_size: int
    components: tuple[AnticommutationComponent, ...]


def analyze_two_segment_blocks(
    model: SharedQuasiStaticModel,
    circuit: CircuitDescription,
) -> tuple[TwoSegmentBlockStructure, ...]:
    """Analyze all fixed `window_size = 2` blocks in a circuit."""

    blocks = build_fixed_window_blocks(circuit, window_size=2)
    validate_blocks_against_circuit(blocks, circuit)
    frame_history = build_clifford_frame_history(circuit, model.num_qubits)
    segments = build_segment_generators(model, frame_history)

    analyses: list[TwoSegmentBlockStructure] = []
    for block in blocks:
        if block.num_segments != 2:
            continue
        analyses.append(_analyze_one_block(block, segments))
    return tuple(analyses)


def _analyze_one_block(
    block: BlockDescriptor,
    segments: tuple[SegmentGenerator, ...],
) -> TwoSegmentBlockStructure:
    """Analyze one two-segment block from the raw segment generators."""

    segment_1 = segments[block.start_segment]
    segment_2 = segments[block.end_segment]

    summary_1 = _summarize_generator(segment_1.terms)
    summary_2 = _summarize_generator(segment_2.terms)

    generators_equal = summary_1.signed_counts == summary_2.signed_counts
    generators_negatives = summary_1.signed_counts == {
        label: -count for label, count in summary_2.signed_counts.items()
    }

    all_cross_terms_commute = True
    for term_1 in summary_1.distinct_labels:
        for term_2 in summary_2.distinct_labels:
            if pauli_commutation_sign(term_1, term_2) == -1:
                all_cross_terms_commute = False
                break
        if not all_cross_terms_commute:
            break

    components = _anticommutation_components(
        tuple(sorted(set(summary_1.distinct_labels) | set(summary_2.distinct_labels)))
    )
    return TwoSegmentBlockStructure(
        block=block,
        generator_1=summary_1,
        generator_2=summary_2,
        generators_equal=generators_equal,
        generators_negatives=generators_negatives,
        all_cross_terms_commute=all_cross_terms_commute,
        num_components=len(components),
        max_component_size=max((component.size for component in components), default=0),
        components=components,
    )


def _summarize_generator(terms: tuple[SignedPauliTerm, ...]) -> GeneratorMultiplicitySummary:
    """Compress signed Pauli terms into a label -> signed multiplicity map."""

    signed_counts: dict[str, int] = defaultdict(int)
    for term in terms:
        signed_counts[term.pauli_string] += term.sign
    cleaned = {label: count for label, count in signed_counts.items() if count != 0}
    return GeneratorMultiplicitySummary(
        signed_counts=dict(sorted(cleaned.items())),
        distinct_labels=tuple(sorted(cleaned)),
    )


def _anticommutation_components(labels: tuple[str, ...]) -> tuple[AnticommutationComponent, ...]:
    """Build connected components of the Pauli-term anticommutation graph."""

    if not labels:
        return ()

    adjacency: dict[str, set[str]] = {label: set() for label in labels}
    for left_index, left in enumerate(labels):
        for right in labels[left_index + 1 :]:
            if pauli_commutation_sign(left, right) == -1:
                adjacency[left].add(right)
                adjacency[right].add(left)

    remaining = set(labels)
    components: list[AnticommutationComponent] = []
    while remaining:
        root = remaining.pop()
        stack = [root]
        component = {root}
        while stack:
            current = stack.pop()
            for neighbor in adjacency[current]:
                if neighbor in remaining:
                    remaining.remove(neighbor)
                    component.add(neighbor)
                    stack.append(neighbor)

        sorted_labels = tuple(sorted(component))
        components.append(
            AnticommutationComponent(
                labels=sorted_labels,
                size=len(sorted_labels),
                support_width=_support_width(sorted_labels),
                support_qubits=_support_qubits(sorted_labels),
            )
        )

    components.sort(key=lambda component: (-component.size, component.labels))
    return tuple(components)


def _support_width(labels: tuple[str, ...]) -> int:
    """Return the number of qubits touched by at least one label in a component."""

    if not labels:
        return 0
    touched = 0
    for qubit_letters in zip(*labels):
        if any(letter != "I" for letter in qubit_letters):
            touched += 1
    return touched


def _support_qubits(labels: tuple[str, ...]) -> tuple[int, ...]:
    """Return the sorted tuple of qubits touched by a component."""

    if not labels:
        return ()
    touched: list[int] = []
    for index, qubit_letters in enumerate(zip(*labels)):
        if any(letter != "I" for letter in qubit_letters):
            touched.append(index)
    return tuple(touched)
