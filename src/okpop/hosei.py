from pathlib import Path

import pandas as pd

from okpop import area, utildate


# 補正済データの読み込み
def read_hosei(file):
    f = Path(file)
    xls = pd.ExcelFile(f)
    sheets = xls.sheet_names

    ans = []

    for s in sheets:
        # シートから取り出し
        df = xls.parse(sheet_name=s,
                       header=None)

        # 整形
        df = _read_df(df)

        # 日付列を追加
        df["observation_date"] = (
            utildate.wareki_to_timestamp(s, day=False))

        # 答リストへdfを追加
        ans.append(df)

    return pd.concat(ans, ignore_index=True)

#####################################################
# サブルーチン
#####################################################
def _read_df(df_one):
    """個々のdfを処理する関数"""

    # 列数の違いで処理わけ
    match df_one.shape[1]:
        case 10:
            df = _read_10(df_one)
        case 11:
            df = _read_11(df_one)
        case _:
            raise ValueError(
                f"Unknown col count: {df_one.shape[1]}"
            )

    # 列名を付ける
    df.columns = HOSEI_COLUMNS
    #df = df.astype(HOSEI_DTYPES)

    # 型
    ## 地域名の型str
    df["area_name"] = df["area_name"].astype("string")

    ## 列すべての型Int64
    pop_columns = HOSEI_COLUMNS[1:]
    df[pop_columns] = (
        df[pop_columns]
        .apply(pd.to_numeric, errors="coerce")
        .astype("Int64")
    )

    # 人口の無い行を消す
    df = df.dropna(subset=["total_population"])

    # area_nameの空白を削除
    df["area_name"] = (
        df["area_name"]
        .str
        .replace(r"\s+", "", regex=True)
    )

    # 地域名を検証してDB用名称へ変換
    df = area.normalize_area_name_col(df)

    return df

def _read_10(df):
    left = df.iloc[6:,0:5].copy()
    right = df.iloc[6:,5:].copy()
    left.columns = HOSEI_COLUMNS
    right.columns = HOSEI_COLUMNS

    return pd.concat([left,right])

def _read_11(df):
    left = df.iloc[6:,0:6].copy()
    right = df.iloc[6:,6:].copy()

    left[0] = left[0].fillna("") + left[1].fillna("")
    left = left.drop(columns=[1])

    left.columns = HOSEI_COLUMNS
    right.columns = HOSEI_COLUMNS

    return pd.concat([left,right])

HOSEI_COLUMNS = [
    "area_name",
    "total_households",
    "total_population",
    "male_population",
    "female_population",
]
