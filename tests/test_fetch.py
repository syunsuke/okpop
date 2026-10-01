from pathlib import Path

import pandas as pd
import pytest

from okpop import fetch


def test_fetch(monkeypatch, tmp_path):
    called = {}

    def fake_files_from_page(
        url: str,
        patterns: list[str],
        directory: str | Path,
    ) -> list[Path]:
        called["url"] = url
        called["patterns"] = patterns
        called["directory"] = directory

        return [
            Path(directory) / "sample.xlsx",
        ]

    monkeypatch.setattr(
        fetch.dl,
        "files_from_page",
        fake_files_from_page,
    )

    result = fetch.fetch(
        "suikei_current",
        raw_dir=tmp_path,
    )

    source = fetch.SOURCES["suikei_current"]

    assert called["url"] == source.url
    assert called["patterns"] == source.patterns
    assert called["directory"] == tmp_path / "suikei"

    assert result == [
        tmp_path / "suikei" / "sample.xlsx",
    ]


def test_fetch_datatype(monkeypatch, tmp_path):
    called = []

    def fake_fetch(
        source_name: str,
        raw_dir: str | Path,
    ) -> list[Path]:
        called.append(source_name)

        return [
            Path(raw_dir) / f"{source_name}.xlsx",
        ]

    monkeypatch.setattr(
        fetch,
        "fetch",
        fake_fetch,
    )

    result = fetch.fetch_datatype(
        "suikei",
        raw_dir=tmp_path,
    )

    assert called == [
        "suikei_current",
        "suikei_archive",
    ]

    assert result == [
        tmp_path / "suikei_current.xlsx",
        tmp_path / "suikei_archive.xlsx",
    ]


def test_fetch_datatype_unknown(tmp_path):
    with pytest.raises(ValueError):
        fetch.fetch_datatype(
            "hoge",
            raw_dir=tmp_path,
        )


def test_check_datatype(monkeypatch, tmp_path):
    """指定したend_dateがcheck_datesへ渡される。"""

    called = {}

    def fake_dates_from_dir(directory):
        called["directory"] = directory

        return pd.DatetimeIndex([
            "2015-11-01",
            "2015-12-01",
        ])

    def fake_check_dates(
        dates,
        start_date=None,
        end_date=None,
    ):
        called["dates"] = dates
        called["start_date"] = start_date
        called["end_date"] = end_date

        return {
            "missing": [],
            "duplicate": [],
        }

    monkeypatch.setattr(
        fetch.filecheck,
        "dates_from_dir",
        fake_dates_from_dir,
    )

    monkeypatch.setattr(
        fetch.filecheck,
        "check_dates",
        fake_check_dates,
    )

    result = fetch.check_datatype(
        "suikei",
        end_date="2026-09-01",
        raw_dir=tmp_path,
    )

    assert called["directory"] == tmp_path / "suikei"

    assert called["start_date"] == pd.Timestamp(
        "2015-11-01"
    )

    assert called["end_date"] == pd.Timestamp(
        "2026-09-01"
    )

    assert result == {
        "missing": [],
        "duplicate": [],
    }


def test_check_datatype_same_directory_only_once(
    monkeypatch,
    tmp_path,
):
    """複数Sourceが同じdirectoryなら1回だけ読む。"""

    called = []

    def fake_dates_from_dir(directory):
        called.append(directory)

        return pd.DatetimeIndex([
            "2020-11-01",
        ])

    monkeypatch.setattr(
        fetch.filecheck,
        "dates_from_dir",
        fake_dates_from_dir,
    )

    monkeypatch.setattr(
        fetch.filecheck,
        "check_dates",
        lambda dates, start_date, end_date: {
            "missing": [],
            "duplicate": [],
        },
    )

    fetch.check_datatype(
        "suikei",
        end_date="2020-11-01",
        raw_dir=tmp_path,
    )

    assert called == [
        tmp_path / "suikei",
    ]


def test_check_datatype_multiple_directories(
    monkeypatch,
    tmp_path,
):
    """異なるdirectoryの日付をすべて集める。"""

    sources = fetch.SOURCES.copy()

    source_type = type(sources["suikei_current"])

    sources["suikei_current"] = source_type(
        datatype="suikei",
        url="https://example.com/current",
        patterns=[r"current.*\.xlsx"],
        directory="suikei/current",
        start_date="2020-11-01",
    )

    sources["suikei_archive"] = source_type(
        datatype="suikei",
        url="https://example.com/archive",
        patterns=[r"archive.*\.xlsx"],
        directory="suikei/archive",
        start_date="2015-11-01",
        end_date="2020-09-01",
    )

    monkeypatch.setattr(
        fetch,
        "SOURCES",
        sources,
    )

    def fake_dates_from_dir(directory):
        if directory == tmp_path / "suikei/current":
            return pd.DatetimeIndex([
                "2020-11-01",
            ])

        if directory == tmp_path / "suikei/archive":
            return pd.DatetimeIndex([
                "2020-09-01",
            ])

        return pd.DatetimeIndex([])

    called = {}

    def fake_check_dates(
        dates,
        start_date=None,
        end_date=None,
    ):
        called["dates"] = dates

        return {
            "missing": [],
            "duplicate": [],
        }

    monkeypatch.setattr(
        fetch.filecheck,
        "dates_from_dir",
        fake_dates_from_dir,
    )

    monkeypatch.setattr(
        fetch.filecheck,
        "check_dates",
        fake_check_dates,
    )

    fetch.check_datatype(
        "suikei",
        end_date="2020-11-01",
        raw_dir=tmp_path,
    )

    expected = pd.DatetimeIndex([
        "2020-09-01",
        "2020-11-01",
    ])

    assert called["dates"].equals(expected)


def test_check_datatype_current_source_uses_current_month(
    monkeypatch,
    tmp_path,
):
    """end_date=NoneのSourceがあれば現在月まで確認する。"""

    called = {}

    monkeypatch.setattr(
        fetch.filecheck,
        "dates_from_dir",
        lambda directory: pd.DatetimeIndex([]),
    )

    def fake_check_dates(
        dates,
        start_date=None,
        end_date=None,
    ):
        called["end_date"] = end_date

        return {
            "missing": [],
            "duplicate": [],
        }

    monkeypatch.setattr(
        fetch.filecheck,
        "check_dates",
        fake_check_dates,
    )

    fetch.check_datatype(
        "suikei",
        raw_dir=tmp_path,
    )

    expected = (
        pd.Timestamp.now()
        .to_period("M")
        .to_timestamp()
    )

    assert called["end_date"] == expected


def test_check_datatype_finished_source_uses_source_end_date(
    monkeypatch,
    tmp_path,
):
    """全Sourceが確定済みならSourceの終了月を使う。"""

    called = {}

    monkeypatch.setattr(
        fetch.filecheck,
        "dates_from_dir",
        lambda directory: pd.DatetimeIndex([]),
    )

    def fake_check_dates(
        dates,
        start_date=None,
        end_date=None,
    ):
        called["end_date"] = end_date

        return {
            "missing": [],
            "duplicate": [],
        }

    monkeypatch.setattr(
        fetch.filecheck,
        "check_dates",
        fake_check_dates,
    )

    fetch.check_datatype(
        "hosei",
        raw_dir=tmp_path,
    )

    assert called["end_date"] == pd.Timestamp(
        "2020-09-01"
    )


def test_check_datatype_unknown(tmp_path):
    with pytest.raises(ValueError):
        fetch.check_datatype(
            "hoge",
            raw_dir=tmp_path,
        )
