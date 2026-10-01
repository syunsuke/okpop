from dataclasses import dataclass


@dataclass(frozen=True)
class Source:
    datatype: str
    url: str
    patterns: list[str]
    directory: str
    start_date: str
    end_date: str | None = None

SOURCES = {
    "suikei_current": Source(
        datatype="suikei",
        url=(
            "https://www.pref.osaka.lg.jp/"
            "o040090/toukei/jinkou/jinkou-xlslist.html"
        ),
        patterns=[
            r"jk20\d{6}.*\.xlsx",
        ],
        directory="suikei",
        start_date="2020-11-01",
        end_date=None,
    ),

    "suikei_archive": Source(
        datatype="suikei",
        url=(
            "https://www.pref.osaka.lg.jp/"
            "o040090/toukei/jinkou/jinkou-h2.html"
        ),
        patterns=[
            r"jk20\d{6}.*\.xlsx",
            r"jtsukikakuhou20\d{4}.*\.xlsx",
        ],
        directory="suikei",
        start_date="2015-11-01",
        end_date="2020-09-01",
    ),

    "kubun_current": Source(
        datatype="kubun",
        url=(
            "https://www.pref.osaka.lg.jp/"
            "o040090/toukei/jinkou/jinkou-xlslist.html"
        ),
        patterns=[
            r".*5sai.*\.xlsx",
        ],
        directory="kubun",
        start_date="2020-10-01",
        end_date=None,
    ),

    "kubun_archive": Source(
        datatype="kubun",
        url=(
            "https://www.pref.osaka.lg.jp/"
            "o040090/toukei/jinkou/jinkou-h2.html"
        ),
        patterns=[
            r".*5sai.*\.xlsx",
        ],
        directory="kubun",
        start_date="2016-11-01",
        end_date="2020-09-01",
    ),

    "hosei": Source(
        datatype="hosei",
        url=(
            "https://www.pref.osaka.lg.jp/"
            "o040090/toukei/jinkou/jinkou-h.html"
        ),
        patterns=[
            r"hosei20\d{4}_\d{2}.*\.xlsx",
        ],
        directory="hosei",
        start_date="2010-11-01",
        end_date="2020-09-01",
    ),

    "census_2020": Source(
    datatype="census",
    url=(
        "https://www.pref.osaka.lg.jp/"
        "o040090/toukei/top_portal/kokucho.html"
    ),
    patterns=[
        r"r2kokutyo_osakahu_kakuhou_syousai\.xlsx"
    ],
    directory="census",
    start_date="2020-10-01",
    end_date="2020-10-01",
),

}
