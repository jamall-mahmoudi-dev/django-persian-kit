"""Form fields that accept Persian digits and normalise the cleaned value."""

import datetime

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .jalali import JalaliDate
from .validation import clean_digits, normalize_mobile, normalize_sheba
from .validators import (
    validate_bank_card,
    validate_mobile,
    validate_national_id,
    validate_postal_code,
    validate_sheba,
)


class _NormalizedCharField(forms.CharField):
    """CharField that normalises input (e.g. Persian digits -> ASCII) before validating."""

    normalizer = staticmethod(clean_digits)
    default_max_length = None
    input_mode = "numeric"

    def __init__(self, **kwargs):
        kwargs.setdefault("max_length", self.default_max_length)
        super().__init__(**kwargs)

    def to_python(self, value):
        value = super().to_python(value)
        if value in self.empty_values:
            return value
        return self.normalizer(value)

    def widget_attrs(self, widget):
        attrs = super().widget_attrs(widget)
        attrs.update({"dir": "ltr", "inputmode": self.input_mode})
        return attrs


class NationalIDField(_NormalizedCharField):
    """Iranian national ID (کد ملی)."""

    default_max_length = 10
    default_validators = [validate_national_id]


class MobileNumberField(_NormalizedCharField):
    """Iranian mobile number; cleaned to ``09XXXXXXXXX``."""

    default_max_length = 11
    default_validators = [validate_mobile]
    normalizer = staticmethod(normalize_mobile)
    input_mode = "tel"


class BankCardNumberField(_NormalizedCharField):
    """16-digit bank card number (Luhn)."""

    default_max_length = 16
    default_validators = [validate_bank_card]


class ShebaField(_NormalizedCharField):
    """Iranian IBAN (شبا); cleaned to ``IR`` + 24 digits."""

    default_max_length = 26
    default_validators = [validate_sheba]
    normalizer = staticmethod(normalize_sheba)
    input_mode = "text"


class PostalCodeField(_NormalizedCharField):
    """Iranian 10-digit postal code (کد پستی)."""

    default_max_length = 10
    default_validators = [validate_postal_code]


class JalaliDateField(forms.Field):
    """Accepts a Jalali date such as ``1403/01/15`` and returns a Gregorian ``datetime.date``."""

    widget = forms.TextInput
    default_error_messages = {
        "invalid": _("Enter a valid Jalali date, e.g. 1403/01/15."),
    }

    def to_python(self, value):
        if value in self.empty_values:
            return None
        if isinstance(value, datetime.datetime):
            return value.date()
        if isinstance(value, datetime.date):
            return value
        try:
            return JalaliDate.parse(str(value)).to_gregorian()
        except (ValueError, OverflowError):
            raise ValidationError(self.error_messages["invalid"], code="invalid") from None

    def prepare_value(self, value):
        if isinstance(value, datetime.date):  # datetime is a date subclass
            return str(JalaliDate.from_gregorian(value))
        return value

    def widget_attrs(self, widget):
        attrs = super().widget_attrs(widget)
        attrs.setdefault("dir", "ltr")
        attrs.setdefault("placeholder", "1403/01/15")
        return attrs
