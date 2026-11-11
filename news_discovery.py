
import requests
import feedparser

from bs4 import BeautifulSoup
from urllib.parse import urlencode
from collections import Counter

from source_manager import get_sources
from country_service import get_country_language
from deduplicator import deduplicate_articles


def clean_html(content):
    """Convert HTML content into readable plain text."""

    if not content:
        return ""

    soup = BeautifulSoup(content, "html.parser")

    return soup.get_text(" ", strip=True)


def fetch_rss_feed(url, country, source_name, language):
    """Retrieve and normalize articles from an RSS feed."""

    print(f"[RSS] Requesting {source_name}: {url}")

    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; AI-News-Assistant/1.0)"
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=45,
    )

    response.raise_for_status()

    print(
        f"[RSS] {source_name}: HTTP {response.status_code}, "
        f"{len(response.content)} bytes received."
    )

    feed = feedparser.parse(response.content)

    if feed.bozo:
        print(
            f"[RSS WARNING] {source_name}: "
            f"Feed parsing warning: {feed.bozo_exception}"
        )

    articles = []

    for entry in feed.entries:

        article_url = entry.get("link", "")

        if not article_url:
            continue

        title = clean_html(
            entry.get("title", "Untitled")
        )

        article = {
            "title": title or "Untitled",
            "url": article_url,
            "source": source_name,
            "published_at": entry.get(
                "published",
                entry.get("updated", ""),
            ),
            "language": language,
            "source_country": country,
            "summary": clean_html(
                entry.get(
                    "summary",
                    entry.get("description", ""),
                )
            ),
        }

        articles.append(article)

    print(
        f"[RSS RESULT] {source_name}: "
        f"{len(articles)} articles retrieved."
    )

    if not articles:
        print(
            f"[RSS WARNING] {source_name}: "
            "The feed returned no usable articles."
        )

    return articles


def fetch_google_news(country):
    """
    Discover news using the country's preferred
    Google News language and regional edition.

    If the preferred edition returns no articles,
    try the English edition as a fallback.
    """

    country_settings = get_country_language(country)

    country_code = country_settings["country_code"]

    preferred_language = country_settings.get(
        "language",
        country_settings.get("preferred_language", "English"),
    )

    # Support both ceid_language and full ceid settings.
    ceid_setting = country_settings.get(
        "ceid_language",
        country_settings.get("ceid", ""),
    )

    if ":" in ceid_setting:
        ceid_language = ceid_setting.split(":")[-1]
    else:
        ceid_language = ceid_setting or "en"

    google_country_code = country_settings.get(
        "gl",
        country_code,
    )

    def retrieve_edition(hl, edition_language, language):
        """Retrieve articles from a specific Google News edition."""

        parameters = {
            "hl": hl,
            "gl": google_country_code,
            "ceid": f"{google_country_code}:{edition_language}",
        }

        url = (
            "https://news.google.com/rss?"
            + urlencode(parameters)
        )

        print(
            f"[GOOGLE NEWS] Requesting {country} edition: "
            f"{url}"
        )

        return fetch_rss_feed(
            url=url,
            country=country,
            source_name="Google News",
            language=language,
        )

    print(
        f"[GOOGLE NEWS] Fallback activated for {country}."
    )

    # First attempt: country-specific preferred language.
    articles = retrieve_edition(
        hl=country_settings["hl"],
        edition_language=ceid_language,
        language=preferred_language,
    )

    if articles:
        return articles

    # Second attempt: English edition if needed.
    if preferred_language != "English":

        articles = retrieve_edition(
            hl="en-US",
            edition_language="en",
            language="English",
        )

        if articles:
            print(
                f"[GOOGLE NEWS] No articles found in the "
                f"preferred {preferred_language} edition "
                f"for {country}. Using English instead."
            )

    return articles


def fetch_news(country, max_records=20):
    """
    Retrieve news from configured local RSS feeds.

    Articles from multiple configured publishers are
    distributed fairly using round-robin selection.

    Google News is used only when no configured local
    RSS feed returns usable articles.
    """

    if not 1 <= max_records <= 100:
        raise ValueError(
            "max_records must be between 1 and 100."
        )

    print("\n" + "=" * 60)
    print(f"[NEWS] Starting news retrieval for: {country}")
    print("=" * 60)

    sources = get_sources(country)

    print(
        f"[NEWS] Configured local RSS sources: {len(sources)}"
    )

    if sources:
        for source in sources:
            print(
                f"[NEWS] Configured publisher: "
                f"{source.get('name', 'Unknown')}"
            )
    else:
        print(
            f"[NEWS WARNING] No local RSS sources "
            f"configured for {country}."
        )

    article_groups = []

    # Retrieve articles from configured local feeds.
    for source in sources:

        source_name = source.get("name", "Unknown publisher")

        try:
            source_articles = fetch_rss_feed(
                url=source["url"],
                country=country,
                source_name=source_name,
                language=source["language"],
            )

            if source_articles:
                article_groups.append(source_articles)

        except requests.RequestException as error:

            print(
                f"[RSS ERROR] {source_name}: "
                f"{type(error).__name__}: {error}"
            )

        except Exception as error:

            print(
                f"[RSS ERROR] Unexpected error for "
                f"{source_name}: {type(error).__name__}: {error}"
            )

    # Use Google News only if no local articles were retrieved.
    if not article_groups:

        print(
            f"[NEWS WARNING] No local articles retrieved "
            f"for {country}."
        )

        print(
            "[NEWS] Activating Google News fallback."
        )

        try:
            google_articles = fetch_google_news(country)

            if google_articles:
                article_groups.append(google_articles)

        except Exception as error:

            print(
                f"[GOOGLE NEWS ERROR] "
                f"{type(error).__name__}: {error}"
            )

            raise RuntimeError(
                f"Could not retrieve news for {country}: {error}"
            ) from error

    else:

        print(
            f"[NEWS] Local RSS feeds succeeded. "
            "Google News fallback will not be used."
        )

    # Distribute articles fairly across publishers.
    articles = []

    if article_groups:

        max_group_size = max(
            len(group) for group in article_groups
        )

        for index in range(max_group_size):

            for group in article_groups:

                if index < len(group):
                    articles.append(group[index])

    # Remove duplicate articles.
    unique_articles = deduplicate_articles(articles)

    final_articles = unique_articles[:max_records]

    # Report publisher distribution.
    publisher_counts = Counter(
        article.get("source", "Unknown")
        for article in final_articles
    )

    print("\n[NEWS SUMMARY]")
    print(f"Country: {country}")
    print(f"Configured local feeds: {len(sources)}")
    print(f"Article groups retrieved: {len(article_groups)}")
    print(f"Articles before deduplication: {len(articles)}")
    print(f"Articles after deduplication: {len(unique_articles)}")
    print(f"Articles returned: {len(final_articles)}")

    print("[NEWS SUMMARY] Publisher distribution:")

    for publisher, count in publisher_counts.items():
        print(f"  {publisher}: {count}")

    print("=" * 60 + "\n")

    return final_articles
