"""Sparse simulator-facing export for blockwise hidden-memory channels.

The exact ``ultra`` block projector can produce a full Pauli channel over the
entire ``4^n`` basis. That is the right oracle for small cases, but it is too
expensive to treat as the default simulator object once ``n`` grows.

This module converts an exact conditional block channel into a sparse exported
distribution suitable for sampling:

- keep only the faults worth exporting,
- track the discarded probability mass explicitly,
- renormalize the kept support for downstream sampling.

This does introduce an additional approximation when truncation is active, but
it moves the cost knob to the simulator-facing layer instead of forcing every
consumer to materialize the full block Pauli channel.
"""

from __future__ import annotations

from dataclasses import dataclass

from .block_pauli_projector import BlockPauliChannel
from .block_partition import BlockDescriptor


@dataclass(frozen=True)
class SparseBlockFaultDistribution:
    """Sparse exported block-fault distribution used by the sampler.

    Attributes
    ----------
    block:
        The block this exported distribution belongs to.
    xi:
        Shared hidden-memory value for the current shot.
    probabilities:
        Kept Pauli-fault probabilities after applying truncation and
        renormalization.  This map is what downstream samplers use directly.
    discarded_weight:
        Probability mass removed by the export truncation before the kept
        support was renormalized.
    kept_probability_mass:
        Total probability mass retained before renormalization.
    normalization_mode:
        Policy used to turn the kept support into a valid sampling
        distribution.  The first implementation always renormalizes the kept
        support.
    source_support_size:
        Number of Pauli strings in the original exact block channel.
    """

    block: BlockDescriptor
    xi: float
    probabilities: dict[str, float]
    discarded_weight: float
    kept_probability_mass: float
    normalization_mode: str
    source_support_size: int


@dataclass(frozen=True)
class SparseExportConfig:
    """Configuration for sparse block-fault export.

    Parameters are intentionally simple:

    - ``top_k_non_identity`` keeps at most this many non-identity faults,
    - ``probability_threshold`` drops faults below the threshold,
    - ``max_pauli_weight`` drops faults above the chosen Pauli weight.

    The identity fault is always retained, because removing it would make the
    exported distribution hard to interpret.
    """

    top_k_non_identity: int | None = None
    probability_threshold: float | None = None
    max_pauli_weight: int | None = None
    normalization_mode: str = "renormalize_kept"

    def cache_key(self) -> tuple[int | None, float | None, int | None, str]:
        """Return a stable tuple key for cache lookup."""

        return (
            self.top_k_non_identity,
            self.probability_threshold,
            self.max_pauli_weight,
            self.normalization_mode,
        )


def export_sparse_block_fault_distribution(
    block_channel: BlockPauliChannel,
    *,
    config: SparseExportConfig | None = None,
) -> SparseBlockFaultDistribution:
    """Convert an exact block Pauli channel into a sparse exported distribution."""

    return export_sparse_probabilities(
        block=block_channel.block,
        xi=block_channel.xi,
        probabilities=block_channel.probabilities,
        config=config,
        source_support_size=len(block_channel.probabilities),
    )


def export_sparse_probabilities(
    *,
    block: BlockDescriptor,
    xi: float,
    probabilities: dict[str, float],
    config: SparseExportConfig | None = None,
    source_support_size: int | None = None,
) -> SparseBlockFaultDistribution:
    """Convert an exact or partial probability map into a sparse export."""

    export_config = config if config is not None else SparseExportConfig()
    if export_config.top_k_non_identity is not None and export_config.top_k_non_identity < 0:
        raise ValueError("top_k_non_identity must be non-negative when provided.")
    if (
        export_config.probability_threshold is not None
        and export_config.probability_threshold < 0.0
    ):
        raise ValueError("probability_threshold must be non-negative when provided.")
    if export_config.max_pauli_weight is not None and export_config.max_pauli_weight < 0:
        raise ValueError("max_pauli_weight must be non-negative when provided.")
    if export_config.normalization_mode != "renormalize_kept":
        raise ValueError(
            "Only normalization_mode='renormalize_kept' is currently supported."
        )

    probabilities = dict(probabilities)
    num_qubits = len(next(iter(probabilities)))
    identity_label = "I" * num_qubits

    kept_non_identity = []
    for pauli_string, probability in probabilities.items():
        if pauli_string == identity_label:
            continue
        if export_config.probability_threshold is not None and probability < export_config.probability_threshold:
            continue
        if (
            export_config.max_pauli_weight is not None
            and _pauli_weight(pauli_string) > export_config.max_pauli_weight
        ):
            continue
        kept_non_identity.append((pauli_string, probability))

    kept_non_identity.sort(key=lambda item: (-item[1], item[0]))
    if export_config.top_k_non_identity is not None:
        kept_non_identity = kept_non_identity[: export_config.top_k_non_identity]

    kept_probabilities = {identity_label: probabilities.get(identity_label, 0.0)}
    kept_probabilities.update(dict(kept_non_identity))

    kept_probability_mass = sum(kept_probabilities.values())
    if kept_probability_mass <= 0.0:
        raise ValueError("Sparse block export kept zero total probability mass.")

    discarded_weight = max(0.0, 1.0 - kept_probability_mass)
    renormalized = {
        pauli_string: probability / kept_probability_mass
        for pauli_string, probability in kept_probabilities.items()
    }

    return SparseBlockFaultDistribution(
        block=block,
        xi=xi,
        probabilities=renormalized,
        discarded_weight=discarded_weight,
        kept_probability_mass=kept_probability_mass,
        normalization_mode=export_config.normalization_mode,
        source_support_size=(
            len(probabilities) if source_support_size is None else source_support_size
        ),
    )


def _pauli_weight(pauli_string: str) -> int:
    """Return the number of non-identity letters in a Pauli string."""

    return sum(letter != "I" for letter in pauli_string)
