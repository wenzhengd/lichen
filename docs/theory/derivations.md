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

This is the simulator-facing block object.

## 4. Shot-Level Approximate Process

The package-level approximation is therefore

Eq. (8)
$$
\mathcal E_{\mathrm{block}}(\rho)
:=
\int d\xi\, g(\xi)
\Big(
\widetilde{\mathcal N}_B^{(\xi)} \circ \mathcal C_B \circ \cdots \circ
\widetilde{\mathcal N}_1^{(\xi)} \circ \mathcal C_1
\Big)(\rho),
$$

where the same hidden `\xi` is reused across all blocks in the shot.

## 5. Why Delayed Projection Matters

The decisive sanity check is a one-qubit sign-flip pair. Consider two consecutive segments of equal duration `\Delta` with generators `+Z` then `-Z`. The exact conditional block unitary is

Eq. (9)
$$
U_{\mathrm{pair}}(\xi)
= e^{-i\xi\Delta(-Z)} e^{-i\xi\Delta(+Z)} = I.
$$

So if projection is delayed until after the pair, the block channel is exactly identity.

By contrast, if each segment were projected separately, each one would look like a dephasing channel, and the cancellation would be lost. This is the reason the package is built around blockwise, not segmentwise, projection.

## 6. Free-Vs-Echo Sanity Checks

The same logic appears in the `L = 8` one-qubit tests.

### Free evolution

With `C_j = I` and `\Delta_j = \Delta`, every segment has `A_j = Z`, so the eight-segment conditional unitary is

Eq. (10)
$$
U_{\mathrm{free},8}(\xi) = e^{-i 8\xi\Delta Z}.
$$

This yields a nontrivial dephasing channel after projection.

### Sign-flip dynamical decoupling

With alternating sign in the toggling frame, the blockwise ordered product can cancel exactly. The block construction therefore preserves the DD/free distinction that is destroyed by too-early projection.

## 7. How The Code Implements This

The derivation maps directly to the package modules:

- `src/lichen/frame_tracker.py`: build `G_j`
- `src/lichen/segment_generators.py`: build the signed `A_j`
- `src/lichen/block_partition.py`: choose the short blocks
- `src/lichen/block_probability_search.py`: compute exact short-block Pauli amplitudes
- `src/lichen/block_fault_export.py`: export a sparse block-fault distribution
- `src/lichen/block_sampler.py`: sample one block fault per block in a shot
