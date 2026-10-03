from pathlib import Path
from shutil import rmtree

from okpop import database, fetch, importer, report

SANDBOX_DIR = Path("sandbox/data/build")
RAW_DIR = SANDBOX_DIR / "raw"
DB_PATH = SANDBOX_DIR / "population_osaka.sqlite"

DATATYPES = [
    "census",
    "suikei",
    "hosei",
    "kubun",
]


def main():
    # ----------------------------------------
    # 0. 完全に何もない状態にする
    # ----------------------------------------

    print("=== Reset sandbox ===")

    if SANDBOX_DIR.exists():
        rmtree(SANDBOX_DIR)

    RAW_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # ----------------------------------------
    # 1. ファイルをダウンロード
    # ----------------------------------------

    print("\n=== Download ===")

    for datatype in DATATYPES:
        print(f"\n[{datatype}]")

        files = fetch.fetch_datatype(
            datatype,
            raw_dir=RAW_DIR,
        )

        print(
            f"{len(files)} files downloaded"
        )

    # ----------------------------------------
    # 2. DBを新規作成
    # ----------------------------------------

    print("\n=== Create database ===")

    database.init_database(
        dbname=DB_PATH,
        reset=True,
    )

    # ----------------------------------------
    # 3. 全ファイルをDBへ取り込む
    # ----------------------------------------

    print("\n=== Import ===")

    for datatype in DATATYPES:
        print(f"\n[{datatype}]")

        directory = (
            RAW_DIR
            / datatype
        )

        importer.import_directory(
            directory=directory,
            db_path=DB_PATH,
        )

    # ----------------------------------------
    # 4. Viewを作成
    # ----------------------------------------

    print("\n=== Create views ===")

    database.create_views(
        dbname=DB_PATH,
    )

    # ----------------------------------------
    # 完了
    # ----------------------------------------

    print("\n=== Complete ===")
    print(f"Raw data : {RAW_DIR}")
    print(f"Database : {DB_PATH}")


    # ----------------------------------------
    # 検証
    # ----------------------------------------

    print("\n=== Verify database ===")
    
    df = report.read_report_data(
        area_name="大阪市福島区",
        db_path=DB_PATH,
    )
    
    report.validate_report_data(df)
    
    print(
        "Latest report date:",
        df["observation_date"].iloc[0],
    )
    
    print("Database validation OK")


if __name__ == "__main__":
    main()
