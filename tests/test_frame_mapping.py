from __future__ import annotations

import unittest

import numpy as np

from lichen import (
    CircuitDescription,
    CircuitLayer,
    HiddenMemorySample,
    SharedQuasiStaticModel,
    build_blockwise_hidden_memory_process,
)


def build_circuit(*gate_names: str) -> CircuitDescription:
    return CircuitDescription(
        layers=tuple(
            CircuitLayer(layer_index=index, gate_name=gate_name, qubits=(0,))
            for index, gate_name in enumerate(gate_names)
        )
    )


class FrameMappingTest(unittest.TestCase):
    def test_h_block_maps_toggling_fault_into_physical_frame(self) -> None:
        circuit = build_circuit("H")
        model = SharedQuasiStaticModel(
            num_qubits=1,
            sigma2=0.0,
            segment_durations=(0.25,),
        )
        process = build_blockwise_hidden_memory_process(
            model,
            circuit,
            window_size=1,
            memory=HiddenMemorySample(xi=np.pi),
            rng=np.random.default_rng(0),
        )

        fault = process.block_faults[0]
        self.assertEqual(fault.toggling_frame_pauli_string, "X")
        self.assertEqual(fault.physical_pauli_string, "Z")
        self.assertEqual(fault.pauli_string, "Z")

    def test_identity_frame_keeps_same_fault_label(self) -> None:
        circuit = build_circuit("I")
        model = SharedQuasiStaticModel(
            num_qubits=1,
            sigma2=0.0,
            segment_durations=(0.25,),
        )
        process = build_blockwise_hidden_memory_process(
            model,
            circuit,
            window_size=1,
            memory=HiddenMemorySample(xi=np.pi),
            rng=np.random.default_rng(0),
        )

        fault = process.block_faults[0]
        self.assertEqual(fault.toggling_frame_pauli_string, "Z")
        self.assertEqual(fault.physical_pauli_string, "Z")
        self.assertEqual(fault.pauli_string, "Z")

    def test_two_segment_dd_pair_still_cancels(self) -> None:
        circuit = build_circuit("X", "X")
        model = SharedQuasiStaticModel(
            num_qubits=1,
            sigma2=0.0,
            segment_durations=(0.25, 0.25),
        )
        process = build_blockwise_hidden_memory_process(
            model,
            circuit,
            window_size=2,
            memory=HiddenMemorySample(xi=np.pi),
            rng=np.random.default_rng(0),
        )

        fault = process.block_faults[0]
        self.assertIsNone(fault.toggling_frame_pauli_string)
        self.assertIsNone(fault.physical_pauli_string)
        self.assertEqual(process.block_channels[0].probabilities, {"I": 1.0})


if __name__ == "__main__":
    unittest.main()
