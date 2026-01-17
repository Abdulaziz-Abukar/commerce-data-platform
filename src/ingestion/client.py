# src/ingestion/client.py
from __future__ import annotations
import time
import requests
from typing import Any, Dict, List, Optional

class APIClient:
    def __init__(self, base_url: str, timeout: int = 30, retries: int = 3, backoff_sec: float = 1.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.retries = retries
        self.backoff_sec = backoff_sec
        self.session = requests.Session()

    def _get(self, path: str, params: Optional[dict] = None) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        last_err: Exception | None = None

        for attempt in range(1, self.retries + 1):
            try:
                resp = self.session.get(url, params=params, timeout=self.timeout)
                if resp.status_code == 200:
                    return resp.json()
                
                last_err = RuntimeError(f"GET {url} failed: {resp.status_code} {resp.text[:200]}")
            except Exception as e:
                last_err = e
            
            time.sleep(self.backoff_sec * attempt)

        raise RuntimeError(f"GET {url} failed after {self.retries} retries: {last_err}")
    
    def fetch_paginated(self, path: str, records_key: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        DummyJSON pagination:
            GET /users?limit100&skip=0
            returns: {users: [...], total: N, skip: x, limit: y}
        """
        all_records: List[Dict[str, Any]] = []
        skip = 0

        while True:
            data = self._get(path, params={"limit": limit, "skip": skip})
            batch = data.get(records_key, [])
            all_records.extend(batch)

            total = data.get("total")
            if not batch:
                break
            if total is not None and len(all_records) >= int(total):
                break

            skip += limit
        
        return all_records
    