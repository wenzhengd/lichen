# lichen-q

`lichen-q` is the standalone PyPI distribution for the `lichen` import
package. It provides blockwise hidden-memory correlated environment-noise
simulation.

It provides the blockwise hidden-memory correlated environment-noise simulator
used for DD-aware noisy-circuit sampling.

## Install

From this repo root:

```bash
python -m pip install -e .[dev]
```

## Test

From this repo root:

```bash
python -m pytest -q
```

or:

```bash
python -m unittest discover -s tests -t . -q
```

## Build

From this repo root:

```bash
python -m build
```

## Wheel Check

From this repo root:

```bash
python -m pip install dist/*.whl
```

For users installing from PyPI:

```bash
python -m pip install lichen-q
```

## Contents

- block partitioning
- Clifford-frame tracking
- exact short-block Pauli-amplitude convolution
- sparse block-fault export
- blockwise hidden-memory sampling

## Validation

The package ships with a validation notebook under `examples/lichen_validation.ipynb`.
