from dataclasses import dataclass


@dataclass(frozen=True)
class Source:
    datatype: str
    url: str
    patterns: list[str]
    directory: str
    start_date: str
    end_date: str | None = None


BASE = (
    "https://www.pref.osaka.lg.jp/"
    "o040090/toukei/jinkou/"
)

SOURCES = {
    "suikei_current": Source(
        datatype="suikei",
        url=BASE + "jinkou-xlslist.html",
        patterns=[
            r"(?:kakuhou_|kakutei_)?jk20\d{6}"
            r"(?:[-_]\d+)?\.xlsx$",
        ],
        directory="suikei",
        start_date="2025-11-01",
    ),
    "suikei_archive": Source(
        datatype="suikei",
        url=BASE + "jinkou-h2.html",
        patterns=[
            r"(?:kakuhou_|kakutei_)?jk20\d{6}"
            r"(?:[-_]\d+)?\.xlsx$",
            r"jtsukikakuhou20\d{4}.*\.xlsx$",
        ],
        directory="suikei",
        start_date="2020-11-01",
        end_date="2025-09-01",
    ),
    "kubun_current": Source(
        datatype="kubun",
        url=BASE + "jinkou-xlslist.html",
        patterns=[r".*5sai.*\.xlsx$"],
        directory="kubun",
        start_date="2025-10-01",
    ),
    "kubun_archive": Source(
        datatype="kubun",
        url=BASE + "jinkou-h2.html",
        patterns=[r".*5sai.*\.xlsx$"],
        directory="kubun",
        start_date="2020-11-01",
        end_date="2025-09-01",
    ),
    "kubun_older": Source(
        datatype="kubun",
        url=BASE + "jinkou-h.html",
        patterns=[
            r"hosei20\d{4}.*5sai.*\.xlsx$",
            r"202010kakutei5sai\.xlsx$",
        ],
        directory="kubun",
        start_date="2016-11-01",
        end_date="2020-10-01",
    ),
    "hosei": Source(
        datatype="hosei",
        url=BASE + "jinkou-h.html",
        patterns=[r"hosei20\d{4}_\d{2}.*\.xlsx$"],
        directory="hosei",
        start_date="2000-10-01",
        end_date="2020-09-01",
    ),
    "census_2020": Source(
        datatype="census",
        url=(
            "https://www.pref.osaka.lg.jp/"
            "o040090/toukei/top_portal/kokucho.html"
        ),
        patterns=[
            r"r2kokutyo_osakahu_"
            r"kakuhou_syousai\.xlsx$",
        ],
        directory="census",
        start_date="2020-10-01",
        end_date="2020-10-01",
    ),
    "census_2025": Source(
        datatype="census",
        url=BASE + "r7kokuseichousa.html",
        patterns=[
            r"r7census_osaka_kakutei_"
            r"gaiyou_data\.xlsx$",
        ],
        directory="census",
        start_date="2025-10-01",
        end_date="2025-10-01",
    ),
}
