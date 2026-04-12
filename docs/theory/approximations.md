# Approximations

## Why An Approximation Is Needed

The exact environment is coherent and correlated across time. Keeping the full off-diagonal structure everywhere would destroy the Stim-style efficiency that the project needs for large circuits.

So the question is not whether to approximate, but where to place the approximation boundary.

The three package families correspond to three different answers:

- `pro`: keep a global retained-diagonal analysis object;
- `max`: project after every raw segment;
- `ultra`: project after a short block.

`lichen` is built around the `ultra` choice.

## The Three Env Families

### `pro`

`pro` keeps a retained-diagonal / effective correlated Pauli-channel picture.
It is useful as an analysis reference, but it is too global for simulator construction.

### `max`

`max` projects after every raw segment.
This is cheap and simple, but it removes the phase/sign information too early.
That is why the DD sanity check collapses back to the free-evolution channel.

### `ultra`

`ultra` delays projection until after a short block.
This preserves the cancellation physics inside the block while still exporting a Pauli-channel-compatible object at the end.

This is the preferred simulator-facing compromise.

The key improvement over `max` is that the sign-sensitive internal evolution
is allowed to complete before any Pauli projection happens.
For dynamical-decoupling-style sequences, that is the difference between
capturing cancellation and erasing it.

The key improvement over `pro` is that the exported object is local to a block
and can therefore be sampled or truncated without reconstructing a full global
channel over all `4^n` Paulis.

## Current `lichen` Assumptions

`lichen` uses the following controlled approximations:

- hidden memory is one shared Gaussian scalar `\xi` per shot;
- blocks are short, fixed-width windows;
- exact coherent evolution is kept within a block;
- off-diagonal block structure is dropped only at the block boundary;
- the exported block alphabet may be truncated with explicit knobs when needed.

## Why This Is A Good Compromise

The blockwise strategy keeps enough coherence for dynamical-decoupling cancellation to survive, but still ends in a Pauli-channel object that a Clifford simulator can consume.
That is the main tradeoff the package is designed around.

It is also the reason the package can remain practical:

- it does not try to simulate the full coherent environment exactly;
- it does not collapse everything segment by segment;
- it keeps just enough structure to make the DD/free distinction visible in the
  canonical sanity checks;
- and it still exports a simulator-friendly block channel at a fixed window
  size.

## Practical Implications

For users of the package:

- if you want a cheap reference analysis, `pro` is useful;
- if you want the simplest fast sampler, `max` is useful;
- if you want the best current compromise between physics and efficiency,
  `ultra` is the default recommendation.

The validation notebook and the modular theory notes should be read in that
order.
