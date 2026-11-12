from pathlib import Path
from unittest.mock import patch
import tempfile

import pandas as pd

from okpop import (filecheck,fetch)


def test_filename():
    samples = {
        'jk20250901.xlsx': ('suikei', '2025-09-01'),
        'kakuhou_jk20251101.xlsx': ('suikei', '2025-11-01'),
        'kakutei_jk20201101.xlsx': ('suikei', '2020-11-01'),
        'jk20231001_2.xlsx': ('suikei', '2023-10-01'),
        '202406suikei_5sai.xlsx': ('kubun', '2024-06-01'),
        '202510suikei5sai.xlsx': ('kubun', '2025-10-01'),
        'hosei201910_suikei5sai.xlsx': ('kubun', '2019-10-01'),
    }
    for name, (kind, date) in samples.items():
        assert filecheck.guess_datatype(name) == kind
        result = filecheck.dates_from_filename(name)
        assert result is not None
        assert str(result[0].date()) == date


def test_selection():
    urls = [
        'https://example.com/jk20250901.xlsx',
        'https://example.com/kakuhou_jk20251101.xlsx',
        'https://example.com/jk20261001.xlsx',
    ]
    with patch.object(fetch.dl, 'urls_from_page', return_value=urls):
        assert len(fetch._source_urls('suikei_current')) == 2
        assert len(fetch._source_urls('suikei_archive')) == 1


def test_duplicate():
    with tempfile.TemporaryDirectory() as tmp:
        mapping = {
            'suikei_current': [
                'https://example.com/kakuhou_jk20251101.xlsx',
                'https://example.com/jk20251101.xlsx',
            ]
        }
        try:
            fetch._check_duplicates(mapping, tmp)
        except ValueError as exc:
            assert '2025-11-01' in str(exc)
        else:
            raise AssertionError('should detect duplicates')


def test_missing():
    result = filecheck.check_dates(
        pd.DatetimeIndex(['2025-09-01', '2025-11-01']),
        start_date='2025-09-01',
        end_date='2025-11-01',
    )
    assert list(map(str, result['missing'])) == [
        '2025-10-01 00:00:00'
    ]


if __name__ == '__main__':
    test_filename()
    test_selection()
    test_duplicate()
    test_missing()
    print('PASS: filename, period, duplicate, missing')
