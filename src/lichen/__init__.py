"""Blockwise hidden-memory env construction from thought-2-Ultra."""

from .circuit import CircuitDescription, CircuitLayer
from .block_fault_export import (
    SparseBlockFaultDistribution,
    SparseExportConfig,
    export_sparse_probabilities,
    export_sparse_block_fault_distribution,
)
from .block_partition import BlockDescriptor, build_fixed_window_blocks, validate_blocks_against_circuit
from .block_pauli_projector import BlockPauliChannel, build_block_pauli_channel
from .block_propagator import ExactBlockUnitary, build_exact_block_unitary
from .block_structure_analyzer import (
    AnticommutationComponent,
    GeneratorMultiplicitySummary,
    TwoSegmentBlockStructure,
    analyze_two_segment_blocks,
)
from .block_probability_search import (
    SupportedBlockProbabilitySearch,
    build_supported_block_probability_search,
    enumerate_generated_block_paulis,
)
from .block_sampler import (
    BlockFaultChoice,
    BlockwiseHiddenMemoryProcess,
    BlockwiseHiddenMemoryProcessBatch,
    build_blockwise_hidden_memory_process,
    sample_blockwise_hidden_memory_processes,
)
from .block_template_cache import UltraBlockTemplateCache, build_block_signature
from .hidden_memory import (
    HiddenMemoryQuadrature,
    HiddenMemorySample,
    build_hidden_memory_quadrature,
    hidden_memory_samples_from_quadrature,
    sample_hidden_memory,
)
from .model import SharedQuasiStaticModel
from .pauli import (
    SignedPauliTerm,
    count_xy_support,
    conjugate_pauli_by_gate,
    conjugate_pauli_by_gate_with_sign,
    enumerate_pauli_basis,
    multiply_pauli_strings,
    pauli_commutation_sign,
    pauli_string_to_matrix,
    single_qubit_pauli_string,
    validate_pauli_string,
)

__all__ = [
    "AnticommutationComponent",
    "BlockDescriptor",
    "BlockFaultChoice",
    "BlockPauliChannel",
    "SparseBlockFaultDistribution",
    "SparseExportConfig",
    "SupportedBlockProbabilitySearch",
    "BlockwiseHiddenMemoryProcess",
    "BlockwiseHiddenMemoryProcessBatch",
    "CircuitDescription",
    "CircuitLayer",
    "ExactBlockUnitary",
    "GeneratorMultiplicitySummary",
    "HiddenMemoryQuadrature",
    "HiddenMemorySample",
    "TwoSegmentBlockStructure",
    "analyze_two_segment_blocks",
    "build_block_pauli_channel",
    "build_supported_block_probability_search",
    "build_block_signature",
    "build_hidden_memory_quadrature",
    "build_blockwise_hidden_memory_process",
    "build_exact_block_unitary",
    "build_fixed_window_blocks",
    "count_xy_support",
    "conjugate_pauli_by_gate",
    "conjugate_pauli_by_gate_with_sign",
    "enumerate_generated_block_paulis",
    "enumerate_pauli_basis",
    "export_sparse_probabilities",
    "export_sparse_block_fault_distribution",
    "hidden_memory_samples_from_quadrature",
    "multiply_pauli_strings",
    "pauli_commutation_sign",
    "pauli_string_to_matrix",
    "sample_hidden_memory",
    "sample_blockwise_hidden_memory_processes",
    "SharedQuasiStaticModel",
    "SignedPauliTerm",
    "UltraBlockTemplateCache",
    "single_qubit_pauli_string",
    "validate_blocks_against_circuit",
    "validate_pauli_string",
]
