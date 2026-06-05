"""Core ID encoding/decoding for the DIEF-MO framework.

A DIEF-MO identifier follows the pattern:
    <EXPERIMENT>_<AREA>_<MATRIX>_<SEQ>
for example: E001_PRO_M001_001
"""
import re

# Regex used both to validate and to extract the parts of an identifier.
DIEF_ID_PATTERN = re.compile(
    r"^(?P<experiment>[A-Za-z0-9]+)_"
    r"(?P<area>[A-Za-z0-9]+)_"
    r"(?P<matrix>[A-Za-z0-9]+)_"
    r"(?P<seq>\d{3,})$"
)


def generate_id(experiment: str, area: str, matrix: str, seq: int) -> str:
    """Build a DIEF-MO identifier from its parts.

    The sequence is zero-padded to at least three digits (001, 002, ...).
    """
    for label, value in (("experiment", experiment), ("area", area), ("matrix", matrix)):
        if value is None or str(value).strip() == "":
            raise ValueError(f"'{label}' nao pode ser vazio.")
    seq = int(seq)
    if seq < 1:
        raise ValueError("'seq' deve ser >= 1.")
    return f"{experiment}_{area}_{matrix}_{seq:03d}"


def decode_id(dief_id: str) -> dict:
    """Parse a DIEF-MO identifier back into its components using regex."""
    match = DIEF_ID_PATTERN.match(str(dief_id).strip())
    if not match:
        raise ValueError(f"Identificador invalido: {dief_id!r}")
    parts = match.groupdict()
    parts["seq"] = int(parts["seq"])
    return parts
