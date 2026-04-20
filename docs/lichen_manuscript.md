
# LICHEN: Blockwise Hidden-Memory Pauli Export for Shared Quasi-Static Noise in Clifford Circuits

## Abstract

We develop a self-contained construction for fast noisy-circuit simulation in the presence of shared quasi-static Gaussian dephasing and ideal Clifford control. The exact environmental effect is governed by one hidden Gaussian scalar sampled once per shot and reused throughout the entire circuit run. Under nontrivial Clifford control, the exact environmental channel is generally not Pauli-diagonal and cannot be rewritten as a composition of independent layer-local Pauli channels. A direct reduction to standard stabilizer sampling is therefore unavailable.

The goal of this work is not to force the exact channel into an exact Pauli form, but to construct a physically motivated and computationally useful Pauli-compatible export. The central observation is that, in this correlated setting, the decisive modeling choice is not only whether off-diagonal Pauli-transfer structure is discarded, but also when it is discarded. If projection is applied after every raw segment, sign-sensitive cancellation is destroyed before it can occur. This failure is already visible in the simplest quasi-static dynamical-decoupling example.

Our adopted construction is a **blockwise hidden-memory Pauli export**. One keeps the same hidden Gaussian variable across the shot, propagates coherently through a short block of segments, and only then projects the completed block map to a Pauli channel. This preserves cancellation internal to the block while still producing a simulator-facing object that can be sampled as blockwise Pauli faults. A central technical point of the present revision is to separate carefully the **toggling-frame environmental process** from the **physical lab-frame circuit with inserted Pauli faults**. We derive the exact channel, formulate the corrected blockwise construction, establish the exact relation between block Pauli probabilities and block Pauli-expansion coefficients, analyze the principal-domain restriction of the block fault alphabet, and specialize the framework to the practically important case `window_size = 2`. Throughout, we explain the conventions with small examples so that the mathematical construction can be followed without referring back to earlier notes.

---

## I. Introduction

The noise model considered here is simple to state but subtle to simulate. We study an `n`-qubit circuit built from ideal Clifford layers and noisy intervals. The environmental field is a shared quasi-static Gaussian dephasing signal: one scalar random variable is drawn once per shot and acts on all qubits during the entire circuit execution. In the laboratory frame the noise Hamiltonian is just a collective `Z` field. However, once nontrivial Clifford control is inserted, the toggling-frame noise generator changes from segment to segment. The exact environmental effect is therefore a continuous Gaussian mixture of coherent non-Clifford unitaries, rather than a discrete Pauli channel.

For fast simulation, one would nevertheless like a Pauli-compatible description. The natural temptation is to project after every raw segment and export a sequence of Pauli channels between Clifford layers. This temptation is misleading. The first problem is global correlation: the same hidden Gaussian variable appears in every segment, so the exact process is correlated across the full shot. The second problem is more physical: projection after every segment destroys the coherent sign information needed for cancellation. In the quasi-static sign-flip dynamical-decoupling problem, a sequence that refocuses exactly at the unitary level can become indistinguishable from free evolution after over-early projection.

The correct question is therefore not simply how to obtain a Pauli channel, but how to obtain one **without discarding the cancellation mechanism that made the control useful in the first place**. This paper adopts the following answer. One keeps the shared hidden memory shot-by-shot, groups consecutive segments into short blocks, propagates exactly or near-exactly through each block, and only then projects the completed block map to a Pauli channel. The resulting blockwise hidden-memory Pauli export remains compatible with a stabilizer backend while preserving the cancellation physics internal to the chosen block.

A second goal of this revision is to clean up an important frame issue. In earlier drafts, toggling-frame conditional channels were written as though they could simply be interleaved with physical lab-frame Clifford channels. That is not the cleanest exact statement. The exact environmental process is most naturally defined in the toggling frame. Only after a block Pauli fault has been sampled in the toggling frame should it be conjugated back into a physical lab-frame fault inserted after the corresponding ideal block. Once this distinction is respected, the theory becomes both cleaner and easier to implement.

The paper is organized as follows. Section II defines the physical model and establishes the exact relation between the lab-frame circuit and the toggling-frame environmental unitary. Section III recalls why the exact environmental channel is generally not Pauli-diagonal. Section IV states the adopted blockwise simulator object in its corrected form. Section V reviews two simpler constructions—global retained-diagonal projection and segmentwise hidden-memory projection—not as rival stories, but as diagnostics that expose what information is lost and why the blockwise rule is the appropriate compromise. Section VI shows explicitly why segmentwise projection fails in the sign-flip DD test. Sections VII–IX derive the block probabilities, the principal-domain restriction, and the special structure of `window_size = 2`. Section X works through the canonical free and DD examples. Section XI closes with the scope and limitations of the approximation.

---

## II. Physical model and exact frame bookkeeping

### A. Raw circuit and quasi-static noise model

We consider `n` qubits acted on by ideal Clifford layers `C_j`, separated by noisy segments of durations `\Delta_j`. The environmental field is quasi-static:

Eq. (1)
```math
f(t)=\xi,
\qquad
\xi\sim \mathcal N(0,\sigma^2).
```

The laboratory-frame noise Hamiltonian is

Eq. (2)
```math
H_{\mathrm{noise}}(t)=\xi\sum_{a=1}^n Z_a.
```

The raw physical circuit is segmented as

Eq. (3)
```math
[C_1,N_1,C_2,N_2,\ldots,C_m,N_m].
```

Here `m` is the number of raw noisy segments. Let

Eq. (4)
```math
V_j(\xi):=e^{-i\xi\Delta_j \sum_{a=1}^n Z_a}
```

denote the laboratory-frame noise unitary during segment `j`. The exact physical unitary for one realization `\xi` is then

Eq. (5)
```math
W(\xi)=V_m(\xi) C_m \cdots V_1(\xi) C_1.
```

This is the exact lab-frame circuit-level object.

A good way to read Eq. (5) is the following. In the lab frame, every noise segment looks formally the same: it is always generated by the same collective `Z` field. The control dependence has not disappeared; it is simply encoded in the way those identical noise segments are interleaved with the different Clifford layers.

### B. Toggling-frame generators

Define the cumulative ideal Clifford before segment `j` by

Eq. (6)
```math
G_j:=C_j C_{j-1}\cdots C_1.
```

The toggling-frame generator during segment `j` is

Eq. (7)
```math
A_j:=G_j^\dagger\Big(\sum_{a=1}^n Z_a\Big)G_j.
```

Because `G_j` is Clifford, every conjugated `Z_a` is again a Pauli string, so

