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
- `J_b = \{s_b, \dots, e_b\}`: the segment index set belonging to block `b`
- `U_j(\xi)`: conditional segment unitary
- `U_b(\xi)`: exact conditional block unitary
- `d_{b,B}(\xi)`: retained diagonal coefficient for Pauli basis element `B`
- `u_{b,P}(\xi)`: Pauli-expansion coefficient for basis element `P`
- `q_{b,P}(\xi)`: block Pauli-channel probability for `P`

## States And Channels

- `\rho`: system density matrix
- `\mathcal N_j^{(\xi)}`: exact conditional noisy map of one segment
- `\widetilde{\mathcal N}_b^{(\xi)}`: Pauli-projected conditional block map
- `\mathcal E`: exact hidden-memory process
- `\mathcal E_{\mathrm{block}}`: blockwise approximate process implemented by the package

## Code Mapping

- `frame_tracker.py`: builds `G_j`
- `segment_generators.py`: builds `A_j`
- `block_partition.py`: defines the block decomposition
- `block_probability_search.py`: computes exact short-block Pauli amplitudes
- `block_fault_export.py`: exports sparse simulator-facing block channels
- `block_sampler.py`: samples block faults shot by shot
