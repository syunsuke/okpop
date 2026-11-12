import sqlite3
from contextlib import closing
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from okpop import (
    census, census2025, database, filecheck,
    hosei, kubun, suikei,
)


@dataclass(frozen=True)
class ImportData:
    dataframe: pd.DataFrame
    table: str


def read_file(file: str | Path) -> ImportData:
    """Excelを読み、書き込み先の表も返す。"""
    file = Path(file)
    datatype = filecheck.guess_datatype(file)

    match datatype:
        case "census":
            if file.name.lower().startswith(
                "r7census_osaka_"
            ):
                df = census2025.read_census2025(file)
            else:
                df = census.read_census2020(file)
            return ImportData(df, "census")

        case "suikei":
            return ImportData(
                suikei.read_suikei(file), "suikei"
            )

        case "hosei":
            return ImportData(
                hosei.read_hosei(file), "hosei"
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
            return ImportData(df, table)

        case _:
            raise ValueError(
                f"unknown datatype: {file.name}"
            )


def is_imported(
    data: ImportData,
    db_path: str | Path = database.DEFAULT_DB_PATH,
) -> bool:
    """ImportDataの対象日がすべてDBにあるか。"""
    dates = data.dataframe[
        "observation_date"
    ].drop_duplicates()
    with closing(sqlite3.connect(db_path)) as con:
        for date in dates:
            date_str = pd.Timestamp(date).strftime(
                "%Y-%m-%d"
            )
            row = con.execute(
                f"SELECT COUNT(*) FROM {data.table} "
                "WHERE observation_date = ?",
                (date_str,),
            ).fetchone()
            if row is None or row[0] == 0:
                return False
    return True


def import_data(
    data: ImportData,
    db_path: str | Path = database.DEFAULT_DB_PATH,
) -> None:
    """ImportDataをデータベースに書き込む。"""
    df = data.dataframe.copy()
    df["observation_date"] = (
        pd.to_datetime(df["observation_date"])
        .dt.strftime("%Y-%m-%d")
    )
    database.write_df_to_db(
        df=df,
        table_name=data.table,
        dbname=Path(db_path),
    )


def import_file(
    file: str | Path,
    db_path: str | Path = database.DEFAULT_DB_PATH,
) -> None:
    import_data(
        read_file(file),
        db_path=Path(db_path),
    )


def import_directory(
    directory: str | Path,
    db_path: str | Path = database.DEFAULT_DB_PATH,
) -> None:
    directory = Path(directory)
    db_path = Path(db_path)
    for file in sorted(directory.glob("*.xlsx")):
        data = read_file(file)
        if is_imported(data, db_path):
            print(f"skip: {file.name}")
            continue
        print(f"import: {file.name}")
        import_data(data, db_path=db_path)
