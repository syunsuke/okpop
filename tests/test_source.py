import pytest

from okpop.source import (
    SOURCES,
    Source,
)


def test_source():
    source = Source(
        datatype="suikei",
        url="https://example.com/",
        patterns=[r"jk20\d{6}.*\.xlsx"],
        directory="suikei",
        start_date="2020-11-01",
    )

    assert source.datatype == "suikei"
    assert source.url == "https://example.com/"
    assert source.patterns == [r"jk20\d{6}.*\.xlsx"]
    assert source.directory == "suikei"
    assert source.start_date == "2020-11-01"
    assert source.end_date is None

def test_source_with_end_date():
    source = Source(
        datatype="suikei",
        url="https://example.com/",
        patterns=[r"jk20\d{6}.*\.xlsx"],
        directory="suikei",
        start_date="2015-11-01",
        end_date="2020-10-01",
    )

    assert source.start_date == "2015-11-01"
    assert source.end_date == "2020-10-01"


def test_source_is_frozen():
    source = Source(
        datatype="suikei",
        url="https://example.com/",
        patterns=[r"jk20\d{6}.*\.xlsx"],
        directory="suikei",
        start_date="2020-11-01",
    )

    with pytest.raises(AttributeError):
        source.url = "https://other.example.com/"
        


def test_source_keys():
    assert set(SOURCES) == {
        "census_2020",
        "suikei_current",
        "suikei_archive",
        "kubun_current",
        "kubun_archive",
        "hosei",
    }

def test_census_2020():
    source = SOURCES["census_2020"]

    assert source.datatype == "census"
    assert source.url == (
        "https://www.pref.osaka.lg.jp/"
        "o040090/toukei/top_portal/kokucho.html"
    )
    assert source.patterns == [
        r"r2kokutyo_osakahu_kakuhou_syousai\.xlsx",
    ]
    assert source.directory == "census"
    assert source.start_date == "2020-10-01"
    assert source.end_date == "2020-10-01"

def test_suikei_current():
    source = SOURCES["suikei_current"]

    assert source.datatype == "suikei"
    assert source.directory == "suikei"
    assert source.patterns == [
        r"jk20\d{6}.*\.xlsx",
    ]
    assert source.start_date == "2020-11-01"
    assert source.end_date is None


def test_suikei_archive():
    source = SOURCES["suikei_archive"]

    assert source.datatype == "suikei"
    assert source.directory == "suikei"
    assert source.patterns == [
        r"jk20\d{6}.*\.xlsx",
        r"jtsukikakuhou20\d{4}.*\.xlsx",
    ]
    assert source.start_date == "2015-11-01"
    assert source.end_date == "2020-09-01"


def test_kubun_current():
    source = SOURCES["kubun_current"]

    assert source.datatype == "kubun"
    assert source.directory == "kubun"
    assert source.patterns == [
        r".*5sai.*\.xlsx",
    ]
    assert source.start_date == "2020-10-01"
    assert source.end_date is None


def test_kubun_archive():
    source = SOURCES["kubun_archive"]

    assert source.datatype == "kubun"
    assert source.directory == "kubun"
    assert source.patterns == [
        r".*5sai.*\.xlsx",
    ]
    assert source.start_date == "2016-11-01"
    assert source.end_date == "2020-09-01"


def test_hosei():
    source = SOURCES["hosei"]

    assert source.datatype == "hosei"
    assert source.directory == "hosei"
    assert source.patterns == [
        r"hosei20\d{4}_\d{2}.*\.xlsx",
    ]
    assert source.start_date == "2010-11-01"
    assert source.end_date == "2020-09-01"

def test_source_urls():
    for source in SOURCES.values():
        assert source.url.startswith(
            "https://www.pref.osaka.lg.jp/"
        )
