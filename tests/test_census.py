from pathlib import Path

import pandas as pd

from okpop import area, census

CENSUS_FILE = (
    Path(__file__).parent
    / "fixtures"
    / "census"
    / "r2kokutyo_osakahu_kakuhou_syousai.xlsx"
)


def test_read_census2020():
    df = census.read_census2020(CENSUS_FILE)

    # DataFrameが返る
    assert isinstance(df, pd.DataFrame)

    # 地域数
    assert len(df) == area.AREA_LEN_V002

    # 列
    assert list(df.columns) == [
        *census.CENSUS_COLUMNS,
        "observation_date",
    ]

    # 地域名
    assert list(df["area_name"]) == area.AREA_NAME_V002_COL_NAME

    # 調査日
    assert (df["observation_date"] == pd.Timestamp("2020-10-01")).all()


def test_read_census2020_values():
    df = census.read_census2020(CENSUS_FILE)

    osaka = df.loc[
        df["area_name"] == "大阪府全市町村"
    ].iloc[0]

    assert osaka["total_population"] == 8_837_685
    assert osaka["male_population"] == 4_235_956
    assert osaka["female_population"] == 4_601_729
