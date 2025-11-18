"""
File-backed replacement for MongoDB decision logs and audit trails.

This module implements a JSON-file-backed storage that mirrors the
interface previously provided by `MongoDBClient` so the rest of the
application (routers, services) does not need any changes.

Behavior summary:
- Creates `fairfinance_logs/` at repo root on startup.
- Uses `fairfinance_logs/decision_logs.json` and
  `fairfinance_logs/audit_trails.json` for persistence.
- Loads existing files (parses ISO timestamps) or creates empty arrays.
- Appends new entries in-memory and overwrites JSON files on each insert.
- Provides the same methods as before: `insert_decision_log`,
  `get_decision_logs`, `get_decision_log`, `insert_audit_trail`,
  `get_audit_trails`.

Notes:
- This implementation is thread-safe (simple Lock around file ops).
- Timestamps are preserved as Python `datetime` objects for callers
  (they are serialized to ISO strings in the JSON files).
"""

from __future__ import annotations

import json
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List


class JSONLogStore:
    def __init__(self, base_dir: Optional[Path] = None):
        # Determine repo base dir if not provided
        if base_dir is None:
            base_dir = Path(__file__).resolve().parents[2]

        self.logs_dir = base_dir / "fairfinance_logs"
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        self.decision_path = self.logs_dir / "decision_logs.json"
        self.audit_path = self.logs_dir / "audit_trails.json"

        # Internal in-memory lists (store dicts with Python datetimes)
        self._decision_logs: List[Dict[str, Any]] = []
        self._audit_trails: List[Dict[str, Any]] = []

        # Lock to protect concurrent file access
        self._lock = threading.Lock()

        # Initialize files and load existing content
        self._ensure_file(self.decision_path)
        self._ensure_file(self.audit_path)
        self._load()

    def _ensure_file(self, path: Path) -> None:
        """Ensure JSON file exists; create empty array if not."""
        if not path.exists():
            path.write_text("[]", encoding="utf-8")

    def _load(self) -> None:
        """Load JSON files into memory and parse timestamps."""
        with self._lock:
            try:
                raw = json.loads(self.decision_path.read_text(encoding="utf-8"))
                self._decision_logs = [self._deserialize_item(i) for i in raw]
            except Exception:
                self._decision_logs = []

            try:
                raw = json.loads(self.audit_path.read_text(encoding="utf-8"))
                self._audit_trails = [self._deserialize_item(i) for i in raw]
            except Exception:
                self._audit_trails = []

    def _serialize_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Python objects (datetime) to JSON-serializable forms."""
        out = dict(item)
        if "timestamp" in out and isinstance(out["timestamp"], datetime):
            out["timestamp"] = out["timestamp"].isoformat()
        return out

    def _deserialize_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Convert serialized JSON item into runtime representation.

        Specifically, convert ISO timestamp strings back into datetimes.
        """
        out = dict(item)
        ts = out.get("timestamp")
        if isinstance(ts, str):
            try:
                out["timestamp"] = datetime.fromisoformat(ts)
            except Exception:
                # Leave as string if parsing fails (preserve original)
                out["timestamp"] = ts
        return out

    def _write_decision_file(self) -> None:
        """Write decision logs to JSON file (called within lock)."""
        with self._lock:
            serializable = [self._serialize_item(i) for i in self._decision_logs]
            self.decision_path.write_text(
                json.dumps(serializable, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

    def _write_audit_file(self) -> None:
        """Write audit trails to JSON file (called within lock)."""
        with self._lock:
            serializable = [self._serialize_item(i) for i in self._audit_trails]
            self.audit_path.write_text(
                json.dumps(serializable, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

    # Public API matching previous MongoDBClient
    def insert_decision_log(self, log_data: Dict[str, Any]) -> str:
        """Insert immutable decision log and persist to JSON file.

        Returns the inserted id (string).
        """
        entry = dict(log_data)  # copy
        # Preserve timestamp as-is if provided, otherwise set to now
        if "timestamp" not in entry or entry["timestamp"] is None:
            entry["timestamp"] = datetime.utcnow()

        # Create deterministic id if not provided
        if "id" not in entry:
            app_id = entry.get("application_id")
            # Use integer timestamp to avoid collisions
            entry["id"] = f"{app_id}_{int(datetime.utcnow().timestamp())}"

        with self._lock:
            self._decision_logs.append(entry)

        # Persist to file
        self._write_decision_file()

        return str(entry.get("id"))

    def get_decision_logs(
        self, user_id: Optional[int] = None, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get decision logs, optionally filtered by `user_id` and limited.

        Returns a list of entries (with Python datetime timestamps).
        """
        with self._lock:
            logs = list(self._decision_logs)

        if user_id is not None:
            logs = [log for log in logs if log.get("user_id") == user_id]

        # Sort by timestamp descending; entries may have timestamps as datetime or string
        def _ts_key(item: Dict[str, Any]):
            t = item.get("timestamp")
            if isinstance(t, datetime):
                return t
            try:
                return datetime.fromisoformat(str(t))
            except Exception:
                return datetime.min

        logs_sorted = sorted(logs, key=_ts_key, reverse=True)
        return logs_sorted[:limit]

    def get_decision_log(self, application_id: int) -> Optional[Dict[str, Any]]:
        """Get the decision log for a specific application id."""
        with self._lock:
            for log in self._decision_logs:
                if log.get("application_id") == application_id:
                    return log
        return None

    def insert_audit_trail(self, audit_data: Dict[str, Any]) -> str:
        """Insert audit trail entry and persist to JSON file.

        Returns the inserted id (string).
        """
        entry = dict(audit_data)
        if "timestamp" not in entry or entry["timestamp"] is None:
            entry["timestamp"] = datetime.utcnow()

        if "id" not in entry:
            entry["id"] = f"audit_{int(datetime.utcnow().timestamp())}"

        with self._lock:
            self._audit_trails.append(entry)

        # Persist to file
        self._write_audit_file()

        return str(entry.get("id"))

    def get_audit_trails(
        self, user_id: Optional[int] = None, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get audit trails, optionally filtered by user_id and limited."""
        with self._lock:
            trails = list(self._audit_trails)

        if user_id is not None:
            trails = [t for t in trails if t.get("user_id") == user_id]

        def _ts_key(item: Dict[str, Any]):
            t = item.get("timestamp")
            if isinstance(t, datetime):
                return t
            try:
                return datetime.fromisoformat(str(t))
            except Exception:
                return datetime.min

        trails_sorted = sorted(trails, key=_ts_key, reverse=True)
        return trails_sorted[:limit]


# Create global instance for importers
json_log_client = JSONLogStore()

# Backwards-compatible name expected by callers
mongodb_client = json_log_client

