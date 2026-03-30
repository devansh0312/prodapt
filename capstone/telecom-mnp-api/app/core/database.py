import json
from pathlib import Path
from threading import Lock
from typing import Any
from uuid import uuid4

from app.core.config import get_settings


class FileCollection:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()
        if not self.path.exists():
            self.path.write_text("[]", encoding="utf-8")

    def _read(self) -> list[dict[str, Any]]:
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _write(self, records: list[dict[str, Any]]) -> None:
        self.path.write_text(json.dumps(records, indent=2), encoding="utf-8")

    def all(self) -> list[dict[str, Any]]:
        with self._lock:
            return self._read()

    def find_one(self, **conditions: Any) -> dict[str, Any] | None:
        with self._lock:
            for record in self._read():
                if all(record.get(key) == value for key, value in conditions.items()):
                    return record
        return None

    def find_many(self, **conditions: Any) -> list[dict[str, Any]]:
        with self._lock:
            records = self._read()
            if not conditions:
                return records
            return [
                record
                for record in records
                if all(record.get(key) == value for key, value in conditions.items())
            ]

    def insert_one(self, record: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            records = self._read()
            new_record = {"id": record.get("id", str(uuid4())), **record}
            records.append(new_record)
            self._write(records)
            return new_record

    def update_one(self, record_id: str, updates: dict[str, Any]) -> dict[str, Any] | None:
        with self._lock:
            records = self._read()
            for index, record in enumerate(records):
                if record["id"] == record_id:
                    records[index] = {**record, **updates}
                    self._write(records)
                    return records[index]
        return None

    def upsert(self, key: str, value: Any, payload: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            records = self._read()
            for index, record in enumerate(records):
                if record.get(key) == value:
                    records[index] = {**record, **payload, "id": record["id"]}
                    self._write(records)
                    return records[index]
            new_record = {"id": payload.get("id", str(uuid4())), key: value, **payload}
            records.append(new_record)
            self._write(records)
            return new_record


class FileDatabase:
    def __init__(self):
        base_dir = get_settings().data_dir
        self.users = FileCollection(base_dir / "users.json")
        self.operators = FileCollection(base_dir / "operators.json")
        self.port_requests = FileCollection(base_dir / "port_requests.json")
        self.documents = FileCollection(base_dir / "documents.json")
        self.otp_logs = FileCollection(base_dir / "otp_logs.json")


db = FileDatabase()
