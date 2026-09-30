import sqlite3

import pandas as pd
import pytest

from okpop import database


def test_init_database(tmp_path):
    """DBファイルと必要なテーブルが作成される"""

    db_path = tmp_path / "test.sqlite"

    database.init_database(dbname=db_path)

    assert db_path.exists()

    with sqlite3.connect(db_path) as con:
        tables = con.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            """
        ).fetchall()

    table_names = {row[0] for row in tables}

    assert database.TBL_CENSUS in table_names
    assert database.TBL_SUIKEI in table_names
    assert database.TBL_HOSEI in table_names
    assert database.TBL_AGE5_V001 in table_names
    assert database.TBL_AGE5_V002 in table_names

def test_init_database_reset(tmp_path):
    """reset=Trueなら既存DBを作り直す"""

    db_path = tmp_path / "test.sqlite"

    database.init_database(dbname=db_path)

    with sqlite3.connect(db_path) as con:
        con.execute("CREATE TABLE dummy (id INTEGER)")

    database.init_database(
        dbname=db_path,
        reset=True,
    )

    with sqlite3.connect(db_path) as con:
        result = con.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
              AND name = 'dummy'
            """
        ).fetchone()

    assert result is None


def test_write_df_to_db(tmp_path):
    """DataFrameをcensusテーブルへ書き込める"""

    db_path = tmp_path / "test.sqlite"
    database.init_database(dbname=db_path)

    df = pd.DataFrame(
        {
            "area_name": ["大阪府"],
            "total_population": [8800000],
            "observation_date": ["2020-10-01"],
        }
    )

    count = database.write_df_to_db(
        df,
        database.TBL_CENSUS,
        dbname=db_path,
    )

    assert count == 1

    with sqlite3.connect(db_path) as con:
        result = con.execute(
            """
            SELECT area_name, total_population, observation_date
            FROM census
            """
        ).fetchone()

    assert result == ("大阪府", 8800000, "2020-10-01")
    

def test_write_duplicate_row(tmp_path):
    db_path = tmp_path / "test.sqlite"
    database.init_database(dbname=db_path)

    df = pd.DataFrame(
        {
            "area_name": ["大阪府"],
            "total_population": [8800000],
            "observation_date": ["2020-10-01"],
        }
    )

    database.write_df_to_db(
        df,
        database.TBL_CENSUS,
        dbname=db_path,
    )

    with pytest.raises(pd.errors.DatabaseError):
        database.write_df_to_db(
            df,
            database.TBL_CENSUS,
            dbname=db_path,
        )
