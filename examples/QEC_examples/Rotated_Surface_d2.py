"""Distance-2 rotated surface-code syndrome round for lichen.

This example uses the smallest planar rotated surface code:

- 4 data qubits carrying the ``[[4, 1, 2]]`` code state,
- 3 ancilla qubits for one syndrome-extraction round,
- 7 total qubits, matching the smallest Stim-generated rotated-memory layout.

The ideal circuit here is a single Clifford syndrome-extraction round with:

- one X-type ancilla measuring ``X0 X1 X2 X3``,
- two Z-type ancillas measuring ``Z0 Z1`` and ``Z2 Z3``.

The current ``lichen`` package does not model reset/measurement as first-class
gates, so this example stops at the entangling Clifford schedule. That still
provides a realistic small surface-code control pattern for noisy simulation.
"""

from __future__ import annotations

from dataclasses import dataclass

from lichen import CircuitDescription, CircuitLayer


TOTAL_QUBITS = 7
DATA_QUBITS: tuple[int, ...] = (0, 1, 2, 3)
X_ANCILLA = 4
Z_ANCILLAS: tuple[int, int] = (5, 6)


@dataclass(frozen=True)
class RotatedSurfaceD2Layout:
    """Named qubit layout for the distance-2 rotated surface-code example."""

    total_qubits: int = TOTAL_QUBITS
    data_qubits: tuple[int, ...] = DATA_QUBITS
    x_ancilla: int = X_ANCILLA
    z_ancillas: tuple[int, int] = Z_ANCILLAS
    x_stabilizer_support: tuple[int, ...] = DATA_QUBITS
    z_stabilizer_supports: tuple[tuple[int, int], ...] = (
        (0, 1),
        (2, 3),
    )


def build_rotated_surface_d2_syndrome_circuit() -> CircuitDescription:
    """Return one Clifford syndrome-extraction round for the d=2 rotated patch."""

    layers: list[CircuitLayer] = []

    def append(gate_name: str, qubits: tuple[int, ...], *, note: str) -> None:
        layers.append(
            CircuitLayer(
                layer_index=len(layers),
                gate_name=gate_name,
                qubits=qubits,
                metadata={"note": note},
            )
        )

    append("H", (X_ANCILLA,), note="prepare X-check ancilla in the X basis")

    for data_qubit in DATA_QUBITS:
        append(
            "CNOT",
            (X_ANCILLA, data_qubit),
            note=f"couple X ancilla to data qubit {data_qubit}",
        )

    append(
        "CNOT",
        (0, Z_ANCILLAS[0]),
        note="left Z-check: data qubit 0 into ancilla 5",
    )
    append(
        "CNOT",
        (1, Z_ANCILLAS[0]),
        note="left Z-check: data qubit 1 into ancilla 5",
    )
    append(
        "CNOT",
        (2, Z_ANCILLAS[1]),
        note="right Z-check: data qubit 2 into ancilla 6",
    )
    append(
        "CNOT",
        (3, Z_ANCILLAS[1]),
        note="right Z-check: data qubit 3 into ancilla 6",
    )

    append("H", (X_ANCILLA,), note="rotate X-check ancilla back for measurement")

    return CircuitDescription(layers=tuple(layers))


def build_rotated_surface_d2_layout() -> RotatedSurfaceD2Layout:
    """Return the named qubit layout used by the example circuit."""

    return RotatedSurfaceD2Layout()


def render_ascii_circuit(
    circuit: CircuitDescription,
    *,
    num_qubits: int,
) -> str:
    """Render a small Clifford circuit as an ASCII diagram."""

    cell_width = 7
    wires = [f"q{qubit}: " for qubit in range(num_qubits)]

    for layer in circuit.layers:
        cells = ["-" * cell_width for _ in range(num_qubits)]

        if layer.gate_name == "H":
            target = layer.qubits[0]
            cells[target] = "--H----"
        elif layer.gate_name == "CNOT":
            control, target = layer.qubits
            lower = min(control, target)
            upper = max(control, target)
            cells[control] = "--@----"
            cells[target] = "--X----"
            for qubit in range(lower + 1, upper):
                cells[qubit] = "--|----"
        else:
            targets = ",".join(str(qubit) for qubit in layer.qubits)
            label = f"{layer.gate_name}({targets})"
            clipped = label[: cell_width - 2]
            cells[layer.qubits[0]] = clipped.center(cell_width, "-")

        for qubit in range(num_qubits):
            wires[qubit] += cells[qubit]

    return "\n".join(wires)


def plot_rotated_surface_d2_syndrome_circuit() -> str:
    """Return an ASCII plot of the distance-2 rotated surface-code round."""

    return render_ascii_circuit(
        build_rotated_surface_d2_syndrome_circuit(),
        num_qubits=TOTAL_QUBITS,
    )


if __name__ == "__main__":
    layout = build_rotated_surface_d2_layout()
    circuit = build_rotated_surface_d2_syndrome_circuit()
    print("Distance-2 rotated surface-code syndrome round")
    print("total_qubits =", layout.total_qubits)
    print("data_qubits =", layout.data_qubits)
    print("x_ancilla =", layout.x_ancilla)
    print("z_ancillas =", layout.z_ancillas)
    print("x_stabilizer_support =", layout.x_stabilizer_support)
    print("z_stabilizer_supports =", layout.z_stabilizer_supports)
    print("circuit_depth =", circuit.circuit_depth)
    print("layers:")
    for layer in circuit.layers:
        print(
            layer.layer_index,
            layer.gate_name,
            layer.qubits,
            layer.metadata.get("note", ""),
        )
    print("")
    print("ASCII circuit:")
    print(plot_rotated_surface_d2_syndrome_circuit())
