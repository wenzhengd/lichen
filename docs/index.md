# lichen Documentation

`lichen` is a standalone package for blockwise hidden-memory simulation of correlated environment noise in Clifford circuits.

The package keeps the hidden environmental variable coherent inside a short block, then projects the resulting block map to a Pauli-channel-compatible object that can be sampled efficiently. The documentation is organized so that a new user can understand the physical setup, the derivation, the approximation boundary, and the executable workflow without reading one monolithic note.

## Read In This Order

1. [Physical Model](theory/physical_model.md)
2. [Derivations](theory/derivations.md)
3. [Approximations](theory/approximations.md)
4. [Notation](theory/notation.md)
5. [End-to-End Demo](tutorials/end_to_end_demo.ipynb)

## Package Scope

The package currently covers:

- shared quasi-static Gaussian environment noise,
- ideal circuits composed of 1-qubit Clifford gates and `CNOT`,
- blockwise hidden-memory propagation,
- exact short-block Pauli-amplitude computation,
- sparse block-fault export for downstream simulation.

## Main Idea

The central design choice is to project **late, not early**.

- If projection happens after every raw segment, sign-sensitive cancellation is lost too early.
- If projection is delayed until after a short block, the cancellation can complete before the channel is reduced to a Pauli-compatible simulator object.

That delayed projection is the defining method implemented by `lichen`.
