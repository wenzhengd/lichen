"""Track cumulative ideal Clifford frames for the env-side approximation.

The diagonal-env approximation in ``thought-2-pro.md`` is driven by the
cumulative Clifford frames

    G_j = C_j C_{j-1} ... C_1

before each noisy segment.  This module computes those frames in a way that is
directly useful for Pauli-basis propagation.
"""

from __future__ import annotations

from dataclasses import dataclass

from .circuit import CircuitDescription, CircuitLayer
from .pauli import (
    conjugate_pauli_by_gate,
    conjugate_pauli_by_gate_with_sign,
    validate_pauli_string,
)


@dataclass(frozen=True)
class CliffordFrameHistory:
    """Cumulative Clifford frame history for env-noise tracking.

    Each stored layer is the cumulative ideal circuit prefix before one noisy
    segment.  In the current convention, segment ``j`` occurs after ideal
    layer ``j``, so ``cumulative_layers[j]`` corresponds to the frame built
    from layers ``0..j``.
    """

    num_qubits: int
    cumulative_layers: tuple[CircuitLayer, ...]

    @property
    def num_segments(self) -> int:
        """Return the number of noisy segments represented by the history."""

        return len(self.cumulative_layers)

    def propagate_pauli_to_segment(self, pauli_string: str, segment_index: int) -> str:
        """Return ``G_j B G_j^dagger`` for the chosen segment and Pauli string."""

        validate_pauli_string(pauli_string, expected_num_qubits=self.num_qubits)
        if segment_index < 0 or segment_index >= self.num_segments:
            raise ValueError(
                f"segment_index must be between 0 and {self.num_segments - 1}, got {segment_index}."
            )

        propagated = pauli_string
        for layer in self.cumulative_layers[: segment_index + 1]:
            propagated = conjugate_pauli_by_gate(propagated, layer.gate_name, layer.qubits)
        return propagated

    def propagate_signed_pauli_to_segment(self, pauli_string: str, segment_index: int) -> tuple[int, str]:
        """Return ``(+/-1, label)`` for ``G_j B G_j^dagger``.

        This is needed when the sign of the propagated Pauli matters, as in the
        construction of the toggling-frame generators ``A_j`` for the env model.
        """

        validate_pauli_string(pauli_string, expected_num_qubits=self.num_qubits)
        if segment_index < 0 or segment_index >= self.num_segments:
            raise ValueError(
                f"segment_index must be between 0 and {self.num_segments - 1}, got {segment_index}."
            )

        sign = 1
        propagated = pauli_string
        for layer in self.cumulative_layers[: segment_index + 1]:
            layer_sign, propagated = conjugate_pauli_by_gate_with_sign(
                propagated, layer.gate_name, layer.qubits
            )
            sign *= layer_sign
        return sign, propagated


def build_clifford_frame_history(circuit: CircuitDescription, num_qubits: int) -> CliffordFrameHistory:
    """Build cumulative Clifford frames from an ideal circuit description.

    The env approximation only supports the project gate policy: single-qubit
    Clifford gates from ``docs/stim_gate_support.md`` and ``CNOT`` as the only
    two-qubit Clifford gate.
    """

    if num_qubits < 1:
        raise ValueError("num_qubits must be positive.")
    if not circuit.layers:
        raise ValueError("The ideal circuit must contain at least one layer.")

    for layer in circuit.layers:
        _validate_layer(layer, num_qubits)

    return CliffordFrameHistory(num_qubits=num_qubits, cumulative_layers=circuit.layers)


def _validate_layer(layer: CircuitLayer, num_qubits: int) -> None:
    """Validate that the layer is compatible with env-side Clifford tracking."""

    for qubit in layer.qubits:
        if qubit < 0 or qubit >= num_qubits:
            raise ValueError(
                f"Layer {layer.layer_index} uses out-of-range qubit {qubit} for {num_qubits} qubits."
            )

    if len(layer.qubits) == 1:
        # Validation is deferred to the Pauli conjugation helper so that there is
        # only one source of truth for supported single-qubit Clifford names.
        conjugate_pauli_by_gate("I" * num_qubits, layer.gate_name, layer.qubits)
        return

    if len(layer.qubits) == 2 and layer.gate_name == "CNOT":
        conjugate_pauli_by_gate("I" * num_qubits, layer.gate_name, layer.qubits)
        return

    raise ValueError(
        "Env Clifford tracking only supports single-qubit Clifford gates and 2-qubit CNOT layers. "
        f"Unsupported layer: {layer.gate_name} on {layer.qubits}."
    )
