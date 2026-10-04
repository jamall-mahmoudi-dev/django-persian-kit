import datetime as dt

from django.template import Context, Template
from django.utils import timezone


def render(source, **context):
    return Template("{% load persian_kit %}" + source).render(Context(context))


def test_digit_filters():
    assert render("{{ v|persian_digits }}", v=1403) == "۱۴۰۳"
    assert render("{{ v|persian_digits }}", v=None) == ""
    assert render("{{ v|english_digits }}", v="۱۲۳") == "123"


def test_jalali_filter_date_and_default_format():
    assert render("{{ d|jalali }}", d=dt.date(2024, 3, 20)) == "1403/01/01"
    assert render('{{ d|jalali:"%-d %B %Y" }}', d=dt.date(2024, 3, 24)) == "5 فروردین 1403"
    assert render("{{ d|jalali|persian_digits }}", d=dt.date(2024, 3, 20)) == "۱۴۰۳/۰۱/۰۱"


def test_jalali_filter_uses_current_timezone_for_aware_datetimes():
    # 2024-03-19 21:00 UTC is 2024-03-20 00:30 in Tehran (UTC+3:30)
    value = dt.datetime(2024, 3, 19, 21, 0, tzinfo=dt.timezone.utc)
    assert render("{{ d|jalali }}", d=value) == "1403/01/01"
    with timezone.override("UTC"):
        assert render("{{ d|jalali }}", d=value) == "1402/12/29"


def test_jalali_filter_fails_silently():
    assert render("{{ d|jalali }}", d=None) == ""
    assert render("{{ d|jalali }}", d="not a date") == ""
    assert render("{{ d|jalali }}", d=dt.date(100, 1, 1)) == ""


def test_fa_intcomma_and_number_words():
    assert render("{{ v|fa_intcomma }}", v=1234567) == "۱٬۲۳۴٬۵۶۷".replace("٬", ",")
    assert render("{{ v|fa_intcomma }}", v="") == ""
    assert render("{{ v|number_words }}", v=1200000) == "یک میلیون و دویست هزار"
    assert render("{{ v|number_words }}", v="abc") == ""
    assert render("{{ v|number_words }}", v=1.5) == ""


def test_jalali_now_tag():
    out = render('{% jalali_now "%Y" %}')
    assert out.isdigit() and len(out) == 4
