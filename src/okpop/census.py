from pathlib import Path

import pandas as pd

from okpop import area


def read_census2020(file):
    """国勢調査2020(令和2年)ファイルの読み込み"""

    file = Path(file)

    df = pd.read_excel(
            file, 
            skiprows=5,
            sheet_name="表9-1", 
            usecols="B:L",
            header=None)

    # 人口列が数字のものだけをえらびたい
    pop = pd.to_numeric(df[2],errors="coerce")
    df = df.loc[pop.notna()]  # pyright: ignore[reportAttributeAccessIssue]

    # 列の名前と型
    df.columns = CENSUS_COLUMNS
    df = df.astype(CENSUS_DTYPES)

    # 地域名は並びを確認済み
    df["area_name"] = area.AREA_NAME_V002_COL_NAME 

    # 日付列を付ける
    df["observation_date"] = pd.Timestamp("2020-10-01")

    return df


# 列名
CENSUS_COLUMNS = [
    "area_name",
    "total_population",
    "male_population",
    "female_population",

    "population_change",
    "population_change_rate",

    "total_households",
    "general_households",
    "general_household_members",
    "general_household_size",
    "population_density",
]

# 対応する型
CENSUS_DTYPES = {
    "area_name": "string",
    "total_population": "Int64",
    "male_population": "Int64",
    "female_population": "Int64",
    "population_change": "Int64",
    "population_change_rate": "Float64",
    "total_households": "Int64",
    "general_households": "Int64",
    "general_household_members": "Int64",
    "general_household_size": "Float64",
    "population_density": "Float64",
}


