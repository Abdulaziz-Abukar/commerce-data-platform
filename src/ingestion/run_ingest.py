# src/ingestion/run_ingest.py
from __future__ import annotations

import argparse
from datetime import date
from typing import Dict

from .config import(
    API_BASE_URL, API_PAGE_SIZE, SOURCE_NAME,
    GCP_PROJECT_ID, BQ_RAW_DATASET, BQ_LOCATION
)
from .client import APIClient
from .loaders import ingest_entity_to_raw

ENTITY_CONFIG: Dict[str, Dict[str, str]] = {
    "users":        {"path": "/users",      "records_key": "users",     "raw_table": "users",       "id_col": "user_id"},
    "products":     {"path": "/products",    "records_key": "products",  "raw_table": "products",    "id_col": "product_id"},
    "carts":        {"path": "/carts",      "records_key": "carts",     "raw_table": "carts",       "id_col": "cart_id"},
}

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--entity", choices=ENTITY_CONFIG.keys(), required=True)
    p.add_argument("--batch_date", help="YYYY-MM-DD (defaults to today)")
    p.add_argument("--limit", type=int, default=API_PAGE_SIZE)
    return p.parse_args()

def main():
    args = parse_args()
    batch_date = date.fromisoformat(args.batch_date) if args.batch_date else date.today()

    cfg = ENTITY_CONFIG[args.entity]
    client = APIClient(API_BASE_URL)

    print(f"[extract] entity={args.entity} batch_date={batch_date}")
    records = client.fetch_paginated(cfg["path"], cfg["records_key"], limit=args.limit)
    print(f"[extracted] fetched={len(records)}")

    print(f"[load] bigquery project={GCP_PROJECT_ID} dataset={BQ_RAW_DATASET} table={cfg['raw_table']}")
    n = ingest_entity_to_raw(
        project_id=GCP_PROJECT_ID,
        location=BQ_LOCATION,
        raw_dataset=BQ_RAW_DATASET,
        entity_name=args.entity,
        raw_table=cfg["raw_table"],
        id_col=cfg["id_col"],
        records=records,
        batch_date=batch_date,
        source_name=SOURCE_NAME,
    )
    print(f"[load] merged_rows={n}")
    print("[done]")

if __name__ == "__main__":
    main()