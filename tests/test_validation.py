import pytest

from persian_kit import (
    is_valid_bank_card,
    is_valid_mobile,
    is_valid_national_id,
    is_valid_postal_code,
    is_valid_sheba,
)
from persian_kit.validation import normalize_mobile, normalize_sheba


@pytest.mark.parametrize("value", ["0084575948", "0499370899", "۰۰۸۴۵۷۵۹۴۸", "008-457-5948", " 0084575948 "])
def test_national_id_valid(value):
    assert is_valid_national_id(value)


@pytest.mark.parametrize("value", ["0084575949", "1111111111", "0000000000", "123", "", "00845759481", "abcdefghij"])
def test_national_id_invalid(value):
    assert not is_valid_national_id(value)


@pytest.mark.parametrize(
    "value",
    ["09123456789", "۰۹۱۲۳۴۵۶۷۸۹", "+989123456789", "+98 912 345 6789", "00989123456789", "989123456789", "9123456789", "0912-345-6789"],
)
def test_mobile_valid(value):
    assert is_valid_mobile(value)
    assert normalize_mobile(value) == "09123456789"


@pytest.mark.parametrize("value", ["08123456789", "0912345678", "091234567890", "09abc456789", "", "02112345678"])
def test_mobile_invalid(value):
    assert not is_valid_mobile(value)


@pytest.mark.parametrize("value", ["4539578763621486", "4539 5787 6362 1486", "۴۵۳۹۵۷۸۷۶۳۶۲۱۴۸۶", "4539-5787-6362-1486"])
def test_bank_card_valid(value):
    assert is_valid_bank_card(value)


@pytest.mark.parametrize("value", ["4539578763621487", "1111111111111111", "0000000000000000", "453957876362148", "", "abcd"])
def test_bank_card_invalid(value):
    assert not is_valid_bank_card(value)


@pytest.mark.parametrize(
    "value",
    ["IR062960000000100324200001", "ir062960000000100324200001", "062960000000100324200001", "IR06 2960 0000 0010 0324 2000 01"],
)
def test_sheba_valid(value):
    assert is_valid_sheba(value)
    assert normalize_sheba(value) == "IR062960000000100324200001"


@pytest.mark.parametrize("value", ["IR062960000000100324200002", "IR06296000000010032420000", "GB82WEST12345698765432", "", "IR"])
def test_sheba_invalid(value):
    assert not is_valid_sheba(value)


@pytest.mark.parametrize("value", ["1396956748", "۱۳۹۶۹۵۶۷۴۸"])
def test_postal_code_valid(value):
    assert is_valid_postal_code(value)


@pytest.mark.parametrize("value", ["2396956748", "0396956748", "1111111111", "13969567", "13969567480", "1396256748", ""])
def test_postal_code_invalid(value):
    assert not is_valid_postal_code(value)
