# Derivations

## 1. Toggling-Frame Segment Generator

The lab-frame dephasing operator is `\sum_a Z_a`. Under the ideal Clifford frame before segment `j`, the segment generator becomes

Eq. (2)
$$
A_j := G_j^\dagger \Big(\sum_{a=1}^n Z_a\Big) G_j.
$$

Since `G_j` is Clifford, `A_j` is a signed Pauli sum. This is the first structural reduction: the environment remains exact, but it is expressed in the Pauli basis.

## 2. Segment And Block Unitaries

For a segment duration `\Delta_j`, the conditional segment unitary is

Eq. (3)
$$
U_j(\xi) = e^{-i\xi \Delta_j A_j}.
$$

Let block `b` contain consecutive segments `j \in J_b = \{s_b, \dots, e_b\}`. The exact conditional block unitary is

Eq. (4)
$$
U_b(\xi)
:=
\prod_{j=e_b}^{s_b} U_j(\xi)
=
\prod_{j=e_b}^{s_b} e^{-i\xi \Delta_j A_j}.
$$

This is the exact environmental evolution inside the block. Nothing is projected away before `U_b(\xi)` is formed.

## 3. Blockwise Pauli Projection

Only after building `U_b(\xi)` does the package drop off-diagonal Pauli-transfer structure.

For an `n`-qubit Pauli basis element `B`, define the retained diagonal coefficient

Eq. (5)
$$
d_{b,B}(\xi)
:=
2^{-n}\,\mathrm{Tr}\!\left[
B\,U_b(\xi)\,B\,U_b(\xi)^\dagger
\right].
$$

The corresponding Pauli-diagonal block map is

Eq. (6)
$$
\widetilde{\mathcal N}_b^{(\xi)}(B) = d_{b,B}(\xi)\,B.
$$

Equivalently, after inversion to the Pauli-channel representation,

Eq. (7)
$$
\widetilde{\mathcal N}_b^{(\xi)}(\rho)
=
\sum_{P \in \mathcal P_n} q_{b,P}(\xi)\, P\rho P.
$$

This is the conditional **toggling-frame** block object.

## 4. Toggling-Frame To Physical Fault Mapping

The sampled Pauli label from Eq. (7) is naturally a toggling-frame block fault
`Q_b`. It is not yet the physical Pauli that should be inserted directly into
the circuit diagram.

If block `b` ends at segment `e_b`, the corresponding physical inserted fault is

Eq. (8)
$$
F_b := G_{e_b} Q_b G_{e_b}^\dagger.
$$

This is the simulator-facing Pauli fault. The current sampler returns both:

- the sampled toggling-frame label `Q_b`,
- the physical inserted label `F_b`.

## 5. Shot-Level Approximate Process

At the environmental level, the package-level approximation is

Eq. (9)
$$
\widetilde{\mathcal E}_{\mathrm{tf,block}}(\rho)
:=
\int d\xi\, g(\xi)
\Big(
\widetilde{\mathcal N}_B^{(\xi)} \circ \cdots \circ
\widetilde{\mathcal N}_1^{(\xi)}
\Big)(\rho),
$$

with the same hidden `\xi` reused across all blocks in the shot.

For simulation, one should read this as:

- sample one common hidden `\xi`,
- sample one toggling-frame block fault `Q_b` from each block distribution,
- map `Q_b` to the physical inserted fault `F_b = G_{e_b} Q_b G_{e_b}^\dagger`,
- insert `F_b` after the ideal block.

The essential point is that the block distribution is computed in the toggling
frame, but the inserted simulator fault lives in the physical frame.

## 6. Why Delayed Projection Matters

The decisive sanity check is a one-qubit sign-flip pair. Consider two consecutive segments of equal duration `\Delta` with generators `+Z` then `-Z`. The exact conditional block unitary is

Eq. (10)
$$
U_{\mathrm{pair}}(\xi)
= e^{-i\xi\Delta(-Z)} e^{-i\xi\Delta(+Z)} = I.
$$

So if projection is delayed until after the pair, the block channel is exactly identity.

By contrast, if each segment were projected separately, each one would look like a dephasing channel, and the cancellation would be lost. This is the reason the package is built around blockwise, not segmentwise, projection.

## 7. Free-Vs-Echo Sanity Checks

The same logic appears in the `L = 8` one-qubit tests.

### Free evolution

With `C_j = I` and `\Delta_j = \Delta`, every segment has `A_j = Z`, so the eight-segment conditional unitary is

Eq. (11)
$$
U_{\mathrm{free},8}(\xi) = e^{-i 8\xi\Delta Z}.
$$

This yields a nontrivial dephasing channel after projection.

### Sign-flip dynamical decoupling

With alternating sign in the toggling frame, the blockwise ordered product can cancel exactly. The block construction therefore preserves the DD/free distinction that is destroyed by too-early projection.

### Multi-Qubit Collective Free Evolution

There is also a simple analytic free-evolution case for arbitrary qubit number
`n`. If every ideal layer is identity, then every segment has

Eq. (12)
$$
A_j = \sum_{a=1}^n Z_a.
$$

For one block `b`, let

Eq. (13)
$$
T_b := \sum_{j\in J_b} \Delta_j,
\qquad
\theta_b(\xi) := \xi T_b.
$$

Then the exact block unitary is

Eq. (14)
$$
U_b(\xi) = e^{-i\theta_b(\xi)\sum_{a=1}^n Z_a}
= \prod_{a=1}^n e^{-i\theta_b(\xi) Z_a}.
$$

So the block Pauli support lies entirely inside the all-`Z` subgroup generated
by `Z_1, ..., Z_n`. Writing `Z_S := \prod_{a\in S} Z_a` for a subset
`S \subseteq \{1,\dots,n\}`, the exact block probabilities are

Eq. (15)
$$
q_{b,Z_S}(\xi)
=
\sin^{2|S|}\!\theta_b(\xi)\,
\cos^{2(n-|S|)}\!\theta_b(\xi).
$$

For `n=2`, this gives

Eq. (16)
$$
q_{b,II}=(1-p_b)^2,
\qquad
q_{b,ZI}=q_{b,IZ}=p_b(1-p_b),
\qquad
q_{b,ZZ}=p_b^2,
$$

where `p_b(\xi) := \sin^2(\theta_b(\xi))`. In the weak-block limit,
`ZI` and `IZ` therefore dominate `ZZ`. This is the expected pattern in the
two-qubit free notebook test.

## 8. How The Code Implements This

The derivation maps directly to the package modules:

- `src/lichen/frame_tracker.py`: build `G_j`
- `src/lichen/segment_generators.py`: build the signed `A_j`
- `src/lichen/block_partition.py`: choose the short blocks
- `src/lichen/block_probability_search.py`: compute exact short-block Pauli amplitudes
- `src/lichen/block_fault_export.py`: export a sparse toggling-frame block distribution
- `src/lichen/block_sampler.py`: sample `Q_b` and map it to the physical inserted fault `F_b`
