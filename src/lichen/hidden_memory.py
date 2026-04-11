"""Hidden-memory variables for the layerized env process.

The key upgrade from ``thought-2-pro`` to ``thought-2-Max`` is that the env
construction must retain one shared classical memory across the full circuit
run.  In the present quasi-static model this memory is a single Gaussian scalar
``xi``.  For engineering convenience, the same role can also be played by a
discrete Gauss-Hermite label ``k``.

This module defines those memory objects without yet deciding how the segment
faults are sampled.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .model import SharedQuasiStaticModel


@dataclass(frozen=True)
class HiddenMemorySample:
    """One sampled hidden-memory realization.

    Attributes
    ----------
    xi:
        The shared quasi-static scalar used across the whole shot.
    label:
        Optional discrete label, for example a Gauss-Hermite node index.
    weight:
        Optional deterministic weight attached to the sample.  This is useful
        when the hidden-memory process is integrated by quadrature instead of
        by Monte Carlo.
    """

    xi: float
    label: int | None = None
    weight: float | None = None


@dataclass(frozen=True)
class HiddenMemoryQuadrature:
    """Discrete hidden-memory support obtained from Gauss-Hermite quadrature."""

    xi_values: tuple[float, ...]
    weights: tuple[float, ...]

    def __post_init__(self) -> None:
        if len(self.xi_values) != len(self.weights):
            raise ValueError("xi_values and weights must have the same length.")
        if not self.xi_values:
            raise ValueError("HiddenMemoryQuadrature must contain at least one node.")


def sample_hidden_memory(
    model: SharedQuasiStaticModel,
    *,
    rng: np.random.Generator | None = None,
) -> HiddenMemorySample:
    """Sample one continuous Gaussian hidden-memory value ``xi``."""

    generator = rng if rng is not None else np.random.default_rng()
    xi_value = float(generator.normal(loc=0.0, scale=np.sqrt(model.sigma2)))
    return HiddenMemorySample(xi=xi_value)


def build_hidden_memory_quadrature(
    model: SharedQuasiStaticModel,
    *,
    quadrature_order: int = 24,
) -> HiddenMemoryQuadrature:
    """Build a discrete Gauss-Hermite support for the hidden-memory variable."""

    if quadrature_order < 1:
        raise ValueError("quadrature_order must be positive.")

    nodes, weights = np.polynomial.hermite.hermgauss(quadrature_order)
    xi_values = tuple(float(np.sqrt(2.0 * model.sigma2) * node) for node in nodes)
    normalized_weights = tuple(float(weight / np.sqrt(np.pi)) for weight in weights)
    return HiddenMemoryQuadrature(xi_values=xi_values, weights=normalized_weights)


def hidden_memory_samples_from_quadrature(
    quadrature: HiddenMemoryQuadrature,
) -> tuple[HiddenMemorySample, ...]:
    """Convert quadrature nodes into explicit hidden-memory samples."""

    return tuple(
        HiddenMemorySample(xi=xi_value, label=index, weight=weight)
        for index, (xi_value, weight) in enumerate(
            zip(quadrature.xi_values, quadrature.weights)
        )
    )
