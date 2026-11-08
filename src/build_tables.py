from google.cloud import bigquery
from src.bq import client, render, dry_run
from src.config import SQL_DIR, MAX_BYTES

LAYERS = ["01_staging", "02_intermediate", "03_marts", "tests"]

def main() -> None:
    for layer in LAYERS:
        for path in sorted((SQL_DIR / layer).glob("*.sql")):
            raw = path.read_text()
            if layer == "tests":
                print(f"[tests] {path.name}")
            else:
                print(f"[{layer}] {path.name}: ~{dry_run(raw):.2f} GB")
            cfg = bigquery.QueryJobConfig(maximum_bytes_billed=MAX_BYTES)
            client().query(render(raw), job_config=cfg).result()
    print("All tables built and tests passed.")

if __name__ == "__main__":
    main()