from pathlib import Path

import pandas as pd

from okpop import area, utildate


def read_kubun(file):

    f = Path(file)
    rowdata = pd.read_excel(f, header=None)

    df = None

    if rowdata.shape[1] == 22:
        df = read_kubun_95(rowdata)
        version = "v002"

    elif rowdata.shape[1] == 20:
        df = read_kubun_85(rowdata)
        version = "v001"

    else:
        raise ValueError(
                "does not match with any known format."
                )

    return  df, version

###################################################
# database用DFに変換する関数
# 置き場は後で考える
###################################################
def to_db_dataframe(dfs):
    """性別ごとのDataFrameをDB書き込み形式に変換する。"""

    frames = []

    for sex, df in dfs.items():
        tmp = df.copy()
        tmp["sex"] = sex
        frames.append(tmp)

    return pd.concat(frames, ignore_index=True)

###################################################
# サブルーチン
###################################################

# 95歳まで区分のエクセルファイルを読む
# 3つのDataFrameを辞書で返す
# 全体total、男male、女female
def read_kubun_95(df):
    """5歳区分の新しいエクセルファイルを読む"""

    # 読み込み
    rowdata = df

    # 日付データの確保
    datestamp = utildate.wareki_to_timestamp(
                    rowdata.iloc[1,0]
                    )

    # 必要部分の切り出し
    df = rowdata.iloc[3:,0:22].copy()
    df.columns = SUIKEI_5SAI_22_COLUMNS

    # 地域名の型str
    df["area_name"] = df["area_name"].astype("string")

    # 年齢関係の列すべての型Int64
    age_columns = SUIKEI_5SAI_22_COLUMNS[1:]
    df[age_columns] = (
        df[age_columns]
        .apply(pd.to_numeric, errors="coerce")
        .astype("Int64")
    )

    # area_nameの空白を削除
    df["area_name"] = (
        df["area_name"]
        .str
        .replace(r"\s+", "", regex=True)
    )

    # 人口の無い行を消す
    df = df.dropna(subset=["age_total"])


    df["observation_date"] = datestamp

    t,m,f = _sub_div_df(df, area.AREA_LEN_V002)

    return {"total": t,
            "male": m,
            "female": f}


# 85歳まで区分のエクセルファイルを読む
# 3つのDataFrameを辞書で返す
# 全体total、男male、女female
def read_kubun_85(df):

    # 読み込み
    rowdata = df

    # 日付データの確保
    datestamp = utildate.wareki_to_timestamp(
                    rowdata.iloc[1,0]
                    )

    # 必要部分の切り出し
    df = rowdata.iloc[3:, 0:20].copy()
    df.columns = SUIKEI_5SAI_20_COLUMNS

    # 地域名の型str
    df["area_name"] = df["area_name"].astype("string")

    # 年齢関係の列すべての型Int64
    age_columns = SUIKEI_5SAI_20_COLUMNS[1:]
    df[age_columns] = (
        df[age_columns]
        .apply(pd.to_numeric, errors="coerce")
        .astype("Int64")
    )

    # area_nameの空白を削除
    df["area_name"] = (
        df["area_name"]
        .str
        .replace(r"\s+", "", regex=True)
    )

    # 人口の無い行を消す
    df = df.dropna(subset=["age_total"])

    # 日付行を追加
    df["observation_date"] = datestamp

    t,m,f = _sub_div_df(df, area.AREA_LEN_V001)

    return {"total": t,
            "male": m,
            "female": f}

# DFを3分割するサブルーチン
def _sub_div_df(df, area_count):
    alen = area_count
    offset = {"total":0,
              "male":alen,
              "female":alen*2}

    # 全体データ
    tdf = (df
           .iloc[offset["total"]:offset["total"]+alen]
           .copy()
          )

    # 男性データ
    mdf = (df
           .iloc[offset["male"]:offset["male"]+alen]
           .copy()
          )

    # 女性データ
    fdf = (df
           .iloc[offset["female"]:offset["female"]+alen]
           .copy()
           )

    # 地域名を検証してDB用名称へ変換
    tdf = area.normalize_area_name_col(tdf)
    mdf = area.normalize_area_name_col(mdf)
    fdf = area.normalize_area_name_col(fdf)

    return (tdf, mdf, fdf)



###########################################################
### 列名
###########################################################

SUIKEI_5SAI_22_COLUMNS = [
    "area_name",
    "age_total",
    "age_00_04",
    "age_05_09",
    "age_10_14",
    "age_15_19",
    "age_20_24",
    "age_25_29",
    "age_30_34",
    "age_35_39",
    "age_40_44",
    "age_45_49",
    "age_50_54",
    "age_55_59",
    "age_60_64",
    "age_65_69",
    "age_70_74",
    "age_75_79",
    "age_80_84",
    "age_85_89",
    "age_90_94",
    "age_95plus",
]

SUIKEI_5SAI_20_COLUMNS = [
    "area_name",
    "age_total",
    "age_00_04",
    "age_05_09",
    "age_10_14",
    "age_15_19",
    "age_20_24",
    "age_25_29",
    "age_30_34",
    "age_35_39",
    "age_40_44",
    "age_45_49",
    "age_50_54",
    "age_55_59",
    "age_60_64",
    "age_65_69",
    "age_70_74",
    "age_75_79",
    "age_80_84",
    "age_85plus",
]


###########################################################
# テスト用
###########################################################
if __name__ == "__main__":
    file_95 = "report/kubun5sai/202608suikei5sai.xlsx"

    #df = read_kubun_95(target_file)
    df = read_kubun(file_95)

    print(df)
