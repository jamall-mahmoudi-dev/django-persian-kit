"""Validators for Iranian identifiers (no Django required).

All ``is_valid_*`` functions accept Persian/Arabic digits and tolerate
spaces, hyphens and invisible direction marks.
"""

from __future__ import annotations

import re

from .digits import to_english_digits

_NOISE = re.compile(r"[\s\-()\u200c\u200e\u200f\u202a-\u202e]")


def clean_digits(value) -> str:
    """Convert to ASCII digits and drop spaces, hyphens, brackets and RTL marks."""
    return _NOISE.sub("", to_english_digits(str(value)))


# -- national ID (کد ملی) ----------------------------------------------------
def is_valid_national_id(value) -> bool:
    """Check an Iranian 10-digit national ID (کد ملی) including its check digit."""
    code = clean_digits(value)
    if not re.fullmatch(r"[0-9]{10}", code) or len(set(code)) == 1:
        return False
    total = sum(int(code[i]) * (10 - i) for i in range(9))
    remainder = total % 11
    check = int(code[9])
    return check == remainder if remainder < 2 else check == 11 - remainder


# -- mobile -------------------------------------------------------------------
def normalize_mobile(value) -> str:
    """Return an Iranian mobile number as ``09XXXXXXXXX`` when it can be recognised.

    Handles ``+98912...``, ``0098912...``, ``98912...`` and ``912...``. Anything
    else is returned cleaned but otherwise unchanged (and will fail validation).
    """
    number = clean_digits(value).lstrip("+")
    if number.startswith("0098"):
        number = "0" + number[4:]
    elif number.startswith("98") and len(number) == 12:
        number = "0" + number[2:]
    elif len(number) == 10 and number.startswith("9"):
        number = "0" + number
    return number


def is_valid_mobile(value) -> bool:
    return re.fullmatch(r"09[0-9]{9}", normalize_mobile(value)) is not None


# -- bank card ------------------------------------------------------------------
def _luhn_ok(number: str) -> bool:
    total = 0
    for index, char in enumerate(reversed(number)):
        digit = int(char)
        if index % 2 == 1:
            digit *= 2
            if digit > 9:
                digit -= 9
        total += digit
    return total % 10 == 0


def is_valid_bank_card(value) -> bool:
    """Check a 16-digit bank card number with the Luhn algorithm."""
    number = clean_digits(value)
    if not re.fullmatch(r"[0-9]{16}", number) or len(set(number)) == 1:
        return False
    return _luhn_ok(number)


# -- Sheba (IBAN) ---------------------------------------------------------------
def normalize_sheba(value) -> str:
    """Return the Sheba in the form ``IR`` + 24 digits (adds ``IR`` if missing)."""
    text = re.sub(r"[\s\-\u200c\u200e\u200f]", "", to_english_digits(str(value))).upper()
    if text and not text.startswith("IR"):
        text = "IR" + text
    return text


def is_valid_sheba(value) -> bool:
    """Check an Iranian IBAN (شبا) with the ISO 13616 mod-97 algorithm."""
    sheba = normalize_sheba(value)
    if not re.fullmatch(r"IR[0-9]{24}", sheba):
        return False
    rearranged = sheba[4:] + sheba[:4]
    return int("".join(str(int(char, 36)) for char in rearranged)) % 97 == 1


# -- postal code ----------------------------------------------------------------
_POSTAL_RE = re.compile(r"(?!([0-9])\1{3})[13-9]{4}[1346-9][013-9]{5}")


def is_valid_postal_code(value) -> bool:
    """Check an Iranian 10-digit postal code (کد پستی) against the official pattern."""
    return _POSTAL_RE.fullmatch(clean_digits(value)) is not None
