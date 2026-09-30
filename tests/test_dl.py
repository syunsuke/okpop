from pathlib import Path

from okpop import dl

PAGE_URL = (
    "https://www.pref.osaka.lg.jp/"
    "o040090/toukei/jinkou/jinkou-xlslist.html"
)

SUIKEI_PATTERNS = [
    r"jk20\d{6}.*\.xlsx",
]


def test_urls_from_page():
    urls = dl.urls_from_page(
        PAGE_URL,
        SUIKEI_PATTERNS,
    )

    assert len(urls) > 0

    for url in urls:
        assert url.startswith("http")
        assert url.endswith(".xlsx")

def test_file_from_url(tmp_path):
    urls = dl.urls_from_page(
        PAGE_URL,
        SUIKEI_PATTERNS,
    )

    url = urls[0]

    output = dl.file_from_url(
        url,
        tmp_path,
    )

    assert isinstance(output, Path)
    assert output.exists()
    assert output.suffix == ".xlsx"
    assert output.stat().st_size > 0

def test_files_from_page(tmp_path, monkeypatch):

    urls = [
        "https://example.com/a.xlsx",
        "https://example.com/b.xlsx",
    ]

    def fake_urls_from_page(url, patterns):
        return urls

    def fake_file_from_url(url, directory):
        filename = Path(url).name
        output = directory / filename
        output.write_bytes(b"test")
        return output

    monkeypatch.setattr(
        dl,
        "urls_from_page",
        fake_urls_from_page,
    )

    monkeypatch.setattr(
        dl,
        "file_from_url",
        fake_file_from_url,
    )

    files = dl.files_from_page(
        "https://example.com/",
        [r".*\.xlsx"],
        tmp_path,
        interval=0,
    )

    assert len(files) == 2

    assert tmp_path / "a.xlsx" in files
    assert tmp_path / "b.xlsx" in files

    assert (tmp_path / "a.xlsx").exists()
    assert (tmp_path / "b.xlsx").exists()


def test_files_from_page_skips_existing(tmp_path, monkeypatch):

    urls = [
        "https://example.com/a.xlsx",
        "https://example.com/b.xlsx",
    ]

    def fake_urls_from_page(url, patterns):
        return urls

    def fake_file_from_url(url, directory):
        filename = Path(url).name
        output = directory / filename
        output.write_bytes(b"new")
        return output

    monkeypatch.setattr(
        dl,
        "urls_from_page",
        fake_urls_from_page,
    )

    monkeypatch.setattr(
        dl,
        "file_from_url",
        fake_file_from_url,
    )

    # a.xlsx は既に持っている
    existing = tmp_path / "a.xlsx"
    existing.write_bytes(b"old")

    files = dl.files_from_page(
        "https://example.com/",
        [r".*\.xlsx"],
        tmp_path,
        interval=0,
    )

    # 新しく取得したのはb.xlsxだけ
    assert files == [
        tmp_path / "b.xlsx",
    ]

    # a.xlsxは上書きされていない
    assert existing.read_bytes() == b"old"

    # b.xlsxは新しく作られた
    assert (tmp_path / "b.xlsx").read_bytes() == b"new"
