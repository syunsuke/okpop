import sqlite3
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from okpop import census, database, filecheck, hosei, kubun, suikei


@dataclass(frozen=True)
class ImportData:
    dataframe: pd.DataFrame
    table: str


def read_file(file: str | Path) -> ImportData:
    """ファイルを読み込み、DataFrameと書き込み先テーブルを返す。"""

    file = Path(file)
    datatype = filecheck.guess_datatype(file)

    match datatype:
        case "census":
            df = census.read_census2020(file)

            return ImportData(
                dataframe=df,
                table="census",
            )

        case "suikei":
            df = suikei.read_suikei(file)

            return ImportData(
                dataframe=df,
                table="suikei",
            )

        case "hosei":
            df = hosei.read_hosei(file)

            return ImportData(
                dataframe=df,
                table="hosei",
            )

        case "kubun":
            dfs, version = kubun.read_kubun(file)
            df = kubun.to_db_dataframe(dfs)

            match version:
                case "v001":
                    table = "population_age5_v001"

                case "v002":
                    table = "population_age5_v002"

                case _:
                    raise ValueError(
                        f"unknown kubun version: {version}"
                    )

            return ImportData(
                dataframe=df,
                table=table,
            )

        case _:
            raise ValueError(
                f"unknown datatype: {file.name}"
            )

def is_imported(
    data: ImportData,
    db_path: str | Path = database.DEFAULT_DB_PATH,
) -> bool:
    """ImportDataの対象日がすべてDBに存在するか確認する。"""

    db_path = Path(db_path)

    dates = (
        data.dataframe["observation_date"]
        .drop_duplicates()
    )

    with sqlite3.connect(db_path) as con:
        for date in dates:
            date_str = pd.Timestamp(date).strftime("%Y-%m-%d")

            row = con.execute(
                f"""
                SELECT COUNT(*)
                FROM {data.table}
                WHERE observation_date = ?
                """,
                (date_str,),
            ).fetchone()

            if row is None:
                return False

            count = row[0]

            if count == 0:
                return False

    return True

def import_data(
    data: ImportData,
    db_path: str | Path = database.DEFAULT_DB_PATH,
) -> None:
    """ImportDataをデータベースへ書き込む。"""

    db_path = Path(db_path)

    df = data.dataframe.copy()
    df["observation_date"] = (
        pd.to_datetime(df["observation_date"])
        .dt.strftime("%Y-%m-%d")
    )
    database.write_df_to_db(
        df=df,
        table_name=data.table,
        dbname=db_path,
    )


def import_file(
    file: str | Path,
    db_path: str | Path = database.DEFAULT_DB_PATH,
) -> None:
    """1つのExcelファイルをデータベースへ書き込む。"""

    db_path = Path(db_path)
    data = read_file(file)

    import_data(
        data=data,
        db_path=db_path,
    )

def import_directory(
    directory: str | Path,
    db_path: str | Path = database.DEFAULT_DB_PATH,
) -> None:
    """ディレクトリ内のExcelファイルをDBへ取り込む。"""

    directory = Path(directory)
    db_path = Path(db_path)

    for file in sorted(directory.glob("*.xlsx")):
        data = read_file(file)

        if is_imported(data, db_path):
            print(f"skip: {file.name}")
            continue

        print(f"import: {file.name}")

        import_data(
            data=data,
            db_path=db_path,
        )

