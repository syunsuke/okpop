from pathlib import Path

from okpop import database, fetch, importer

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
    # 0. 既存DBを確認
    # ----------------------------------------

    print("=== Check existing database ===")

    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"database not found: {DB_PATH}"
        )

    print(f"Database: {DB_PATH}")

    # ----------------------------------------
    # 1. 最新ファイルを取得
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
    # 2. DBを更新
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


    print("\n=== Complete ===")
    print(f"Database: {DB_PATH}")


if __name__ == "__main__":
    main()
