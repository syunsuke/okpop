import pandas as pd
import pytest

from okpop import area

# =======================
# check_area_order
# =======================

def test_check_area_order():
    target = ["大阪府", "大阪市", "枚方市"]
    correct = ["大阪府", "大阪市", "枚方市"]

    area.check_area_order(target, correct)


def test_check_area_order_wrong_length():
    target = ["大阪府", "大阪市"]
    correct = ["大阪府", "大阪市", "枚方市"]

    with pytest.raises(ValueError):
        area.check_area_order(target, correct)


def test_check_area_order_wrong_name():
    target = ["大阪府", "大阪市", "寝屋川市"]
    correct = ["大阪府", "大阪市", "枚方市"]

    with pytest.raises(ValueError):
        area.check_area_order(target, correct)


# =======================
# V001 / V002 の定義
# =======================

def test_area_v001_definition():
    assert area.AREA_LEN_V001 == 93
    assert len(area.AREA_NAME_V001_CHECK) == 93
    assert len(area.AREA_NAME_V001_COL_NAME) == 93


def test_area_v002_definition():
    assert area.AREA_LEN_V002 == 86
    assert len(area.AREA_NAME_V002_CHECK) == 86
    assert len(area.AREA_NAME_V002_COL_NAME) == 86


# ========================
# normalize_area_names
# ========================

def test_normalize_area_names_v001():
    result = area.normalize_area_names(
        area.AREA_NAME_V001_CHECK
    )

    assert result == area.AREA_NAME_V001_COL_NAME


def test_normalize_area_names_v002():
    result = area.normalize_area_names(
        area.AREA_NAME_V002_CHECK
    )

    assert result == area.AREA_NAME_V002_COL_NAME


def test_normalize_area_names_unknown_format():
    with pytest.raises(ValueError):
        area.normalize_area_names(
            ["大阪府", "枚方市"]
        )


# ============================
# normalize_area_name_col
# ============================

def test_normalize_area_name_col_v002():
    df = pd.DataFrame({
        "area_name": area.AREA_NAME_V002_CHECK
    })

    result = area.normalize_area_name_col(df)

    assert list(result["area_name"]) == area.AREA_NAME_V002_COL_NAME


def test_normalize_area_name_col_wrong_order():
    names = area.AREA_NAME_V002_CHECK.copy()

    names[0], names[1] = names[1], names[0]

    df = pd.DataFrame({
        "area_name": names
    })

    with pytest.raises(ValueError):
        area.normalize_area_name_col(df)
