
import requests
import feedparser

from bs4 import BeautifulSoup
from urllib.parse import urlencode
from collections import Counter
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime, format_datetime

from source_manager import get_sources
from country_service import get_country_language
from deduplicator import deduplicate_articles


# Maximum permitted age for articles in the latest-news overview.
MAX_ARTICLE_AGE_DAYS = 7


def clean_html(content):
    """Convert HTML content into readable plain text."""

    if not content:
        return ""

    soup = BeautifulSoup(content, "html.parser")

    return soup.get_text(" ", strip=True)


def parse_publication_date(date_string):
    """
    Parse RSS publication dates.

    Supports RFC-formatted dates and ISO-formatted dates.
    Returns a timezone-aware UTC datetime or None.
    """

    if not date_string:
        return None

    try:
        published_date = parsedate_to_datetime(date_string)

        if published_date.tzinfo is None:
            published_date = published_date.replace(
                tzinfo=timezone.utc
            )

        return published_date.astimezone(timezone.utc)

    except (ValueError, TypeError, OverflowError):

        try:
            published_date = datetime.fromisoformat(
                date_string.strip().replace("Z", "+00:00")
            )

            if published_date.tzinfo is None:
                published_date = published_date.replace(
                    tzinfo=timezone.utc
                )

            return published_date.astimezone(timezone.utc)

        except (ValueError, TypeError, OverflowError):
            return None


def filter_recent_articles(
    articles,
    source_name,
    max_age_days=MAX_ARTICLE_AGE_DAYS,
):
    """
    Keep articles with valid publication dates
    within the configured age limit.

    Missing, invalid, old and future-dated articles
    are excluded.
    """

    now = datetime.now(timezone.utc)

    oldest_allowed = now - timedelta(
        days=max_age_days
    )

    recent_articles = []

    rejected_old = 0
    rejected_invalid = 0
    rejected_future = 0

    for article in articles:

        published_date = parse_publication_date(
            article.get("published_at", "")
        )

        if published_date is None:
            rejected_invalid += 1
            continue

        if published_date < oldest_allowed:
            rejected_old += 1
            continue

        if published_date > now + timedelta(minutes=5):
            rejected_future += 1
            continue

        recent_articles.append(article)

    print(
        f"[DATE FILTER] {source_name}: "
        f"{len(recent_articles)} recent, "
        f"{rejected_old} too old, "
        f"{rejected_invalid} missing/invalid dates, "
        f"{rejected_future} future-dated."
    )

    return recent_articles


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

        # First try the original RSS publication date.
        published_at = entry.get("published", "")

        if not published_at:
            published_at = entry.get("updated", "")

        # If the original date is unavailable,
        # use feedparser's structured date.
        if not published_at:

            parsed_date = entry.get("published_parsed")

            if not parsed_date:
                parsed_date = entry.get("updated_parsed")

            if parsed_date:
                try:
                    parsed_datetime = datetime(
                        *parsed_date[:6],
                        tzinfo=timezone.utc,
                    )

                    published_at = format_datetime(
                        parsed_datetime
                    )

                except (ValueError, TypeError, OverflowError):
                    published_at = ""

        article = {
            "title": title or "Untitled",
            "url": article_url,
            "source": source_name,
            "published_at": published_at,
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

    If the preferred edition has no recent articles,
    try the English edition.
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

    # First attempt: preferred country-specific edition.
    articles = retrieve_edition(
        hl=country_settings["hl"],
        edition_language=ceid_language,
        language=preferred_language,
    )

    articles = filter_recent_articles(
        articles,
        "Google News",
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

        articles = filter_recent_articles(
            articles,
            "Google News English",
        )

        if articles:
            print(
                f"[GOOGLE NEWS] No recent articles found "
                f"in the preferred {preferred_language} "
                f"edition for {country}. Using English instead."
            )

    return articles


def fetch_news(country, max_records=20):
    """
    Retrieve recent news from configured local RSS feeds.

    Articles are filtered by publication date before
    round-robin distribution and duplicate removal.

    Google News is used only when no configured local
    RSS feed returns usable recent articles.
    """

    if not 1 <= max_records <= 100:
        raise ValueError(
            "max_records must be between 1 and 100."
        )

    print("\n" + "=" * 60)
    print(f"[NEWS] Starting news retrieval for: {country}")
    print("=" * 60)

    print(
        f"[NEWS] Maximum article age: "
        f"{MAX_ARTICLE_AGE_DAYS} days."
    )

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

    # Retrieve and filter articles from local feeds.
    for source in sources:

        source_name = source.get(
            "name",
            "Unknown publisher",
        )

        try:
            source_articles = fetch_rss_feed(
                url=source["url"],
                country=country,
                source_name=source_name,
                language=source["language"],
            )

            recent_articles = filter_recent_articles(
                source_articles,
                source_name,
            )

            if recent_articles:
                article_groups.append(recent_articles)

            else:
                print(
                    f"[RSS WARNING] {source_name}: "
                    "No recent articles available."
                )

        except requests.RequestException as error:

            print(
                f"[RSS ERROR] {source_name}: "
                f"{type(error).__name__}: {error}"
            )

        except Exception as error:

            print(
                f"[RSS ERROR] Unexpected error for "
                f"{source_name}: "
                f"{type(error).__name__}: {error}"
            )

    # Use Google News if no local feeds provide recent articles.
    if not article_groups:

        print(
            f"[NEWS WARNING] No recent local articles "
            f"retrieved for {country}."
        )

        print(
            "[NEWS] Activating Google News fallback."
        )

        try:
            google_articles = fetch_google_news(country)

            if google_articles:
                article_groups.append(google_articles)

            else:
                print(
                    "[GOOGLE NEWS WARNING] "
                    "No recent Google News articles found."
                )

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
            f"[NEWS] Recent local RSS feeds succeeded. "
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
    print(f"Maximum article age: {MAX_ARTICLE_AGE_DAYS} days")
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
