# src/ingestion/config.py
import os

# API
API_BASE_URL = os.getenv("API_BASE_URL", "https://dummyjson.com")
API_PAGE_SIZE = int(os.getenv("API_PAGE_SIZE", "100"))
SOURCE_NAME = os.getenv("SOURCE_NAME", "dummyjson")

# BigQuery
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "commerce-data-platform-484619")
BQ_RAW_DATASET = os.getenv("BQ_RAW_DATASET", "raw")
BQ_LOCATION = os.getenv("BQ_LOCATION", "US")