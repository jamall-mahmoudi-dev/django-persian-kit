import datetime as dt

import pytest

from persian_kit import JalaliDate, format_jalali

VECTORS = [
    (dt.date(1979, 2, 11), (1357, 11, 22)),
    (dt.date(2020, 3, 20), (1399, 1, 1)),
    (dt.date(2021, 3, 20), (1399, 12, 30)),  # leap year end
    (dt.date(2021, 3, 21), (1400, 1, 1)),
    (dt.date(2023, 3, 21), (1402, 1, 1)),
    (dt.date(2024, 3, 20), (1403, 1, 1)),
    (dt.date(2025, 3, 20), (1403, 12, 30)),  # leap year end
    (dt.date(2025, 3, 21), (1404, 1, 1)),
    (dt.date(2024, 4, 3), (1403, 1, 15)),
]


@pytest.mark.parametrize("gregorian, jalali", VECTORS)
def test_known_conversions(gregorian, jalali):
    assert JalaliDate.from_gregorian(gregorian) == JalaliDate(*jalali)
    assert JalaliDate(*jalali).to_gregorian() == gregorian


def test_round_trip_every_day_1178_to_1633():
    start = JalaliDate(1178, 1, 1).to_gregorian()
    end = JalaliDate(1633, 12, 29).to_gregorian()
    day = start
    while day <= end:
        jd = JalaliDate.from_gregorian(day)
        assert jd.to_gregorian() == day
        day += dt.timedelta(days=1)


def test_leap_years():
    for year in (1399, 1403, 1408, 1412):
        assert JalaliDate(year, 12, 30).year == year
    for year in (1400, 1401, 1402, 1404):
        with pytest.raises(ValueError):
            JalaliDate(year, 12, 30)


def test_validation():
    for args in [(0, 1, 1), (1403, 0, 1), (1403, 13, 1), (1403, 7, 31), (1403, 1, 32), (1403, 1, 0)]:
        with pytest.raises(ValueError):
            JalaliDate(*args)


def test_names_and_weekday():
    jd = JalaliDate(1403, 1, 1)  # Wednesday 20 March 2024
    assert jd.month_name == "فروردین"
    assert jd.weekday_name == "چهارشنبه"
    assert JalaliDate.from_gregorian(dt.date(2024, 3, 23)).weekday_name == "شنبه"  # Saturday
    assert JalaliDate.from_gregorian(dt.date(2024, 3, 22)).weekday_name == "جمعه"  # Friday
    assert JalaliDate(1403, 12, 30).day_of_year == 366


def test_formatting():
    jd = JalaliDate(1403, 1, 5)
    assert str(jd) == "1403/01/05"
    assert jd.isoformat() == "1403-01-05"
    assert jd.strftime("%-d %B %Y") == "5 فروردین 1403"
    assert jd.strftime("%Y-%m-%d %y %% %A") == "1403-01-05 03 % یکشنبه"
    value = dt.datetime(2024, 3, 24, 9, 5, 7)
    assert format_jalali(value, "%Y/%m/%d %H:%M:%S") == "1403/01/05 09:05:07"
    assert format_jalali(value, "%-H:%M") == "9:05"
    assert format_jalali(dt.date(2024, 3, 24)) == "1403/01/05"


def test_parse():
    assert JalaliDate.parse("1403/01/15") == JalaliDate(1403, 1, 15)
    assert JalaliDate.parse("۱۴۰۳/۰۱/۱۵") == JalaliDate(1403, 1, 15)
    assert JalaliDate.parse(" 1403-1-5 ") == JalaliDate(1403, 1, 5)
    assert JalaliDate.parse("1403.01.05") == JalaliDate(1403, 1, 5)
    for bad in ["", "abc", "1403/13/01", "1403/01", "1403/1/1/1", "14033/01/01"]:
        with pytest.raises(ValueError):
            JalaliDate.parse(bad)


def test_arithmetic_and_ordering():
    assert JalaliDate(1399, 12, 30) + dt.timedelta(days=1) == JalaliDate(1400, 1, 1)
    assert dt.timedelta(days=1) + JalaliDate(1399, 12, 30) == JalaliDate(1400, 1, 1)
    assert JalaliDate(1400, 1, 1) - dt.timedelta(days=1) == JalaliDate(1399, 12, 30)
    assert JalaliDate(1400, 1, 1) - JalaliDate(1399, 1, 1) == dt.timedelta(days=366)
    assert JalaliDate(1403, 1, 1) < JalaliDate(1403, 1, 2) < JalaliDate(1404, 1, 1)


def test_today_and_type_errors():
    assert isinstance(JalaliDate.today(), JalaliDate)
    with pytest.raises(TypeError):
        JalaliDate.from_gregorian("2024-03-20")
    with pytest.raises(ValueError):
        JalaliDate.from_gregorian(dt.date(100, 1, 1))