Eq. (8)
```math
A_j=\sum_{a=1}^n P_{a,j},
\qquad
P_{a,j}:=G_j^\dagger Z_a G_j.
```

For fixed `j`, the strings `P_{a,j}` commute with one another because the original `Z_a` commute. Across different segments, however, `A_j` and `A_{j'}` need not commute.

Define the toggling-frame segment unitary

Eq. (9)
```math
U_j(\xi):=e^{-i\xi\Delta_j A_j}.
```

By construction,

Eq. (10)
```math
U_j(\xi)=G_j^\dagger V_j(\xi) G_j.
```

The physical meaning of Eq. (10) is important. The object `U_j(\xi)` is **not** a bare lab-frame noise channel attached only to segment `j`. It is the same laboratory noise, rewritten in the frame that has already followed the ideal control history up to that point. That is why it depends on the cumulative Clifford `G_j`, not only on the local gate `C_j`.

A one-qubit sign-flip example makes this concrete. If every Clifford layer is `X`, then `G_j=X^j`, and
```math
A_j=G_j^\dagger Z G_j = (-1)^j Z.
```
So the laboratory noise is always a `Z` field, but in the toggling frame it alternates between `+Z` and `-Z`. This sign alternation is precisely the piece of information that a too-early projection will destroy.

### C. Exact relation between lab frame and toggling frame

The toggling-frame environmental unitary is

Eq. (11)
```math
U(\xi)=\prod_{j=m}^{1} U_j(\xi)
=
\prod_{j=m}^{1} e^{-i\xi\Delta_j A_j}.
```

The exact physical unitary and the toggling-frame unitary are related by

Eq. (12)
```math
W(\xi)=G_m\,U(\xi).
```

This follows by repeatedly using the identity `V_j(\xi) G_j = G_j U_j(\xi)` and telescoping through the circuit.

It is worth pausing here, because Eq. (12) is the main bookkeeping convention used in the rest of the paper. The lab-frame circuit `W(\xi)` and the toggling-frame object `U(\xi)` are **not** two different physics models. They are the same realization, written in two different frames. The toggling-frame form is better for analysis because all ideal Clifford history is absorbed into the generators `A_j`. The lab-frame form is better for final simulator export because the sampled Pauli faults must eventually be inserted into a physical circuit.

A two-segment example makes Eq. (12) transparent. For `m=2`,
```math
W(\xi)=V_2(\xi)C_2V_1(\xi)C_1.
```
Using `G_1=C_1` and `G_2=C_2C_1`, one has
```math
V_1(\xi)C_1 = C_1 U_1(\xi),
```
and
```math
V_2(\xi)C_2C_1 = C_2C_1 U_2(\xi)=G_2 U_2(\xi).
```
Therefore
```math
W(\xi)=G_2 U_2(\xi)U_1(\xi)=G_2 U(\xi).
```
The general formula is nothing more than the repeated version of this two-step identity.

The exact toggling-frame environmental channel is therefore

Eq. (13)
```math
\mathcal E_{\mathrm{tf}}(\rho)
=
\int_{-\infty}^{\infty}
\frac{d\xi}{\sqrt{2\pi\sigma^2}}
e^{-\xi^2/(2\sigma^2)}
\,U(\xi)\rho U(\xi)^\dagger,
```

whereas the exact physical circuit channel is

Eq. (14)
```math
\mathcal M_{\mathrm{phys}}(\rho)
=
\mathcal C_{\mathrm{id}}\!\left(\mathcal E_{\mathrm{tf}}(\rho)\right),
\qquad
\mathcal C_{\mathrm{id}}(\rho):=G_m\rho G_m^\dagger.
```

This distinction between `\mathcal E_{\mathrm{tf}}` and `\mathcal M_{\mathrm{phys}}` will be maintained throughout the rest of the paper.

---

## III. Exact channel and Pauli-basis structure

### A. Why the exact environmental channel is generally not Pauli-diagonal

A Pauli channel has the form

Eq. (15)
```math
\Phi(\rho)=\sum_{P\in\mathcal P_n} q_P\,P\rho P,
```

and is diagonal in the Pauli-transfer basis. By contrast, for a fixed value of `\xi`, the unitary `U(\xi)` in Eq. (11) is generally a continuous-angle non-Clifford unitary. Conjugation by `U(\xi)` therefore maps a Pauli operator into a linear combination of Pauli operators. After Gaussian averaging, that mixing generally survives. Hence the exact channel in Eq. (13) is typically neither a Pauli channel nor diagonal in the Pauli-transfer representation.

This point is more than formal. It means that the exact environmental process cannot, in general, be simulated by simply sampling a discrete Pauli fault and feeding the result to a stabilizer backend.

### B. Exact Pauli-basis propagation

Let `B` be any `n`-qubit Pauli operator. Since the factors inside `A_j` commute within a segment, one has

Eq. (16)
```math
e^{-i\xi\Delta_j A_j} B e^{+i\xi\Delta_j A_j}
=
\prod_{a=1}^n
\Big(
e^{-i\xi\Delta_j P_{a,j}}\,B\,e^{+i\xi\Delta_j P_{a,j}}
\Big).
```

For one Pauli string `P`, the conjugation rule is exact:

Eq. (17)
```math
e^{-i\theta P} B e^{+i\theta P}
=
\begin{cases}
B, & [P,B]=0, \\[4pt]
\cos(2\theta)\,B-i\sin(2\theta)\,PB, & \{P,B\}=0.
\end{cases}
```

This formula looks more complicated than it really is. It simply says: if `P` commutes with `B`, nothing happens; if `P` anticommutes with `B`, then `B` rotates within the two-dimensional Pauli subspace spanned by `B` and `PB`.

For example, with one qubit, `P=Z` and `B=X`, Eq. (17) becomes
```math
e^{-i\theta Z} X e^{+i\theta Z}
=
\cos(2\theta)X+\sin(2\theta)Y.
```
So a continuous-angle `Z` rotation mixes `X` and `Y`. This is exactly why the exact channel is not usually Pauli-diagonal.

Iterating over all segments yields

Eq. (18)
```math
U(\xi)B_\nu U(\xi)^\dagger
=
\sum_\mu c_{\mu\nu}(\xi)\,B_\mu,
```

where each coefficient `c_{\mu\nu}(\xi)` is a finite trigonometric polynomial in `\xi`. Writing each coefficient as a finite Fourier sum,

Eq. (19)
```math
c_{\mu\nu}(\xi)=\sum_{\lambda\in\Lambda_{\mu\nu}}\alpha_{\mu\nu}(\lambda)e^{i\lambda\xi},
```

and using the Gaussian average

