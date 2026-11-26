"""
Fetch book records from the OpenLibrary API and persist unique entries to SQLite.
"""

from __future__ import annotations

import logging
import sqlite3
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("books_pipeline")

# Fallback dataset if external API is unreachable or times out
FALLBACK_BOOKS: List[Dict[str, Any]] = [
    {
        "title": "Designing Data-Intensive Applications",
        "author": "Martin Kleppmann",
        "publication_year": 2017,
    },
    {
        "title": "Security Engineering: A Guide to Building Dependable Distributed Systems",
        "author": "Ross Anderson",
        "publication_year": 2020,
    },
    {
        "title": "The Tangled Web: A Guide to Securing Modern Web Applications",
        "author": "Michal Zalewski",
        "publication_year": 2011,
    },
    {
        "title": "Applied Cryptography: Protocols, Algorithms, and Source Code in C",
        "author": "Bruce Schneier",
        "publication_year": 1996,
    },
    {
        "title": "Threat Modeling: Designing for Security",
        "author": "Adam Shostack",
        "publication_year": 2014,
    },
    {
        "title": "Hacking: The Art of Exploitation",
        "author": "Jon Erickson",
        "publication_year": 2008,
    },
    {
        "title": "Building Secure and Reliable Systems",
        "author": "Heather Adkins, Betsy Beyer, Paul Blankinship",
        "publication_year": 2020,
    },
]

DEFAULT_API_URL = (
    "https://openlibrary.org/search.json?q=cybersecurity&limit=10&fields=title,author_name,first_publish_year"
)


def get_default_db_path() -> Path:
    base_dir = Path(__file__).resolve().parent.parent
    db_dir = base_dir / "data"
    db_dir.mkdir(parents=True, exist_ok=True)
    return db_dir / "books.db"


def fetch_books_from_api(
    api_url: str = DEFAULT_API_URL, timeout_seconds: float = 4.0
) -> Tuple[List[Dict[str, Any]], str]:
    logger.info(f"Fetching books from API: {api_url}")
    try:
        response = requests.get(
            api_url,
            timeout=timeout_seconds,
            headers={"User-Agent": "BookFetcher/1.0"},
        )
        response.raise_for_status()
        data = response.json()

        docs = data.get("docs", [])
        if not docs:
            logger.warning("Empty API response; using fallback dataset.")
            return FALLBACK_BOOKS, "fallback (empty response)"

        books: List[Dict[str, Any]] = []
        for item in docs:
            title = str(item.get("title", "")).strip()
            authors = item.get("author_name", [])
            author = authors[0] if isinstance(authors, list) and authors else "Unknown Author"
            year = item.get("first_publish_year")
            try:
                year_int = int(year) if year is not None else None
            except (ValueError, TypeError):
                year_int = None

            if title:
                books.append(
                    {
                        "title": title,
                        "author": str(author).strip(),
                        "publication_year": year_int,
                    }
                )

        if books:
            logger.info(f"Retrieved {len(books)} books from API.")
            return books, "external_api"

    except requests.exceptions.Timeout:
        logger.warning(f"Request timed out after {timeout_seconds}s. Engaging fallback.")
    except requests.exceptions.RequestException as exc:
        logger.warning(f"API request failed ({exc}). Engaging fallback.")
    except Exception as exc:
        logger.warning(f"Error parsing API response ({exc}). Engaging fallback.")

    return FALLBACK_BOOKS, "fallback (network error)"


def init_db(db_path: Path | str) -> sqlite3.Connection:
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row

    with conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                publication_year INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(title, author)
            );
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_books_author ON books(author);")
    return conn


def store_books(db_path: Path | str, books: List[Dict[str, Any]]) -> Tuple[int, int]:
    conn = init_db(db_path)
    inserted = 0

    with conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM books")
        initial_count = cur.fetchone()[0]

        insert_query = """
            INSERT OR IGNORE INTO books (title, author, publication_year)
            VALUES (?, ?, ?);
        """
        for b in books:
            cur.execute(
                insert_query,
                (b["title"], b["author"], b.get("publication_year")),
            )

        cur.execute("SELECT COUNT(*) FROM books")
        final_count = cur.fetchone()[0]
        inserted = final_count - initial_count

    conn.close()
    duplicates = len(books) - inserted
    logger.info(f"Database sync: {inserted} inserted, {duplicates} duplicate(s) ignored.")
    return inserted, duplicates


def get_all_books(db_path: Path | str) -> List[Tuple[Any, ...]]:
    conn = init_db(db_path)
    with conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, title, author, publication_year, created_at FROM books ORDER BY id ASC;"
        )
        rows = cur.fetchall()
    conn.close()
    return [tuple(r) for r in rows]


def display_books_table(rows: List[Tuple[Any, ...]], source_desc: str = "") -> None:
    print("\n" + "=" * 86)
    print(f" Stored Books Catalog [data/books.db] (Source: {source_desc})")
    print("=" * 86)

    if not rows:
        print(" [No records found]")
        print("=" * 86 + "\n")
        return

    headers = ("ID", "Title", "Author", "Year", "Stored At (UTC)")
    str_rows = [
        (
            str(r[0]),
            (r[1][:42] + "...") if len(str(r[1])) > 45 else str(r[1]),
            (r[2][:22] + "...") if len(str(r[2])) > 25 else str(r[2]),
            str(r[3]) if r[3] is not None else "N/A",
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
    db_path = get_default_db_path()
    books, source = fetch_books_from_api()
    store_books(db_path, books)
    records = get_all_books(db_path)
    display_books_table(records, source_desc=source)


if __name__ == "__main__":
    main()
