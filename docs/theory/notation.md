# Notation

This note collects the symbols used across the `lichen` documentation.

## Circuit And Noise

- `C_j`: ideal Clifford layer at step `j`
- `G_j`: cumulative Clifford frame before the `j`-th noisy segment
- `A_j`: toggling-frame segment generator
- `\Delta_j`: duration of segment `j`
- `\xi`: shared quasi-static Gaussian hidden memory sampled once per shot
- `\sigma^2`: variance of the hidden-memory distribution

## Block Objects

- `b`: a short block of consecutive noisy segments
- `U_j(\xi)`: conditional segment unitary
- `U_b(\xi)`: exact conditional block unitary
- `u_{b,P}(\xi)`: Pauli-expansion coefficient for basis element `P`
- `q_{b,P}(\xi)`: block Pauli-channel probability for `P`

## Simulator Families

- `pro`: retained-diagonal / global effective channel analysis
- `max`: segmentwise hidden-memory sampling
- `ultra`: blockwise hidden-memory sampling

## Package Files

- `frame_tracker.py`: builds `G_j`
- `segment_generators.py`: builds `A_j`
- `block_probability_search.py`: computes exact short-block Pauli amplitudes
- `block_fault_export.py`: exports sparse simulator-facing block channels
- `block_sampler.py`: samples block faults shot by shot
