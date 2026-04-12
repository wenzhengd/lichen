# Physical Model

## Setting

`lichen` models noisy Clifford circuits with one shared hidden environmental variable per shot.

The ideal circuit is a sequence of Clifford layers

$$
\mathcal C = C_L \circ C_{L-1} \circ \cdots \circ C_1,
$$

where each `C_j` is a 1-qubit Clifford gate or a `CNOT` layer.
The environment is a shared quasi-static Gaussian noise source

$$
\xi \sim \mathcal N(0, \sigma^2),
$$

sampled once per shot and reused across the full circuit run.

## Hilbert Space

For `n` qubits the system lives in

$$
\mathcal H_n = (\mathbb C^2)^{\otimes n}.
$$

The environment is not an extra Hilbert-space factor in the simulator backend. It is represented by the hidden scalar `\xi` and the conditional block channels it induces.

## Segment and Block View

The circuit is partitioned into noisy segments between ideal Clifford layers. A segment generator is the toggling-frame image of the collective dephasing operator:

$$
A_j = G_j^\dagger \Big(\sum_{a=1}^n Z_a\Big) G_j.
$$

Here `G_j` is the cumulative Clifford frame before the noisy segment.

For the blockwise simulator, consecutive segments are grouped into a short block. The block is the unit of exact hidden-memory propagation before Pauli projection.

## Simulator Object

Conditioned on `\xi`, a block produces a Pauli-channel-compatible object that can be sampled by the rest of the simulator stack.
That is the interface `lichen` is built to provide.
