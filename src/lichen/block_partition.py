"""Block partition helpers for the blockwise hidden-memory env construction.

The central idea of ``thought-2-Ultra.md`` is that Pauli projection should be
applied only after a short control block, not after every raw noisy segment.
This module defines the block descriptors used by the rest of the ``ultra``
path.
"""

from __future__ import annotations

from dataclasses import dataclass

from .circuit import CircuitDescription


@dataclass(frozen=True)
class BlockDescriptor:
    """A contiguous block of noisy segments.

    Attributes
    ----------
    block_index:
        Zero-based block index.
    start_segment:
        Inclusive start segment index.
    end_segment:
        Inclusive end segment index.

    The current env conventions use one noisy segment after each ideal layer, so
    segment indices and ideal-layer indices move in lock-step.
    """

    block_index: int
    start_segment: int
    end_segment: int

    def __post_init__(self) -> None:
        if self.block_index < 0:
            raise ValueError("block_index must be non-negative.")
        if self.start_segment < 0:
            raise ValueError("start_segment must be non-negative.")
        if self.end_segment < self.start_segment:
            raise ValueError("end_segment must be at least start_segment.")

    @property
    def num_segments(self) -> int:
        """Return the number of raw segments in the block."""

        return self.end_segment - self.start_segment + 1


def build_fixed_window_blocks(
    circuit: CircuitDescription,
    *,
    window_size: int,
) -> tuple[BlockDescriptor, ...]:
    """Partition a circuit into consecutive fixed-width blocks.

    This is the simplest practical block rule for the first ``ultra``
    implementation.  It keeps the code deterministic and makes it easy to
    reproduce the canonical sanity checks:

    - `window_size = 8` for the full `L=8` one-qubit checks,
    - `window_size = 2` for the pair-block DD check.
    """

    if window_size < 1:
        raise ValueError("window_size must be positive.")
    if circuit.circuit_depth < 1:
        raise ValueError("circuit must contain at least one layer.")

    blocks: list[BlockDescriptor] = []
    start = 0
    block_index = 0
    while start < circuit.circuit_depth:
        end = min(start + window_size - 1, circuit.circuit_depth - 1)
        blocks.append(
            BlockDescriptor(
                block_index=block_index,
                start_segment=start,
                end_segment=end,
            )
        )
        start = end + 1
        block_index += 1
    return tuple(blocks)


def validate_blocks_against_circuit(
    blocks: tuple[BlockDescriptor, ...],
    circuit: CircuitDescription,
) -> None:
    """Validate that the block partition exactly covers the circuit segments."""

    if not blocks:
        raise ValueError("At least one block descriptor is required.")
    if circuit.circuit_depth < 1:
        raise ValueError("circuit must contain at least one layer.")

    expected_segment = 0
    for block in blocks:
        if block.start_segment != expected_segment:
            raise ValueError(
                "Blocks must cover the circuit contiguously from segment 0. "
                f"Expected start {expected_segment}, got {block.start_segment}."
            )
        expected_segment = block.end_segment + 1

    if expected_segment != circuit.circuit_depth:
        raise ValueError(
            "Blocks do not cover the full circuit depth. "
            f"Covered through segment {expected_segment - 1}, "
            f"but circuit depth is {circuit.circuit_depth}."
        )
