# lichen-q

[![PyPI version](https://img.shields.io/pypi/v/lichen-q.svg)](https://pypi.org/project/lichen-q/)
[![Python versions](https://img.shields.io/pypi/pyversions/lichen-q.svg)](https://pypi.org/project/lichen-q/)
[![CI](https://github.com/wenzhengd/lichen/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/wenzhengd/lichen/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

<img src="docs/lichen_logo.jpg" alt="lichen-q logo" width="280">

`lichen-q` is the standalone PyPI distribution for the `lichen` import
package. It provides blockwise hidden-memory correlated environment-noise
simulation.

It provides the blockwise hidden-memory correlated environment-noise simulator
used for DD-aware noisy-circuit sampling.

## Quick Start

Install from PyPI:

```bash
python -m pip install lichen-q
```

Use it from Python:

```python
from lichen import SharedQuasiStaticModel

model = SharedQuasiStaticModel(
    num_qubits=1,
    sigma2=0.125,
    segment_durations=(0.25, 0.25),
)
print(model.num_qubits)
```

From this repo root, for development:

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

## Contents

- block partitioning
- Clifford-frame tracking
- exact short-block Pauli-amplitude convolution
- sparse block-fault export
- blockwise hidden-memory sampling

## Validation

The canonical validation/tutorial notebook lives under
`docs/tutorials/end_to_end_demo.ipynb`.

The mirrored copy under `examples/lichen_validation.ipynb` is currently kept
for convenience, but the intended repo split is:

- `docs/tutorials/`: validation and theory-connected tutorials
- `examples/`: larger demonstration notebooks and realistic workloads

## Docs

- [docs/README.md](docs/README.md)
- [docs/index.md](docs/index.md)
