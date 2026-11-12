import re

import pandas as pd

from okpop import fetch, filecheck
from okpop.source import SOURCES


def test_october_2020_age5_file():
    name = "202010kakutei5sai.xlsx"
    assert filecheck.guess_datatype(name) == "kubun"
    assert filecheck.dates_from_filename(name)[0] == (
        pd.Timestamp("2020-10-01")
    )
    older = SOURCES["kubun_older"]
    assert any(
        re.search(pattern, name)
        for pattern in older.patterns
    )


def test_older_files_remain_configured():
    assert "kubun_older" in SOURCES
    assert SOURCES["kubun_older"].start_date == (
        "2016-11-01"
    )
    assert SOURCES["kubun_older"].end_date == (
        "2020-10-01"
    )


def test_kubun_missing_only_from_october_2020(
    monkeypatch, tmp_path,
):
    dates = pd.DatetimeIndex([
        "2019-10-01", "2020-10-01",
        "2020-11-01", "2021-01-01",
    ])
    monkeypatch.setattr(
        fetch.filecheck, "dates_from_dir",
        lambda _: dates,
    )
    result = fetch.check_datatype(
        "kubun", raw_dir=tmp_path,
        end_date="2021-01-01",
    )
    assert result["start_date"] == (
        pd.Timestamp("2020-10-01")
    )
    assert result["missing"] == [
        pd.Timestamp("2020-12-01")
    ]
    assert result["duplicate"] == []
