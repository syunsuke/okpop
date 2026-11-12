"""Validate a newly built OKPOP SQLite database."""

import sqlite3
from contextlib import closing
from pathlib import Path

TABLES = (
    "census",
    "suikei",
    "hosei",
    "population_age5_v001",
    "population_age5_v002",
)

REQUIRED_TABLES = (
    "census",
    "suikei",
    "hosei",
    "population_age5_v002",
)

VIEWS = (
    "view_base_data",
    "view_excel_report_data",
)


def validate_database(db_path: str | Path) -> None:
    """Report missing months; fail on invalid or duplicated data."""
    db_path = Path(db_path)
    if not db_path.is_file():
        raise FileNotFoundError(db_path)

    errors = []

    # Open read-only so verification cannot create or mutate the DB.
    with closing(
        sqlite3.connect(
            db_path.resolve().as_uri() + "?mode=ro",
            uri=True,
        )
    ) as con:
        print("\n=== Database verification ===")

        integrity = con.execute(
            "PRAGMA integrity_check"
        ).fetchone()[0]
        if integrity != "ok":
            errors.append(f"integrity_check: {integrity}")

        for table in TABLES:
            count, first, last = con.execute(
                f"SELECT COUNT(*), MIN(observation_date), "
                f"MAX(observation_date) FROM {table}"
            ).fetchone()
            print(f"{table}: {count} rows "
                  f"({first} .. {last})")
            if count == 0 and table in REQUIRED_TABLES:
                errors.append(
                    f"empty table: {table}"
                )
        for view in VIEWS:
            rows = con.execute(
                f"SELECT observation_date, area_name, "
                f"COUNT(*) FROM {view} "
                "GROUP BY observation_date, area_name "
                "HAVING COUNT(*) > 1 "
                "ORDER BY observation_date, area_name"
            ).fetchall()
            print(f"{view}: {len(rows)} duplicate keys")
            if rows:
                for date, area, count in rows[:10]:
                    print(f"  duplicate: {date} "
                          f"{area} ({count})")
                errors.append(
                    f"{view}: {len(rows)} duplicate keys"
                )

        # Missing dates are informative, not a build failure.
        dates = [r[0] for r in con.execute(
            "SELECT DISTINCT observation_date "
            "FROM view_base_data ORDER BY observation_date"
        )]
        if dates:
            from datetime import date
            available = set(dates)
            year, month = map(int, dates[0][:7].split("-"))
            end_year, end_month = map(
                int, dates[-1][:7].split("-")
            )
            missing = []
            while (year, month) <= (end_year, end_month):
                key = date(year, month, 1).isoformat()
                if key not in available:
                    missing.append(key)
                month += 1
                if month == 13:
                    year += 1
                    month = 1
            print(f"Missing months: {len(missing)}")
            for month in missing:
                print(f"  missing: {month}")

    if errors:
        raise ValueError("DB validation failed:\n" +
                         "\n".join(errors))
    print("Database validation OK")
