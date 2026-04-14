# Examples

This directory is intended for demonstration notebooks and larger showcase
workloads.

Repository convention:

- `docs/tutorials/` is the canonical location for validation and
  theory-connected tutorial notebooks.
- `examples/` is reserved for demonstration-oriented notebooks, such as larger
  QEC-style circuits or realistic workflows that are useful to run but are not
  primarily analytic validation targets.

Current demonstration assets:

- [QEC_examples/QEC_examples.ipynb](QEC_examples/QEC_examples.ipynb):
  main QEC demonstration notebook
- [QEC_examples/Shor_9-1-3.py](QEC_examples/Shor_9-1-3.py):
  Shor `[[9,1,3]]` encoding circuit
- [QEC_examples/Rotated_Surface_d2.py](QEC_examples/Rotated_Surface_d2.py):
  7-qubit rotated distance-2 surface-code round
- [QEC_examples/Rotated_Surface_d3_memory_x.py](QEC_examples/Rotated_Surface_d3_memory_x.py):
  17-qubit rotated distance-3 memory-X surface-code scaffold

Current status:

- [lichen_validation.ipynb](lichen_validation.ipynb) is presently a mirrored
  copy of [end_to_end_demo.ipynb](../docs/tutorials/end_to_end_demo.ipynb).
- The QEC notebook is the main place for larger circuit demonstrations and
  performance-facing examples.
- New demonstration notebooks should be added here without duplicating the
  validation/tutorial role of `docs/tutorials/`.
