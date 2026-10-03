import sqlite3
from datetime import date, datetime
from pathlib import Path
from shutil import copyfile, make_archive, rmtree

import pandas as pd
from openpyxl import load_workbook

from . import area, database


def read_report_data(
    area_name: str,
    start_date: str | None = None,
    end_date: str | None = None,
    db_path: str | Path = database.DEFAULT_DB_PATH,
) -> pd.DataFrame:

    with sqlite3.connect(db_path) as con:

        # 人口＋年齢区分がそろっている最新月を取得
        latest_query = """
            SELECT MAX(observation_date)
            FROM view_excel_report_data
            WHERE area_name = ?
              AND total_population IS NOT NULL
              AND total_age_00_04 IS NOT NULL
        """

        latest_params = [area_name]

        if end_date is not None:
            latest_query += """
                AND observation_date <= ?
            """
            latest_params.append(end_date)

        row = con.execute(
            latest_query,
            latest_params,
        ).fetchone()

        latest_date = row[0]

        if latest_date is None:
            raise ValueError(
                f"{area_name} の年齢区分データがありません"
            )

        # 基準月までのデータを取得
        query = """
            SELECT *
            FROM view_excel_report_data
            WHERE area_name = ?
              AND observation_date <= ?
        """

        params = [
            area_name,
            latest_date,
        ]

        if start_date is not None:
            query += """
                AND observation_date >= ?
            """
            params.append(start_date)

        query += """
            ORDER BY observation_date DESC
        """

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


def validate_report_data(
    df: pd.DataFrame,
) -> None:
    """レポート用データの完全性を確認する。"""

    if df.empty:
        raise ValueError(
            "レポートデータがありません"
        )

    # 列数を確認
    if df.shape[1] != 76:
        raise ValueError(
            "レポートデータは76列必要です"
            f"（実際: {df.shape[1]}列）"
        )

    df = df.copy()

    df["observation_date"] = pd.to_datetime(
        df["observation_date"]
    )

    # 日付の古い順に並べる
    df = df.sort_values(
        "observation_date"
    )

    # 直近73か月を取り出す
    latest_data = df.tail(73)

    # 73か月分あるか
    if len(latest_data) < 73:
        raise ValueError(
            "レポート作成には73か月分のデータが必要です"
        )

    # 本来あるべき73か月の日付
    expected_dates = pd.date_range(
        end=latest_data["observation_date"].iloc[-1],
        periods=73,
        freq="MS",
    )

    # 実際の73か月の日付
    actual_dates = pd.DatetimeIndex(
        latest_data["observation_date"]
    )

    # 日付が連続しているか
    if not actual_dates.equals(expected_dates):
        raise ValueError(
            "レポート作成に必要な73か月のデータが"
            "連続していません"
        )

    # 欠損値チェック用のコピーを作る
    check_data = latest_data.copy()

    # 国勢調査月では、月次変動値のNULLを許容する
    monthly_columns = [
        "monthly_population_change",
        "monthly_natural_change",
        "births_monthly",
        "deaths_monthly",
        "monthly_net_migration",
    ]

    census_rows = (
        check_data["source"] == "census"
    )

    check_data.loc[
        census_rows,
        monthly_columns,
    ] = 0

    # 上記以外に欠損値があればエラー
    if check_data.isna().any().any():
        raise ValueError(
            "レポートデータに欠損値があります"
        )






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

    validate_report_data(df)

    write_report(
        df=df,
        template_path=template_path,
        output_path=output_path,
    )

def create_report_archive(
    end_date: str,
    output_dir: str | Path,
    template_path: str | Path,
    db_path: str | Path = database.DEFAULT_DB_PATH,
) -> Path:
    """全地域のExcelレポートを作成し、ZIPアーカイブにする。"""

    output_dir = Path(output_dir)
    template_path = Path(template_path)
    db_path = Path(db_path)

    created_datetime = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    report_dir = output_dir / (
        f"okpop_report_{created_datetime}"
    )

    report_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    for area_name in area.AREA_NAME_V002_COL_NAME:
        output_path = (
            report_dir
            / f"{area_name}_{created_datetime}.xlsx"
        )

        create_report(
            area_name=area_name,
            end_date=end_date,
            output_path=output_path,
            template_path=template_path,
            db_path=db_path,
        )

    archive_base = output_dir / (
        f"okpop_report_{created_datetime}"
    )

    archive_file = Path(
        make_archive(
            base_name=str(archive_base),
            format="zip",
            root_dir=report_dir,
        )
    )

    rmtree(report_dir)

    return archive_file


