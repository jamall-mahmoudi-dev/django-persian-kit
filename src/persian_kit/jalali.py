"""Jalali (Shamsi / Solar Hijri) calendar support (no Django required).

Leap years follow the 33-year arithmetic rule, which matches the official
Iranian calendar for Jalali years 1178-1633 (about 1799-2255 CE). Outside
that range results are an arithmetic approximation.
"""

from __future__ import annotations

import datetime as _dt
import re
from dataclasses import dataclass

from .digits import to_english_digits

MONTH_NAMES = (
    "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
    "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند",
)
# Week starts on Saturday (index 0).
WEEKDAY_NAMES = ("شنبه", "یکشنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنجشنبه", "جمعه")

MIN_YEAR = 1
MAX_YEAR = 9377  # Gregorian year 9999 is the limit of datetime.date

_LEAP_RESIDUES = (1, 5, 9, 13, 17, 22, 26, 30)


def is_leap_year(year: int) -> bool:
    """True if the Jalali ``year`` has 366 days."""
    return year % 33 in _LEAP_RESIDUES


def days_in_month(year: int, month: int) -> int:
    if not 1 <= month <= 12:
        raise ValueError("month must be in 1..12")
    if month <= 6:
        return 31
    if month <= 11:
        return 30
    return 30 if is_leap_year(year) else 29


def _leaps_before(year: int) -> int:
    """Number of leap years among Jalali years 1 .. year-1."""
    cycles, rest = divmod(year - 1, 33)
    return cycles * 8 + sum(1 for r in _LEAP_RESIDUES if r <= rest)


def _days_before_year(year: int) -> int:
    """Days from 1 Farvardin of year 1 to 1 Farvardin of ``year``."""
    return 365 * (year - 1) + _leaps_before(year)


_CYCLE_DAYS = 33 * 365 + 8  # 12053

# Proleptic-Gregorian ordinal of 1 Farvardin of year 1.
# Anchor: 1 Farvardin 1400 == 2021-03-21.
_EPOCH = _dt.date(2021, 3, 21).toordinal() - _days_before_year(1400)


def _from_ordinal(ordinal: int):
    days = ordinal - _EPOCH
    if days < 0:
        raise ValueError("date is before Jalali year 1")
    year = days * 33 // _CYCLE_DAYS + 1
    while _days_before_year(year + 1) <= days:
        year += 1
    while _days_before_year(year) > days:
        year -= 1
    day_of_year = days - _days_before_year(year)
    month = 1
    while day_of_year >= days_in_month(year, month):
        day_of_year -= days_in_month(year, month)
        month += 1
    return year, month, day_of_year + 1


