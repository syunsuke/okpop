from pathlib import Path

import pandas as pd

from okpop import area, utildate


def read_suikei(file):
    """suikeiファイルを読む"""

    f = Path(file)
    rowdf = pd.read_excel(f, header=None)

    # 時刻の確保
    timestamp = utildate.wareki_to_timestamp(
                    rowdf.iloc[0,2]
                )
    
    # 年変動項目のありなし場合わけ
    match rowdf.shape[1]:
        case 13:
            # 年変動なし
            df = read_suikei_12(rowdf)

        case 18:
            # 年変動あり
            df = read_suikei_17(rowdf)

        case _:
            raise ValueError(
                  f"Unknown col count: {rowdf.shape[1]}"
                  )

    # 人口の無い行を消す
    df = df.dropna(subset=["total_population"])

    # 地名処理
    ## area_nameの空白を削除
    df["area_name"] = (
        df["area_name"]
        .str
        .replace(r"\s+", "", regex=True)
    )

    ## 地域名を検証してDB用名称へ変換
    df = area.normalize_area_name_col(df)

    # 時刻データ列をつける
    df["observation_date"] = timestamp

    return df

def read_suikei_12(df):
    ans = df.iloc[7:,1:].copy()
    ans.columns = SUIKEI_12_COLUMNS

    # 型
    ## 地域名の型str
    ans["area_name"] = ans["area_name"].astype("string")

    ## Int64にする列
    int_target = SUIKEI_12_COLUMNS[1:10]
    ans[int_target] = (
        ans[int_target]
        .apply(pd.to_numeric, errors="coerce")
        .astype("Int64")
    )

    ## Float64にする列
    fl_target = SUIKEI_12_COLUMNS[10:]
    ans[fl_target] = (
        ans[fl_target]
        .apply(pd.to_numeric, errors="coerce")
        .astype("Float64")
    )

    return ans

def read_suikei_17(df):
    ans = df.iloc[7:,1:].copy()
    ans.columns = SUIKEI_17_COLUMNS

    # 型
    ## 地域名の型str
    ans["area_name"] = ans["area_name"].astype("string")

    ## Int64にする列
    int_target = SUIKEI_17_COLUMNS[1:15]
    ans[int_target] = (
        ans[int_target]
        .apply(pd.to_numeric, errors="coerce")
        .astype("Int64")
    )

    ## Float64にする列
    fl_target = SUIKEI_17_COLUMNS[15:]
    ans[fl_target] = (
        ans[fl_target]
        .apply(pd.to_numeric, errors="coerce")
        .astype("Float64")
    )

    return ans










######################################################
# 列名
######################################################
SUIKEI_12_COLUMNS = [
    "area_name",                   # 地域名
    "total_households",            # 総世帯数
    "total_population",            # 総人口
    "male_population",             # 男性人口
    "female_population",           # 女性人口

    "monthly_population_change",   # 1か月間の人口増減
    "monthly_natural_change",      # 1か月間の自然増減
    "births_monthly",              # 出生数
    "deaths_monthly",              # 死亡数
    "monthly_net_migration",       # 1か月間の社会増減

    "total_household_size",        # 1世帯当たり人口
    "population_density",          # 人口密度
]

SUIKEI_17_COLUMNS = [
    "area_name",
    "total_households",
    "total_population",
    "male_population",
    "female_population",

    # 1年間の増減
    "annual_population_change",
    "annual_natural_change",
    "births_per_year",
    "deaths_per_year",
    "annual_net_migration",

    # 1か月間の増減
    "monthly_population_change",
    "monthly_natural_change",
    "births_monthly",
    "deaths_monthly",
    "monthly_net_migration",

    # その他
    "total_household_size",
    "population_density",
]

