# src/ingestion/loaders.py
from __future__ import annotations

import hashlib
import json
from datetime import date, datetime, timezone
from typing import Any, Dict, List

from google.cloud import bigquery

def sha256_json(payload: Dict[str, Any]) -> str:
    dumped = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(dumped.encode("utf-8")).hexdigest()

def bq_client(project_id: str, location: str) -> bigquery.Client:
    return bigquery.Client(project=project_id, location=location)

def ensure_dataset(client: bigquery.Client, project_id: str, dataset_id: str, location: str) -> None:
    dataset_ref = bigquery.Dataset(f"{project_id}.{dataset_id}")
    dataset_ref.location = location
    client.create_dataset(dataset_ref, exists_ok=True)

def drop_table(client: bigquery.Client, table_fqid: str) -> None:
    """
    Drops a BigQuery table if it exists.
    """
    client.delete_table(table_fqid, not_found_ok=True)

def load_to_temp_table(
        client: bigquery.Client,
        project_id: str,
        dataset_id: str,
        temp_table_name: str,
        rows: List[Dict[str, Any]]
) -> str:
    """
    Loads rows into a temp table in BigQuery. Returns full table id.
    """
    table_id = f"{project_id}.{dataset_id}.{temp_table_name}"

    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_TRUNCATE",
        autodetect=False,
        schema=[
            bigquery.SchemaField("business_id", "INT64", mode="REQUIRED"),
            bigquery.SchemaField("batch_date", "DATE", mode="REQUIRED"),
            bigquery.SchemaField("source", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("extracted_at", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("loaded_at", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("payload_hash", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("payload", "JSON", mode="REQUIRED"),
        ],
    )
    
    load_job = client.load_table_from_json(rows, table_id, job_config=job_config)
    load_job.result()
    return table_id

def merge_into_raw(
        client: bigquery.Client,
        project_id: str,
        raw_dataset: str,
        raw_table: str,
        id_col: str,
        temp_table_fqid: str,
) -> None:
    """
    MERGE temp rows into raw table based on (id_col, batch_date)
    """
    target = f"`{project_id}.{raw_dataset}.{raw_table}`"
    source = f"`{temp_table_fqid}`"

    sql = f"""
    MERGE {target} T
    USING (
        SELECT
            business_id,
            batch_date,
            source,
            extracted_at,
            loaded_at,
            payload_hash,
            payload
        FROM {source}
    ) S
    ON T.{id_col} = S.business_id AND T.batch_date = S.batch_date
    WHEN MATCHED THEN UPDATE SET
        source = S.source,
        extracted_at = S.extracted_at,
        loaded_at = S.loaded_at,
        payload_hash = S.payload_hash,
        payload = S.payload
    WHEN NOT MATCHED THEN INSERT ({id_col}, batch_date, source, extracted_at, loaded_at, payload_hash, payload)
    VALUES (S.business_id, S.batch_date, S.source, S.extracted_at, S.loaded_at, S.payload_hash, S.payload)
    """

    job = client.query(sql)
    job.result()

def ingest_entity_to_raw(
        *,
        project_id: str,
        location: str,
        raw_dataset: str,
        entity_name: str,
        raw_table: str,
        id_col: str,
        records: List[Dict[str, Any]],
        batch_date: date,
        source_name: str
) -> int:
    """
    End-to-End: records -> temp table -> merge into raw.<table>.
    Returns number of rows processed.
    """
    client = bq_client(project_id, location)
    ensure_dataset(client, project_id, raw_dataset, location)

    extracted_at = datetime.now(timezone.utc)
    loaded_at = extracted_at

    # Convert API records into rows matching our temp schema
    rows: List[Dict[str, Any]] = []
    for r in records:
        business_id = r.get("id")
        if business_id is None:
            continue

        rows.append({
            "business_id": int(business_id),
            "batch_date": batch_date.isoformat(),
            "source": source_name,
            "extracted_at": extracted_at.isoformat(),
            "loaded_at": loaded_at.isoformat(),
            "payload_hash": sha256_json(r),
            "payload": r, # native JSON field
        })

    if not rows:
        return 0
    
    # Use a temp table name that's safe + unique-ish
    temp_table = f"_stg_{entity_name}_{batch_date.isoformat().replace("-", "")}"
    temp_fqid = load_to_temp_table(client, project_id, raw_dataset, temp_table, rows)

    merge_into_raw(
        client=client,
        project_id=project_id,
        raw_dataset=raw_dataset,
        raw_table=raw_table,
        id_col=id_col,
        temp_table_fqid=temp_fqid
    )

    drop_table(client, temp_fqid)
    
    return len(rows)