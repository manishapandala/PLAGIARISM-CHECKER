import csv
import os
import shutil
from typing import Any

from rocksdict import Options, Rdict, WriteBatch


ROW_FLUSH_SIZE = 5000
INDEX_FLUSH_SIZE = 10000


def _as_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return str(value)


def create_kvs(csv_file_path: str, db_path: str):
    if os.path.exists(db_path):
        shutil.rmtree(db_path)

    options = Options()
    options.create_if_missing(True)
    db = Rdict(db_path, options)

    batch = WriteBatch()
    rows_in_batch = 0

    with open(csv_file_path, "r", newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            row_id = _as_text(row.get("id", ""))
            for column_name, cell_value in row.items():
                key = f"{row_id}_{column_name}"
                batch.put(key, _as_text(cell_value))
            rows_in_batch += 1

            if rows_in_batch >= ROW_FLUSH_SIZE:
                db.write(batch)
                batch = WriteBatch()
                rows_in_batch = 0

    if rows_in_batch > 0:
        db.write(batch)

    return db


def multi_get(db, keys: list[str]) -> list[str]:
    if not keys:
        return []
    return list(db[keys])


def iterate_over_range(db, start_key: str, end_key: str) -> list[str]:
    if start_key >= end_key:
        return []

    results: list[str] = []
    for key, value in db.items(from_key=start_key):
        key_text = _as_text(key)
        if key_text >= end_key:
            break
        if "_display_name" in key_text:
            results.append(_as_text(value))
    return results


def delete_key(db, key: str) -> bool:
    try:
        db.delete(key)
        return True
    except Exception:
        return False


def build_secondary_index(db, column_name: str) -> None:
    suffix = f"_{column_name}"
    batch = WriteBatch()
    pending = 0

    for key, value in db.items():
        key_text = _as_text(key)
        if key_text.startswith("__idx_"):
            continue
        if not key_text.endswith(suffix):
            continue

        row_id = key_text[: -len(suffix)]
        value_text = _as_text(value)
        index_key = f"__idx_{column_name}_{len(value_text)}_{value_text}_{row_id}"
        batch.put(index_key, row_id)
        pending += 1

        if pending >= INDEX_FLUSH_SIZE:
            db.write(batch)
            batch = WriteBatch()
            pending = 0

    if pending > 0:
        db.write(batch)


def lookup_by_index(db, column_name: str, value: str) -> list[str]:
    prefix = f"__idx_{column_name}_{len(value)}_{value}_"
    ids: list[str] = []

    for key, indexed_id in db.items(from_key=prefix):
        key_text = _as_text(key)
        if not key_text.startswith(prefix):
            break
        ids.append(_as_text(indexed_id))

    return sorted(ids)
