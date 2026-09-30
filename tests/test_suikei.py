from pathlib import Path

import pandas as pd

from okpop import area, suikei

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "suikei"

SHORT_FILE = FIXTURE_DIR / "kakutei_jk20201101.xlsx"
LONG_FILE = FIXTURE_DIR / "kakutei_jk20211101.xlsx"


# --------------------------------------------------
# 短い形式（13列）
# --------------------------------------------------

def test_read_suikei_short():
    df = suikei.read_suikei(SHORT_FILE)

    assert isinstance(df, pd.DataFrame)

    # 地域形式はV002
    assert len(df) == area.AREA_LEN_V002
    assert list(df["area_name"]) == area.AREA_NAME_V002_COL_NAME

    # 短い形式の列
    assert list(df.columns) == [
        *suikei.SUIKEI_12_COLUMNS,
        "observation_date",
    ]

    # 観測日
    assert (
        df["observation_date"]
        == pd.Timestamp("2020-11-01")
    ).all()


def test_read_suikei_short_values():
    df = suikei.read_suikei(SHORT_FILE)

    osaka = df.loc[
        df["area_name"] == "大阪府全市町村"
    ].iloc[0]

    assert osaka["total_households"] == 4_136_730
    assert osaka["total_population"] == 8_835_395
    assert osaka["male_population"] == 4_234_627
    assert osaka["female_population"] == 4_600_768

    assert osaka["monthly_population_change"] == -2_290
    assert osaka["monthly_natural_change"] == -2_216
    assert osaka["births_monthly"] == 5_532
    assert osaka["deaths_monthly"] == 7_748
    assert osaka["monthly_net_migration"] == -74

    assert osaka["total_household_size"] == 2.14
    assert osaka["population_density"] == 4_637


# --------------------------------------------------
# 長い形式（18列）
# --------------------------------------------------

def test_read_suikei_long():
    df = suikei.read_suikei(LONG_FILE)

    assert isinstance(df, pd.DataFrame)

    # 地域形式はV002
    assert len(df) == area.AREA_LEN_V002
    assert list(df["area_name"]) == area.AREA_NAME_V002_COL_NAME

    # 長い形式の列
    assert list(df.columns) == [
        *suikei.SUIKEI_17_COLUMNS,
        "observation_date",
    ]

    # 観測日
    assert (
        df["observation_date"]
        == pd.Timestamp("2021-11-01")
    ).all()


def test_read_suikei_long_values():
    df = suikei.read_suikei(LONG_FILE)

    osaka = df.loc[
        df["area_name"] == "大阪府全市町村"
    ].iloc[0]

    assert osaka["total_households"] == 4_164_380
    assert osaka["total_population"] == 8_804_619
    assert osaka["male_population"] == 4_215_019
    assert osaka["female_population"] == 4_589_600

    # 年間増減
    assert osaka["annual_population_change"] == -30_776
    assert osaka["annual_natural_change"] == -37_683
    assert osaka["births_per_year"] == 60_987
    assert osaka["deaths_per_year"] == 98_670
    assert osaka["annual_net_migration"] == 6_907

    # 月間増減
    assert osaka["monthly_population_change"] == -2_660
    assert osaka["monthly_natural_change"] == -2_382
    assert osaka["births_monthly"] == 5_213
    assert osaka["deaths_monthly"] == 7_595
    assert osaka["monthly_net_migration"] == -278

    assert osaka["total_household_size"] == 2.11
    assert osaka["population_density"] == 4_621
