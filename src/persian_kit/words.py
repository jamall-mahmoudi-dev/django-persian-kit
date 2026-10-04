"""Convert integers to Persian words (no Django required)."""

from __future__ import annotations

from .digits import to_english_digits

_ONES = (
    "", "یک", "دو", "سه", "چهار", "پنج", "شش", "هفت", "هشت", "نه", "ده",
    "یازده", "دوازده", "سیزده", "چهارده", "پانزده", "شانزده", "هفده", "هجده", "نوزده",
)
_TENS = ("", "", "بیست", "سی", "چهل", "پنجاه", "شصت", "هفتاد", "هشتاد", "نود")
_HUNDREDS = ("", "صد", "دویست", "سیصد", "چهارصد", "پانصد", "ششصد", "هفتصد", "هشتصد", "نهصد")
_SCALES = ("", "هزار", "میلیون", "میلیارد", "تریلیون")

MAX_VALUE = 10 ** (3 * len(_SCALES)) - 1  # 999,999,999,999,999


def _group_to_words(n: int) -> str:
    """Words for 1..999."""
    parts = []
    hundreds, rest = divmod(n, 100)
    if hundreds:
        parts.append(_HUNDREDS[hundreds])
    if rest:
        if rest < 20:
            parts.append(_ONES[rest])
        else:
            tens, ones = divmod(rest, 10)
            parts.append(_TENS[tens])
            if ones:
                parts.append(_ONES[ones])
    return " و ".join(parts)


def number_to_words(value) -> str:
    """Return the Persian words for an integer.

    ``value`` may be an ``int`` or a string of digits (Persian digits are
    accepted). One thousand is written as ``"یک هزار"`` (the form used on
    cheques and invoices).

    >>> number_to_words(1200000)
    'یک میلیون و دویست هزار'
    >>> number_to_words(-21)
    'منفی بیست و یک'
    """
    if isinstance(value, bool):
        raise TypeError("bool is not a valid number")
    if isinstance(value, str):
        text = to_english_digits(value).strip().replace(",", "")
        try:
            number = int(text)
        except ValueError:
            raise ValueError(f"not an integer: {value!r}") from None
    elif isinstance(value, int):
        number = value
    else:
        raise TypeError("value must be an int or a digit string")

    if abs(number) > MAX_VALUE:
        raise ValueError(f"number is too large (max {MAX_VALUE})")
    if number == 0:
        return "صفر"

    sign = "منفی " if number < 0 else ""
    number = abs(number)

    groups = []
    scale = 0
    while number:
        number, chunk = divmod(number, 1000)
        if chunk:
            words = _group_to_words(chunk)
            if _SCALES[scale]:
                words = f"{words} {_SCALES[scale]}"
            groups.append(words)
        scale += 1
    return sign + " و ".join(reversed(groups))
