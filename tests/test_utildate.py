import datetime

import pandas as pd

from okpop import utildate


def test_wareki_reiwa():
    result = utildate.wareki_to_timestamp(
        "令和3年11月1日"
    )

    assert result == pd.Timestamp("2021-11-01")


def test_wareki_heisei():
    result = utildate.wareki_to_timestamp(
        "平成29年2月1日"
    )

    assert result == pd.Timestamp("2017-02-01")


def test_wareki_showa():
    result = utildate.wareki_to_timestamp(
        "昭和60年4月1日"
    )

    assert result == pd.Timestamp("1985-04-01")


def test_wareki_gannen():
    result = utildate.wareki_to_timestamp(
        "令和元年5月1日"
    )

    assert result == pd.Timestamp("2019-05-01")


def test_wareki_without_day():
    result = utildate.wareki_to_timestamp(
        "令和3年11月",
        day=False,
    )

    assert result == pd.Timestamp("2021-11-01")


def test_wareki_zenkaku_number():
    result = utildate.wareki_to_timestamp(
        "令和３年１１月１日"
    )

    assert result == pd.Timestamp("2021-11-01")


def test_datetime():
    value = datetime.datetime(2021, 11, 1)

    result = utildate.wareki_to_timestamp(value)

    assert result == pd.Timestamp("2021-11-01")


def test_invalid_wareki():
    result = utildate.wareki_to_timestamp(
        "これは日付ではない"
    )

    assert result is None