Eq. (20)
```math
\langle e^{i\lambda\xi}\rangle = e^{-\frac12\sigma^2\lambda^2},
```

one obtains

Eq. (21)
```math
\mathcal E_{\mathrm{tf}}(B_\nu)=\sum_\mu \overline c_{\mu\nu} B_\mu,
\qquad
\overline c_{\mu\nu}
=
\sum_{\lambda\in\Lambda_{\mu\nu}}
\alpha_{\mu\nu}(\lambda)e^{-\frac12\sigma^2\lambda^2}.
```

The exact Pauli-transfer matrix is therefore

Eq. (22)
```math
R_{\mu\nu}
=
2^{-n}\operatorname{Tr}\!\left[B_\mu\,\mathcal E_{\mathrm{tf}}(B_\nu)\right]
=
\int d\xi\,g(\xi)\,
2^{-n}\operatorname{Tr}\!\left[
B_\mu U(\xi) B_\nu U(\xi)^\dagger
\right].
```

This exact Pauli-basis picture clarifies the simulation problem: the shared-memory model is analytically structured, but its natural exact description is a full superoperator, not a sampled Pauli channel.

---

## IV. The adopted reduced object: blockwise hidden-memory Pauli export

The simulator goal is precise. We do not require an exact Pauli representation of the full environmental channel. We require a Pauli-compatible export that satisfies three physical conditions:

1. it must preserve the shared hidden memory `\xi` across the shot;
2. it must allow coherent cancellation to occur within the smallest local control motif that realizes that cancellation;
3. it must eventually output a discrete Pauli-fault object that can be inserted into a Clifford-plus-Pauli backend.

These conditions point directly to the adopted blockwise construction. In one sentence:

> we delay Pauli projection until after the smallest control window that is supposed to realize the cancellation.

### A. Block partition and exact block unitary in the toggling frame

Partition the raw segments into ordered blocks. Let block `b` contain the consecutive raw segments

Eq. (23)
```math
J_b=\{s_b,s_b+1,\ldots,e_b\},
\qquad
b=1,\ldots,N_{\mathrm{blk}}.
```

Define the exact conditional block unitary in the toggling frame by

Eq. (24)
```math
U_b(\xi):=
\prod_{j=e_b}^{s_b} e^{-i\xi\Delta_j A_j}.
```

The exact environmental unitary factors as

Eq. (25)
```math
U(\xi)=U_{N_{\mathrm{blk}}}(\xi)\cdots U_2(\xi)U_1(\xi).
```

No approximation has yet been made.

A useful way to view Eq. (24) is that the block is the smallest region inside which one is still willing to keep coherent interference exactly. Everything that happens before the block boundary is treated coherently; everything after the boundary will see only the Pauli-projected summary of that block.

### B. Blockwise Pauli projection in the toggling frame

For a Pauli basis element `B`, define the conditional block retained diagonal

Eq. (26)
```math
d_{b,B}(\xi)
:=
2^{-n}\operatorname{Tr}\!\left[
B\,U_b(\xi) B U_b(\xi)^\dagger
\right].
```

The conditional block Pauli-diagonal channel is

Eq. (27)
```math
\widetilde{\mathcal N}_b^{(\xi)}(B)=d_{b,B}(\xi)\,B.
```

Equivalently,

Eq. (28)
```math
\widetilde{\mathcal N}_b^{(\xi)}(\rho)
=
\sum_{Q\in\mathcal P_n} q_{b,Q}(\xi)\,Q\rho Q.
```

The adopted approximate **environmental** process in the toggling frame is therefore

Eq. (29)
```math
\widetilde{\mathcal E}_{\mathrm{tf,blk}}(\rho)
=
\int d\xi\,g(\xi)\,
\Big(
\widetilde{\mathcal N}_{N_{\mathrm{blk}}}^{(\xi)}
\circ \cdots \circ
\widetilde{\mathcal N}_{1}^{(\xi)}
\Big)(\rho).
```

This is the correct blockwise hidden-memory approximation at the level of the environmental channel.

### C. From toggling-frame block faults to physical inserted faults

The toggling-frame block channel in Eq. (29) is not yet the object one inserts directly into a physical circuit diagram. To obtain a physical lab-frame sampled circuit, one must conjugate each sampled toggling-frame block fault by the cumulative ideal Clifford at the end of that block.

Define the ideal block Clifford unitary

Eq. (30)
```math
K_b:=G_{e_b}G_{e_{b-1}}^\dagger,
\qquad
G_{e_0}:=I,
```

so that

Eq. (31)
```math
G_m = K_{N_{\mathrm{blk}}}\cdots K_2 K_1.
```

Suppose a toggling-frame block fault `Q_b` is sampled from the conditional distribution `q_{b,Q}(\xi)`. The corresponding physical fault inserted **after** ideal block `b` is

Eq. (32)
```math
F_b := G_{e_b} Q_b G_{e_b}^\dagger.
```

This formula is one of the main new conventions in the paper, so it is worth interpreting carefully. The toggling-frame fault `Q_b` is the natural object for the mathematical block analysis. But the simulator ultimately runs a physical circuit after the ideal block has already rotated the computational axes. Conjugating by `G_{e_b}` simply translates the fault from the toggling-frame coordinates back into the physical coordinates.

A one-qubit example makes Eq. (32) intuitive. Suppose a block ends with cumulative Clifford `G_{e_b}=H`, the Hadamard gate, and suppose the sampled toggling-frame fault is `Q_b=Z`. Then
```math
F_b = H Z H = X.
```
So the block analysis may say “insert a toggling-frame `Z` fault,” but the physical circuit actually receives an `X` fault after that block. Nothing inconsistent is happening: this is exactly how a change of frame should work.

The interleaved sampled circuit is correct because the identity

Eq. (33)
```math
F_{N_{\mathrm{blk}}} K_{N_{\mathrm{blk}}}\cdots F_1 K_1
=
G_m\,Q_{N_{\mathrm{blk}}}\cdots Q_1
```

follows by telescoping. Thus the physical sampled circuit conditioned on one sampled `\xi` is

Eq. (34)
```math
K_1 \to F_1 \to K_2 \to F_2 \to \cdots \to K_{N_{\mathrm{blk}}} \to F_{N_{\mathrm{blk}}},
```

with one common hidden `\xi` shared across all sampled block faults.

Equation (34) is the proper simulator-facing interpretation of the blockwise theory. It corrects the earlier draft, which wrote a blockwise interleaving formula without first separating the toggling-frame environmental process from the physical lab-frame insertion rule.

### D. Physical meaning of the blockwise rule

