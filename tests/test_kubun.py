from pathlib import Path

import pandas as pd

from okpop import area, kubun

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "kubun"

V001_FILE = FIXTURE_DIR / "201801suikei5sai.xlsx"
V002_FILE = FIXTURE_DIR / "202608suikei5sai.xlsx"


# --------------------------------------------------
# V001
# 20列・85歳以上
# --------------------------------------------------

def test_read_kubun_v001():
    dfs, version = kubun.read_kubun(V001_FILE)

    assert version == "v001"

    assert set(dfs.keys()) == {
        "total",
        "male",
        "female",
    }

    assert len(dfs["total"]) == area.AREA_LEN_V001
    assert len(dfs["male"]) == area.AREA_LEN_V001
    assert len(dfs["female"]) == area.AREA_LEN_V001


def test_read_kubun_v001_columns():
    dfs, _ = kubun.read_kubun(V001_FILE)

    expected_columns = [
        *kubun.SUIKEI_5SAI_20_COLUMNS,
        "observation_date",
    ]

    assert list(dfs["total"].columns) == expected_columns
    assert list(dfs["male"].columns) == expected_columns
    assert list(dfs["female"].columns) == expected_columns


def test_read_kubun_v001_area():
    dfs, _ = kubun.read_kubun(V001_FILE)

    assert list(dfs["total"]["area_name"]) == area.AREA_NAME_V001_COL_NAME
    assert list(dfs["male"]["area_name"]) == area.AREA_NAME_V001_COL_NAME
    assert list(dfs["female"]["area_name"]) == area.AREA_NAME_V001_COL_NAME


def test_read_kubun_v001_date():
    dfs, _ = kubun.read_kubun(V001_FILE)

    expected = pd.Timestamp("2018-01-01")

    for df in dfs.values():
        assert (df["observation_date"] == expected).all()


def test_read_kubun_v001_values():
    dfs, _ = kubun.read_kubun(V001_FILE)

    total = dfs["total"].loc[
        dfs["total"]["area_name"] == "大阪府全市町村"
    ].iloc[0]

    male = dfs["male"].loc[
        dfs["male"]["area_name"] == "大阪府全市町村"
    ].iloc[0]

    female = dfs["female"].loc[
        dfs["female"]["area_name"] == "大阪府全市町村"
    ].iloc[0]

    # 総数
    assert total["age_total"] == 8_830_955
    assert male["age_total"] == 4_245_652
    assert female["age_total"] == 4_585_303

    # 若年層
    assert total["age_00_04"] == 342_095
    assert male["age_00_04"] == 174_484
    assert female["age_00_04"] == 167_611

    # V001最後の年齢階級
    assert total["age_85plus"] == 305_517
    assert male["age_85plus"] == 93_160
    assert female["age_85plus"] == 212_356

    # 男女計の整合性
    assert male["age_total"] + female["age_total"] == total["age_total"]


# --------------------------------------------------
# V002
# 22列・95歳以上
# --------------------------------------------------

def test_read_kubun_v002():
    dfs, version = kubun.read_kubun(V002_FILE)

    assert version == "v002"

    assert set(dfs.keys()) == {
        "total",
        "male",
        "female",
    }

    assert len(dfs["total"]) == area.AREA_LEN_V002
    assert len(dfs["male"]) == area.AREA_LEN_V002
    assert len(dfs["female"]) == area.AREA_LEN_V002


def test_read_kubun_v002_columns():
    dfs, _ = kubun.read_kubun(V002_FILE)

    expected_columns = [
        *kubun.SUIKEI_5SAI_22_COLUMNS,
        "observation_date",
    ]

    assert list(dfs["total"].columns) == expected_columns
    assert list(dfs["male"].columns) == expected_columns
    assert list(dfs["female"].columns) == expected_columns


def test_read_kubun_v002_area():
    dfs, _ = kubun.read_kubun(V002_FILE)

    assert list(dfs["total"]["area_name"]) == area.AREA_NAME_V002_COL_NAME
    assert list(dfs["male"]["area_name"]) == area.AREA_NAME_V002_COL_NAME
    assert list(dfs["female"]["area_name"]) == area.AREA_NAME_V002_COL_NAME


def test_read_kubun_v002_date():
    dfs, _ = kubun.read_kubun(V002_FILE)

    expected = pd.Timestamp("2026-08-01")

    for df in dfs.values():
        assert (df["observation_date"] == expected).all()


def test_read_kubun_v002_values():
    dfs, _ = kubun.read_kubun(V002_FILE)

    total = dfs["total"].loc[
        dfs["total"]["area_name"] == "大阪府全市町村"
    ].iloc[0]

    male = dfs["male"].loc[
        dfs["male"]["area_name"] == "大阪府全市町村"
    ].iloc[0]

    female = dfs["female"].loc[
        dfs["female"]["area_name"] == "大阪府全市町村"
    ].iloc[0]

    # 総数
    assert total["age_total"] == 8_758_525
    assert male["age_total"] == 4_175_506
    assert female["age_total"] == 4_583_019

    # 若年層
    assert total["age_00_04"] == 280_466
    assert male["age_00_04"] == 143_373
    assert female["age_00_04"] == 137_093

    # V002では高齢層が細分化されている
    assert total["age_85_89"] == 289_493
    assert total["age_90_94"] == 137_693
    assert total["age_95plus"] == 47_105

    assert male["age_95plus"] == 9_682
    assert female["age_95plus"] == 37_423

    # 男女計の整合性
    assert male["age_total"] + female["age_total"] == total["age_total"]



# --------------------------------------------------
# DB用DataFrameへの変換
# --------------------------------------------------

def test_to_db_dataframe_v001():
    dfs, version = kubun.read_kubun(V001_FILE)

    df = kubun.to_db_dataframe(dfs)

    assert version == "v001"

    # 93地域 × 3種類
    assert len(df) == area.AREA_LEN_V001 * 3

    assert set(df["sex"]) == {
        "total",
        "male",
        "female",
    }

    # 元のDataFrameにはsex列を追加しない
    assert "sex" not in dfs["total"].columns
    assert "sex" not in dfs["male"].columns
    assert "sex" not in dfs["female"].columns


def test_to_db_dataframe_v002():
    dfs, version = kubun.read_kubun(V002_FILE)

    df = kubun.to_db_dataframe(dfs)

    assert version == "v002"

    # 86地域 × 3種類
    assert len(df) == area.AREA_LEN_V002 * 3

    assert set(df["sex"]) == {
        "total",
        "male",
        "female",
    }

    # 元のDataFrameにはsex列を追加しない
    assert "sex" not in dfs["total"].columns
    assert "sex" not in dfs["male"].columns
    assert "sex" not in dfs["female"].columns


def test_to_db_dataframe_values():
    dfs, _ = kubun.read_kubun(V002_FILE)

    df = kubun.to_db_dataframe(dfs)

    osaka = df.loc[
        (df["area_name"] == "大阪府全市町村")
        & (df["sex"] == "male")
    ].iloc[0]

    assert osaka["observation_date"] == pd.Timestamp("2026-08-01")
    assert osaka["age_total"] == 4_175_506
    assert osaka["age_00_04"] == 143_373
    assert osaka["age_95plus"] == 9_682

