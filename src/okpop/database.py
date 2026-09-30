import sqlite3
from pathlib import Path

import pandas as pd

DEFAULT_DB_PATH = Path("data/db/population_osaka.sqlite")
DEFAULT_SCHEMA_PATH = Path("sql/schema.sql")

TBL_CENSUS = "census"
TBL_SUIKEI = "suikei"
TBL_HOSEI = "hosei"

TBL_AGE5_V001 = "population_age5_v001"
TBL_AGE5_V002 = "population_age5_v002"

# schemaファイルは、BEGIN TRANSACTION; COMMIT;で
# 包んで、一つのトランザクションを明示する
def init_database(
    dbname=DEFAULT_DB_PATH,
    schema_file=DEFAULT_SCHEMA_PATH,
    reset = False,
    ):

    dbname = Path(dbname)
    schema_file = Path(schema_file)
    dbname.parent.mkdir(parents=True, exist_ok=True)

    # オションでリセット
    if reset:
        dbname.unlink(missing_ok=True)

    # データベース処理
    sql = schema_file.read_text(encoding="utf-8")
    con = sqlite3.connect(dbname)

    try:
        con.executescript(sql)
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


def write_df_to_db(
    df: pd.DataFrame,
    table_name: str,
    dbname=DEFAULT_DB_PATH,
    ):
    """DataFrameをSQLiteのテーブルへ追加する"""
    
    dbname = Path(dbname)
    con = sqlite3.connect(dbname)
    try:
        with con:
            df.to_sql(
                table_name,
                con,
                if_exists="append",
                index=False,
            )
            return len(df)
    finally:
        con.close()
    