Within a block, one retains the exact ordered product of the segment unitaries, and thus preserves sign information, cancellation, and coherent recombination internal to that block. At the block boundary, one discards the off-diagonal Pauli-transfer structure of the completed block map and exports a toggling-frame Pauli channel. Only after that export does one conjugate the sampled Pauli fault into a physical fault inserted after the ideal block.

The central modeling choice is therefore not merely the act of projection itself, but its timing.

---

## V. Two diagnostic constructions and what they teach us

The blockwise export in Eq. (29) is the main story. Two simpler reductions are still useful, but only as diagnostics. They isolate the two main ways information may be discarded too aggressively.

### A. Global retained-diagonal projection

A first approximation is to keep only the Pauli-transfer diagonal of the **full** exact environmental channel. For each Pauli basis element `B`, define

Eq. (35)
```math
\lambda_B
:=
2^{-n}\operatorname{Tr}\!\left[B\,\mathcal E_{\mathrm{tf}}(B)\right].
```

Then the retained-diagonal approximation is

Eq. (36)
```math
\widetilde{\mathcal E}_{\mathrm{tf}}(B)=\lambda_B B.
```

Substituting Eq. (13) gives

Eq. (37)
```math
\lambda_B
=
\int_{-\infty}^{\infty}
\frac{d\xi}{\sqrt{2\pi\sigma^2}}
e^{-\xi^2/(2\sigma^2)}
\,d_B(\xi),
```

with

Eq. (38)
```math
d_B(\xi):=
2^{-n}\operatorname{Tr}\!\left[
B\,U(\xi) B U(\xi)^\dagger
\right].
```

The main lesson is that the retained diagonal must be computed from the **full** unitary `U(\xi)`. One cannot, in general, multiply separate segmentwise diagonal factors, because off-diagonal Pauli weight created in one segment can return to the diagonal in later segments. This is the corrected lesson already established in the earlier retained-diagonal note.

A simple one-qubit free example is worth keeping in mind. If every `A_j=Z`, then the full unitary is
```math
U(\xi)=e^{-i\xi(\sum_j \Delta_j)Z},
```
so the retained diagonal for `B=X` is
```math
d_X(\xi)=\cos\!\left(2\xi\sum_j \Delta_j\right),
```
not the product `\prod_j \cos(2\xi\Delta_j)`. This is the cleanest way to see why the naive segmentwise factorization of the retained diagonal fails.

This approximation is mathematically clean, but it is global and therefore not naturally layerized for simulator export.

### B. Segmentwise hidden-memory projection

Because the `P_{a,j}` commute within one segment, the toggling-frame segment unitary factorizes:

Eq. (39)
```math
U_j(\xi)=\prod_{a=1}^n e^{-i\xi\Delta_j P_{a,j}}.
```

For a single factor `e^{-i\theta P}`, the Pauli-projected channel is

Eq. (40)
```math
\rho \mapsto \cos^2(\theta)\,\rho+\sin^2(\theta)\,P\rho P.
```

Hence the exact **segmentwise** Pauli projection may be sampled using independent Bernoulli variables with

Eq. (41)
```math
p_j(\xi)=\sin^2(\xi\Delta_j).
```

For each `a`, let `s_{a,j}\in\{0,1\}` satisfy

Eq. (42)
```math
\Pr[s_{a,j}=1\mid\xi]=p_j(\xi),
\qquad
\Pr[s_{a,j}=0\mid\xi]=1-p_j(\xi).
```

Then the sampled toggling-frame segment fault is

Eq. (43)
```math
Q_j(\xi,\mathbf s_j):=\prod_{a=1}^n P_{a,j}^{\,s_{a,j}},
```

and the exact segmentwise Pauli-projected channel is

Eq. (44)
```math
\widetilde{\mathcal N}_{j,\mathrm{seg}}^{(\xi)}(\rho)
=
\sum_{\mathbf s_j\in\{0,1\}^n}
\left[
\prod_{a=1}^n p_j(\xi)^{s_{a,j}}(1-p_j(\xi))^{1-s_{a,j}}
\right]
Q_j(\xi,\mathbf s_j)\rho Q_j(\xi,\mathbf s_j).
```

This is exact **for the single-segment Pauli projection**. It makes the shared-memory structure explicit and exposes the small parameter relevant in the weak-segment regime.

### C. Weak-segment limit

Assume each raw segment is weak:

Eq. (45)
```math
|\xi|\Delta_j\ll 1
\qquad
\text{on the statistically relevant support of }\xi,
```

or statistically

Eq. (46)
```math
\sigma\Delta_j\ll 1
\qquad
\text{for all }j.
```

Define

Eq. (47)
```math
\theta_j(\xi):=\xi\Delta_j.
```

Then

Eq. (48)
```math
p_j(\xi)=\theta_j(\xi)^2+O(\theta_j(\xi)^4).
```

If all `P_{a,j}` are distinct, the leading segment channel becomes

Eq. (49)
```math
\widetilde{\mathcal N}_{j,\mathrm{seg}}^{(\xi)}(\rho)
=
\Big(1-n\theta_j(\xi)^2\Big)\rho
+
\theta_j(\xi)^2\sum_{a=1}^n P_{a,j}\rho P_{a,j}
+
O(\theta_j(\xi)^4).
```

Notice that they are not guaranteed to be distinct as Pauli strings: for CNOT it is possible to have $`Z_{1}\rightarrow X_{1}X_{2}; Z_{2}\rightarrow X_{1}X_{2}`$; then $`A_{j} =P_{1,j}+P_{2,j}=X_{1}X_{2}+X_{1}X_{2}=2X_{1}X_{2}`$
 
If one first compresses duplicate strings,

Eq. (50)
```math
A_j=\sum_{\ell=1}^{L_j}\nu_{\ell,j}Q_{\ell,j},
```

then the leading odd-parity class probability is

Eq. (51)
```math
\pi_{\ell,j}^{\mathrm{odd}}(\xi)
=
\nu_{\ell,j}\theta_j(\xi)^2+O(\theta_j(\xi)^4),
```

and

Eq. (52)
```math
\widetilde{\mathcal N}_{j,\mathrm{seg}}^{(\xi)}(\rho)
=
\Big(1-\Lambda_j(\xi)\Big)\rho
+
\sum_{\ell=1}^{L_j}
\pi_{\ell,j}^{\mathrm{odd}}(\xi)\,Q_{\ell,j}\rho Q_{\ell,j}
+
O(\theta_j(\xi)^4),
```

with

Eq. (53)
```math
\Lambda_j(\xi)=\sum_{\ell=1}^{L_j}\pi_{\ell,j}^{\mathrm{odd}}(\xi).
```

