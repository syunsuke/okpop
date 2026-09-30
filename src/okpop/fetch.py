from pathlib import Path

from okpop import dl
from okpop.source import SOURCES

DEFAULT_RAW_DIR = Path("data/raw")


def fetch(
    source_name: str,
    raw_dir: str | Path = DEFAULT_RAW_DIR,
) -> list[Path]:
    source = SOURCES[source_name]

    directory = Path(raw_dir) / source.directory

    return dl.files_from_page(
        url=source.url,
        patterns=source.patterns,
        directory=directory,
    )

def fetch_datatype(
    datatype: str,
    raw_dir: str | Path = DEFAULT_RAW_DIR,
) -> list[Path]:
    source_names = [
        name
        for name, source in SOURCES.items()
        if source.datatype == datatype
    ]

    if not source_names:
        raise ValueError(f"unknown datatype: {datatype}")

    downloaded = []

    for source_name in source_names:
        files = fetch(
            source_name,
            raw_dir=raw_dir,
        )
        downloaded.extend(files)

    return downloaded
