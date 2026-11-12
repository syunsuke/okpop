import re
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd


def _name(file: str | Path) -> str:
    return Path(urlparse(str(file)).path).name


def guess_datatype(
    file: str | Path,
) -> str | None:
    name = _name(file)

    if re.fullmatch(
        r"r2kokutyo_osakahu_kakuhou_syousai\.xlsx",
        name,
    ):
        return "census"

    if re.fullmatch(
        r"r7census_osaka_kakutei_"
        r"gaiyou_data\.xlsx",
        name,
        re.I,
    ):
        return "census"

    if re.search(r"5sai.*\.xlsx$", name, re.I):
        return "kubun"
    if re.fullmatch(
        r"(?:kakuhou_|kakutei_)?jk20\d{6}"
        r"(?:[-_]\d+)?\.xlsx",
        name,
    ):
        return "suikei"
    if re.fullmatch(
        r"jtsukikakuhou20\d{4}.*\.xlsx",
        name,
    ):
        return "suikei"
    if re.fullmatch(
        r"hosei20\d{4}_\d{2}.*\.xlsx",
        name,
    ):
        return "hosei"
    return None


def dates_from_filename(
    file: str | Path,
) -> pd.DatetimeIndex | None:
    name = _name(file)
    datatype = guess_datatype(name)

    if datatype == "suikei":
        match = re.search(
            r"jk(20\d{2})(\d{2})(\d{2})",
            name,
        )
        if match:
            y, m, d = map(int, match.groups())
            return pd.DatetimeIndex([
                pd.Timestamp(y, m, d)
            ])
        match = re.search(
            r"jtsukikakuhou(20\d{2})(\d{2})",
            name,
        )
        if match:
            y, m = map(int, match.groups())
            return pd.DatetimeIndex([
                pd.Timestamp(y, m, 1)
            ])

    if datatype == "kubun":
        match = re.search(
            r"(20\d{2})(\d{2})",
            name,
        )
        if match:
            y, m = map(int, match.groups())
            return pd.DatetimeIndex([
                pd.Timestamp(y, m, 1)
            ])

    if datatype == "hosei":
        match = re.search(
            r"(20\d{2})(\d{2})_(\d{2})",
            name,
        )
        if match:
            y, m1, m2 = map(int, match.groups())
            return pd.date_range(
                start=f"{y}-{m1:02d}-01",
                end=f"{y}-{m2:02d}-01",
                freq="MS",
            )
    return None


def dates_from_dir(
    directory: str | Path,
) -> pd.DatetimeIndex:
    dates = []
    for file in Path(directory).glob("*.xlsx"):
        found = dates_from_filename(file)
        if found is not None:
            dates.extend(found)
    return pd.DatetimeIndex(dates).sort_values()


def check_dates(
    dates: pd.DatetimeIndex,
    start_date: str | pd.Timestamp | None = None,
    end_date: str | pd.Timestamp | None = None,
) -> dict:
    dates = pd.DatetimeIndex(dates)
    if len(dates) == 0:
        if start_date is None or end_date is None:
            raise ValueError(
                "No data: specify start_date and end_date"
            )

    start = (
        pd.Timestamp(start_date)
        if start_date is not None else dates.min()
    )
    end = (
        pd.Timestamp(end_date)
        if end_date is not None else dates.max()
    )
    if start > end:
        raise ValueError("start_date is after end_date")

    index = pd.date_range(start, end, freq="MS")
    counts = dates.value_counts()
    missing = [
        date for date in index
        if counts.get(date, 0) == 0
    ]
    duplicate = [
        date for date in index
        if counts.get(date, 0) > 1
    ]
    return {
        "start_date": start,
        "end_date": end,
        "missing": missing,
        "duplicate": duplicate,
    }
