from collections import defaultdict
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd

from okpop import dl, filecheck
from okpop.paths import RAW_DIR
from okpop.source import SOURCES

DEFAULT_RAW_DIR = RAW_DIR


def _url_dates(source_name: str, url: str):
    """Return observation dates for a configured link.

    Census file names do not contain the reference month.
    Their date comes from the fixed Source period.
    """
    dates = filecheck.dates_from_filename(url)
    if dates is not None:
        return dates
    source = SOURCES[source_name]
    if (
        source.datatype == "census"
        and source.end_date == source.start_date
    ):
        return pd.DatetimeIndex([
            pd.Timestamp(source.start_date)
        ])
    raise ValueError(
        f"Cannot detect reference month: {url}"
    )


def _source_urls(source_name: str) -> list[str]:
    source = SOURCES[source_name]
    urls = dl.urls_from_page(
        source.url,
        source.patterns,
    )
    start = pd.Timestamp(source.start_date)
    end = (
        pd.Timestamp(source.end_date)
        if source.end_date else None
    )
    selected = []
    for url in urls:
        dates = _url_dates(source_name, url)
        if dates.min() < start:
            continue
        if end is not None and dates.max() > end:
            continue
        selected.append(url)
    if not selected:
        raise ValueError(
            f"No applicable Excel links: {source_name}"
        )
    return selected


def _check_duplicates(
    mapping: dict[str, list[str]],
    raw_dir: str | Path,
) -> None:
    seen = defaultdict(set)
    for source_name, urls in mapping.items():
        directory = (
            Path(raw_dir) / SOURCES[source_name].directory
        )
        for url in urls:
            name = Path(urlparse(url).path).name
            dates = _url_dates(source_name, url)
            for date in dates:
                seen[date].add(str(directory / name))
    duplicates = {
        str(date.date()): sorted(paths)
        for date, paths in seen.items()
        if len(paths) > 1
    }
    if duplicates:
        details = "\n".join(
            f"{date}: {', '.join(files)}"
            for date, files in sorted(duplicates.items())
        )
        raise ValueError(
            "Duplicate reference months found:\n"
            + details
        )


def fetch(
    source_name: str,
    raw_dir: str | Path = DEFAULT_RAW_DIR,
) -> list[Path]:
    source = SOURCES[source_name]
    urls = _source_urls(source_name)
    _check_duplicates({source_name: urls}, raw_dir)
    return dl.files_from_page(
        source.url,
        source.patterns,
        Path(raw_dir) / source.directory,
        urls=urls,
    )


def fetch_datatype(
    datatype: str,
    raw_dir: str | Path = DEFAULT_RAW_DIR,
) -> list[Path]:
    source_names = [
        name for name, source in SOURCES.items()
        if source.datatype == datatype
    ]
    if not source_names:
        raise ValueError(f"unknown datatype: {datatype}")
    mapping = {
        name: _source_urls(name)
        for name in source_names
    }
    _check_duplicates(mapping, raw_dir)
    downloaded = []
    for source_name in source_names:
        source = SOURCES[source_name]
        downloaded.extend(dl.files_from_page(
            source.url,
            source.patterns,
            Path(raw_dir) / source.directory,
            urls=mapping[source_name],
        ))
    return downloaded


def check_datatype(
    datatype: str,
    end_date: str | pd.Timestamp | None = None,
    raw_dir: str | Path = DEFAULT_RAW_DIR,
    *,
    start_date: str | pd.Timestamp | None = None,
) -> dict:
    sources = [
        source for source in SOURCES.values()
        if source.datatype == datatype
    ]
    if not sources:
        raise ValueError(f"unknown datatype: {datatype}")
    directories = {
        Path(raw_dir) / source.directory
        for source in sources
    }
    dates = []
    for directory in directories:
        dates.extend(filecheck.dates_from_dir(directory))
    dates = pd.DatetimeIndex(dates).sort_values()
    # Old published files remain available, but the
    # continuity check begins at the agreed month.
    if start_date is not None:
        start = pd.Timestamp(start_date)
    elif datatype == "kubun":
        start = pd.Timestamp("2020-10-01")
    elif datatype == "suikei":
        start = pd.Timestamp("2020-11-01")
    else:
        start = min(
            pd.Timestamp(s.start_date)
            for s in sources
        )
    if end_date is not None:
        end = pd.Timestamp(end_date)
    elif any(s.end_date is None for s in sources):
        # No unpublished month is treated as missing.
        # This does not prove that the latest released
        # Excel has already been downloaded.
        end = (
            dates.max() if len(dates)
            else pd.Timestamp.now()
            .to_period("M").to_timestamp()
        )
    else:
        end = max(
            pd.Timestamp(s.end_date)
            for s in sources if s.end_date
        )
    return filecheck.check_dates(
        dates,
        start_date=start,
        end_date=end,
    )
