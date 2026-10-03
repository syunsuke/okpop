import sqlite3
from datetime import date
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

    df["observation_date"] = pd.to_datetime(
            df["observation_date"]
            )

    return df




def write_report(
    df: pd.DataFrame,
    template_path: str | Path,
    output_path: str | Path,
) -> None:
    """Excelテンプレートにレポート用データを書き込む。"""

    template_path = Path(template_path)
    output_path = Path(output_path)

    # テンプレートを出力先へコピー
    copyfile(template_path, output_path)

    # コピーしたExcelファイルを開く
    wb = load_workbook(output_path)
    ws = wb["source"]

    # 1行目のヘッダーは残して、
    # 2行目以降の古いデータだけ削除
    if ws.max_row >= 2:
        ws.delete_rows(2, ws.max_row - 1)

    # DataFrameのデータを2行目から書き込む
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

    ws_report = wb["report"]

    # 作成日書き込み
    ws_report["BB1"] = date.today()
    ws_report["BB1"].number_format = 'yyyy"年"m"月"d"日"'

    # reportシートを開くようにする
    wb.active = wb.sheetnames.index("report")

    # 選択枠を目立たない右下隅へ
    ws_report.sheet_view.selection[0].activeCell = "A56"
    ws_report.sheet_view.selection[0].sqref = "A56"

    # 表示位置は1ページ目の左上
    ws_report.sheet_view.topLeftCell = "A1"

    # 保存
    wb.save(output_path)


def create_report(
    area_name: str,
    end_date: str,
    output_path: str | Path,
    template_path: str | Path,
    db_path: str | Path = database.DEFAULT_DB_PATH,
) -> None:
    """指定した地域・基準日までのExcelレポートを作成する。"""

    df = read_report_data(
        area_name=area_name,
        end_date=end_date,
        db_path=db_path,
    )

    write_report(
        df=df,
        template_path=template_path,
        output_path=output_path,
    )
