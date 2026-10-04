# django-persian-kit

Persian (Farsi) toolkit for Django: **Jalali (Shamsi) dates**, **Persian digits**, validators for Iranian
**national ID, mobile number, bank card, Sheba (IBAN) and postal code**, **number to Persian words**,
ready-made **form fields, model fields and template filters**.

- No extra dependencies besides Django.
- The helpers in `digits`, `jalali`, `words` and `validation` are plain Python and work without Django too.
- Tested on Django 4.2 LTS, 5.2 LTS and 6.1, Python 3.9 - 3.13 (Django 5.x and later need Python 3.10+).
- Persian translation of all error messages included.

[فارسی ↓](#راهنمای-فارسی)

## Install

```bash
pip install django-persian-kit
```

Add the app (needed for the template filters and translations):

```python
INSTALLED_APPS = [
    # ...
    "persian_kit",
]
```

## Jalali dates

```python
import datetime
from persian_kit import JalaliDate, format_jalali

jd = JalaliDate.from_gregorian(datetime.date(2024, 3, 20))   # JalaliDate(year=1403, month=1, day=1)
jd.to_gregorian()                    # datetime.date(2024, 3, 20)
jd.month_name, jd.weekday_name       # ('فروردین', 'چهارشنبه')
str(jd)                              # '1403/01/01'
jd + datetime.timedelta(days=14)     # JalaliDate(year=1403, month=1, day=15)

JalaliDate.parse("۱۴۰۳/۰۱/۱۵")        # Persian digits and / - . separators are accepted

format_jalali(datetime.date(2024, 3, 24), "%-d %B %Y")   # '5 فروردین 1403'
```

Format tokens: `%Y %y %m %d %B %A %j %H %M %S %%`. Add `-` (`%-d`) to remove zero padding.
The week starts on Saturday (`JalaliDate.weekday()` returns 0 for Saturday).

> **Calendar range.** Leap years follow the 33-year arithmetic rule, verified day by day against the
> official calendar for Jalali years 1178-1633 (about 1799-2255 CE). Outside that range results are an
> arithmetic approximation.

## Persian digits and text

```python
from persian_kit import to_persian_digits, to_english_digits, normalize_persian_text, add_thousands_separator

to_persian_digits("1403/01/15")        # '۱۴۰۳/۰۱/۱۵'
to_english_digits("۰۹۱۲۳۴۵۶۷۸۹")        # '09123456789'
normalize_persian_text("كتاب")         # 'کتاب'  (Arabic ك/ي -> Persian ک/ی, removes tatweel, ASCII digits)
add_thousands_separator(1234567)       # '1,234,567'
```

## Number to words

```python
from persian_kit import number_to_words

number_to_words(1200000)   # 'یک میلیون و دویست هزار'
number_to_words(-21)       # 'منفی بیست و یک'
```

Integers up to 999 trillion. One thousand is written `یک هزار` (cheque/invoice style).

## Validators

```python
from persian_kit import (
    is_valid_national_id, is_valid_mobile, is_valid_bank_card, is_valid_sheba, is_valid_postal_code,
)

is_valid_national_id("0084575948")          # True  (also accepts Persian digits, spaces and hyphens)
is_valid_mobile("+98 912 345 6789")         # True  (09XXXXXXXXX, +98..., 0098..., 9XXXXXXXXX)
is_valid_bank_card("4539 5787 6362 1486")   # True  (16 digits, Luhn)
is_valid_sheba("IR062960000000100324200001")  # True (with or without the IR prefix)
is_valid_postal_code("1396956748")          # True
```

Django validators for your own fields: `persian_kit.validators.validate_national_id`, `validate_mobile`,
`validate_bank_card`, `validate_sheba`, `validate_postal_code`.

> The national-ID, card and Sheba checks verify the **format and check digits only**. They cannot tell you
> whether a card or account really exists.

## Model fields

```python
from django.db import models
from persian_kit.fields import NationalIDField, MobileNumberField, ShebaField

class Customer(models.Model):
    national_id = NationalIDField(unique=True)
    mobile = MobileNumberField()
    sheba = ShebaField(blank=True)
```

Also available: `BankCardNumberField`, `PostalCodeField`.
Values are validated and **stored normalised** (ASCII digits, mobile as `09XXXXXXXXX`, Sheba as `IR` + 24 digits),
so users can type Persian digits and you still get clean data. These fields subclass `CharField`.

## Form fields

```python
from django import forms
from persian_kit.forms import NationalIDField, MobileNumberField, JalaliDateField

class SignupForm(forms.Form):
    national_id = NationalIDField()
    mobile = MobileNumberField()
    birth_date = JalaliDateField()      # user types 1380/05/10, cleaned_data holds a datetime.date
```

`JalaliDateField` shows initial dates in Jalali format. ModelForms use the matching form field automatically for
the model fields above.

## Template filters

```django
{% load persian_kit %}

{{ article.created|jalali }}                      {# 1403/01/05 #}
{{ article.created|jalali:"%-d %B %Y" }}          {# 5 فروردین 1403 #}
{{ article.created|jalali:"%-d %B %Y"|persian_digits }}   {# ۵ فروردین ۱۴۰۳ #}
{{ order.total|fa_intcomma }}                     {# ۱,۲۳۴,۵۶۷ #}
{{ order.total|number_words }}                    {# یک میلیون و ... #}
{{ "۱۲۳"|english_digits }}                        {# 123 #}
{% jalali_now "%Y/%m/%d" %}                       {# today's Jalali date #}
```

Aware datetimes are converted to the current time zone before formatting. Invalid values give an empty string.

## Development

```bash
pip install -e . pytest pytest-django
python -m pytest
```

## License

MIT

---

# راهنمای فارسی

**django-persian-kit** مجموعه‌ای از ابزارهای فارسی برای جنگو است:

- **تاریخ شمسی (جلالی)**: تبدیل، قالب‌بندی، تجزیه‌ی متن و محاسبه (`JalaliDate`)
- **ارقام فارسی**: تبدیل ارقام فارسی، عربی و انگلیسی به هم و نرمال‌سازی متن (ی/ک عربی)
- **اعتبارسنجی**: کد ملی، شماره موبایل، شماره کارت بانکی، شماره شبا و کد پستی
- **عدد به حروف**: `number_to_words(1200000)` ← «یک میلیون و دویست هزار»
- **فیلد مدل و فرم و فیلتر قالب** آماده؛ کاربر می‌تواند با ارقام فارسی وارد کند و مقدار نرمال‌شده در پایگاه داده ذخیره می‌شود

## نصب

```bash
pip install django-persian-kit
```

```python
INSTALLED_APPS = [
    # ...
    "persian_kit",
]
```

## نمونه‌ی استفاده

```python
from persian_kit import JalaliDate, is_valid_national_id, number_to_words

JalaliDate.from_gregorian(datetime.date(2024, 3, 20))   # 1403/01/01
is_valid_national_id("۰۰۸۴۵۷۵۹۴۸")                       # True
number_to_words(2024)                                    # 'دو هزار و بیست و چهار'
```

```python
# models.py
from persian_kit.fields import NationalIDField, MobileNumberField

class Customer(models.Model):
    national_id = NationalIDField(unique=True)
    mobile = MobileNumberField()
```

```django
{% load persian_kit %}
{{ obj.created|jalali:"%-d %B %Y"|persian_digits }}
```

## نکته‌ها

- اعتبارسنجی کد ملی، کارت و شبا فقط **قالب و رقم کنترل** را بررسی می‌کند؛ وجود واقعی کارت یا حساب را نمی‌توان از این راه فهمید.
- قاعده‌ی سال کبیسه برای سال‌های ۱۱۷۸ تا ۱۶۳۳ شمسی با تقویم رسمی روز به روز مقایسه و تأیید شده است.
- پیام‌های خطا ترجمه‌ی فارسی دارند.

مجوز: MIT
