import shutil
import sqlite3
from pathlib import Path

import pandas as pd
import pytest

from okpop import database, importer

FIXTURES = Path("tests/fixtures")


def test_import_file_suikei(tmp_path):
    db_path = tmp_path / "test.sqlite"

    database.init_database(db_path)

    file = (
        FIXTURES
        / "suikei"
        / "kakutei_jk20211101.xlsx"
    )

    importer.import_file(
        file=file,
        db_path=db_path,
    )

    with sqlite3.connect(db_path) as con:
        row = con.execute(
            """
            SELECT
                total_population,
                male_population,
                female_population,
                observation_date
            FROM suikei
            WHERE area_name = '大阪府全市町村'
            """
        ).fetchone()

    assert row is not None
    assert row[0] == 8_804_619
    assert row[1] == 4_215_019
    assert row[2] == 4_589_600
    assert row[3] == "2021-11-01 00:00:00"

def test_read_census():
    file = (
        FIXTURES
        / "census"
        / "r2kokutyo_osakahu_kakuhou_syousai.xlsx"
    )

    result = importer.read_file(file)


    assert isinstance(result, importer.ImportData)
    assert isinstance(result.dataframe, pd.DataFrame)
    assert result.table == "census"
    assert not result.dataframe.empty


def test_read_suikei():
    file = (
        FIXTURES
        / "suikei"
        / "kakutei_jk20211101.xlsx"
    )

    result = importer.read_file(file)

    assert result.table == "suikei"
    assert not result.dataframe.empty


def test_read_hosei():
    file = (
        FIXTURES
        / "hosei"
        / "hosei201511_12.xlsx"
    )

    result = importer.read_file(file)

    assert result.table == "hosei"
    assert not result.dataframe.empty


def test_read_kubun_v001():
    file = (
        FIXTURES
        / "kubun"
        / "201801suikei5sai.xlsx"
    )

    result = importer.read_file(file)

    assert result.table == "population_age5_v001"
    assert not result.dataframe.empty
    assert "sex" in result.dataframe.columns


def test_read_kubun_v002():
    file = (
        FIXTURES
        / "kubun"
        / "202608suikei5sai.xlsx"
    )

    result = importer.read_file(file)

    assert result.table == "population_age5_v002"
    assert not result.dataframe.empty
    assert "sex" in result.dataframe.columns


def test_read_unknown():
    with pytest.raises(ValueError):
        importer.read_file("unknown.xlsx")


def test_is_imported(tmp_path):
    db_path = tmp_path / "test.sqlite"

    database.init_database(db_path)

    file = (
        FIXTURES
        / "suikei"
        / "kakutei_jk20211101.xlsx"
    )

    # Excelを読む
    data = importer.read_file(file)

    # まだDBには入れていない
    assert importer.is_imported(
        data,
        db_path,
    ) is False

    # DBへ書き込む
    importer.import_data(
        data,
        db_path,
    )

    # 今度はDBに存在する
    assert importer.is_imported(
        data,
        db_path,
    ) is True


def test_import_directory(tmp_path):
    db_path = tmp_path / "test.sqlite"
    input_dir = tmp_path / "input"
    input_dir.mkdir()

    database.init_database(db_path)

    # テスト用ディレクトリへ実Excelを2つコピー
    files = [
        (
            FIXTURES
            / "suikei"
            / "kakutei_jk20201101.xlsx"
        ),
        (
            FIXTURES
            / "suikei"
            / "kakutei_jk20211101.xlsx"
        ),
    ]

    for file in files:
        shutil.copy(file, input_dir / file.name)

    # 1回目
    importer.import_directory(
        directory=input_dir,
        db_path=db_path,
    )

    with sqlite3.connect(db_path) as con:
        count1 = con.execute(
            "SELECT COUNT(*) FROM suikei"
        ).fetchone()[0]

    # 2回目
    importer.import_directory(
        directory=input_dir,
        db_path=db_path,
    )

    with sqlite3.connect(db_path) as con:
        count2 = con.execute(
            "SELECT COUNT(*) FROM suikei"
        ).fetchone()[0]

    assert count1 > 0
    assert count2 == count1
