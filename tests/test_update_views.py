import sqlite3

import pytest

from okpop.database import update_views


def test_update_views(tmp_path):
    db_path = tmp_path / "test.sqlite"
    sql_path = tmp_path / "views.sql"

    # テスト用DBを作成
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "CREATE TABLE sample (id INTEGER, name TEXT)"
        )
        conn.execute(
            "INSERT INTO sample VALUES (1, '大阪市')"
        )

    # テスト用のView定義
    sql_path.write_text(
        """
        BEGIN;
    
        DROP VIEW IF EXISTS sample_view;
    
        CREATE VIEW sample_view AS
        SELECT id, name
        FROM sample;
    
        COMMIT;
        """,
        encoding="utf-8",
    )
    # テスト対象の関数を実行
    update_views(
        dbname=db_path,
        views_file=sql_path,
    )

    # Viewが作成されていることを確認
    with sqlite3.connect(db_path) as conn:
        result = conn.execute(
            "SELECT * FROM sample_view"
        ).fetchall()

    assert result == [(1, "大阪市")]


def test_update_views_db_not_found(tmp_path):
    db_path = tmp_path / "not_found.sqlite"
    sql_path = tmp_path / "views.sql"

    sql_path.write_text(
        "CREATE VIEW sample_view AS SELECT 1;",
        encoding="utf-8",
    )

    with pytest.raises(FileNotFoundError):
        update_views(
            dbname=db_path,
            views_file=sql_path,
        )


def test_update_views_rollback(tmp_path):
    db_path = tmp_path / "test.sqlite"
    sql_path = tmp_path / "views.sql"

    # 更新前のView
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "CREATE VIEW sample_view AS SELECT 1 AS value"
        )

    # Viewを削除した直後にエラーを発生させる
    sql_path.write_text(
        """
        BEGIN;

        DROP VIEW sample_view;

        CREATE VIEW sample_view AS
        SELECT FROM;

        COMMIT;
        """,
        encoding="utf-8",
    )

    # SQLエラーが発生すること
    with pytest.raises(sqlite3.OperationalError):
        update_views(
            dbname=db_path,
            views_file=sql_path,
        )

    # 元のViewが残っていること
    with sqlite3.connect(db_path) as conn:
        result = conn.execute(
            "SELECT value FROM sample_view"
        ).fetchone()

    assert result == (1,)
