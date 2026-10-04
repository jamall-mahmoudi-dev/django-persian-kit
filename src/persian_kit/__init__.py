"""django-persian-kit: Persian (Farsi) tools for Django.

Jalali (Shamsi) dates, Persian digit helpers, Iranian-data validators
(national ID, mobile, bank card, Sheba/IBAN, postal code), number-to-words,
form/model fields and template filters.

The pure-Python helpers in this package (``digits``, ``jalali``, ``words``,
``validation``) do not need Django to be configured, so they can also be used
in scripts and non-Django projects.
"""

__version__ = "0.1.0"

from .digits import (  # noqa: F401
    add_thousands_separator,
    normalize_persian_text,
    to_english_digits,
    to_persian_digits,
)
from .jalali import JalaliDate, format_jalali  # noqa: F401
from .validation import (  # noqa: F401
    is_valid_bank_card,
    is_valid_mobile,
    is_valid_national_id,
    is_valid_postal_code,
    is_valid_sheba,
)
from .words import number_to_words  # noqa: F401

__all__ = [
    "__version__",
    "JalaliDate",
    "add_thousands_separator",
    "format_jalali",
    "is_valid_bank_card",
    "is_valid_mobile",
    "is_valid_national_id",
    "is_valid_postal_code",
    "is_valid_sheba",
    "normalize_persian_text",
    "number_to_words",
    "to_english_digits",
    "to_persian_digits",
]
