import os
from pathlib import Path

from okpop import database, mail, report

DB_PATH = database.DEFAULT_DB_PATH

TEMPLATE_PATH = Path(
    "assets/templates/"
    "populaiton_report_template_0001.xlsx"
)

OUTPUT_DIR = Path("data/output")


def main():
    print("=== Create reports ===")

    archive_file = report.create_report_archive(
        output_dir=OUTPUT_DIR,
        template_path=TEMPLATE_PATH,
        db_path=DB_PATH,
        end_date=None,
    )

    print(f"Archive: {archive_file}")

    print("\n=== Send mail ===")

    to_address = os.environ[
        "OKPOP_GMAIL_ADDRESS"
    ]

    mail.send_mail(
        to_address=to_address,
        subject="OKPOP population report",
        body="大阪府人口レポートを送付します。",
        attachment=archive_file,
    )

    print("\n=== Complete ===")


if __name__ == "__main__":
    main()
