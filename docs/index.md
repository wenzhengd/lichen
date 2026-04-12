# lichen Documentation

`lichen` is the standalone package for blockwise hidden-memory correlated environment noise. This documentation is split into short theory notes plus one executable tutorial so that the physics and the implementation can evolve together.

## Start Here

- [Physical Model](theory/physical_model.md)
- [Derivations](theory/derivations.md)
- [Approximations](theory/approximations.md)
- [Notation](theory/notation.md)
- [End-to-End Demo](tutorials/end_to_end_demo.ipynb)

## What This Package Covers

- shared quasi-static Gaussian environment noise
- Clifford-frame tracking for ideal control layers
- blockwise hidden-memory sampling
- exact short-block Pauli-amplitude propagation
- sparse block-fault export for simulation

## Design Principle

The package keeps the hidden memory coherent long enough for short-block cancellation to occur, then projects to a Pauli-channel-compatible object at the block boundary.
