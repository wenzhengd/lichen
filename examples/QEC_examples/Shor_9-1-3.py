"""Shor [[9,1,3]] encoding circuit example for lichen.

This script builds a purely Clifford encoding circuit for the 9-qubit Shor
code using the native ``lichen`` circuit objects. It is intended to serve as a
reusable input example for later noisy-simulation experiments.

Circuit convention
------------------
Qubit 0 starts as the logical data qubit. Qubits 1..8 are ancillas initialized
in ``|0>``. The encoding follows a standard two-level construction:

1. Create the outer three-block repetition structure on qubits ``0, 3, 6``.
2. Apply Hadamards to those block leaders.
3. Fan out each leader to its two block partners.

All gates are Clifford gates already supported by the current lichen package.
"""

from __future__ import annotations

from dataclasses import dataclass

from lichen import CircuitDescription, CircuitLayer


TOTAL_QUBITS = 9
BLOCK_LEADERS: tuple[int, ...] = (0, 3, 6)
BLOCKS: tuple[tuple[int, int, int], ...] = (
    (0, 1, 2),
    (3, 4, 5),
    (6, 7, 8),
)


@dataclass(frozen=True)
class ShorEncodingLayout:
    """Named qubit layout for the Shor [[9,1,3]] encoding example."""

    total_qubits: int = TOTAL_QUBITS
    logical_data_qubit: int = 0
    block_leaders: tuple[int, ...] = BLOCK_LEADERS
    blocks: tuple[tuple[int, int, int], ...] = BLOCKS


def build_shor_9_1_3_encoding_circuit() -> CircuitDescription:
    """Return a Clifford encoding circuit for the Shor [[9,1,3]] code.

    The resulting circuit acts on qubits ``0..8`` and uses only ``H`` and
    ``CNOT`` gates, so it is directly compatible with the current lichen
    circuit and frame-tracking pipeline.
    """

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

    # Outer repetition structure across the three block leaders.
    append("CNOT", (0, 3), note="outer repetition: logical qubit to block leader 3")
    append("CNOT", (0, 6), note="outer repetition: logical qubit to block leader 6")

    # Rotate the three leaders into the X basis before inner block expansion.
    for qubit in BLOCK_LEADERS:
        append("H", (qubit,), note=f"prepare block leader {qubit} in X basis")

    # Expand each leader into its 3-qubit block.
    for leader, first_partner, second_partner in BLOCKS:
        append(
            "CNOT",
            (leader, first_partner),
            note=f"inner repetition: leader {leader} to partner {first_partner}",
        )
        append(
            "CNOT",
            (leader, second_partner),
            note=f"inner repetition: leader {leader} to partner {second_partner}",
        )

    return CircuitDescription(layers=tuple(layers))


def build_shor_9_1_3_layout() -> ShorEncodingLayout:
    """Return the named qubit layout used by the example circuit."""

    return ShorEncodingLayout()


def render_ascii_circuit(
    circuit: CircuitDescription,
    *,
    num_qubits: int,
) -> str:
    """Render a small Clifford circuit as an ASCII diagram.

    The renderer is intentionally lightweight and dependency-free. Each layer is
    placed in its own column so the result can be printed directly in a
    terminal.
    """

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


def plot_shor_9_1_3_encoding_circuit() -> str:
    """Return an ASCII plot of the Shor [[9,1,3]] encoding circuit."""

    return render_ascii_circuit(
        build_shor_9_1_3_encoding_circuit(),
        num_qubits=TOTAL_QUBITS,
    )


if __name__ == "__main__":
    layout = build_shor_9_1_3_layout()
    circuit = build_shor_9_1_3_encoding_circuit()
    print("Shor [[9,1,3]] encoding circuit")
    print("total_qubits =", layout.total_qubits)
    print("logical_data_qubit =", layout.logical_data_qubit)
    print("block_leaders =", layout.block_leaders)
    print("blocks =", layout.blocks)
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
    print(plot_shor_9_1_3_encoding_circuit())
