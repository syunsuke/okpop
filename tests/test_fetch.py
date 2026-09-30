from pathlib import Path

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
