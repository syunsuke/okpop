from pathlib import Path

from okpop import database, report

DB_PATH = database.DEFAULT_DB_PATH

TEMPLATE_PATH = Path(
    "assets/templates/"
    "populaiton_report_template_0001.xlsx"
)

OUTPUT_DIR = Path(
    "data/output"
)


def main():
    # ----------------------------------------
    # 1. DBの存在確認
    # ----------------------------------------

    print("=== Check database ===")

    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"database not found: {DB_PATH}"
        )

    # ----------------------------------------
    # 2. レポート作成
    # ----------------------------------------

    print("\n=== Create reports ===")

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    archive_file = report.create_report_archive(
        output_dir=OUTPUT_DIR,
        template_path=TEMPLATE_PATH,
        db_path=DB_PATH,
    )

    # ----------------------------------------
    # 完了
    # ----------------------------------------

    print("\n=== Complete ===")
    print(f"Archive: {archive_file}")


if __name__ == "__main__":
    main()
