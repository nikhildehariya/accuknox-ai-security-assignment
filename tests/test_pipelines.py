"""
Unit test suite verifying pipeline schema creation, data constraints,
and chart generation.
"""

import importlib.util
import os
import sqlite3
import sys
from pathlib import Path

import pytest

SRC_DIR = Path(__file__).resolve().parent.parent / "src"

def load_module(name: str, file_name: str):
    spec = importlib.util.spec_from_file_location(name, SRC_DIR / file_name)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

books_mod = load_module("books_mod", "1_books_api_sqlite.py")
scores_mod = load_module("scores_mod", "2_student_scores_viz.py")
users_mod = load_module("users_mod", "3_csv_to_sqlite.py")


def test_books_schema_creation(tmp_path):
    test_db = tmp_path / "test_books.db"
    conn = books_mod.init_db(test_db)
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(books);")
    columns = {row["name"]: row["type"] for row in cursor.fetchall()}
    conn.close()

    expected_cols = ["id", "title", "author", "publication_year", "created_at"]
    for col in expected_cols:
        assert col in columns, f"Column '{col}' missing from books table"


def test_books_duplicate_prevention(tmp_path):
    test_db = tmp_path / "test_books.db"
    sample_books = [
        {"title": "Zero Trust Architecture", "author": "NIST", "publication_year": 2020},
        {"title": "The Art of Software Security Assessment", "author": "Mark Dowd", "publication_year": 2006},
    ]

    inserted1, dupes1 = books_mod.store_books(test_db, sample_books)
    assert inserted1 == 2
    assert dupes1 == 0

    inserted2, dupes2 = books_mod.store_books(test_db, sample_books)
    assert inserted2 == 0
    assert dupes2 == 2

    stored = books_mod.get_all_books(test_db)
    assert len(stored) == 2


def test_books_deterministic_fallback():
    books, source = books_mod.fetch_books_from_api(
        api_url="http://invalid.domain.that.does.not.exist:9999/api",
        timeout_seconds=0.5,
    )
    assert len(books) >= 5
    assert "fallback" in source
    for b in books:
        assert "title" in b and "author" in b


def test_compute_summary_metrics():
    scores = [80.0, 90.0, 100.0, 70.0]
    metrics = scores_mod.compute_summary_metrics(scores)

    assert metrics["count"] == 4
    assert metrics["average"] == 85.0
    assert metrics["median"] == 85.0
    assert metrics["min"] == 70.0
    assert metrics["max"] == 100.0
    assert metrics["std_dev"] > 0

    with pytest.raises(ValueError):
        scores_mod.compute_summary_metrics([])


def test_chart_file_creation(tmp_path):
    chart_file = tmp_path / "student_scores.png"
    students = ["Alice", "Bob", "Charlie", "Diana"]
    scores = [95.0, 82.0, 74.0, 88.0]

    result_path = scores_mod.generate_bar_chart(students, scores, chart_file, dpi=150)
    assert result_path.exists()
    assert result_path.stat().st_size > 15000

    with open(result_path, "rb") as f:
        header = f.read(8)
    assert header == b"\x89PNG\r\n\x1a\n", "File does not contain valid PNG magic header"


def test_email_validation_logic():
    valid_emails = [
        "user@example.com",
        "first.last@accuknox.com",
        "ai_sec+tag@sub.domain.org",
        "nikhildehariya100@gmail.com",
    ]
    invalid_emails = [
        "",
        "plainaddress",
        "@missingusername.com",
        "username@.com",
        "user@bad_domain",
        "user..double@domain.com",
        None,
    ]

    for email in valid_emails:
        assert users_mod.validate_email(email) is True

    for email in invalid_emails:
        assert users_mod.validate_email(email) is False


def test_invalid_csv_row_filtering(tmp_path):
    test_csv = tmp_path / "test_users.csv"
    csv_content = """name,email,role
Valid User,valid.user@accuknox.com,Security Engineer
Missing Email,,Data Scientist
Invalid Email,not-an-email,Analyst
,nameless@example.com,Developer
"""
    test_csv.write_text(csv_content, encoding="utf-8")

    valid_users, skipped_records = users_mod.read_and_validate_csv(test_csv)

    assert len(valid_users) == 1
    assert valid_users[0]["name"] == "Valid User"
    assert valid_users[0]["email"] == "valid.user@accuknox.com"

    assert len(skipped_records) == 3
    reasons = [reason for _, reason in skipped_records]
    assert any("Missing or blank 'email'" in r for r in reasons)
    assert any("Invalid email format" in r for r in reasons)
    assert any("Missing or blank 'name'" in r for r in reasons)


def test_users_schema_and_duplicate_prevention(tmp_path):
    test_db = tmp_path / "test_users.db"
    users = [
        {"name": "Alice", "email": "alice@accuknox.com", "role": "Engineer"},
        {"name": "Bob", "email": "bob@accuknox.com", "role": "Analyst"},
    ]

    inserted1, dupes1 = users_mod.insert_users(test_db, users)
    assert inserted1 == 2
    assert dupes1 == 0

    duplicate_users = [
        {"name": "Alice Duplicate", "email": "alice@accuknox.com", "role": "Lead Engineer"},
    ]
    inserted2, dupes2 = users_mod.insert_users(test_db, duplicate_users)
    assert inserted2 == 0
    assert dupes2 == 1

    stored = users_mod.get_all_users(test_db)
    assert len(stored) == 2
    assert stored[0][1] == "Alice"
