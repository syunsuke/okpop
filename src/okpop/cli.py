import argparse

from okpop.database import update_views
from okpop.workflows.setup import setup


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="okpop",
        description="大阪府人口データ管理ツール",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    subparsers.add_parser(
        "setup",
        help="OKPOPの初期設定を実行",
    )

    subparsers.add_parser(
        "update-views",
        help="SQLiteのView定義を更新",
    )

    args = parser.parse_args()

    if args.command == "setup":
        # 既存のsetup処理をここで呼び出す
        setup()

    elif args.command == "update-views":
        update_views()

