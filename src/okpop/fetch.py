from pathlib import Path

import pandas as pd

from okpop import dl, filecheck
from okpop.source import SOURCES

DEFAULT_RAW_DIR = Path("data/raw")


def fetch(
    source_name: str,
    raw_dir: str | Path = DEFAULT_RAW_DIR,
) -> list[Path]:
    """指定したSourceからファイルを取得する。"""

    source = SOURCES[source_name]

    directory = Path(raw_dir) / source.directory

    return dl.files_from_page(
        url=source.url,
        patterns=source.patterns,
        directory=directory,
    )


def fetch_datatype(
    datatype: str,
    raw_dir: str | Path = DEFAULT_RAW_DIR,
) -> list[Path]:
    """指定したdatatypeに属するすべてのSourceからファイルを取得する。"""

    source_names = [
        name
        for name, source in SOURCES.items()
        if source.datatype == datatype
    ]

    if not source_names:
        raise ValueError(f"unknown datatype: {datatype}")

    downloaded = []

    for source_name in source_names:
        files = fetch(
            source_name,
            raw_dir=raw_dir,
        )
        downloaded.extend(files)

    return downloaded


def check_datatype(
    datatype: str,
    end_date: str | pd.Timestamp | None = None,
    raw_dir: str | Path = DEFAULT_RAW_DIR,
) -> dict:
    """指定したdatatypeのファイルの欠落・重複を確認する。"""

    # datatypeに属するSourceをすべて取得
    sources = [
        source
        for source in SOURCES.values()
        if source.datatype == datatype
    ]

    if not sources:
        raise ValueError(f"unknown datatype: {datatype}")

    # 保存先を取得
    # 複数Sourceが同じdirectoryを使う場合は重複を除く
    directories = {
        Path(raw_dir) / source.directory
        for source in sources
    }

    # すべての保存先から日付を集める
    dates = []

    for directory in directories:
        source_dates = filecheck.dates_from_dir(directory)
        dates.extend(source_dates)

    dates = pd.DatetimeIndex(dates).sort_values()

    # datatype全体の開始月
    start = min(
        pd.Timestamp(source.start_date)
        for source in sources
    )

    # 終了月を決定
    if end_date is not None:
        # 呼び出し側の指定を最優先
        end = pd.Timestamp(end_date)

    elif any(source.end_date is None for source in sources):
        # 現在も継続中のSourceがあれば現在月まで
        end = (
            pd.Timestamp.now()
            .to_period("M")
            .to_timestamp()
        )

    else:
        # 全Sourceの期間が確定している場合は、
        # 最も遅い終了月まで
        end = max(
            pd.Timestamp(source.end_date)
            for source in sources
            if source.end_date is not None
        )

    return filecheck.check_dates(
        dates,
        start_date=start,  # pyright: ignore[reportArgumentType]
        end_date=end,  # pyright: ignore[reportArgumentType]
    )

