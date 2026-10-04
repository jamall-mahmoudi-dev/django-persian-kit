import pytest

from persian_kit import (
    add_thousands_separator,
    normalize_persian_text,
    number_to_words,
    to_english_digits,
    to_persian_digits,
)


def test_digit_conversion():
    assert to_persian_digits("Order 1403/01/15") == "Order ۱۴۰۳/۰۱/۱۵"
    assert to_persian_digits("٠١٢") == "۰۱۲"  # Arabic-Indic -> Persian
    assert to_english_digits("۰۹۱۲۳۴۵۶۷۸۹") == "09123456789"
    assert to_english_digits("٠١٢٣") == "0123"
    assert to_english_digits(123) == "123"


def test_normalize_text():
    assert normalize_persian_text("كتاب ي") == "کتاب ی"
    assert normalize_persian_text("ســلام") == "سلام"  # tatweel removed
    assert normalize_persian_text("۱۲۳") == "123"
    assert normalize_persian_text("123", digits="persian") == "۱۲۳"
    assert normalize_persian_text("۱۲۳", digits=None) == "۱۲۳"
    with pytest.raises(ValueError):
        normalize_persian_text("x", digits="bad")


@pytest.mark.parametrize(
    "value, expected",
    [
        (1234567, "1,234,567"),
        (999, "999"),
        ("۱۲۳۴۵.۵", "12,345.5"),
        (-1234, "-1,234"),
        ("abc", "abc"),
        ("", ""),
    ],
)
def test_thousands_separator(value, expected):
    assert add_thousands_separator(value) == expected


@pytest.mark.parametrize(
    "number, words",
    [
        (0, "صفر"),
        (7, "هفت"),
        (11, "یازده"),
        (21, "بیست و یک"),
        (100, "صد"),
        (101, "صد و یک"),
        (999, "نهصد و نود و نه"),
        (1000, "یک هزار"),
        (2024, "دو هزار و بیست و چهار"),
        (1200000, "یک میلیون و دویست هزار"),
        (1000001, "یک میلیون و یک"),
        (-5, "منفی پنج"),
        ("۱۲۳", "صد و بیست و سه"),
        ("1,500", "یک هزار و پانصد"),
    ],
)
def test_number_to_words(number, words):
    assert number_to_words(number) == words


def test_number_to_words_errors():
    with pytest.raises(ValueError):
        number_to_words(10**15)
    with pytest.raises(ValueError):
        number_to_words("abc")
    with pytest.raises(TypeError):
        number_to_words(1.5)
    with pytest.raises(TypeError):
        number_to_words(True)
