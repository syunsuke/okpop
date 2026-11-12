from pathlib import Path

from okpop.workflows.setup import build_database
from okpop.validation import validate_database

db_path = Path(
    "sandbox/data/new_population.sqlite"
)

if db_path.exists():
    raise FileExistsError(db_path)

build_database(db_path)
validate_database(db_path)
