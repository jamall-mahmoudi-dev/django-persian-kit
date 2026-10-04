"""Digit and text normalisation helpers (no Django required)."""

from __future__ import annotations

from typing import Optional

PERSIAN_DIGITS = "۰۱۲۳۴۵۶۷۸۹"
ARABIC_DIGITS = "٠١٢٣٤٥٦٧٨٩"
ASCII_DIGITS = "0123456789"

_TO_ASCII = str.maketrans(PERSIAN_DIGITS + ARABIC_DIGITS, ASCII_DIGITS * 2)
_TO_PERSIAN = str.maketrans(ASCII_DIGITS + ARABIC_DIGITS, PERSIAN_DIGITS * 2)

# Arabic letter forms that are often typed instead of the Persian ones,
# plus the tatweel (kashida) which is removed.
_LETTERS = str.maketrans({"ي": "ی", "ى": "ی", "ك": "ک", "ـ": None})


def to_persian_digits(value) -> str:
    """Convert ASCII and Arabic-Indic digits to Persian digits.

    >>> to_persian_digits("Order 1403/01/15")
    'Order ۱۴۰۳/۰۱/۱۵'
    """
    return str(value).translate(_TO_PERSIAN)


def to_english_digits(value) -> str:
    """Convert Persian and Arabic-Indic digits to ASCII digits.

    >>> to_english_digits("۰۹۱۲۳۴۵۶۷۸۹")
    '09123456789'
    """
    return str(value).translate(_TO_ASCII)


def normalize_persian_text(value, digits: Optional[str] = "ascii") -> str:
    """Normalise text typed with an Arabic keyboard layout.

    * Arabic ``ي`` / ``ى`` become Persian ``ی``; Arabic ``ك`` becomes ``ک``.
    * Tatweel (``ـ``) is removed.
    * ``digits`` controls digits: ``"ascii"`` (default), ``"persian"`` or
      ``None`` to leave them untouched.
    """
    text = str(value).translate(_LETTERS)
    if digits == "ascii":
        text = to_english_digits(text)
    elif digits == "persian":
        text = to_persian_digits(text)
    elif digits is not None:
        raise ValueError("digits must be 'ascii', 'persian' or None")
    return text


def add_thousands_separator(value, sep: str = ",") -> str:
    """Group the integer part of a number in thousands.

    Accepts ints, floats and digit strings (including Persian digits).
    Values that are not numbers are returned unchanged as ``str``.

    >>> add_thousands_separator(1234567)
    '1,234,567'
    >>> add_thousands_separator("۱۲۳۴۵.۵")
    '12,345.5'
    """
    text = to_english_digits(str(value)).strip()
    sign = ""
    if text and text[0] in "+-":
        sign = "-" if text[0] == "-" else ""
        text = text[1:]
    whole, dot, frac = text.partition(".")
    if not (whole.isascii() and whole.isdigit()):
        return str(value)
    if frac and not (frac.isascii() and frac.isdigit()):
        return str(value)
    grouped = f"{int(whole):,}".replace(",", sep)
    return f"{sign}{grouped}{dot}{frac}"
