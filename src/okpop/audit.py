"""Inspect published links and test local Excel imports.

Run without modifying the production SQLite database.
"""

import argparse
import sqlite3
import tempfile
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlparse

from okpop import database, dl, importer
from okpop.paths import RAW_DIR
from okpop.source import SOURCES
from okpop.fetch import _source_urls


def check_links(raw_dir: Path) -> bool:
    """List discovered links, including rejected ones."""
    ok = True
    for key, source in SOURCES.items():
        try:
            all_urls = dl.urls_from_page(
                source.url, source.patterns
            )
            selected = _source_urls(key)
        except Exception as exc:
            print(f"ERROR {key}: {exc}")
            ok = False
            continue
        missing = []
        for url in selected:
            name = Path(urlparse(url).path).name
            target = raw_dir / source.directory / name
            if not target.is_file():
                missing.append(name)
        print(
            f"{key}: {len(selected)} selected, "
            f"{len(missing)} not downloaded"
        )
        for name in missing:
            print(f"  MISSING {name}")
        if missing:
            ok = False
    return ok


def _local_files(raw_dir: Path):
    seen = set()
    for source in SOURCES.values():
        folder = raw_dir / source.directory
        if folder in seen:
            continue
        seen.add(folder)
        yield from sorted(folder.glob("*.xlsx"))


def check_files(raw_dir: Path) -> bool:
    """Read each Excel and insert into a temporary DB."""
    files = list(_local_files(raw_dir))
    if not files:
        print(f"ERROR no Excel files: {raw_dir}")
        return False

    # The database is created ONLY under the temporary
    # directory. Original Excel and SQLite stay unchanged.
    errors = []
    rows = defaultdict(int)
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "audit.sqlite"
        database.init_database(dbname=db_path)

        for file in files:
            try:
                parsed = importer.read_file(file)
                df = parsed.dataframe
                if df.empty:
                    raise ValueError("empty DataFrame")
                if "observation_date" not in df:
                    raise ValueError("missing observation_date")
                if "area_name" not in df:
                    raise ValueError("missing area_name")
                # Validate actual table compatibility,
                # not merely successful pandas parsing.
                importer.import_data(parsed, db_path=db_path)
                rows[parsed.table] += len(df)
                print(
                    f"OK {file.name} -> "
                    f"{parsed.table}: {len(df)} rows"
                )
            except Exception as exc:
                errors.append((file, str(exc)))
                print(f"ERROR {file.name}: {exc}")

        with sqlite3.connect(db_path) as con:
            for table in sorted(rows):
                actual = con.execute(
                    f'SELECT COUNT(*) FROM "{table}"'
                ).fetchone()[0]
                print(f"DB {table}: {actual} rows")

    print(
        f"Checked: {len(files)} files; "
        f"errors: {len(errors)}"
    )
    return not errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "mode", choices=["links", "files"]
    )
    parser.add_argument(
        "--raw-dir", type=Path,
        default=RAW_DIR,
    )
    args = parser.parse_args()
    if args.mode == "links":
        ok = check_links(args.raw_dir)
    else:
        ok = check_files(args.raw_dir)
    if not ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
