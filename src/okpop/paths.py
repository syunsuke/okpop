from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
DB_DIR = DATA_DIR / "db"
OUTPUT_DIR = DATA_DIR / "output"

DB_PATH = DB_DIR / "population_osaka.sqlite"

DATA_TYPES = (
    "census",
    "suikei",
    "hosei",
    "kubun",
)
