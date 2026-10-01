from pathlib import Path
from pprint import pprint

from okpop.fetch import check_datatype, fetch_datatype

SANDBOX_DATA = Path("sandbox/data")


def main():
    datatype = "kubun"

    downloaded = fetch_datatype(
        datatype,
        raw_dir=SANDBOX_DATA,
    )

    print("downloaded:")
    for file in downloaded:
        print(file)

    result = check_datatype(
        datatype,
        raw_dir=SANDBOX_DATA,
    )

    print("\ncheck:")
    pprint(result)


if __name__ == "__main__":
    main()
