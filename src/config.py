import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

PROJECT_ID = os.getenv("GCP_PROJECT_ID", "")
DATASET = "ga4_funnel"

ROOT = Path(__file__).resolve().parents[1]
SQL_DIR = ROOT / "sql"
PROCESSED_DIR = ROOT / "data" / "processed"
FIG_DIR = ROOT / "reports" / "figures"

MAX_BYTES = 5 * 1024**3