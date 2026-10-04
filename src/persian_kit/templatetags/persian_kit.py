"""Template filters and tags. Use with ``{% load persian_kit %}``."""

import datetime

from django import template
from django.utils import timezone

from persian_kit.digits import (
    add_thousands_separator,
    to_english_digits,
    to_persian_digits,
)
from persian_kit.jalali import format_jalali
from persian_kit.words import number_to_words

register = template.Library()


def _as_date(value):
    if isinstance(value, datetime.datetime):
        if timezone.is_aware(value):
            value = timezone.localtime(value)
        return value
    if isinstance(value, datetime.date):
        return value
    return None


@register.filter(name="persian_digits")
def persian_digits(value):
    """``{{ 123|persian_digits }}`` -> ۱۲۳"""
    if value is None:
        return ""
    return to_persian_digits(value)


@register.filter(name="english_digits")
def english_digits(value):
    """``{{ "۱۲۳"|english_digits }}`` -> 123"""
    if value is None:
        return ""
    return to_english_digits(value)


@register.filter(name="jalali")
def jalali(value, fmt="%Y/%m/%d"):
    """``{{ obj.created|jalali:"%-d %B %Y" }}``; returns "" for non-dates."""
    date_value = _as_date(value)
    if date_value is None:
        return ""
    try:
        return format_jalali(date_value, fmt)
    except (ValueError, OverflowError):
        return ""


@register.filter(name="fa_intcomma")
def fa_intcomma(value):
    """Thousands separators + Persian digits: ``{{ 1234567|fa_intcomma }}`` -> ۱,۲۳۴,۵۶۷"""
    if value is None or value == "":
        return ""
    return to_persian_digits(add_thousands_separator(value))


@register.filter(name="number_words")
def number_words(value):
    """``{{ 1200000|number_words }}`` -> یک میلیون و دویست هزار; "" if not an integer."""
    try:
        return number_to_words(value)
    except (ValueError, TypeError):
        return ""


@register.simple_tag
def jalali_now(fmt="%Y/%m/%d"):
    """``{% jalali_now "%Y/%m/%d" %}`` -> today's Jalali date."""
    now = timezone.now()
    if timezone.is_aware(now):
        now = timezone.localtime(now)
    return format_jalali(now, fmt)
