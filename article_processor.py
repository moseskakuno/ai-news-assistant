
from datetime import timezone
from email.utils import parsedate_to_datetime
from collections import Counter


def normalize_date(date_string):
    """Convert an RSS publication date into ISO format."""

    if not date_string:
        return None

    try:
        date = parsedate_to_datetime(date_string)

        if date.tzinfo is None:
            date = date.replace(tzinfo=timezone.utc)

        return date.isoformat()

    except (ValueError, TypeError, OverflowError):
        return None


def process_article(article):
    """Clean and standardize an RSS article."""

    title = article.get("title", "").strip()
    url = article.get("url", "").strip()
    summary = article.get("summary", "").strip()

    if not title or not url:
        return None

    if not url.startswith(("https://", "http://")):
        return None

    return {
        "title": title,
        "url": url,
        "source": article.get("source", "Unknown"),
        "published_at": normalize_date(
            article.get("published_at", "")
        ),
        "language": article.get("language", "Unknown"),
        "source_country": article.get("source_country", ""),
        "summary": summary[:3000],
        "content_type": "rss_summary",
    }


def process_articles(articles):
    """Process articles and identify repeated timestamps."""

    processed = []

    for article in articles:
        result = process_article(article)

        if result:
            processed.append(result)

    # Count how often each publication timestamp occurs.
    date_counts = Counter(
        article["published_at"]
        for article in processed
        if article["published_at"]
    )

    # Mark repeated timestamps as unreliable.
    for article in processed:
        published_at = article["published_at"]

        if not published_at:
            article["published_at"] = (
                "Publication time not individually provided"
            )

        elif date_counts[published_at] > 1:
            article["published_at"] = (
                "Publication time not individually verified"
            )

    return processed
