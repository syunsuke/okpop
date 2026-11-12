import re
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup, Tag


def _get_href(tag: Tag) -> str | None:
    href = tag.get("href")
    return href if isinstance(href, str) else None


def urls_from_page(
    url: str,
    patterns: list[str],
) -> list[str]:
    res = requests.get(url, timeout=20)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")
    urls = []
    seen = set()
    for a in soup.find_all("a"):
        href = _get_href(a)
        if not href:
            continue
        absolute = urljoin(url, href)
        filename = Path(urlparse(absolute).path).name
        if any(
            re.search(pattern, filename, re.I)
            for pattern in patterns
        ) and absolute not in seen:
            urls.append(absolute)
            seen.add(absolute)
    return urls


def file_from_url(
    url: str,
    directory: str | Path,
) -> Path:
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    filename = Path(urlparse(url).path).name
    output = directory / filename
    res = requests.get(url, timeout=30)
    res.raise_for_status()
    # Do not leave a partial file on failure.
    temporary = output.with_suffix(output.suffix + ".part")
    try:
        temporary.write_bytes(res.content)
        temporary.replace(output)
    finally:
        temporary.unlink(missing_ok=True)
    return output


def files_from_page(
    url: str,
    patterns: list[str],
    directory: str | Path,
    interval: float = 0.3,
    *,
    urls: list[str] | None = None,
) -> list[Path]:
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    if urls is None:
        urls = urls_from_page(url, patterns)
    print(f"{len(urls)} files found")
    downloaded = []
    for i, file_url in enumerate(urls, start=1):
        filename = Path(urlparse(file_url).path).name
        output = directory / filename
        if output.exists():
            print(f"[{i}/{len(urls)}] skip: {filename}")
            continue
        print(f"[{i}/{len(urls)}] download: {filename}")
        downloaded.append(file_from_url(
            file_url,
            directory,
        ))
        time.sleep(interval)
    return downloaded