The interpretation is simple: if each raw segment is weak, then each segment is usually identity and only rarely inserts one Pauli fault. This is why the weak-segment model can be computationally attractive. But it also reveals the core weakness of segmentwise projection: projection is performed before neighboring segments have had a chance to cancel coherently.

---

## VI. Why segmentwise projection fails in DD-type settings

The failure is most transparent in the one-qubit sign-flip problem. Consider `n=1`, equal segment durations `\Delta`, and ideal `X` pulses that alternate the sign of the toggling-frame generator. Then

Eq. (54)
```math
A_j=(-1)^j Z.
```

For a two-segment pair, the exact conditional toggling-frame unitary is

Eq. (55)
```math
U_{\mathrm{pair}}(\xi)=e^{+i\xi\Delta Z}e^{-i\xi\Delta Z}=I.
```

Thus the quasi-static dephasing cancels perfectly inside the pair.

By contrast, the segmentwise Pauli projection of each segment depends only on `\sin^2(\xi\Delta)` and is insensitive to the sign of `A_j`. The two segments therefore project to the same dephasing channel one would obtain in free evolution. The control has not failed physically; the description has failed by projecting before cancellation was allowed to occur.

This example isolates the central rule of the present paper:

> the block must contain the cancellation motif one wants to preserve.

For the sign-flip DD problem, the minimal such block has size two.

---

## VII. Exact block probabilities from block Pauli coefficients

We now return to the adopted blockwise construction and derive its most useful identity.

Expand the exact conditional block unitary in the Pauli basis:

Eq. (56)
```math
U_b(\xi)=\sum_{Q\in\mathcal P_n} u_{b,Q}(\xi)\,Q,
\qquad
u_{b,Q}(\xi)=2^{-n}\operatorname{Tr}[Q U_b(\xi)].
```

Then the block Pauli-projected channel is obtained exactly by

Eq. (57)
```math
q_{b,Q}(\xi)=|u_{b,Q}(\xi)|^2.
```

The proof is immediate. Starting from

Eq. (58)
```math
U_b(\xi)\rho U_b(\xi)^\dagger
=
\sum_{Q,Q'} u_{b,Q}(\xi)u_{b,Q'}(\xi)^*\,Q\rho Q',
```

Pauli projection drops all terms with `Q\neq Q'`, leaving

Eq. (59)
```math
\Pi_{\mathrm{Pauli}}\!\left[U_b(\xi)\rho U_b(\xi)^\dagger\right]
=
\sum_Q |u_{b,Q}(\xi)|^2\,Q\rho Q.
```

Therefore

Eq. (60)
```math
\widetilde{\mathcal N}_b^{(\xi)}(\rho)
=
\sum_{Q\in\mathcal P_n}|u_{b,Q}(\xi)|^2\,Q\rho Q.
```

This identity is central to the simulator construction: it provides the most direct route from coherent block evolution to a discrete block-fault distribution.

A simple one-qubit example is again helpful. If a block unitary is
```math
U_b(\xi)=\cos\phi\,I-i\sin\phi\,Z,
```
then the Pauli coefficients are
```math
u_{b,I}=\cos\phi,\qquad u_{b,Z}=-i\sin\phi,
```
and therefore
```math
q_{b,I}=\cos^2\phi,\qquad q_{b,Z}=\sin^2\phi.
```
So Eq. (57) is nothing mysterious: it is just the statement that after Pauli projection, only the squared magnitudes of the Pauli amplitudes survive.

---

## VIII. Principal-domain restriction

The usefulness of Eq. (57) depends on the support of the Pauli expansion. Let `\mathcal S_b` be the set of distinct Pauli labels appearing in the segment generators inside block `b`. Define the phase-stripped Pauli subgroup they generate,

Eq. (61)
```math
\mathcal G_b:=\langle \mathcal S_b\rangle.
```

Here `\mathcal G_b` is understood modulo irrelevant global phases, so it is a subgroup of Hermitian Pauli strings.

Then every Pauli appearing in the expansion of `U_b(\xi)` lies inside `\mathcal G_b`. Hence

Eq. (62)
```math
u_{b,Q}(\xi)=0
\qquad
\text{for all } Q\notin \mathcal G_b,
```

and therefore

Eq. (63)
```math
q_{b,Q}(\xi)=0
\qquad
\text{for all } Q\notin \mathcal G_b.
```

We refer to `\mathcal G_b` as the **principal domain** of block `b`.

The principal-domain restriction has two consequences. First, it clarifies the physics: the effective fault alphabet of a block is determined by the local algebra generated by that block, not by the full `4^n` Pauli space. Second, it sharpens the computation: if `|\mathcal G_b|` is much smaller than `4^n`, then exact probability extraction may be restricted to that smaller domain. This is an exact reduction, not an additional approximation.

A tiny example helps. If one block has only `A_1=Z` and `A_2=Z`, then the generated subgroup is just
```math
\mathcal G_b=\{I,Z\},
```
so only `I` and `Z` can appear in the projected block channel. By contrast, if one block contains `A_1=Z` and `A_2=X`, then the generated subgroup is
```math
\mathcal G_b=\{I,X,Y,Z\},
```
which is the full one-qubit Pauli set. The point is that the size of the search space is controlled by the actual local generators in the block, not by the total number of qubits in the entire circuit.

---

## IX. Specialization to `window_size = 2`

We now specialize to the minimal nontrivial choice

Eq. (64)
```math
\texttt{window\_size}=2.
```

For one two-segment block,

Eq. (65)
```math
U_b(\xi)=e^{-i\xi\Delta_2 A_2}e^{-i\xi\Delta_1 A_1}.
```

This object is already much more structured than a generic `n`-qubit unitary because each `A_j` is itself a sum of mutually commuting Pauli strings.

### A. Commuting pair blocks

If

Eq. (66)
```math
[A_1,A_2]=0,
```

then the pair collapses exactly to

Eq. (67)
```math
U_b(\xi)=e^{-i\xi(\Delta_1 A_1+\Delta_2 A_2)}.
```

This includes the canonical special cases

Eq. (68)
```math
A_2=A_1
\qquad\Longrightarrow\qquad
U_b(\xi)=e^{-i\xi(\Delta_1+\Delta_2)A_1},
```

Eq. (69)
```math
A_2=-A_1,\ \Delta_1=\Delta_2
\qquad\Longrightarrow\qquad
U_b(\xi)=I.
```

The sign-flip DD pair is therefore solved exactly with no dense reconstruction.

### B. Anticommutation components

When `[A_1,A_2]\neq 0`, the union of Pauli strings appearing in the pair may still decompose into several anticommutation components. Write

