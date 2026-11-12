import pandas as pd

from okpop import fetch


CENSUS_URL = (
    'https://www.pref.osaka.lg.jp/documents/12026/'
    'r2kokutyo_osakahu_kakuhou_syousai.xlsx'
)


def test_census_2020_fixed_reference_date():
    assert list(fetch._url_dates(
        'census_2020', CENSUS_URL
    )) == [pd.Timestamp('2020-10-01')]


def test_census_2020_link_selection(monkeypatch):
    monkeypatch.setattr(
        fetch.dl, 'urls_from_page',
        lambda *_: [CENSUS_URL],
    )
    assert fetch._source_urls('census_2020') == [
        CENSUS_URL
    ]
    fetch._check_duplicates(
        {'census_2020': [CENSUS_URL]},
        'data/raw',
    )
