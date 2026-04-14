from __future__ import annotations

import unittest

import numpy as np

from lichen import (
    BlockDescriptor,
    CircuitDescription,
    CircuitLayer,
    SharedQuasiStaticModel,
    build_prepared_blockwise_hidden_memory_process,
    build_fixed_window_blocks,
    export_sparse_probabilities,
    prepare_blockwise_hidden_memory_simulation,
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
        first_fault = batch.processes[0].block_faults[0]
        self.assertIsNone(first_fault.toggling_frame_pauli_string)
        self.assertIsNone(first_fault.physical_pauli_string)
        self.assertIsNone(first_fault.pauli_string)

    def test_prepared_sampling_reuses_circuit_side_state(self) -> None:
        circuit = build_circuit("I")
        model = SharedQuasiStaticModel(
            num_qubits=1,
            sigma2=0.125,
            segment_durations=(0.25,) * circuit.circuit_depth,
        )
        prepared = prepare_blockwise_hidden_memory_simulation(
            model,
            circuit,
            window_size=2,
        )
        process = build_prepared_blockwise_hidden_memory_process(
            prepared,
            rng=np.random.default_rng(321),
        )
        self.assertEqual(len(prepared.blocks), 4)
        self.assertEqual(len(prepared.block_signatures), 4)
        self.assertEqual(len(process.block_channels), 4)
        self.assertEqual(len(process.block_faults), 4)

    def test_sparse_export_handles_missing_identity_support(self) -> None:
        export = export_sparse_probabilities(
            block=BlockDescriptor(block_index=0, start_segment=0, end_segment=0),
            xi=0.0,
            probabilities={"Z": 1.0},
        )
        self.assertEqual(export.probabilities, {"I": 0.0, "Z": 1.0})
        self.assertEqual(export.kept_probability_mass, 1.0)
        self.assertEqual(export.discarded_weight, 0.0)

    def test_parallel_batch_sampling_runs_and_is_reproducible(self) -> None:
        circuit = build_circuit("I")
        model = SharedQuasiStaticModel(
            num_qubits=1,
            sigma2=0.125,
            segment_durations=(0.25,) * circuit.circuit_depth,
        )
        batch_a = sample_blockwise_hidden_memory_processes(
            model,
            circuit,
            window_size=2,
            num_shots=4,
            rng=np.random.default_rng(123),
            num_workers=2,
        )
        batch_b = sample_blockwise_hidden_memory_processes(
            model,
            circuit,
            window_size=2,
            num_shots=4,
            rng=np.random.default_rng(123),
            num_workers=2,
        )
        self.assertEqual(batch_a.num_shots, 4)
        self.assertEqual(batch_b.num_shots, 4)
        self.assertEqual(
            [process.hidden_memory.xi for process in batch_a.processes],
            [process.hidden_memory.xi for process in batch_b.processes],
        )
        self.assertEqual(
            [
                tuple(fault.physical_pauli_string for fault in process.block_faults)
                for process in batch_a.processes
            ],
            [
                tuple(fault.physical_pauli_string for fault in process.block_faults)
                for process in batch_b.processes
            ],
        )


if __name__ == "__main__":
    unittest.main()
