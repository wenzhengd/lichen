from __future__ import annotations

import unittest

import numpy as np

from lichen import (
    CircuitDescription,
    CircuitLayer,
    SharedQuasiStaticModel,
    build_fixed_window_blocks,
    sample_blockwise_hidden_memory_processes,
)


def build_circuit(gate_name: str, num_layers: int = 8) -> CircuitDescription:
    return CircuitDescription(
        layers=tuple(
            CircuitLayer(layer_index=index, gate_name=gate_name, qubits=(0,))
            for index in range(num_layers)
        )
    )


class LichenSmokeTest(unittest.TestCase):
    def test_package_imports_and_block_partition(self) -> None:
        circuit = build_circuit("I")
        blocks = build_fixed_window_blocks(circuit, window_size=2)
        self.assertEqual(len(blocks), 4)
        self.assertEqual(blocks[0].start_segment, 0)
        self.assertEqual(blocks[-1].end_segment, 7)

    def test_one_shot_blockwise_sampling_runs(self) -> None:
        circuit = build_circuit("I")
        model = SharedQuasiStaticModel(
            num_qubits=1,
            sigma2=0.125,
            segment_durations=(0.25,) * circuit.circuit_depth,
        )
        batch = sample_blockwise_hidden_memory_processes(
            model,
            circuit,
            window_size=2,
            num_shots=1,
            rng=np.random.default_rng(123),
        )
        self.assertEqual(batch.num_shots, 1)
        self.assertEqual(len(batch.processes[0].block_channels), 4)


if __name__ == "__main__":
    unittest.main()
