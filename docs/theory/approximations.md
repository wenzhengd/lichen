# Approximations

## 1. Why An Approximation Is Unavoidable

The exact hidden-memory process keeps coherent off-diagonal structure across the whole circuit. That is too expensive for the intended simulator workflow, especially if the final output must still be a Pauli-channel-compatible object.

So the real design question is not whether to approximate, but **where to place the approximation boundary**.

## 2. What `lichen` Keeps

Inside each short block, conditioned on the sampled hidden variable `\xi`, the package keeps:

- the exact ordered product of the segment unitaries,
- the sign structure of the toggling-frame generators,
- the cancellation and interference completed within that block,
- the exact short-block Pauli amplitudes on the generated support.

## 3. What `lichen` Discards

At the block boundary, the package discards:

- off-diagonal Pauli-transfer structure of the full block map,
- coherent relations between different Pauli components after the block,
- coherent cross-block propagation of the discarded off-diagonal terms.

This is the essential approximation.

## 4. Why The Approximation Boundary Is At The Block Edge

If projection happens after every raw segment, local cancellation can be destroyed before it finishes.

If projection is delayed until after a short block, the intended cancellation pattern can complete first, and only then is the map reduced to a Pauli-channel-compatible object.

This is the main compromise implemented by `lichen`:

- late enough to preserve local cancellation,
- early enough to remain simulable.

## 5. Choosing A Block Size

Block size is a modeling knob.

- Too small: the relevant cancellation is cut in half.
- Too large: exact internal propagation becomes expensive and the exported block channel becomes less sparse.

The practical rule is:

> choose the smallest block that contains the dominant local cancellation pattern.

In the current package workflow, the validation notebook focuses on `window_size = 2`, which is the smallest nontrivial block for the canonical sign-flip sanity checks.

## 6. Sparse Export

After exact short-block propagation, the resulting block channel is exported as a sparse Pauli distribution.

This gives the package its downstream efficiency:

- identity with high probability,
- a sparse set of nontrivial block faults,
- optional truncation knobs when needed,
- one shared hidden `\xi` reused across the whole shot.

## 7. Practical Interpretation

`lichen` should therefore be understood as a **blockwise hidden-memory Pauli simulator**.

It is not:

- an exact global simulator of the full coherent environment,
- a purely segmentwise Pauli approximation,
- or a general-purpose non-Clifford solver.

It is a controlled compromise designed to preserve the short-range cancellation physics that matters for correlated dephasing while still exporting a Pauli-compatible object for efficient simulation.
