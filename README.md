# lichen-q

[![PyPI version](https://img.shields.io/pypi/v/lichen-q.svg)](https://pypi.org/project/lichen-q/)
[![Python versions](https://img.shields.io/pypi/pyversions/lichen-q.svg)](https://pypi.org/project/lichen-q/)
[![CI](https://github.com/wenzhengd/lichen/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/wenzhengd/lichen/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

<img src="docs/lichen_logo.jpg" alt="lichen-q logo" width="280">

`lichen-q` is the standalone PyPI distribution for the `lichen` import package.
It implements blockwise hidden-memory correlated-noise sampling for ideal
Clifford circuits under the current shared quasi-static dephasing model.

The current codebase is organized around one approximation boundary:

- evolve exactly inside a short block in the toggling frame,
- project only at the block boundary into a Pauli channel,
- sample one block fault per block,
- then map the sampled toggling-frame fault into the physical inserted fault
  after the ideal block.

That simulator-facing `Q_b -> F_b` convention is aligned with
[docs/lichen_manuscript.md](docs/lichen_manuscript.md).

## Current Scope

The present implementation is intentionally narrow:

- ideal circuit gates are Clifford-only, mainly single-qubit Cliffords and
  `CNOT`,
- noise is one shared Gaussian hidden variable `xi` reused across the full
  shot,
- each ideal layer is followed by one noisy segment,
- fixed-width block partitioning is the default runtime path.

This is enough for DD-style validation cases, small exact block studies, and
larger demonstration circuits such as the QEC examples under `examples/`.

## Quick Start

Install from PyPI:

```bash
python -m pip install lichen-q
```

For development from this repo root:

```bash
python -m pip install -e .[dev]
```

Minimal Python example:

```python
import numpy as np

from lichen import (
    CircuitDescription,
    CircuitLayer,
    SharedQuasiStaticModel,
    sample_blockwise_hidden_memory_processes,
)

circuit = CircuitDescription(
    layers=(
        CircuitLayer(layer_index=0, gate_name="H", qubits=(0,)),
        CircuitLayer(layer_index=1, gate_name="H", qubits=(0,)),
    )
)
model = SharedQuasiStaticModel(
    num_qubits=1,
    sigma2=0.04,
    segment_durations=(1.0, 1.0),
)
batch = sample_blockwise_hidden_memory_processes(
    model,
    circuit,
    window_size=2,
    num_shots=10,
    rng=np.random.default_rng(0),
    num_workers=1,
)
print(batch.num_shots)
```

## Main Capabilities

- block partitioning of layerized ideal circuits
- Clifford-frame tracking and toggling-frame segment-generator construction
- exact short-block Pauli-amplitude convolution on sparse generated support
- sparse exported block-fault distributions
- sampled block processes carrying both toggling-frame and physical fault labels
- process-based Monte Carlo parallelism via `num_workers`

## Repo Layout

- `src/lichen/`: core package code
- `tests/`: unit and smoke tests
- `docs/theory/`: lightweight theory notes aligned with the current code
- `docs/lichen_manuscript.md`: fuller technical report and target modeling reference
- `docs/tutorials/`: canonical validation and tutorial notebooks
- `examples/`: larger demonstration workloads and showcase notebooks
- `examples/QEC_examples/`: QEC circuit scripts and the QEC notebook

## Notebooks

Canonical validation notebook:

- [docs/tutorials/end_to_end_demo.ipynb](docs/tutorials/end_to_end_demo.ipynb)

Demonstration notebook:

- [examples/QEC_examples/QEC_examples.ipynb](examples/QEC_examples/QEC_examples.ipynb)

The mirrored validation copy under
[examples/lichen_validation.ipynb](examples/lichen_validation.ipynb) is kept
for convenience, but `docs/tutorials/` remains the canonical validation home.

## QEC Examples

Current QEC assets include:

- [examples/QEC_examples/Shor_9-1-3.py](examples/QEC_examples/Shor_9-1-3.py)
- [examples/QEC_examples/Rotated_Surface_d2.py](examples/QEC_examples/Rotated_Surface_d2.py)
- [examples/QEC_examples/Rotated_Surface_d3_memory_x.py](examples/QEC_examples/Rotated_Surface_d3_memory_x.py)

The notebook currently contains:

- an executed Shor `[[9,1,3]]` example,
- an executed 7-qubit rotated distance-2 surface-code example,
- a scaffolded 17-qubit rotated distance-3 memory-X example that is currently
  left unexecuted because it is a much heavier exact workload in the present
  one-gate-per-layer model.

## Test

From this repo root:

```bash
python -m pytest -q
```

or:

```bash
PYTHONPATH=src python -m unittest discover -s tests -t . -q
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

## Docs

- [docs/README.md](docs/README.md)
- [docs/index.md](docs/index.md)

## Contact

- `wenzheng.dong.quantum@gmail.com`
