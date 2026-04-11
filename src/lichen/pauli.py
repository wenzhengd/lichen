"""Internal Pauli-string helpers for the env modules.

These helpers are intentionally small and self-contained.  The env-side
approximation in ``thought-2-pro.md`` works entirely in the Pauli basis, so the
implementation needs reliable utilities for:

- enumerating n-qubit Pauli strings,
- conjugating a Pauli string by a supported Clifford gate, and
- testing commutation in the Pauli basis.

For some env calculations, the Pauli sign does matter. In particular, the
toggling-frame generators ``A_j`` for dynamical-decoupling-like behavior depend
on whether a propagated ``Z`` becomes ``+Z`` or ``-Z``.  This file therefore
provides both:

- a sign-discarding Pauli-label conjugation helper, and
- a sign-aware Pauli conjugation helper.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product

import numpy as np

PAULI_LETTERS: tuple[str, ...] = ("I", "X", "Y", "Z")
_LOCAL_MULTIPLICATION_TABLE: dict[tuple[str, str], tuple[complex, str]] = {
    ("I", "I"): (1.0, "I"),
    ("I", "X"): (1.0, "X"),
    ("I", "Y"): (1.0, "Y"),
    ("I", "Z"): (1.0, "Z"),
    ("X", "I"): (1.0, "X"),
    ("X", "X"): (1.0, "I"),
    ("X", "Y"): (1.0j, "Z"),
    ("X", "Z"): (-1.0j, "Y"),
    ("Y", "I"): (1.0, "Y"),
    ("Y", "X"): (-1.0j, "Z"),
    ("Y", "Y"): (1.0, "I"),
    ("Y", "Z"): (1.0j, "X"),
    ("Z", "I"): (1.0, "Z"),
    ("Z", "X"): (1.0j, "Y"),
    ("Z", "Y"): (-1.0j, "X"),
    ("Z", "Z"): (1.0, "I"),
}

_SINGLE_QUBIT_SIGNED_MAPS: dict[str, dict[str, tuple[int, str]]] = {
    "I": {"I": (1, "I"), "X": (1, "X"), "Y": (1, "Y"), "Z": (1, "Z")},
    "X": {"I": (1, "I"), "X": (1, "X"), "Y": (-1, "Y"), "Z": (-1, "Z")},
    "Y": {"I": (1, "I"), "X": (-1, "X"), "Y": (1, "Y"), "Z": (-1, "Z")},
    "Z": {"I": (1, "I"), "X": (-1, "X"), "Y": (-1, "Y"), "Z": (1, "Z")},
    "H": {"I": (1, "I"), "X": (1, "Z"), "Y": (-1, "Y"), "Z": (1, "X")},
    "S": {"I": (1, "I"), "X": (1, "Y"), "Y": (-1, "X"), "Z": (1, "Z")},
    "S_DAG": {"I": (1, "I"), "X": (-1, "Y"), "Y": (1, "X"), "Z": (1, "Z")},
    # The sqrt gates remain available, but if they matter later the sign-aware
    # rules can be extended explicitly.  For the current gate policy and env
    # tests, H/S/CNOT are the important cases.
    "SQRT_X": {"I": (1, "I"), "X": (1, "X"), "Y": (1, "Z"), "Z": (-1, "Y")},
    "SQRT_X_DAG": {"I": (1, "I"), "X": (1, "X"), "Y": (-1, "Z"), "Z": (1, "Y")},
    "SQRT_Y": {"I": (1, "I"), "X": (-1, "Z"), "Y": (1, "Y"), "Z": (1, "X")},
    "SQRT_Y_DAG": {"I": (1, "I"), "X": (1, "Z"), "Y": (1, "Y"), "Z": (-1, "X")},
    "SQRT_Z": {"I": (1, "I"), "X": (1, "Y"), "Y": (-1, "X"), "Z": (1, "Z")},
    "SQRT_Z_DAG": {"I": (1, "I"), "X": (-1, "Y"), "Y": (1, "X"), "Z": (1, "Z")},
}

_CNOT_LOCAL_SIGNED_MAP: dict[tuple[str, str], tuple[int, str, str]] = {}


@dataclass(frozen=True)
class SignedPauliTerm:
    """A Pauli string with a real sign.

    The env-side shared-noise model needs signed Pauli generators because
    toggling-frame Clifford propagation can map ``Z`` to either ``+P`` or
    ``-P``.  The sign is stored separately from the label because the retained
    diagonal is still expressed in the ordinary phase-free Pauli basis.
    """

    sign: int
    pauli_string: str

    def __post_init__(self) -> None:
        if self.sign not in {-1, 1}:
            raise ValueError("SignedPauliTerm.sign must be either +1 or -1.")
        validate_pauli_string(self.pauli_string)


def validate_pauli_string(pauli_string: str, *, expected_num_qubits: int | None = None) -> None:
    """Validate that a string is a well-formed n-qubit Pauli label."""

    if expected_num_qubits is not None and len(pauli_string) != expected_num_qubits:
        raise ValueError(
            f"Expected a {expected_num_qubits}-qubit Pauli string, got {len(pauli_string)}."
        )

    invalid_letters = sorted(set(pauli_string) - set(PAULI_LETTERS))
    if invalid_letters:
        raise ValueError(
            "Pauli strings may only contain I, X, Y, Z. "
            f"Invalid letters: {', '.join(invalid_letters)}."
        )


def enumerate_pauli_basis(num_qubits: int) -> tuple[str, ...]:
    """Return the full n-qubit Pauli basis in lexicographic order."""

    if num_qubits < 1:
        raise ValueError("num_qubits must be positive.")
    return tuple("".join(letters) for letters in product(PAULI_LETTERS, repeat=num_qubits))


def count_xy_support(pauli_string: str) -> int:
    """Count the qubits where the Pauli string carries X or Y."""

    validate_pauli_string(pauli_string)
    return sum(letter in {"X", "Y"} for letter in pauli_string)


def pauli_string_to_matrix(pauli_string: str) -> np.ndarray:
    """Convert an n-qubit Pauli string into its dense matrix representation."""

    validate_pauli_string(pauli_string)

    local_matrices = {
        "I": np.array([[1.0, 0.0], [0.0, 1.0]], dtype=complex),
        "X": np.array([[0.0, 1.0], [1.0, 0.0]], dtype=complex),
        "Y": np.array([[0.0, -1.0j], [1.0j, 0.0]], dtype=complex),
        "Z": np.array([[1.0, 0.0], [0.0, -1.0]], dtype=complex),
    }

    matrix = np.array([[1.0]], dtype=complex)
    for letter in pauli_string:
        matrix = np.kron(matrix, local_matrices[letter])
    return matrix


def single_qubit_pauli_string(num_qubits: int, qubit: int, letter: str) -> str:
    """Return an n-qubit Pauli string with one non-identity local factor."""

    if num_qubits < 1:
        raise ValueError("num_qubits must be positive.")
    if qubit < 0 or qubit >= num_qubits:
        raise ValueError(f"Qubit index {qubit} is out of range for {num_qubits} qubits.")
    if letter not in {"X", "Y", "Z"}:
        raise ValueError("letter must be X, Y, or Z.")

    letters = ["I"] * num_qubits
    letters[qubit] = letter
    return "".join(letters)


def pauli_commutation_sign(left: str, right: str) -> int:
    """Return +1 for commuting Pauli strings and -1 for anticommuting ones."""

    validate_pauli_string(left)
    validate_pauli_string(right, expected_num_qubits=len(left))

    anticommute_count = 0
    for left_letter, right_letter in zip(left, right):
        if left_letter == "I" or right_letter == "I":
            continue
        if left_letter != right_letter:
            anticommute_count += 1
    return 1 if anticommute_count % 2 == 0 else -1


def multiply_pauli_strings(left: str, right: str) -> tuple[complex, str]:
    """Multiply two phase-free Pauli labels.

    Returns
    -------
    (phase, label):
        ``phase`` is one of ``{+1, -1, +i, -i}``, and ``label`` is the Pauli
        string after removing that global phase.

    This is the key primitive for sparse Pauli-basis propagation under
    conjugation by ``exp(-i theta P)``.
    """

    validate_pauli_string(left)
    validate_pauli_string(right, expected_num_qubits=len(left))

    phase = 1.0 + 0.0j
    letters: list[str] = []
    for left_letter, right_letter in zip(left, right):
        local_phase, local_letter = _LOCAL_MULTIPLICATION_TABLE[(left_letter, right_letter)]
        phase *= local_phase
        letters.append(local_letter)
    return phase, "".join(letters)


def conjugate_pauli_by_gate(pauli_string: str, gate_name: str, qubits: tuple[int, ...]) -> str:
    """Conjugate an n-qubit Pauli string by a supported ideal Clifford gate.

    The result is returned as another Pauli string with the same length.  Global
    phases are discarded because the env approximation only needs Pauli labels.
    """

    sign, label = conjugate_pauli_by_gate_with_sign(pauli_string, gate_name, qubits)
    _ = sign
    return label


def conjugate_pauli_by_gate_with_sign(
    pauli_string: str, gate_name: str, qubits: tuple[int, ...]
) -> tuple[int, str]:
    """Conjugate an n-qubit Pauli string by a supported Clifford gate.

    Returns
    -------
    (sign, pauli_label):
        ``sign`` is either ``+1`` or ``-1``.  The returned Pauli label carries
        no phase.  This is the correct level of detail for Clifford conjugation
        of Pauli observables in the env modules.
    """

    validate_pauli_string(pauli_string)

    num_qubits = len(pauli_string)
    letters = list(pauli_string)
    for qubit in qubits:
        if qubit < 0 or qubit >= num_qubits:
            raise ValueError(f"Qubit index {qubit} is out of range for {num_qubits} qubits.")

    if gate_name in _SINGLE_QUBIT_SIGNED_MAPS:
        if len(qubits) != 1:
            raise ValueError(f"Gate {gate_name} must act on exactly one qubit.")
        target = qubits[0]
        sign, mapped = _SINGLE_QUBIT_SIGNED_MAPS[gate_name][letters[target]]
        letters[target] = mapped
        return sign, "".join(letters)

    if gate_name == "CNOT":
        if len(qubits) != 2:
            raise ValueError("CNOT must act on exactly two qubits.")
        control, target = qubits
        sign, new_control, new_target = _CNOT_LOCAL_SIGNED_MAP[(letters[control], letters[target])]
        letters[control] = new_control
        letters[target] = new_target
        return sign, "".join(letters)

    matrix = pauli_string_to_matrix(pauli_string)
    unitary = _gate_unitary(gate_name, qubits, num_qubits)
    conjugated = unitary @ matrix @ unitary.conj().T
    return _matrix_to_signed_pauli_label(conjugated)


def _booleans_to_pauli_letter(has_x: bool, has_z: bool) -> str:
    """Convert symplectic X/Z support bits into a Pauli letter."""

    if has_x and has_z:
        return "Y"
    if has_x:
        return "X"
    if has_z:
        return "Z"
    return "I"


def _gate_unitary(gate_name: str, qubits: tuple[int, ...], num_qubits: int) -> np.ndarray:
    """Return the dense unitary matrix of a supported ideal Clifford gate."""

    for qubit in qubits:
        if qubit < 0 or qubit >= num_qubits:
            raise ValueError(f"Qubit index {qubit} is out of range for {num_qubits} qubits.")

    local_matrices = {
        "I": np.array([[1.0, 0.0], [0.0, 1.0]], dtype=complex),
        "X": np.array([[0.0, 1.0], [1.0, 0.0]], dtype=complex),
        "Y": np.array([[0.0, -1.0j], [1.0j, 0.0]], dtype=complex),
        "Z": np.array([[1.0, 0.0], [0.0, -1.0]], dtype=complex),
        "H": (1.0 / np.sqrt(2.0)) * np.array([[1.0, 1.0], [1.0, -1.0]], dtype=complex),
        "S": np.array([[1.0, 0.0], [0.0, 1.0j]], dtype=complex),
        "S_DAG": np.array([[1.0, 0.0], [0.0, -1.0j]], dtype=complex),
        "SQRT_X": 0.5 * np.array(
            [[1.0 + 1.0j, 1.0 - 1.0j], [1.0 - 1.0j, 1.0 + 1.0j]], dtype=complex
        ),
        "SQRT_X_DAG": 0.5 * np.array(
            [[1.0 - 1.0j, 1.0 + 1.0j], [1.0 + 1.0j, 1.0 - 1.0j]], dtype=complex
        ),
        "SQRT_Y": 0.5 * np.array(
            [[1.0 + 1.0j, -1.0 - 1.0j], [1.0 + 1.0j, 1.0 + 1.0j]], dtype=complex
        ),
        "SQRT_Y_DAG": 0.5 * np.array(
            [[1.0 - 1.0j, 1.0 - 1.0j], [-1.0 + 1.0j, 1.0 - 1.0j]], dtype=complex
        ),
        "SQRT_Z": np.array([[1.0, 0.0], [0.0, 1.0j]], dtype=complex),
        "SQRT_Z_DAG": np.array([[1.0, 0.0], [0.0, -1.0j]], dtype=complex),
    }

    if gate_name in local_matrices:
        if len(qubits) != 1:
            raise ValueError(f"Gate {gate_name} must act on exactly one qubit.")
        target = qubits[0]
        unitary = np.array([[1.0]], dtype=complex)
        for qubit in range(num_qubits):
            local = local_matrices[gate_name] if qubit == target else local_matrices["I"]
            unitary = np.kron(unitary, local)
        return unitary

    if gate_name != "CNOT":
        raise ValueError(f"Unsupported Clifford gate for env tracking: {gate_name}.")
    if len(qubits) != 2:
        raise ValueError("CNOT must act on exactly two qubits.")

    control, target = qubits
    dimension = 2**num_qubits
    unitary = np.zeros((dimension, dimension), dtype=complex)
    for basis_index in range(dimension):
        bits = [(basis_index >> (num_qubits - 1 - idx)) & 1 for idx in range(num_qubits)]
        if bits[control] == 1:
            bits[target] ^= 1
        output_index = 0
        for bit in bits:
            output_index = (output_index << 1) | bit
        unitary[output_index, basis_index] = 1.0
    return unitary


def _matrix_to_signed_pauli_label(matrix: np.ndarray) -> tuple[int, str]:
    """Convert a Pauli matrix with sign into ``(+/-1, label)``."""

    num_qubits = int(round(np.log2(matrix.shape[0])))
    basis = enumerate_pauli_basis(num_qubits)
    for pauli_string in basis:
        pauli_matrix = pauli_string_to_matrix(pauli_string)
        if np.allclose(matrix, pauli_matrix):
            return 1, pauli_string
        if np.allclose(matrix, -pauli_matrix):
            return -1, pauli_string
    raise ValueError("Matrix is not a signed Pauli operator.")


def _initialize_cnot_lookup() -> None:
    """Populate the local 2-qubit CNOT Pauli conjugation table once."""

    if _CNOT_LOCAL_SIGNED_MAP:
        return

    cnot = np.array(
        [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]],
        dtype=complex,
    )
    local_basis = ("I", "X", "Y", "Z")
    for left in local_basis:
        for right in local_basis:
            local_label = left + right
            local_matrix = pauli_string_to_matrix(local_label)
            conjugated = cnot @ local_matrix @ cnot.conj().T
            sign, mapped = _matrix_to_signed_pauli_label(conjugated)
            _CNOT_LOCAL_SIGNED_MAP[(left, right)] = (sign, mapped[0], mapped[1])


_initialize_cnot_lookup()
