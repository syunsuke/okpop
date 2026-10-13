from okpop.workflows.setup import setup
import argparse


def main():
    parser = argparse.ArgumentParser(
        prog="okpop",
        description=
        "Osaka Prefecture Population Toolkit",
   )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    subparsers.add_parser(
        "setup",
        help="Set up OKPOP",
    )

    args = parser.parse_args()

    if args.command == "setup":
        setup()
