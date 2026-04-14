# Physical Model

## 1. Setting

`lichen` models correlated environment noise in an ideal Clifford circuit with one shared hidden environmental variable per shot.

The ideal circuit is

$$
\mathcal C = C_L \circ C_{L-1} \circ \cdots \circ C_1,
$$

where each `C_j` is a supported 1-qubit Clifford gate or a `CNOT` layer.

The environment is represented by one quasi-static Gaussian scalar

$$
\xi \sim \mathcal N(0, \sigma^2),
$$

sampled once per shot and reused throughout the full circuit run.

## 2. Hilbert Space And Noise Representation

For `n` qubits, the system Hilbert space is

$$
\mathcal H_n = (\mathbb C^2)^{\otimes n}.
$$

The package does **not** represent the environment as an explicit extra Hilbert-space factor. Instead, the hidden environmental memory is carried by the sampled scalar `\xi` and the conditional channels it induces.

## 3. Segment View

The circuit is divided into noisy segments between ideal Clifford layers. Let `G_j` denote the cumulative ideal Clifford frame before segment `j`. The collective dephasing operator in the toggling frame is

$$
A_j = G_j^\dagger \Big(\sum_{a=1}^n Z_a\Big) G_j.
$$

Because `G_j` is Clifford, each `A_j` is a signed Pauli sum. This is the key representation used by the code.

## 4. Exact Hidden-Memory Process

If `\mathcal N_j^{(\xi)}` denotes the exact conditional noisy map of segment `j`, then the full hidden-memory process is

Eq. (1)
$$
\mathcal E(\rho)
=
\int d\xi\, g(\xi)
\Big(
\mathcal N_L^{(\xi)} \circ \mathcal C_L \circ \cdots \circ \mathcal N_1^{(\xi)} \circ \mathcal C_1
\Big)(\rho),
$$

where the same `\xi` appears in every segment in the shot.

This exact process is the starting point of the derivation. The package does not
simulate Eq. (1) globally because that would keep too much coherent structure
for large circuits.

## 5. Block View

Instead of projecting after each raw segment, `lichen` groups consecutive segments into a short **block**. The block is the unit of exact hidden-memory propagation before Pauli projection.

The important frame convention is:

- exact propagation is carried out inside the block in the toggling frame,
- the resulting block Pauli distribution is therefore also a toggling-frame
  object,
- a sampled block Pauli fault is then conjugated by the cumulative Clifford at
  the end of the block to obtain the physical inserted fault,
- the same hidden `\xi` is reused across all blocks in the shot.

So the simulator-facing object is not only "a block Pauli channel". It is:

- exact internal evolution inside a short block,
- then a toggling-frame block Pauli distribution,
- then a physical inserted Pauli fault obtained from that sampled
  toggling-frame fault.
