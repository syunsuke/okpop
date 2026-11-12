"""2025年国勢調査・概要データの付表を読む。"""

from pathlib import Path

import pandas as pd

from okpop import area


SOURCE_COLUMNS = [
    "area_name",
    "total_households",
    "general_households",
    "total_population",
    "male_population",
    "female_population",
    "population_change",
    "population_change_rate",
]

INTEGER_COLUMNS = [
    "total_households",
    "general_households",
    "total_population",
    "male_population",
    "female_population",
    "population_change",
]


def read_census2025(file: str | Path):
    """2025年の付表から地域別人口等を取得。"""
    raw = pd.read_excel(
        file,
        sheet_name="付表",
        header=None,
    )

    # 表は途中に説明欄と再掲見出しがある。
    # 位置を限定して、説明欄を混入させない。
    first = raw.iloc[4:47, 1:9]
    second = raw.iloc[65:114, 1:9]
    df = pd.concat([first, second]).copy()
    df.columns = SOURCE_COLUMNS

    df = df.loc[
        pd.to_numeric(
            df["total_population"],
            errors="coerce",
        ).notna()
    ].reset_index(drop=True)

    # 86地域の順序を必ず照合する。
    # 大阪市と堺市の同名区を取り違えない。
    df["area_name"] = (
        df["area_name"]
        .astype("string")
        .str.replace(
            r"\s+",
            "",
            regex=True,
        )
        .str.replace(
            r"^[（(]|[）)]$",
            "",
            regex=True,
        )
    )

    df = area.normalize_area_name_col(df)

    for col in INTEGER_COLUMNS:
        df[col] = pd.to_numeric(
            df[col], errors="raise"
        ).astype("Int64")

    df["population_change_rate"] = (
        pd.to_numeric(
            df["population_change_rate"],
            errors="raise",
        ).astype("Float64")
    )

    # 2020年用DBにあるが、今回の概要表に
    # 存在しない項目は埋めずにNULLにする。
    df["general_household_members"] = (
        pd.Series(pd.NA, index=df.index)
        .astype("Int64")
    )
    for col in [
        "general_household_size",
        "population_density",
    ]:
        df[col] = (
            pd.Series(pd.NA, index=df.index)
            .astype("Float64")
        )

    if not (
        df["male_population"]
        + df["female_population"]
        == df["total_population"]
    ).all():
        raise ValueError(
            "Male + female population mismatch"
        )

    df["observation_date"] = pd.Timestamp(
        "2025-10-01"
    )

    # censusテーブルの列に合わせる。
    return df[[
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
        "observation_date",
    ]]
