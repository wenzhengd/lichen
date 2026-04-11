"""Shared quasi-static env-noise model used by the first correlated Pauli channel.

This module packages the narrow physics assumptions from ``thought-2-pro.md``
into a compact data object.  The purpose is to keep the later computation code
clean: frame tracking should not also validate noise parameters, and channel
reconstruction should not also decide what the noise model means.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SharedQuasiStaticModel:
    """Shared quasi-static Gaussian dephasing model.

    Attributes
    ----------
    num_qubits:
        Number of qubits in the ideal circuit.
    sigma2:
        Variance of the shared quasi-static Gaussian field.  In the notation of
        ``thought-2-pro.md``, the random field is ``xi ~ N(0, sigma2)``.
    segment_durations:
        Durations of the noisy intervals between ideal Clifford layers.  The
        first implementation assumes one noisy segment after each ideal layer,
        so the number of durations must match the number of tracked frames.
    """

    num_qubits: int
    sigma2: float
    segment_durations: tuple[float, ...]

    def __post_init__(self) -> None:
        if self.num_qubits < 1:
            raise ValueError("num_qubits must be positive.")
        if self.sigma2 < 0.0:
            raise ValueError("sigma2 must be non-negative.")
        if not self.segment_durations:
            raise ValueError("segment_durations must not be empty.")
        if any(duration < 0.0 for duration in self.segment_durations):
            raise ValueError("segment durations must be non-negative.")

    @property
    def num_segments(self) -> int:
        """Return the number of noisy segments."""

        return len(self.segment_durations)
