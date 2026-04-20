# Documentation

Start with [index.md](index.md).

This directory contains the canonical documentation for the current `lichen`
implementation:

- lightweight theory notes under `docs/theory/`,
- the fuller technical report in [lichen_manuscript.md](lichen_manuscript.md),
- validation and tutorial notebooks under `docs/tutorials/`.

Directory roles:

- `docs/tutorials/`: canonical validation and tutorial notebooks tied to the theory notes
- `examples/`: larger demonstration notebooks and realistic showcase workloads

Recommended reading order:

1. [index.md](index.md)
2. [theory/physical_model.md](theory/physical_model.md)
3. [theory/derivations.md](theory/derivations.md)
4. [theory/approximations.md](theory/approximations.md)
5. [theory/notation.md](theory/notation.md)
6. [architecture_mermaid.md](architecture_mermaid.md) for a high-level code map
7. [lichen_manuscript.md](lichen_manuscript.md) for the fuller report

Important current convention:

- block probabilities are computed in the toggling frame,
- sampled block faults are first toggling-frame objects,
- simulator-facing inserted faults are physical Pauli labels obtained after
  block-end conjugation.

Canonical executable tutorial:

- [tutorials/end_to_end_demo.ipynb](tutorials/end_to_end_demo.ipynb)

Related demonstration material:

- [../examples/QEC_examples/QEC_examples.ipynb](../examples/QEC_examples/QEC_examples.ipynb)
