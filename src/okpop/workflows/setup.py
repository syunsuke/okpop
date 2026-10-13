from pathlib import Path

from okpop import database, fetch, importer
from okpop.paths import (
    DATA_DIR,
    DATA_TYPES,
    DB_DIR,
    DB_PATH,
    OUTPUT_DIR,
    RAW_DIR,
)


def prepare_directories():
    """OKPOPのデータ保存用ディレクトリを作成する。"""

    directories = [
        DATA_DIR,
        RAW_DIR,
        DB_DIR,
        OUTPUT_DIR,
    ]

    directories.extend(
        RAW_DIR / datatype
        for datatype in DATA_TYPES
    )

    for directory in directories:
        directory.mkdir(
            parents=True,
            exist_ok=True,
        )
        print(f"Ready: {directory}")


def setup():
    """OKPOPの初期セットアップ。"""

    print("=== OKPOP setup ===")

    prepare_directories()
    download_data()

    if DB_PATH.exists():
        print(f"Database already exists: {DB_PATH}")
        print("Skipping database build.")
    else:
        temporary_path = (
            DB_DIR / 
            "population_osaka.building.sqlite"
        )

        try:
            build_database(temporary_path)
            install_database(temporary_path)
        finally:
            temporary_path.unlink(missing_ok=True)

    print("Setup completed.")


def download_data():
    """大阪府の人口データをダウンロードする。"""

    print(f"Download directory: {RAW_DIR}")

    for datatype in DATA_TYPES:
        print(f"Downloading: {datatype}")

        files = fetch.fetch_datatype(
            datatype,
            raw_dir=RAW_DIR,
        )

        print(f"Processed: {len(files)} files")


def build_database(db_path: str | Path) -> None:
    """ExcelファイルからSQLiteデータベースを構築する。"""

    db_path = Path(db_path)

    if db_path.exists():
        raise FileExistsError(
            f"Database already exists: {db_path}"
        )

    print(f"Building database: {db_path}")

    database.init_database(
        dbname=db_path,
        reset=True,
    )

    for datatype in DATA_TYPES:
        directory = RAW_DIR / datatype

        print(f"Importing: {datatype}")

        importer.import_directory(
            directory=directory,
            db_path=db_path,
        )

    database.create_views(
        dbname=db_path,
    )

    print("Database build completed.")


def install_database(
    temporary_path: str | Path,
    db_path: str | Path = DB_PATH,
) -> None:
    """構築済みDBを本番DBとして配置する。"""

    temporary_path = Path(temporary_path)
    db_path = Path(db_path)

    if not temporary_path.is_file():
        raise FileNotFoundError(temporary_path)

    if db_path.exists():
        raise FileExistsError(
            f"Database already exists: {db_path}"
        )

    temporary_path.replace(db_path)

    print(f"Database installed: {db_path}")
