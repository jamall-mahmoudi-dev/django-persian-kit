"""Model fields for Iranian identifiers. They store normalised ASCII values."""

from django.db import models

from . import forms as persian_forms
from .validation import clean_digits, normalize_mobile, normalize_sheba
from .validators import (
    validate_bank_card,
    validate_mobile,
    validate_national_id,
    validate_postal_code,
    validate_sheba,
)


class _NormalizedCharMixin:
    default_max_length = None
    normalizer = staticmethod(clean_digits)
    form_class = None

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("max_length", self.default_max_length)
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if kwargs.get("max_length") == self.default_max_length:
            del kwargs["max_length"]
        return name, path, args, kwargs

    def to_python(self, value):
        value = super().to_python(value)
        if isinstance(value, str) and value:
            return self.normalizer(value)
        return value

    def formfield(self, **kwargs):
        kwargs.setdefault("form_class", self.form_class)
        return super().formfield(**kwargs)


class NationalIDField(_NormalizedCharMixin, models.CharField):
    """Iranian national ID (کد ملی), stored as 10 ASCII digits."""

    default_max_length = 10
    default_validators = [validate_national_id]
    form_class = persian_forms.NationalIDField


class MobileNumberField(_NormalizedCharMixin, models.CharField):
    """Iranian mobile number, stored as ``09XXXXXXXXX``."""

    default_max_length = 11
    default_validators = [validate_mobile]
    normalizer = staticmethod(normalize_mobile)
    form_class = persian_forms.MobileNumberField


class BankCardNumberField(_NormalizedCharMixin, models.CharField):
    """16-digit bank card number, stored as ASCII digits."""

    default_max_length = 16
    default_validators = [validate_bank_card]
    form_class = persian_forms.BankCardNumberField


class ShebaField(_NormalizedCharMixin, models.CharField):
    """Iranian IBAN (شبا), stored as ``IR`` + 24 digits."""

    default_max_length = 26
    default_validators = [validate_sheba]
    normalizer = staticmethod(normalize_sheba)
    form_class = persian_forms.ShebaField


class PostalCodeField(_NormalizedCharMixin, models.CharField):
    """Iranian 10-digit postal code, stored as ASCII digits."""

    default_max_length = 10
    default_validators = [validate_postal_code]
    form_class = persian_forms.PostalCodeField
