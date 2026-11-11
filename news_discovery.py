
import requests
import feedparser

from bs4 import BeautifulSoup
from urllib.parse import urlencode

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

    headers = {
        "User-Agent": "AI-News-Assistant/1.0"
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=20,
    )

    response.raise_for_status()

    feed = feedparser.parse(response.content)

    articles = []

    for entry in feed.entries:

        article_url = entry.get("link", "")

        if not article_url:
            continue

        # Always use the configured publisher name.
        publisher = source_name

        # Remove HTML markup from article titles.
        title = clean_html(
            entry.get("title", "Untitled")
        )

        article = {
            "title": title or "Untitled",
            "url": article_url,
            "source": publisher,
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

    preferred_language = country_settings["language"]

    def retrieve_edition(hl, ceid_language, language):
        """Retrieve articles from a specific Google News edition."""

        parameters = {
            "hl": hl,
            "gl": country_code,
            "ceid": f"{country_code}:{ceid_language}",
        }

        url = (
            "https://news.google.com/rss?"
            + urlencode(parameters)
        )

        return fetch_rss_feed(
            url=url,
            country=country,
            source_name="Google News",
            language=language,
        )

    # First attempt: country-specific preferred language.
    articles = retrieve_edition(
        hl=country_settings["hl"],
        ceid_language=country_settings["ceid_language"],
        language=preferred_language,
    )

    if articles:
        return articles

    # Second attempt: English edition if the preferred
    # language edition returned no articles.
    if preferred_language != "English":

        articles = retrieve_edition(
            hl="en-US",
            ceid_language="en",
            language="English",
        )

        if articles:
            print(
                f"No articles found in the preferred "
                f"{preferred_language} edition for {country}. "
                "Using the English edition instead."
            )

    return articles


def fetch_news(country, max_records=20):
    """
    Retrieve news from configured local RSS feeds.

    Articles from multiple configured publishers are
    distributed fairly using round-robin selection.

    If no local feeds are available or all configured
    feeds return no articles, use country-specific
    Google News RSS discovery.
    """

    if not 1 <= max_records <= 100:
        raise ValueError(
            "max_records must be between 1 and 100."
        )

    sources = get_sources(country)

    article_groups = []

    # Retrieve articles from configured local feeds.
    if sources:

        for source in sources:

            try:
                source_articles = fetch_rss_feed(
                    url=source["url"],
                    country=country,
                    source_name=source["name"],
                    language=source["language"],
                )

                if source_articles:
                    article_groups.append(source_articles)

            except requests.RequestException as error:

                print(
                    f"Could not retrieve {source['name']}: {error}"
                )

    # Use Google News RSS if no local articles were retrieved.
    if not article_groups:

        try:
            google_articles = fetch_google_news(country)

            if google_articles:
                article_groups.append(google_articles)

        except requests.RequestException as error:

            raise RuntimeError(
                f"Could not retrieve news for {country} "
                f"from Google News RSS: {error}"
            ) from error

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

    return unique_articles[:max_records]
