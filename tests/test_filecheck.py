import pandas as pd

from okpop import filecheck


def test_dates_from_filename_suikei():
    dates = filecheck.dates_from_filename(
        "kakutei_jk20201101.xlsx"
    )

    assert dates is not None

    assert len(dates) == 1
    assert dates[0] == pd.Timestamp("2020-11-01")

def test_dates_from_filename_hosei():
    dates = filecheck.dates_from_filename(
        "hosei201011_12.xlsx"
    )

    assert dates is not None

    expected = pd.date_range(
        "2010-11-01",
        "2010-12-01",
        freq="MS",
    )

    assert dates.equals(expected)


def test_dates_from_filename_kubun():
    dates = filecheck.dates_from_filename(
        "202608suikei5sai.xlsx"
    )

    assert dates is not None

    expected = pd.DatetimeIndex([
        "2026-08-01",
    ])

    assert dates.equals(expected)

def test_dates_from_filename_unknown():
    dates = filecheck.dates_from_filename(
        "hoge.xlsx"
    )

    assert dates is None


def test_dates_from_dir(tmp_path):
    (tmp_path / "kakutei_jk20201101.xlsx").touch()
    (tmp_path / "kakutei_jk20201201.xlsx").touch()
    (tmp_path / "hoge.xlsx").touch()

    dates = filecheck.dates_from_dir(tmp_path)

    expected = pd.DatetimeIndex([
        "2020-11-01",
        "2020-12-01",
    ])

    assert dates.equals(expected)

def test_check_dates():
    dates = pd.DatetimeIndex([
        "2026-01-01",
        "2026-02-01",
        "2026-04-01",
        "2026-04-01",
        "2026-05-01",
    ])

    result = filecheck.check_dates(dates)

    assert result["start_date"] == pd.Timestamp("2026-01-01")
    assert result["end_date"] == pd.Timestamp("2026-05-01")

    assert result["missing"] == [
        pd.Timestamp("2026-03-01"),
    ]

    assert result["duplicate"] == [
        pd.Timestamp("2026-04-01"),
    ]

def test_check_dates_with_range():
    dates = pd.DatetimeIndex([
        "2021-01-01",
        "2021-02-01",
    ])

    result = filecheck.check_dates(
        dates,
        start_date="2020-11-01",
        end_date="2021-03-01",
    )

    assert result["missing"] == [
        pd.Timestamp("2020-11-01"),
        pd.Timestamp("2020-12-01"),
        pd.Timestamp("2021-03-01"),
    ]

    assert result["duplicate"] == []
