"""Pomoćne funkcije za tekst: ćirilica → latinica i normalizacija."""

import re

_CIR_LAT = {
    "А": "A", "Б": "B", "В": "V", "Г": "G", "Д": "D", "Ђ": "Đ", "Е": "E", "Ж": "Ž", "З": "Z",
    "И": "I", "Ј": "J", "К": "K", "Л": "L", "Љ": "Lj", "М": "M", "Н": "N", "Њ": "Nj", "О": "O",
    "П": "P", "Р": "R", "С": "S", "Т": "T", "Ћ": "Ć", "У": "U", "Ф": "F", "Х": "H", "Ц": "C",
    "Ч": "Č", "Џ": "Dž", "Ш": "Š",
}
_CIR_LAT.update({k.lower(): v.lower() for k, v in list(_CIR_LAT.items())})


def u_latinicu(tekst: str) -> str:
    """Prebacuje ćirilicu u latinicu (ostali znakovi ostaju isti)."""
    return "".join(_CIR_LAT.get(z, z) for z in tekst)


def normalizuj(tekst: str) -> str:
    """Latinica, mala slova, jedan razmak. Koristi se za poređenje naziva veština."""
    tekst = u_latinicu(tekst or "").lower()
    return re.sub(r"\s+", " ", tekst).strip()
