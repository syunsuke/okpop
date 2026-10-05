import sqlite3

from okpop.app import actions


def test_create_reports(
    monkeypatch,
    tmp_path,
):
    expected_archive = (
        tmp_path / "okpop_report.zip"
    )

    called = {}

    def fake_create_report_archive(
        output_dir,
        template_path,
        db_path,
        end_date,
    ):
        called["output_dir"] = output_dir
        called["template_path"] = template_path
        called["db_path"] = db_path
        called["end_date"] = end_date

        return expected_archive

    monkeypatch.setattr(
        actions.report,
        "create_report_archive",
        fake_create_report_archive,
    )

    result = actions.create_reports()

    assert result == expected_archive

    assert called["output_dir"] == (
        actions.OUTPUT_DIR
    )

    assert called["template_path"] == (
        actions.TEMPLATE_PATH
    )

    assert called["db_path"] == (
        actions.DB_PATH
    )

    assert called["end_date"] is None

def test_get_database_status(
    monkeypatch,
    tmp_path,
):
    db_path = tmp_path / "test.sqlite"

    with sqlite3.connect(db_path) as con:
        for table in [
            "census",
            "suikei",
            "hosei",
        ]:
            con.execute(
                f"""
                CREATE TABLE {table} (
                    observation_date TEXT
                )
                """
            )

        con.executemany(
            """
            INSERT INTO census
            VALUES (?)
            """,
            [
                ("2020-10-01",),
                ("2025-10-01",),
            ],
        )

        con.executemany(
            """
            INSERT INTO suikei
            VALUES (?)
            """,
            [
                ("2026-08-01",),
                ("2026-09-01",),
            ],
        )

        con.execute(
            """
            INSERT INTO hosei
            VALUES (?)
            """,
            ("2025-09-01",),
        )

    monkeypatch.setattr(
        actions,
        "DB_PATH",
        db_path,
    )

    result = actions.get_database_status()

    assert result == {
        "census": "2025-10-01",
        "suikei": "2026-09-01",
        "hosei": "2025-09-01",
    }

def test_update_database(
    monkeypatch,
    tmp_path,
):
    fetched = []
    imported = []

    raw_dir = tmp_path / "raw"
    db_path = tmp_path / "test.sqlite"

    db_path.touch()

    def fake_fetch_datatype(
        datatype,
        raw_dir,
    ):
        fetched.append(
            (datatype, raw_dir)
        )

    def fake_import_directory(
        directory,
        db_path,
    ):
        imported.append(
            (directory, db_path)
        )

    monkeypatch.setattr(
        actions,
        "RAW_DIR",
        raw_dir,
    )

    monkeypatch.setattr(
        actions,
        "DB_PATH",
        db_path,
    )

    monkeypatch.setattr(
        actions.fetch,
        "fetch_datatype",
        fake_fetch_datatype,
    )

    monkeypatch.setattr(
        actions.importer,
        "import_directory",
        fake_import_directory,
    )

    actions.update_database()

    assert [
        datatype
        for datatype, _ in fetched
    ] == [
        "census",
        "suikei",
        "hosei",
        "kubun",
    ]

    assert [
        directory.name
        for directory, _ in imported
    ] == [
        "census",
        "suikei",
        "hosei",
        "kubun",
    ]
