from pathlib import Path

import pandas as pd

from okpop import area, hosei

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "hosei"

FILE_10 = FIXTURE_DIR / "hosei201011_12.xlsx"
FILE_11 = FIXTURE_DIR / "hosei201511_12.xlsx"


def test_read_hosei_10():
    df = hosei.read_hosei(FILE_10)

    assert isinstance(df, pd.DataFrame)

    # 2か月 × V001（93地域）
    assert len(df) == area.AREA_LEN_V001 * 2

    assert list(df.columns) == [
        *hosei.HOSEI_COLUMNS,
        "observation_date",
    ]

    # 2010年11月・12月
    assert set(df["observation_date"]) == {
        pd.Timestamp("2010-11-01"),
        pd.Timestamp("2010-12-01"),
    }


def test_read_hosei_10_area():
    df = hosei.read_hosei(FILE_10)

    november = df.loc[
        df["observation_date"] == pd.Timestamp("2010-11-01")
    ]

    assert list(november["area_name"]) == area.AREA_NAME_V001_COL_NAME


def test_read_hosei_10_values():
    df = hosei.read_hosei(FILE_10)

    osaka = df.loc[
        (df["area_name"] == "大阪府全市町村")
        & (df["observation_date"] == pd.Timestamp("2010-11-01"))
    ].iloc[0]

    assert osaka["total_households"] == 3_833_797
    assert osaka["total_population"] == 8_865_532
    assert osaka["male_population"] == 4_285_666
    assert osaka["female_population"] == 4_579_866


def test_read_hosei_11():
    df = hosei.read_hosei(FILE_11)

    assert isinstance(df, pd.DataFrame)

    # 2か月 × V002（86地域）
    assert len(df) == area.AREA_LEN_V002 * 2

    assert list(df.columns) == [
        *hosei.HOSEI_COLUMNS,
        "observation_date",
    ]

    # 2015年11月・12月
    assert set(df["observation_date"]) == {
        pd.Timestamp("2015-11-01"),
        pd.Timestamp("2015-12-01"),
    }


def test_read_hosei_11_area():
    df = hosei.read_hosei(FILE_11)

    november = df.loc[
        df["observation_date"] == pd.Timestamp("2015-11-01")
    ]

    assert list(november["area_name"]) == area.AREA_NAME_V002_COL_NAME


def test_read_hosei_11_values():
    df = hosei.read_hosei(FILE_11)

    osaka = df.loc[
        (df["area_name"] == "大阪府全市町村")
        & (df["observation_date"] == pd.Timestamp("2015-11-01"))
    ].iloc[0]

    assert osaka["total_households"] == 3_927_733
    assert osaka["total_population"] == 8_841_569
    assert osaka["male_population"] == 4_256_912
    assert osaka["female_population"] == 4_584_657
