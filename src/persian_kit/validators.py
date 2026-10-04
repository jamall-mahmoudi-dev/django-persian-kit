"""Django validators (callables that raise ``ValidationError``)."""

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .validation import (
    is_valid_bank_card,
    is_valid_mobile,
    is_valid_national_id,
    is_valid_postal_code,
    is_valid_sheba,
)


def validate_national_id(value):
    if not is_valid_national_id(value):
        raise ValidationError(_("Enter a valid Iranian national ID (10 digits)."), code="invalid_national_id")


def validate_mobile(value):
    if not is_valid_mobile(value):
        raise ValidationError(
            _("Enter a valid Iranian mobile number (e.g. 09123456789)."), code="invalid_mobile"
        )


def validate_bank_card(value):
    if not is_valid_bank_card(value):
        raise ValidationError(_("Enter a valid 16-digit bank card number."), code="invalid_bank_card")


def validate_sheba(value):
    if not is_valid_sheba(value):
        raise ValidationError(_("Enter a valid Sheba (IBAN) number."), code="invalid_sheba")


def validate_postal_code(value):
    if not is_valid_postal_code(value):
        raise ValidationError(_("Enter a valid 10-digit postal code."), code="invalid_postal_code")