@dataclass(frozen=True, order=True)
class JalaliDate:
    """An immutable Jalali calendar date.

    >>> JalaliDate.from_gregorian(_dt.date(2024, 3, 20))
    JalaliDate(year=1403, month=1, day=1)
    >>> str(JalaliDate(1403, 1, 15).to_gregorian())
    '2024-04-03'
    """

    year: int
    month: int
    day: int

    def __post_init__(self):
        if not MIN_YEAR <= self.year <= MAX_YEAR:
            raise ValueError(f"year must be in {MIN_YEAR}..{MAX_YEAR}")
        if not 1 <= self.month <= 12:
            raise ValueError("month must be in 1..12")
        length = days_in_month(self.year, self.month)
        if not 1 <= self.day <= length:
            raise ValueError(f"day must be in 1..{length} for {self.year}/{self.month:02d}")

    # -- construction ------------------------------------------------------
    @classmethod
    def from_gregorian(cls, value) -> "JalaliDate":
        """Build from a ``datetime.date`` or ``datetime.datetime``."""
        if isinstance(value, _dt.datetime):
            value = value.date()
        if not isinstance(value, _dt.date):
            raise TypeError("expected a date or datetime")
        return cls(*_from_ordinal(value.toordinal()))

    @classmethod
    def today(cls) -> "JalaliDate":
        return cls.from_gregorian(_dt.date.today())

    @classmethod
    def parse(cls, text: str) -> "JalaliDate":
        """Parse ``1403/01/15`` (also ``-`` or ``.`` separators, Persian digits)."""
        match = _PARSE_RE.match(to_english_digits(text))
        if not match:
            raise ValueError(f"invalid Jalali date: {text!r}")
        year, month, day = (int(g) for g in match.groups())
        return cls(year, month, day)

    # -- conversion --------------------------------------------------------
    def _ordinal(self) -> int:
        before_month = sum(days_in_month(self.year, m) for m in range(1, self.month))
        return _EPOCH + _days_before_year(self.year) + before_month + self.day - 1

    def to_gregorian(self) -> _dt.date:
        return _dt.date.fromordinal(self._ordinal())

    # -- properties --------------------------------------------------------
    @property
    def is_leap_year(self) -> bool:
        return is_leap_year(self.year)

    @property
    def month_name(self) -> str:
        return MONTH_NAMES[self.month - 1]

    def weekday(self) -> int:
        """0 = Saturday ... 6 = Friday."""
        return (self.to_gregorian().weekday() + 2) % 7

    @property
    def weekday_name(self) -> str:
        return WEEKDAY_NAMES[self.weekday()]

    @property
    def day_of_year(self) -> int:
        return sum(days_in_month(self.year, m) for m in range(1, self.month)) + self.day

    # -- formatting --------------------------------------------------------
    def isoformat(self) -> str:
        return f"{self.year:04d}-{self.month:02d}-{self.day:02d}"

    def strftime(self, fmt: str) -> str:
        return _format(self, fmt)

    def __str__(self) -> str:
        return f"{self.year:04d}/{self.month:02d}/{self.day:02d}"

    # -- arithmetic --------------------------------------------------------
    def __add__(self, other):
        if isinstance(other, _dt.timedelta):
            return JalaliDate.from_gregorian(self.to_gregorian() + other)
        return NotImplemented

    __radd__ = __add__

    def __sub__(self, other):
        if isinstance(other, _dt.timedelta):
            return JalaliDate.from_gregorian(self.to_gregorian() - other)
        if isinstance(other, JalaliDate):
            return self.to_gregorian() - other.to_gregorian()
        return NotImplemented


_PARSE_RE = re.compile(r"^\s*(\d{1,4})\s*[/\-.]\s*(\d{1,2})\s*[/\-.]\s*(\d{1,2})\s*$", re.ASCII)
_TOKEN_RE = re.compile(r"%(-?)(.)")


def _format(jd: JalaliDate, fmt: str, hour: int = 0, minute: int = 0, second: int = 0) -> str:
    def pad(number: int, width: int, no_pad: bool) -> str:
        return str(number) if no_pad else f"{number:0{width}d}"

    def repl(match):
        flag, code = match.group(1), match.group(2)
        no_pad = bool(flag)
        if code == "Y":
            return f"{jd.year:04d}"
        if code == "y":
            return pad(jd.year % 100, 2, False)
        if code == "m":
            return pad(jd.month, 2, no_pad)
        if code == "d":
            return pad(jd.day, 2, no_pad)
        if code == "B":
            return jd.month_name
        if code == "A":
            return jd.weekday_name
        if code == "j":
            return pad(jd.day_of_year, 3, no_pad)
        if code == "H":
            return pad(hour, 2, no_pad)
        if code == "M":
            return pad(minute, 2, no_pad)
        if code == "S":
            return pad(second, 2, no_pad)
        if code == "%" and not flag:
            return "%"
        return match.group(0)

    return _TOKEN_RE.sub(repl, fmt)


def format_jalali(value, fmt: str = "%Y/%m/%d") -> str:
    """Format a ``date`` or ``datetime`` using the Jalali calendar.

    Supported tokens: ``%Y %y %m %d %B %A %j %H %M %S %%``. Put ``-`` after
    ``%`` (``%-d``) to drop zero padding. Digits are ASCII; pass the result
    through :func:`persian_kit.to_persian_digits` if you want Persian digits.

    >>> format_jalali(_dt.date(2024, 3, 24), "%-d %B %Y")
    '5 فروردین 1403'
    """
    jd = JalaliDate.from_gregorian(value)
    if isinstance(value, _dt.datetime):
        return _format(jd, fmt, value.hour, value.minute, value.second)
    return _format(jd, fmt)
