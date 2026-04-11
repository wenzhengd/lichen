"""General circuit-layer data structures for lichen."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class CircuitLayer:
    """One ideal circuit layer.

    This is a general layer representation, not specific to the non-Clifford
    wrapper. Wrapper modules consume these layers when constructing interleaved
    branch circuits.
    """

    layer_index: int
    gate_name: str
    qubits: tuple[int, ...]
    params: tuple[float, ...] = ()
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class CircuitDescription:
    """An ordered ideal circuit description."""

    layers: tuple[CircuitLayer, ...]

    @property
    def circuit_depth(self) -> int:
        return len(self.layers)