Eq. (70)
```math
\mathcal S_b
=
\mathcal S_{b,1}\sqcup \mathcal S_{b,2}\sqcup \cdots \sqcup \mathcal S_{b,R_b},
```

such that different components commute with one another, while within a component nontrivial anticommutation may occur.

If two distinct components act on disjoint qubit supports, then the block factorizes exactly:

Eq. (71)
```math
U_b(\xi)=\prod_{r=1}^{R_b} U_{b,r}(\xi),
```

with mutually commuting factors acting on disjoint supports. The projected block channel then factorizes as a product or tensor combination of the component channels. This avoids any global `4^n` reconstruction over the full set of qubits.

### C. Direct principal-domain search

If neither of the previous exact reductions is sufficient, the exact block probabilities are still governed by Eq. (57), and the coefficient support is still confined to the principal domain `\mathcal G_b`. The practical hierarchy for `window_size = 2` is therefore:

1. test whether the pair commutes and collapse it if it does;
2. if not, decompose the pair into commuting anticommutation components;
3. if the components are support-disjoint, factorize exactly;
4. otherwise, compute the exact Pauli coefficients only within `\mathcal G_b`.

This is the adopted two-segment analysis hierarchy.

---

## X. Worked examples

### A. One-qubit free evolution over eight equal segments

Take

Eq. (72)
```math
n=1,
\qquad
L=8,
\qquad
\Delta_j=\Delta,
\qquad
C_j=I
\quad\text{for all }j.
```

Then

Eq. (73)
```math
G_j=I,
\qquad
A_j=Z
\quad\text{for all }j.
```

If the full eight-segment cycle is taken as one block, the exact conditional block unitary is

Eq. (74)
```math
U_{\mathrm{free},8}(\xi)=e^{-i8\xi\Delta Z}.
```

Its Pauli expansion is

Eq. (75)
```math
U_{\mathrm{free},8}(\xi)
=
\cos(8\xi\Delta)\,I
-i\sin(8\xi\Delta)\,Z.
```

Hence the exact block Pauli export is

Eq. (76)
```math
\widetilde{\mathcal N}_{\mathrm{free},8}^{(\xi)}(\rho)
=
\cos^2(8\xi\Delta)\,\rho
+
\sin^2(8\xi\Delta)\,Z\rho Z,
```

or equivalently

Eq. (77)
```math
\widetilde{\mathcal N}_{\mathrm{free},8}^{(\xi)}(\rho)
=
\big(1-p_{\mathrm{free},8}(\xi)\big)\rho
+
p_{\mathrm{free},8}(\xi)\,Z\rho Z,
```

with

Eq. (78)
```math
p_{\mathrm{free},8}(\xi)=\sin^2(8\xi\Delta).
```

If `|\xi|\Delta\ll 1`, then

Eq. (79)
```math
p_{\mathrm{free},8}(\xi)
=
64\,\xi^2\Delta^2+O((\xi\Delta)^4).
```

Thus the free block is nontrivial and dephasing.

### B. One-qubit sign-flip DD over eight equal segments

Now take

Eq. (80)
```math
n=1,
\qquad
L=8,
\qquad
\Delta_j=\Delta,
\qquad
C_j=X
\quad\text{for all }j.
```

Then `G_j=X^j`, and because `XZX=-Z` one obtains

Eq. (81)
```math
A_j=(-1)^j Z.
```

If the full eight-segment cycle is taken as one block, the exact conditional unitary is

Eq. (82)
```math
U_{\mathrm{DD},8}(\xi)
=
\prod_{j=1}^{8} e^{-i(-1)^j\xi\Delta Z}
=
I.
```

Hence the exact block Pauli export is simply

Eq. (83)
```math
\widetilde{\mathcal N}_{\mathrm{DD},8}^{(\xi)}(\rho)=\rho.
```

This is the correct quasi-static DD refocusing result.

The contrast with the free case is now as sharp as it should be:

- free block: nontrivial `Z` dephasing,
- DD block: identity.

This is exactly the distinction that segmentwise projection destroyed.

### C. Minimal two-segment pair blocks

The same distinction already appears at `window_size = 2`.

For the free pair,

Eq. (84)
```math
U_{\mathrm{free},2}(\xi)=e^{-i2\xi\Delta Z},
```

so

Eq. (85)
```math
\widetilde{\mathcal N}_{\mathrm{free},2}^{(\xi)}(\rho)
=
\big(1-p_{\mathrm{free},2}(\xi)\big)\rho
+
p_{\mathrm{free},2}(\xi)\,Z\rho Z,
```

with

Eq. (86)
```math
p_{\mathrm{free},2}(\xi)=\sin^2(2\xi\Delta)
=
4\,\xi^2\Delta^2+O((\xi\Delta)^4).
```

For the DD pair,

Eq. (87)
```math
U_{\mathrm{DD},2}(\xi)=e^{+i\xi\Delta Z}e^{-i\xi\Delta Z}=I,
```

and therefore

Eq. (88)
```math
\widetilde{\mathcal N}_{\mathrm{DD},2}^{(\xi)}(\rho)=\rho.
```

Thus `window_size = 2` is already sufficient to separate free evolution from sign-flip DD. This is the smallest block size that restores the relevant cancellation physics.

### D. Multi-qubit collective free evolution

It is also useful to record the analytic free-evolution case for arbitrary
qubit number `n`, because it gives a clean validation target for the
multi-qubit notebook tests.

Take

Eq. (89)
```math
n \text{ arbitrary},
\qquad
C_j = I
\quad\text{for all }j.
```

Then every cumulative Clifford is trivial, so

Eq. (90)
```math
G_j = I,
\qquad
A_j = \sum_{a=1}^n Z_a
\quad\text{for all }j.
```

For one block `b`, define the total block duration

Eq. (91)
```math
T_b := \sum_{j\in J_b} \Delta_j,
\qquad
\theta_b(\xi) := \xi T_b.
```

The exact conditional block unitary becomes

Eq. (92)
```math
U_b(\xi)
=
e^{-i\theta_b(\xi)\sum_{a=1}^n Z_a}
=
\prod_{a=1}^n e^{-i\theta_b(\xi) Z_a}.
```

Since all local `Z_a` commute, this expands exactly as

Eq. (93)
```math
U_b(\xi)
=
\sum_{S\subseteq \{1,\dots,n\}}
\big(-i\sin\theta_b(\xi)\big)^{|S|}
\big(\cos\theta_b(\xi)\big)^{n-|S|}
Z_S,
```

where
```math
Z_S := \prod_{a\in S} Z_a,
\qquad
Z_{\varnothing}:=I.
```

