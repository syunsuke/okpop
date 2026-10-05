import sqlite3
from pathlib import Path

from okpop import database, fetch, importer, report

TEMPLATE_PATH = Path(
    "assets/templates/"
    "populaiton_report_template_0001.xlsx"
)

OUTPUT_DIR = Path("data/output")

RAW_DIR = Path("data/raw")

DB_PATH = database.DEFAULT_DB_PATH


DATATYPES = [
    "census",
    "suikei",
    "hosei",
    "kubun",
]


def get_latest_report_archive() -> Path:
    """最新のレポートZIPを取得する。なければ作成する。"""

    return report.create_report_archive(
        output_dir=OUTPUT_DIR,
        template_path=TEMPLATE_PATH,
        db_path=DB_PATH,
        end_date=None,
    )


def update_database() -> None:
    """GUIからデータベースを更新する。"""

    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"database not found: {DB_PATH}"
        )

    for datatype in DATATYPES:
        fetch.fetch_datatype(
            datatype,
            raw_dir=RAW_DIR,
        )

    for datatype in DATATYPES:
        importer.import_directory(
            RAW_DIR / datatype,
            db_path=DB_PATH,
        )


def get_database_status() -> dict[str, str | None]:
    """各テーブルの最新データ日を取得する。"""

    status = {}

    with sqlite3.connect(DB_PATH) as con:
        for table in [
            "census",
            "suikei",
            "hosei",
            "population_age5_v002",
        ]:
            row = con.execute(
                f"""
                SELECT MAX(observation_date)
                FROM {table}
                """
            ).fetchone()

            status[table] = row[0]

    return status


def create_report_archive_for_date(
    year: int,
    month: int,
) -> Path:
    """指定した基準年月のレポートZIPを取得する。"""

    end_date = f"{year:04d}-{month:02d}-01"

    return report.create_report_archive(
        output_dir=OUTPUT_DIR,
        template_path=TEMPLATE_PATH,
        db_path=DB_PATH,
        end_date=end_date,
    )

