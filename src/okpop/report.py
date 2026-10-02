import sqlite3
from pathlib import Path
from shutil import copyfile

import pandas as pd
from openpyxl import load_workbook

from . import database


def read_report_data(
    area_name: str,
    start_date: str | None = None,
    end_date: str | None = None,
    db_path: str | Path = database.DEFAULT_DB_PATH,
) -> pd.DataFrame:
    """Excelレポート用の人口データを日付の降順で取得する。"""

    query = """
        SELECT *
        FROM view_excel_report_data
        WHERE area_name = ?
    """

    params = [area_name]

    if start_date is not None:
        query += " AND observation_date >= ?"
        params.append(start_date)

    if end_date is not None:
        query += " AND observation_date <= ?"
        params.append(end_date)

    query += " ORDER BY observation_date DESC"

    with sqlite3.connect(db_path) as con:
        df = pd.read_sql_query(
            query,
            con,
            params=params,
        )

    df["observation_date"] = pd.to_datetime(df["observation_date"])

    return df


def read_report_data3(
    area_name: str,
    db_path: str | Path = database.DEFAULT_DB_PATH,
) -> pd.DataFrame:
    """Excelレポート用の人口データを全期間取得する。"""

    query = """
        SELECT *
        FROM view_excel_report_data
        WHERE area_name = ?
        ORDER BY observation_date DESC
    """

    with sqlite3.connect(db_path) as con:
        df = pd.read_sql_query(
            query,
            con,
            params=[area_name],
        )

    df["observation_date"] = pd.to_datetime(df["observation_date"])

    return df

def read_report_data2(
    area_name: str,
    start_date: str,
    end_date: str,
    db_path: str | Path = database.DEFAULT_DB_PATH,
) -> pd.DataFrame:
    """Excelレポート用の人口データを取得する。"""

    query = """
        SELECT *
        FROM view_excel_report_data
        WHERE area_name = ?
          AND observation_date BETWEEN ? AND ?
        ORDER BY observation_date
    """

    with sqlite3.connect(db_path) as con:
        df = pd.read_sql_query(
            query,
            con,
            params=[area_name, start_date, end_date],
        )

    df["observation_date"] = pd.to_datetime(df["observation_date"])

    return df


def write_report(
    df: pd.DataFrame,
    template_path: str | Path,
    output_path: str | Path,
) -> None:
    """DataFrameをExcelレポートテンプレートのsourceシートへ書き込む。"""

    template_path = Path(template_path)
    output_path = Path(output_path)

    copyfile(template_path, output_path)

    wb = load_workbook(output_path)
    ws = wb["source"]

    # sourceシートの既存データを削除
    ws.delete_rows(1, ws.max_row)

    # ヘッダー
    for col, column_name in enumerate(df.columns, start=1):
        ws.cell(
            row=1,
            column=col,
            value=column_name,
        )

    # データ
    for row, values in enumerate(
        df.itertuples(index=False, name=None),
        start=2,
    ):
        for col, value in enumerate(values, start=1):

            if isinstance(value, pd.Timestamp):
                value = value.to_pydatetime()

            ws.cell(
                row=row,
                column=col,
                value=value,
            )

    wb.save(output_path)

