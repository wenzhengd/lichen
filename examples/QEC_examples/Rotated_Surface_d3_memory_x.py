"""Distance-3 rotated-memory-X surface-code round for lichen.

This example mirrors the smallest nontrivial Stim-style rotated surface-code
memory patch beyond the 7-qubit distance-2 case:

- 9 data qubits on a 3x3 rotated patch,
- 8 ancilla qubits measuring the patch stabilizers,
- 17 total qubits, matching the standard ``surface-17`` size.

The circuit is a lichen-compatible Clifford control schedule for one syndrome
round in the rotated-memory-X family:

- four X-type stabilizer ancillas,
- four Z-type stabilizer ancillas,
- Hadamards on the X ancillas before and after the entangling schedule,
- no explicit reset or measurement, because those are not yet modeled as
  first-class circuit gates inside ``lichen``.
"""

from __future__ import annotations

from dataclasses import dataclass

from lichen import CircuitDescription, CircuitLayer


TOTAL_QUBITS = 17
DATA_QUBITS: tuple[int, ...] = tuple(range(9))
X_ANCILLAS: tuple[int, ...] = (9, 10, 11, 12)
Z_ANCILLAS: tuple[int, ...] = (13, 14, 15, 16)

# Data qubits are laid out row-major on a 3x3 grid:
#
#   0  1  2
#   3  4  5
#   6  7  8
#
# The stabilizer supports match a standard rotated d=3 patch with four X checks
# and four Z checks, including weight-2 boundary checks.
X_STABILIZER_SUPPORTS: tuple[tuple[int, ...], ...] = (
    (0, 1),
    (1, 2, 4, 5),
    (3, 4, 6, 7),
    (7, 8),
)
Z_STABILIZER_SUPPORTS: tuple[tuple[int, ...], ...] = (
    (3, 6),
    (0, 1, 3, 4),
    (4, 5, 7, 8),
    (2, 5),
)


@dataclass(frozen=True)
class RotatedSurfaceD3MemoryXLayout:
    """Named qubit layout for the distance-3 rotated-memory-X example."""

    total_qubits: int = TOTAL_QUBITS
    data_qubits: tuple[int, ...] = DATA_QUBITS
    x_ancillas: tuple[int, ...] = X_ANCILLAS
    z_ancillas: tuple[int, ...] = Z_ANCILLAS
    x_stabilizer_supports: tuple[tuple[int, ...], ...] = X_STABILIZER_SUPPORTS
    z_stabilizer_supports: tuple[tuple[int, ...], ...] = Z_STABILIZER_SUPPORTS


def build_rotated_surface_d3_memory_x_circuit() -> CircuitDescription:
    """Return one Clifford syndrome round for the rotated d=3 memory-X patch."""

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

    for ancilla in X_ANCILLAS:
        append("H", (ancilla,), note=f"prepare X-check ancilla {ancilla} in the X basis")

    for ancilla, support in zip(X_ANCILLAS, X_STABILIZER_SUPPORTS):
        for data_qubit in support:
            append(
                "CNOT",
                (ancilla, data_qubit),
                note=f"X check ancilla {ancilla} couples to data qubit {data_qubit}",
            )

    for ancilla, support in zip(Z_ANCILLAS, Z_STABILIZER_SUPPORTS):
        for data_qubit in support:
            append(
                "CNOT",
                (data_qubit, ancilla),
                note=f"Z check ancilla {ancilla} receives parity from data qubit {data_qubit}",
            )

    for ancilla in X_ANCILLAS:
        append("H", (ancilla,), note=f"rotate X-check ancilla {ancilla} back for measurement")

    return CircuitDescription(layers=tuple(layers))


def build_rotated_surface_d3_memory_x_layout() -> RotatedSurfaceD3MemoryXLayout:
    """Return the named qubit layout used by the example circuit."""

    return RotatedSurfaceD3MemoryXLayout()


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


def plot_rotated_surface_d3_memory_x_circuit() -> str:
    """Return an ASCII plot of the distance-3 rotated-memory-X round."""

    return render_ascii_circuit(
        build_rotated_surface_d3_memory_x_circuit(),
        num_qubits=TOTAL_QUBITS,
    )


if __name__ == "__main__":
    layout = build_rotated_surface_d3_memory_x_layout()
    circuit = build_rotated_surface_d3_memory_x_circuit()
    print("Distance-3 rotated-memory-X surface-code round")
    print("total_qubits =", layout.total_qubits)
    print("data_qubits =", layout.data_qubits)
    print("x_ancillas =", layout.x_ancillas)
    print("z_ancillas =", layout.z_ancillas)
    print("x_stabilizer_supports =", layout.x_stabilizer_supports)
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
    print(plot_rotated_surface_d3_memory_x_circuit())
