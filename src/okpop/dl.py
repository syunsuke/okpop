import re
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup, Tag


def _get_href(tag: Tag) -> str | None:
    """aタグからhrefを取得する。"""

    href = tag.get("href")

    if isinstance(href, str):
        return href

    return None


def urls_from_page(
    url: str,
    patterns: list[str],
) -> list[str]:
    """Webページからパターンに一致するURLを取得する。"""

    res = requests.get(url, timeout=10)
    res.raise_for_status()

    soup = BeautifulSoup(res.text, "html.parser")

    urls = []

    for a in soup.find_all("a"):
        href = _get_href(a)

        if href is None:
            continue

        for pattern in patterns:
            if re.search(pattern, href):
                urls.append(urljoin(url, href))
                break

    return urls


def file_from_url(
    url: str,
    directory: str | Path,
) -> Path:
    """URLから1ファイルをダウンロードする。"""

    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)

    filename = Path(urlparse(url).path).name
    output = directory / filename

    res = requests.get(url, timeout=30)
    res.raise_for_status()

    output.write_bytes(res.content)

    return output


def files_from_page(
    url: str,
    patterns: list[str],
    directory: str | Path,
    interval: float = 0.3,
) -> list[Path]:
    """Webページから対象ファイルをまとめてダウンロードする。"""

    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)

    urls = urls_from_page(url, patterns)

    downloaded = []

    for file_url in urls:
        filename = Path(urlparse(file_url).path).name
        output = directory / filename

        if output.exists():
            continue

        path = file_from_url(
            file_url,
            directory,
        )

        downloaded.append(path)

        time.sleep(interval)

    return downloaded
