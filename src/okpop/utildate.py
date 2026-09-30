import datetime
import re
import unicodedata

import pandas as pd


######################################################
# 和暦文字列から日付を得る
######################################################
def wareki_to_timestamp(text, day = True):

    # セルに直接日時型の値がある場合がある
    # 見た目が和暦なので関数処理にいれる
    if isinstance(text, datetime.datetime):
        return pd.Timestamp(text)

    # 全角数字 → 半角数字など
    text = unicodedata.normalize("NFKC", text)

    if day:
        match = re.search(
            r"(令和|平成|昭和)(元|\d+)年(\d+)月(\d+)日",
            text
        )
        if match is None:
            return None

        era, year, month, day = match.groups()

    else:
        match = re.search(
            r"(令和|平成|昭和)(元|\d+)年(\d+)月",
            text
        )
        if match is None:
            return None

        era, year, month = match.groups()
        day = 1

    year = 1 if year == "元" else int(year)

    offsets = {
        "令和": 2018,
        "平成": 1988,
        "昭和": 1925,
    }

    western_year = offsets[era] + year

    return pd.Timestamp(
        year=western_year,
        month=int(month),
        day=int(day),
    )


