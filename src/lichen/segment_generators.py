"""Segment-level toggling-frame generators for the hidden-memory env model.

This module is the first layer of the ``thought-2-Max`` construction.

For each noisy segment ``j``, the shared quasi-static dephasing generator is

    A_j = G_j^\dagger (sum_a Z_a) G_j

where ``G_j`` is the cumulative ideal Clifford frame before that segment.
Because ``G_j`` is Clifford, every propagated ``Z_a`` remains a signed Pauli
string.  The natural code object is therefore not a dense matrix, but an
explicit list of signed Pauli terms.

The output of this module is reused by both:

- the older retained-diagonal/global-channel analysis path, and
- the newer hidden-memory sparse per-segment sampler.
"""

from __future__ import annotations

from dataclasses import dataclass

from .frame_tracker import CliffordFrameHistory
from .model import SharedQuasiStaticModel
from .pauli import SignedPauliTerm, single_qubit_pauli_string


@dataclass(frozen=True)
class SegmentGenerator:
    """One toggling-frame segment generator in signed-Pauli form.

    Attributes
    ----------
    segment_index:
        Zero-based segment index.
    duration:
        Duration ``Delta_j`` of the noisy interval.
    terms:
        Signed Pauli strings appearing in

            A_j = sum_a sign_{a,j} P_{a,j}.

        These terms commute within a segment because they arise from conjugated
        single-qubit ``Z`` operators under one Clifford frame.
    """

    segment_index: int
    duration: float
    terms: tuple[SignedPauliTerm, ...]


def build_segment_generators(
    model: SharedQuasiStaticModel,
    frame_history: CliffordFrameHistory,
) -> tuple[SegmentGenerator, ...]:
    """Build all segment generators for the shared-memory env process.

    This is the direct code counterpart of Eq. (7) in
    ``docs/thoughts/thought-2-Max.md``.  The function is intentionally simple:
    given the ideal Clifford history, propagate each physical ``Z_a`` into the
    toggling frame of each segment and store the resulting signed Pauli labels.
    """

    _validate_model_and_history(model, frame_history)

    generators: list[SegmentGenerator] = []
    for segment_index, duration in enumerate(model.segment_durations):
        terms: list[SignedPauliTerm] = []
        for qubit in range(model.num_qubits):
            z_pauli = single_qubit_pauli_string(model.num_qubits, qubit, "Z")
            sign, propagated = frame_history.propagate_signed_pauli_to_segment(
                z_pauli,
                segment_index,
            )
            terms.append(SignedPauliTerm(sign=sign, pauli_string=propagated))
        generators.append(
            SegmentGenerator(
                segment_index=segment_index,
                duration=duration,
                terms=tuple(terms),
            )
        )
    return tuple(generators)


def _validate_model_and_history(
    model: SharedQuasiStaticModel,
    frame_history: CliffordFrameHistory,
) -> None:
    """Validate that the model and frame history describe the same circuit."""

    if model.num_qubits != frame_history.num_qubits:
        raise ValueError(
            "SharedQuasiStaticModel and CliffordFrameHistory must use the same num_qubits."
        )
    if model.num_segments != frame_history.num_segments:
        raise ValueError(
            "The number of segment durations must match the number of tracked Clifford frames."
        )