Therefore the exact block Pauli export is supported only on the all-`Z`
subgroup

Eq. (94)
```math
\mathcal G_b
=
\langle Z_1,\dots,Z_n\rangle
=
\{Z_S : S\subseteq \{1,\dots,n\}\},
```

and the conditional block probabilities are

Eq. (95)
```math
q_{b,Z_S}(\xi)
=
\sin^{2|S|}\!\theta_b(\xi)\,
\cos^{2(n-|S|)}\!\theta_b(\xi).
```

Equivalently, if
```math
p_b(\xi):=\sin^2\!\theta_b(\xi),
```
then
```math
q_{b,Z_S}(\xi)=p_b(\xi)^{|S|}\big(1-p_b(\xi)\big)^{n-|S|}.
```
So conditioned on the hidden variable `\xi`, the free collective block channel
is exactly the product distribution of `n` identical `Z`-flip Bernoulli
variables.

For `n=2`, one obtains explicitly
```math
q_{b,II}=(1-p_b)^2,
\qquad
q_{b,ZI}=q_{b,IZ}=p_b(1-p_b),
\qquad
q_{b,ZZ}=p_b^2.
```
In the weak-block limit `|\theta_b(\xi)|\ll 1`, this gives
```math
q_{b,ZI}=q_{b,IZ}=\theta_b(\xi)^2 + O(\theta_b(\xi)^4),
\qquad
q_{b,ZZ}=\theta_b(\xi)^4 + O(\theta_b(\xi)^6).
```
Thus the two single-`Z` faults dominate the double-`Z` fault at small angle,
which is exactly the pattern expected in the notebook's two-qubit free test.

### E. Two-qubit alternating-`CNOT` cycle

We now consider a two-qubit Clifford history that is still analytically
tractable but already nontrivial:

Eq. (96)
```math
n=2,
\qquad
L=8,
\qquad
\Delta_j=\Delta,
```

with the ideal depth-8 control sequence
```math
C_1,\dots,C_8
=
\mathrm{CNOT}_{12},
\mathrm{CNOT}_{21},
\mathrm{CNOT}_{12},
\mathrm{CNOT}_{21},
\mathrm{CNOT}_{12},
\mathrm{CNOT}_{21},
\mathrm{CNOT}_{12},
\mathrm{CNOT}_{21}.
```

Let
```math
A:=\mathrm{CNOT}_{12},
\qquad
B:=\mathrm{CNOT}_{21}.
```
Using the standard Clifford conjugation rules
```math
A^\dagger Z_1 A = Z_1,
\qquad
A^\dagger Z_2 A = Z_1 Z_2,
```
and
```math
B^\dagger Z_1 B = Z_1 Z_2,
\qquad
B^\dagger Z_2 B = Z_2,
```
one obtains the segment generators

Eq. (97)
```math
\begin{aligned}
A_1 &= Z_1 + Z_1 Z_2,\\
A_2 &= Z_1 + Z_1 Z_2,\\
A_3 &= Z_1 + Z_2,\\
A_4 &= Z_2 + Z_1 Z_2,\\
A_5 &= Z_2 + Z_1 Z_2,\\
A_6 &= Z_1 + Z_2,\\
A_7 &= Z_1 + Z_1 Z_2,\\
A_8 &= Z_1 + Z_1 Z_2.
\end{aligned}
```

Every `A_j` is a sum of `Z`-type Paulis, so all of them commute. Thus the
exact analysis is simple even though the ideal control is not trivial.

For the practical notebook choice `\texttt{window\_size}=2`, the depth-8 cycle
splits into four pair blocks:

Eq. (98)
```math
(A_1,A_2),\quad (A_3,A_4),\quad (A_5,A_6),\quad (A_7,A_8).
```

There are only two distinct block types.

#### Type-I blocks: `b=1,4`

The first and fourth blocks both satisfy

Eq. (99)
```math
A_{2r-1}=A_{2r}=Z_1+Z_1 Z_2,
\qquad r\in\{1,4\}.
```

Hence

Eq. (100)
```math
U_b(\xi)
=
e^{-i2\xi\Delta (Z_1+Z_1 Z_2)}
=
e^{-i2\xi\Delta Z_1}\,e^{-i2\xi\Delta Z_1 Z_2}.
```

Let
```math
P(\xi):=\sin^2(2\xi\Delta).
```
Then the exact block Pauli export is

Eq. (101)
```math
\begin{aligned}
q_{b,II}(\xi) &= (1-P(\xi))^2,\\
q_{b,ZI}(\xi) &= P(\xi)\big(1-P(\xi)\big),\\
q_{b,ZZ}(\xi) &= P(\xi)\big(1-P(\xi)\big),\\
q_{b,IZ}(\xi) &= P(\xi)^2.
\end{aligned}
```

So a Type-I block is biased toward `ZI` and `ZZ`, with `IZ` appearing only at
the higher-order rate `P^2`.

#### Type-II blocks: `b=2,3`

The second and third blocks are

Eq. (102)
```math
(A_3,A_4)=(Z_1+Z_2,\; Z_2+Z_1 Z_2),
```

and similarly for `(A_5,A_6)` in reversed order. Since all participating terms
commute, both blocks have the same exact Pauli export.

Let
```math
p(\xi):=\sin^2(\xi\Delta),
\qquad
P(\xi):=\sin^2(2\xi\Delta).
```
Then

Eq. (103)
```math
\begin{aligned}
q_{b,ZI}(\xi) &= p(\xi)\big(1-p(\xi)\big),\\
q_{b,ZZ}(\xi) &= p(\xi)\big(1-p(\xi)\big),\\
q_{b,II}(\xi) &= \big(1-P(\xi)\big)\big(1-p(\xi)\big)^2 + P(\xi)\,p(\xi)^2,\\
q_{b,IZ}(\xi) &= \big(1-P(\xi)\big)p(\xi)^2 + P(\xi)\big(1-p(\xi)\big)^2.
\end{aligned}
```

In the weak-segment limit `|\xi|\Delta\ll 1`, this gives
```math
q_{b,ZI}(\xi)=q_{b,ZZ}(\xi)=\xi^2\Delta^2 + O((\xi\Delta)^4),
```
while
```math
q_{b,IZ}(\xi)=4\xi^2\Delta^2 + O((\xi\Delta)^4).
```
So the Type-II blocks are dominated by `IZ`, with smaller but equal `ZI` and
`ZZ` contributions.

This example is useful because it is still analytically closed, but it already
shows a nontrivial block pattern generated purely by Clifford history.

---

## XI. Accuracy, scope, and interpretation

