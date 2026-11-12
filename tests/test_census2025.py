from pathlib import Path

import pandas as pd

from okpop import area, census2025, filecheck, importer


NAME = (
    'r7census_osaka_kakutei_'
    'gaiyou_data.xlsx'
)


def test_new_census_file_recognized():
    assert filecheck.guess_datatype(NAME) == 'census'


def test_census2025_import_route(monkeypatch):
    expected = pd.DataFrame({
        'observation_date': [
            pd.Timestamp('2025-10-01')
        ]
    })
    monkeypatch.setattr(
        census2025,
        'read_census2025',
        lambda _: expected,
    )
    result = importer.read_file(Path(NAME))
    assert result.table == 'census'
    assert result.dataframe is expected


def test_census2025_86_areas(monkeypatch):
    # The published 付表 has two separated blocks.
    raw = pd.DataFrame(
        [[None] * 9 for _ in range(114)]
    )
    names = list(area.AREA_NAME_V002_CHECK)
    for i in list(range(13, 37)) + list(
        range(38, 45)
    ):
        names[i] = '（' + names[i] + '）'
    positions = (
        list(range(4, 47))
        + list(range(65, 114))
    )
    for name, row in zip(
        names,
        [r for r in positions if r not in {
            5, 7, 11, 15, 17, 21
        }],
    ):
        raw.iloc[row, 1:9] = [
            name, 200, 199, 500,
            240, 260, 10, 2.04,
        ]
    monkeypatch.setattr(
        census2025.pd,
        'read_excel',
        lambda *args, **kwargs: raw,
    )
    df = census2025.read_census2025('dummy.xlsx')
    assert len(df) == 86
    assert df.area_name.is_unique
    assert df.observation_date.nunique() == 1
    assert df.area_name.iloc[0] == (
        '大阪府全市町村'
    )
    assert df.area_name.iloc[13] == (
        '大阪市都島区'
    )
    assert df.area_name.iloc[38] == '堺市堺区'
    assert df.general_household_members.isna().all()
