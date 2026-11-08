from pathlib import Path
import pandas as pd
from google.cloud import bigquery
from src.config import PROJECT_ID, DATASET, SQL_DIR, MAX_BYTES, PROCESSED_DIR

_client = None

def client() -> bigquery.Client:
    global _client
    if _client is None:
        _client = bigquery.Client(project=PROJECT_ID)
    return _client

def render(sql: str) -> str:
    """Fill {project} and {dataset} placeholders."""
    return sql.format(project=PROJECT_ID, dataset=DATASET)

def dry_run(sql: str) -> float:
    """GB the query would scan, without running it."""
    cfg = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
    return client().query(render(sql), job_config=cfg).total_bytes_processed / 1024**3

def run(sql: str) -> pd.DataFrame:
    cfg = bigquery.QueryJobConfig(maximum_bytes_billed=MAX_BYTES)
    return client().query(render(sql), job_config=cfg).to_dataframe()

def run_file(rel_path: str) -> pd.DataFrame:
    sql = (SQL_DIR / rel_path).read_text()
    print(f"{rel_path}: ~{dry_run(sql):.2f} GB")
    return run(sql)

def save(df: pd.DataFrame, name: str) -> Path:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    path = PROCESSED_DIR / f"{name}.csv"
    df.to_csv(path, index=False)
    return path