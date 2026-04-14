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
- `Q_b`: sampled block fault in the toggling frame
- `F_b`: sampled physical inserted fault after conjugation by `G_{e_b}`

## States And Channels

- `\rho`: system density matrix
- `\mathcal N_j^{(\xi)}`: exact conditional noisy map of one segment
- `\widetilde{\mathcal N}_b^{(\xi)}`: Pauli-projected conditional block map
- `\mathcal E`: exact hidden-memory process
- `\widetilde{\mathcal E}_{\mathrm{tf,block}}`: blockwise approximate environmental process in the toggling frame

## Code Mapping

- `frame_tracker.py`: builds `G_j`
- `segment_generators.py`: builds `A_j`
- `block_partition.py`: defines the block decomposition
- `block_probability_search.py`: computes exact short-block Pauli amplitudes
- `block_fault_export.py`: exports sparse toggling-frame block distributions
- `block_sampler.py`: samples toggling-frame block faults and maps them to physical inserted faults
