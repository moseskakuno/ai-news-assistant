
import requests
import feedparser

from bs4 import BeautifulSoup
from source_manager import get_sources
from deduplicator import deduplicate_articles


def clean_html(content):
    """Convert HTML content into readable plain text."""
    if not content:
        return ""

    soup = BeautifulSoup(content, "html.parser")
    return soup.get_text(" ", strip=True)


def fetch_news(country, max_records=20):
    """
    Retrieve news articles from configured RSS feeds.

    Returns normalized article metadata and available summaries.
    """

    if not 1 <= max_records <= 100:
        raise ValueError("max_records must be between 1 and 100.")

    sources = get_sources(country)

    if not sources:
        raise ValueError(
            f"No verified RSS sources configured for {country} yet."
        )

    articles = []

    headers = {
        "User-Agent": "AI-News-Assistant/1.0"
    }

    for source in sources:
        try:
            response = requests.get(
                source["url"],
                headers=headers,
                timeout=20,
            )

            response.raise_for_status()

            feed = feedparser.parse(response.content)

            if feed.bozo and not feed.entries:
                continue

            for entry in feed.entries:
                article = {
                    "title": entry.get("title", "Untitled"),
                    "url": entry.get("link", ""),
                    "source": source["name"],
                    "published_at": entry.get(
                        "published",
                        entry.get("updated", ""),
                    ),
                    "language": source["language"],
                    "source_country": country,
                    "summary": clean_html(
                        entry.get(
                            "summary",
                            entry.get("description", ""),
                        )
                    ),
                }

                if article["url"]:
                    articles.append(article)

        except requests.RequestException as error:
            print(
                f"Could not retrieve {source['name']}: {error}"
            )

    # Remove duplicate articles based on their URLs.
    # Remove duplicate articles using the deduplication module.
    unique_articles = deduplicate_articles(articles)

    return unique_articles[:max_records]