The blockwise hidden-memory export is not exact for the full circuit. Its accuracy statement is instead local and physically transparent:

1. the exact shared memory `\xi` is preserved across the shot;
2. coherent propagation is kept exactly or near-exactly within each block;
3. off-diagonal Pauli-transfer structure is discarded only at block boundaries;
4. cancellation mechanisms completed inside the chosen block are preserved;
5. coherent recombination spanning different blocks is not preserved once the block boundary has been crossed.

The residual approximation error therefore comes from cross-block coherence that has been intentionally discarded. If an important cancellation pattern extends over several blocks, the block size must be enlarged accordingly. The window size is thus a physical modeling parameter, not a merely formal one.

When the raw segments are weak, one may further sparsify the already-computed block channel by retaining only the dominant block faults. That additional truncation is controlled by the same rare-event scaling that appears in the weak-segment expansion. But it should be viewed as a secondary approximation. The primary modeling improvement of the present paper is the **delayed projection** itself.

---
## XIII. Conclusion

The present noise model is controlled by one simple but far-reaching structural fact: the same hidden quasi-static Gaussian variable is shared across the entire circuit shot. Under Clifford control, this produces an exact channel that is a continuous Gaussian mixture of coherent non-Clifford unitaries. In general, the exact map is not Pauli-diagonal and cannot be rewritten as a product of independent layer-local Pauli channels.

For fast simulation, the relevant question is therefore not how to force the full exact channel into an exact Pauli form, but how to construct a reduced Pauli-compatible description that preserves the physics most relevant to control. The central answer of this paper is that the decisive modeling choice is the timing of projection. Projection after every raw segment preserves neither the global correlation structure nor the local sign-sensitive cancellation mechanism in a satisfactory way. Projection after a completed block does.

The resulting blockwise hidden-memory Pauli export keeps the shared hidden variable shot-by-shot, propagates coherently through a short control window, and only then converts that completed block to a Pauli channel. This construction produces a clear and physically motivated simulator object, retains the dominant cancellation physics internal to each block, and remains compatible with stabilizer-based sampling. For `window_size = 2`, the method acquires additional exact structure—commuting-pair collapse, support-disjoint factorization of anticommutation components, and principal-domain restriction—that makes the minimal nontrivial block already useful in practice.

The main lesson is therefore concise. In correlated hidden-memory noise models, the success of a Pauli export depends not only on what is projected away, but on **when** that projection is performed. A faithful fast simulator must preserve the shared memory, allow the intended local cancellation to happen, and only then apply Pauli projection.







## Appendix: Minimal End-to-End Recipe for Channel Construction (Code-Oriented)

This appendix is a **concise implementation guide**, not a re-derivation.  
It lists only the objects and equations **actually needed in code**.

---

### A. Required Inputs

- Clifford circuit: list of gates → defines cumulative frames
- Number of segments: $`L`$
- Segment durations: $`\{\Delta_j\}_{j=1}^L`$
- Noise strength: $`\sigma`$ (Gaussian std)
- Block size: $`w`$ (default $`=2`$)
- Number of samples: $`N_{\text{MC}}`$ (if Monte Carlo)

---

### B. Preprocessing: Build Toggling-Frame Generators

Compute cumulative Clifford -- **stim support efficient simulation for large qubits**:
```math
G_j = C_j C_{j-1} \cdots C_1
```

Then generators:
```math
A_j = G_j^\dagger \left(\sum_a Z_a\right) G_j
```

Represent each $`A_j`$ as a list of Pauli strings:
```math
A_j = \sum_\ell \nu_{\ell,j} Q_{\ell,j}
```

(Combine duplicate Pauli strings into multiplicities $`\nu_{\ell,j}`$)

---

### C. Block Construction

Partition segments into blocks of size $`w`$:

Block $`b`$:
```math
J_b = \{s_b, \dots, e_b\}
```

Block unitary:
```math
U_b(\xi) = \prod_{j=e_b}^{s_b} e^{-i \xi \Delta_j A_j}
```

---

### D. Block → Pauli Channel (Core Step)

Expand:
```math
U_b(\xi) = \sum_{Q \in \mathcal{G}_b} u_{b,Q}(\xi)\, Q
```

Then probabilities:
```math
q_{b,Q}(\xi) = |u_{b,Q}(\xi)|^2
```

👉 This is the ONLY formula needed for Pauli sampling.

---

### E. Principal Domain Restriction

Define:
```math
\mathcal{G}_b = \langle \{Q_{\ell,j} : j \in J_b\} \rangle
```

Only compute over:
```math
Q \in \mathcal{G}_b
```

(All others have zero probability.)

---

### F. Sampling Procedure (Monte Carlo)

Repeat for each shot:

#### 1. Sample noise
```math
\xi \sim \mathcal{N}(0,\sigma^2)
```

#### 2. For each block $`b`$:
- Compute $`U_b(\xi)`$ (exact or via simplification)
- Compute $`q_{b,Q}(\xi)`$ over $`Q \in \mathcal{G}_b`$
- Sample one Pauli $`Q_b`$ from $`\{q_{b,Q}\}`$

#### 3. Convert to physical Pauli fault
```math
F_b = G_{e_b} \, Q_b \, G_{e_b}^\dagger
```

#### 4. Apply to circuit
Insert $`F_b`$ after block $`b`$

---

### G. Final Output

Monte Carlo estimate of channel:
```math
\mathcal{E}(\rho) \approx \frac{1}{N_{\text{MC}}} \sum_{\text{shots}} \left( \prod_b F_b \right) \rho \left( \prod_b F_b \right)^\dagger
```

---

### H. Special Optimization: $`w=2`$

For each block:

#### Case 1: $`[A_1, A_2]=0`$
```math
U_b(\xi) = e^{-i \xi (\Delta_1 A_1 + \Delta_2 A_2)}
```

#### Case 2: $`A_2 = -A_1`$, $`\Delta_1=\Delta_2`$
```math
U_b(\xi) = I
```

#### Otherwise:
- compute only within $`\mathcal{G}_b`$

---

### I. Notes for Implementation

- All Pauli propagation uses Clifford conjugation → efficient
- $`\mathcal{G}_b`$ is typically small for $`w=2`$
- Main cost: computing $`u_{b,Q}(\xi)`$
- Use sparse representation of Pauli strings

---

### Summary (Minimal Core)

The simulation reduces to:

1. Build $`A_j`$
2. Form $`U_b(\xi)`$
3. Compute $`q_{b,Q} = |u_{b,Q}|^2`$
4. Sample $`Q_b`$
5. Map to physical $`F_b`$
6. Repeat

Everything else is optional.
