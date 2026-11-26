"""
Validates user CSV records and ingests clean rows into a SQLite database.
"""

from __future__ import annotations

import csv
import logging
import re
import sqlite3
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("csv_to_sqlite")

# RFC 5322-compliant pattern for email format checks
EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)+$"
)


def get_default_paths() -> Tuple[Path, Path]:
    base_dir = Path(__file__).resolve().parent.parent
    data_dir = base_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / "sample_users.csv", data_dir / "users.db"


def validate_email(email: Optional[str]) -> bool:
    if not email or not isinstance(email, str):
        return False
    email = email.strip()
    if not email or len(email) > 254:
        return False
    if ".." in email:
        return False
    return bool(EMAIL_REGEX.match(email))


def validate_row(row: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    name = str(row.get("name") or "").strip()
    email = str(row.get("email") or "").strip()
    role = str(row.get("role") or "").strip()

    if not name:
        return False, "Missing or blank 'name'"
    if not email:
        return False, "Missing or blank 'email'"
    if not validate_email(email):
        return False, f"Invalid email format: '{email}'"
    if not role:
        return False, "Missing or blank 'role'"

    return True, None


def read_and_validate_csv(
    csv_path: Path | str,
) -> Tuple[List[Dict[str, str]], List[Tuple[Dict[str, Any], str]]]:
    file_path = Path(csv_path)
    if not file_path.exists():
        raise FileNotFoundError(f"CSV file not found: {file_path}")

    valid_users: List[Dict[str, str]] = []
    skipped_records: List[Tuple[Dict[str, Any], str]] = []

    with open(file_path, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row_num, raw_row in enumerate(reader, start=2):
            clean_row = {k.strip(): (v.strip() if v else "") for k, v in raw_row.items() if k}
            is_valid, reason = validate_row(clean_row)
            if is_valid:
                valid_users.append(clean_row)
            else:
                logger.warning(f"Row {row_num} skipped ({reason}): {clean_row}")
                skipped_records.append((clean_row, reason or "Validation failure"))

    logger.info(f"Parsed {len(valid_users)} valid records, skipped {len(skipped_records)} rows.")
    return valid_users, skipped_records


def init_users_db(db_path: Path | str) -> sqlite3.Connection:
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row

    with conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                role TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);")
    return conn


def insert_users(db_path: Path | str, users: List[Dict[str, str]]) -> Tuple[int, int]:
    conn = init_users_db(db_path)
    inserted = 0

    with conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM users")
        initial_count = cur.fetchone()[0]

        insert_query = """
            INSERT OR IGNORE INTO users (name, email, role)
            VALUES (?, ?, ?);
        """
        for u in users:
            cur.execute(insert_query, (u["name"], u["email"], u["role"]))

        cur.execute("SELECT COUNT(*) FROM users")
        final_count = cur.fetchone()[0]
        inserted = final_count - initial_count

    conn.close()
    duplicates = len(users) - inserted
    logger.info(f"Database sync: {inserted} inserted, {duplicates} duplicate(s) ignored.")
    return inserted, duplicates


def get_all_users(db_path: Path | str) -> List[Tuple[Any, ...]]:
    conn = init_users_db(db_path)
    with conn:
        cur = conn.cursor()
        cur.execute("SELECT id, name, email, role, created_at FROM users ORDER BY id ASC;")
        rows = cur.fetchall()
    conn.close()
    return [tuple(r) for r in rows]


def display_users_table(rows: List[Tuple[Any, ...]]) -> None:
    print("\n" + "=" * 86)
    print(" Active Users Database [data/users.db]")
    print("=" * 86)

    if not rows:
        print(" [No records found]")
        print("=" * 86 + "\n")
        return

    headers = ("ID", "Name", "Email Address", "Role", "Created At (UTC)")
    str_rows = [
        (
            str(r[0]),
            (r[1][:20] + "...") if len(str(r[1])) > 23 else str(r[1]),
            (r[2][:30] + "...") if len(str(r[2])) > 33 else str(r[2]),
            (r[3][:18] + "...") if len(str(r[3])) > 20 else str(r[3]),
            str(r[4])[:19] if r[4] else "N/A",
        )
        for r in rows
    ]

    col_widths = [
        max(len(headers[i]), max(len(row[i]) for row in str_rows))
        for i in range(len(headers))
    ]

    header_fmt = " | ".join(f"{{:<{w}}}" for w in col_widths)
    separator = "-+-".join("-" * w for w in col_widths)

    print(header_fmt.format(*headers))
    print(separator)
    for row in str_rows:
        print(header_fmt.format(*row))
    print("=" * 86)
    print(f" Total records: {len(rows)}\n")


def main() -> None:
    csv_path, db_path = get_default_paths()
    valid_users, _ = read_and_validate_csv(csv_path)
    insert_users(db_path, valid_users)
    records = get_all_users(db_path)
    display_users_table(records)


if __name__ == "__main__":
    main()
