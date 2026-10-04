import datetime as dt

import pytest
from django import forms
from django.core.exceptions import ValidationError
from django.utils import translation

from persian_kit import fields as model_fields
from persian_kit import forms as pk_forms


def test_national_id_form_field_normalizes_digits():
    field = pk_forms.NationalIDField()
    assert field.clean("۰۰۸۴۵۷۵۹۴۸") == "0084575948"
    assert field.clean(" 008-457-5948 ") == "0084575948"
    with pytest.raises(ValidationError) as exc:
        field.clean("0084575949")
    assert exc.value.error_list[0].code == "invalid_national_id"


def test_required_and_optional():
    with pytest.raises(ValidationError):
        pk_forms.NationalIDField().clean("")
    assert pk_forms.NationalIDField(required=False).clean("") == ""


def test_mobile_field():
    field = pk_forms.MobileNumberField()
    assert field.clean("+98 912 345 6789") == "09123456789"
    assert field.clean("۰۹۱۲۳۴۵۶۷۸۹") == "09123456789"
    with pytest.raises(ValidationError):
        field.clean("0812345678")


def test_card_sheba_postal_fields():
    assert pk_forms.BankCardNumberField().clean("4539 5787 6362 1486") == "4539578763621486"
    assert pk_forms.ShebaField().clean("ir06 2960 0000 0010 0324 2000 01") == "IR062960000000100324200001"
    assert pk_forms.PostalCodeField().clean("۱۳۹۶۹۵۶۷۴۸") == "1396956748"
    for field, bad in [
        (pk_forms.BankCardNumberField(), "4539578763621487"),
        (pk_forms.ShebaField(), "IR062960000000100324200002"),
        (pk_forms.PostalCodeField(), "2396956748"),
    ]:
        with pytest.raises(ValidationError):
            field.clean(bad)


def test_widget_attrs():
    html = pk_forms.MobileNumberField().widget.render("m", "", attrs=pk_forms.MobileNumberField().widget_attrs(forms.TextInput()))
    assert 'dir="ltr"' in html and 'inputmode="tel"' in html


def test_jalali_date_field():
    field = pk_forms.JalaliDateField()
    assert field.clean("1403/01/15") == dt.date(2024, 4, 3)
    assert field.clean("۱۴۰۳/۰۱/۱۵") == dt.date(2024, 4, 3)
    assert pk_forms.JalaliDateField(required=False).clean("") is None
    for bad in ["1403/13/01", "hello", "1401/12/30"]:
        with pytest.raises(ValidationError) as exc:
            field.clean(bad)
        assert exc.value.code == "invalid"
    assert field.prepare_value(dt.date(2024, 3, 20)) == "1403/01/01"
    assert field.prepare_value(dt.datetime(2024, 3, 20, 10, 0)) == "1403/01/01"
    assert field.prepare_value("1403/01/01") == "1403/01/01"


def test_form_integration():
    class SignupForm(forms.Form):
        national_id = pk_forms.NationalIDField()
        mobile = pk_forms.MobileNumberField()
        birth = pk_forms.JalaliDateField(initial=dt.date(2024, 3, 20))

    form = SignupForm({"national_id": "۰۰۸۴۵۷۵۹۴۸", "mobile": "+989123456789", "birth": "1380/05/10"})
    assert form.is_valid(), form.errors
    assert form.cleaned_data["national_id"] == "0084575948"
    assert form.cleaned_data["mobile"] == "09123456789"
    assert form.cleaned_data["birth"] == dt.date(2001, 8, 1)
    assert 'value="1403/01/01"' in str(SignupForm()["birth"])

    bad = SignupForm({"national_id": "1", "mobile": "1", "birth": "x"})
    assert not bad.is_valid()
    assert set(bad.errors) == {"national_id", "mobile", "birth"}


def test_persian_error_messages():
    with translation.override("fa"):
        with pytest.raises(ValidationError) as exc:
            pk_forms.NationalIDField().clean("123")
        assert "کد ملی" in exc.value.messages[0]
    with translation.override("en"):
        with pytest.raises(ValidationError) as exc:
            pk_forms.NationalIDField().clean("123")
        assert "national ID" in exc.value.messages[0]


# ---- model fields (no database needed) -----------------------------------
@pytest.mark.parametrize(
    "field_cls, form_cls, max_length",
    [
        (model_fields.NationalIDField, pk_forms.NationalIDField, 10),
        (model_fields.MobileNumberField, pk_forms.MobileNumberField, 11),
        (model_fields.BankCardNumberField, pk_forms.BankCardNumberField, 16),
        (model_fields.ShebaField, pk_forms.ShebaField, 26),
        (model_fields.PostalCodeField, pk_forms.PostalCodeField, 10),
    ],
)
def test_model_field_basics(field_cls, form_cls, max_length):
    field = field_cls()
    assert field.max_length == max_length
    assert "max_length" not in field.deconstruct()[3]  # default hidden from migrations
    formfield = field.formfield()
    assert isinstance(formfield, form_cls)
    assert formfield.max_length == max_length
    assert field_cls(max_length=max_length + 5).deconstruct()[3]["max_length"] == max_length + 5


def test_model_field_clean_normalizes_and_validates():
    assert model_fields.NationalIDField().clean("۰۰۸۴۵۷۵۹۴۸", None) == "0084575948"
    assert model_fields.MobileNumberField().clean("+989123456789", None) == "09123456789"
    assert model_fields.ShebaField().clean("062960000000100324200001", None) == "IR062960000000100324200001"
    with pytest.raises(ValidationError):
        model_fields.NationalIDField().clean("0084575949", None)
    with pytest.raises(ValidationError):
        model_fields.PostalCodeField().clean("2396956748", None)
    # stored value is normalised even without full_clean()
    assert model_fields.MobileNumberField().get_prep_value("۰۹۱۲۳۴۵۶۷۸۹") == "09123456789"
    assert model_fields.NationalIDField(blank=True).get_prep_value("") == ""
    assert model_fields.NationalIDField(null=True).get_prep_value(None) is None
