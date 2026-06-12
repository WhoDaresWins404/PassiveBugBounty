# src/storage/jsonl_pool.py
import os
import json
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from src.config import settings

class UnstructuredPool:
    def __init__(self):
        self.base_dir = Path(settings.unstructured_pool_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _get_today_file(self) -> Path:
        """Returns the path to today's partitioned jsonl file."""
        today_str = datetime.utcnow().strftime("%Y-%m-%d")
        return self.base_dir / f"traffic_{today_str}.jsonl"

    async def append_session(self, session_data: dict):
        """Append a finalized session to today's jsonl file."""
        file_path = self._get_today_file()
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(session_data) + "\n")

    async def enforce_ttl(self):
        """Delete jsonl files older than the configured TTL (default 72h)."""
        cutoff_date = datetime.utcnow() - timedelta(hours=settings.unstructured_ttl_hours)
        
        for file_path in self.base_dir.glob("traffic_*.jsonl"):
            # Extract date from filename: traffic_YYYY-MM-DD.jsonl
            try:
                date_str = file_path.stem.split("_")[1]
                file_date = datetime.strptime(date_str, "%Y-%m-%d")
                if file_date < cutoff_date:
                    file_path.unlink()
                    print(f"🗑️  Deleted expired unstructured pool file: {file_path.name}")
            except (IndexError, ValueError):
                continue # Skip malformed filenames