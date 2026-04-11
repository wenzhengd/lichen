"""Reusable cache for repeated `window_size = 2` block motifs.

The hidden memory ``xi`` is shared across a full shot, so repeated two-segment
block motifs should not be recomputed from scratch. The cache key deliberately
uses the raw signed-Pauli generator data instead of dense matrices, because the
goal is to reuse work before paying for exact block projection.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .segment_generators import SegmentGenerator
from .block_fault_export import SparseBlockFaultDistribution, SparseExportConfig
from .block_partition import BlockDescriptor


BlockSignature = tuple[tuple[float, tuple[tuple[int, str], ...]], ...]


@dataclass
class UltraBlockTemplateCache:
    """Per-shot cache for sparse exported block-fault distributions."""

    _store: dict[tuple[BlockSignature, float, tuple[int | None, float | None, int | None, str]], SparseBlockFaultDistribution] = field(
        default_factory=dict
    )

    def get(
        self,
        *,
        signature: BlockSignature,
        xi_value: float,
        export_config: SparseExportConfig,
    ) -> SparseBlockFaultDistribution | None:
        """Return the cached distribution if the key is present."""

        return self._store.get((signature, float(xi_value), export_config.cache_key()))

    def put(
        self,
        *,
        signature: BlockSignature,
        xi_value: float,
        export_config: SparseExportConfig,
        distribution: SparseBlockFaultDistribution,
    ) -> None:
        """Store one sparse exported distribution in the cache."""

        self._store[(signature, float(xi_value), export_config.cache_key())] = distribution


def build_block_signature(
    *,
    block: BlockDescriptor,
    segment_generators: tuple[SegmentGenerator, ...],
) -> BlockSignature:
    """Build a stable signature for a short block from raw segment generators."""

    signature: list[tuple[float, tuple[tuple[int, str], ...]]] = []
    for segment_index in range(block.start_segment, block.end_segment + 1):
        segment = segment_generators[segment_index]
        signed_terms = tuple(
            sorted((term.sign, term.pauli_string) for term in segment.terms)
        )
        signature.append((float(segment.duration), signed_terms))
    return tuple(signature)
