
import sqlite3
from pathlib import Path
from datetime import datetime, timezone


# Store the database in the project directory.
DATABASE_PATH = Path(__file__).resolve().parent / "news_assistant.db"


def get_connection():
    """Create a connection to the SQLite database."""

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    return connection


def initialize_database():
    """Create the database tables if they do not exist."""

    with get_connection() as connection:

        # Articles table
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                url TEXT NOT NULL UNIQUE,
                source TEXT,
                published_at TEXT,
                language TEXT,
                source_country TEXT NOT NULL,
                summary TEXT,
                content_type TEXT,
                fetched_at TEXT NOT NULL
            )
            """
        )

        # Daily news digests table
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS digests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                country TEXT NOT NULL,
                language TEXT NOT NULL,
                content TEXT NOT NULL,
                article_count INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )

        # Individual AI-generated article summaries table
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS article_summaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                article_url TEXT NOT NULL,
                language TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL,
                UNIQUE(article_url, language)
            )
            """
        )


def save_articles(articles):
    """Save articles and update existing records by URL."""

    if not articles:
        return 0

    fetched_at = datetime.now(timezone.utc).isoformat()

    saved_count = 0

    with get_connection() as connection:

        for article in articles:

            connection.execute(
                """
                INSERT INTO articles (
                    title,
                    url,
                    source,
                    published_at,
                    language,
                    source_country,
                    summary,
                    content_type,
                    fetched_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)

                ON CONFLICT(url) DO UPDATE SET
                    title = excluded.title,
                    source = excluded.source,
                    published_at = excluded.published_at,
                    language = excluded.language,
                    source_country = excluded.source_country,
                    summary = excluded.summary,
                    content_type = excluded.content_type,
                    fetched_at = excluded.fetched_at
                """,
                (
                    article["title"],
                    article["url"],
                    article.get("source", "Unknown"),
                    article.get("published_at"),
                    article.get("language", "Unknown"),
                    article.get("source_country", "Unknown"),
                    article.get("summary", ""),
                    article.get("content_type", "unknown"),
                    fetched_at,
                ),
            )

            saved_count += 1

    return saved_count


def get_articles(country, limit=50):
    """Retrieve recently fetched articles for a country."""

    if limit < 1:
        raise ValueError("Limit must be greater than zero.")

    with get_connection() as connection:

        rows = connection.execute(
            """
            SELECT *
            FROM articles
            WHERE source_country = ?
            ORDER BY fetched_at DESC
            LIMIT ?
            """,
            (country, limit),
        ).fetchall()

    return [dict(row) for row in rows]


def save_article_summary(article_url, language, content):
    """Save or update an individual AI-generated article summary."""

    if not article_url or not language or not content:
        raise ValueError(
            "Article URL, language, and summary content are required."
        )

    created_at = datetime.now(timezone.utc).isoformat()

    with get_connection() as connection:

        connection.execute(
            """
            INSERT INTO article_summaries (
                article_url,
                language,
                content,
                created_at
            )
            VALUES (?, ?, ?, ?)

            ON CONFLICT(article_url, language) DO UPDATE SET
                content = excluded.content,
                created_at = excluded.created_at
            """,
            (
                article_url,
                language,
                content,
                created_at,
            ),
        )


def get_article_summary(article_url, language):
    """Retrieve an individual article summary in a specific language."""

    with get_connection() as connection:

        row = connection.execute(
            """
            SELECT *
            FROM article_summaries
            WHERE article_url = ? AND language = ?
            """,
            (article_url, language),
        ).fetchone()

    return dict(row) if row else None


def get_article_summaries(article_urls, language):
    """Retrieve saved summaries for multiple articles in one language."""

    if not article_urls:
        return {}

    placeholders = ",".join("?" for _ in article_urls)

    query = f"""
        SELECT *
        FROM article_summaries
        WHERE article_url IN ({placeholders})
        AND language = ?
    """

    with get_connection() as connection:

        rows = connection.execute(
            query,
            (*article_urls, language),
        ).fetchall()

    return {
        row["article_url"]: dict(row)
        for row in rows
    }


def save_digest(country, language, content, article_count):
    """Save a generated AI news digest."""

    created_at = datetime.now(timezone.utc).isoformat()

    with get_connection() as connection:

        connection.execute(
            """
            INSERT INTO digests (
                country,
                language,
                content,
                article_count,
                created_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                country,
                language,
                content,
                article_count,
                created_at,
            ),
        )


def get_latest_digest(country, language):
    """Retrieve the latest digest for a country and language."""

    with get_connection() as connection:

        row = connection.execute(
            """
            SELECT *
            FROM digests
            WHERE country = ? AND language = ?
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (country, language),
        ).fetchone()

    return dict(row) if row else None
