from okpop.importer import read_file
from pathlib import Path

directory = Path("data/raw/census")

for file in sorted(directory.glob("*.xlsx")):
    data = read_file(file)

    print(file.name)
    print(data.table)
    print(len(data.dataframe))
    print(
        data.dataframe["observation_date"]
        .unique()
    )
