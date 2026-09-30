import re
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd


def guess_datatype(file: str | Path) -> str | None:
    """ファイル名からデータ種別を推測する。"""

    filename = Path(urlparse(str(file)).path).name

    if re.fullmatch(r".*5sai\.xlsx", filename):
        return "kubun"

    if re.fullmatch(r".*jk20.*\.xlsx", filename):
        return "suikei"

    if re.fullmatch(r"jtsukikakuhou20.*\.xlsx", filename):
        return "suikei"

    if re.fullmatch(r"hosei20.*\.xlsx", filename):
        return "hosei"

    return None


def dates_from_filename(
    file: str | Path,
) -> pd.DatetimeIndex | None:
    """ファイル名から、そのファイルが対象とする年月を取得する。"""

    filepath = Path(urlparse(str(file)).path)

    match guess_datatype(filepath):

        case "suikei":
            res = re.search(
                r"jk(20\d{2})(\d{2})(\d{2})",
                filepath.name,
            )

            if res:
                y, m, d = res.groups()

                ts = pd.Timestamp(
                    int(y),
                    int(m),
                    int(d),
                )

                return pd.DatetimeIndex([ts])

            res = re.search(
                r"jtsukikakuhou(20\d{2})(\d{2})",
                filepath.name,
            )

            if res:
                y, m = res.groups()

                ts = pd.Timestamp(
                    int(y),
                    int(m),
                    1,
                )

                return pd.DatetimeIndex([ts])

        case "kubun":
            res = re.search(
                r"(20\d{2})(\d{2})",
                filepath.name,
            )

            if res:
                y, m = res.groups()

                ts = pd.Timestamp(
                    int(y),
                    int(m),
                    1,
                )

                return pd.DatetimeIndex([ts])

        case "hosei":
            res = re.search(
                r"(20\d{2})(\d{2})_(\d{2})",
                filepath.name,
            )

            if res:
                y, m1, m2 = res.groups()

                return pd.date_range(
                    start=f"{y}-{m1}-01",
                    end=f"{y}-{m2}-01",
                    freq="MS",
                )

    return None


def dates_from_dir(
    directory: str | Path,
) -> pd.DatetimeIndex:
    """ディレクトリ内のExcelファイルから対象年月を取得する。"""

    directory = Path(directory)

    dates = []

    for file in directory.glob("*.xlsx"):
        file_dates = dates_from_filename(file)

        if file_dates is not None:
            dates.extend(file_dates)

    return pd.DatetimeIndex(dates).sort_values()


def check_dates(
    dates: pd.DatetimeIndex,
    start_date: str | pd.Timestamp | None = None,
    end_date: str | pd.Timestamp | None = None,
) -> dict:
    """月次データの欠落と重複を調べる。"""

    if start_date is None:
        start_date = min(dates)
    else:
        start_date = pd.Timestamp(start_date)  # pyright: ignore[reportAssignmentType]

    if end_date is None:
        end_date = max(dates)
    else:
        end_date = pd.Timestamp(end_date)  # pyright: ignore[reportAssignmentType]

    index = pd.date_range(
        start=start_date,
        end=end_date,
        freq="MS",
    )

    df = pd.DataFrame(
        {"count": 0},
        index=index,
    )

    for date in dates:
        if date in df.index:
            df.loc[date, "count"] += 1

    missing = df[df["count"] == 0].index.tolist()
    duplicate = df[df["count"] > 1].index.tolist()

    return {
        "start_date": start_date,
        "end_date": end_date,
        "missing": missing,
        "duplicate": duplicate,
    }


