
import requests
import feedparser

from bs4 import BeautifulSoup
from urllib.parse import urlencode, urljoin
from collections import Counter
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime, format_datetime

from source_manager import get_sources
from country_service import get_country_language
from deduplicator import deduplicate_articles


# Maximum permitted age for articles in the latest-news overview.
MAX_ARTICLE_AGE_DAYS = 7

# Government of Niue media releases.
NIUE_GOVERNMENT_URL = "https://www.gov.nu/media-releases/"


def clean_html(content):
    """Convert HTML content into readable plain text."""

    if not content:
        return ""

    soup = BeautifulSoup(content, "html.parser")
    return soup.get_text(" ", strip=True)


def parse_publication_date(date_string):
    """Parse RSS and webpage publication dates into UTC."""

    if not date_string:
        return None

    if "<" in date_string and ">" in date_string:
        soup = BeautifulSoup(date_string, "html.parser")
        date_element = soup.find(attrs={"content": True})

        if date_element:
            date_string = date_element.get("content", "")

    date_string = date_string.strip()

    try:
        published_date = parsedate_to_datetime(date_string)

        if published_date.tzinfo is None:
            published_date = published_date.replace(tzinfo=timezone.utc)

        return published_date.astimezone(timezone.utc)

    except (ValueError, TypeError, OverflowError):
        pass

    try:
        published_date = datetime.fromisoformat(
            date_string.replace("Z", "+00:00")
        )

        if published_date.tzinfo is None:
            published_date = published_date.replace(tzinfo=timezone.utc)

        return published_date.astimezone(timezone.utc)

    except (ValueError, TypeError, OverflowError):
        pass

    for date_format in (
        "%a, %b %d, %Y",
        "%B %d, %Y",
        "%b %d, %Y",
    ):
        try:
            published_date = datetime.strptime(date_string, date_format)

            return published_date.replace(tzinfo=timezone.utc)

        except (ValueError, TypeError, OverflowError):
            continue

    return None


def filter_recent_articles(
    articles,
    source_name,
    max_age_days=MAX_ARTICLE_AGE_DAYS,
):
    """Keep articles with valid dates within the configured age limit."""

    now = datetime.now(timezone.utc)
    oldest_allowed = now - timedelta(days=max_age_days)

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


def filter_saint_kitts_observer_articles(articles):
    """
    Keep Observer articles clearly related to Saint Kitts and Nevis.
    This filter is deliberately applied only to the Observer feed.
    """

    local_terms = (
        "saint kitts",
        "st. kitts",
        "st kitts",
        "nevis",
        "basseterre",
        "charlestown",
        "jessup",
        "cayon",
        "sandy point",
        "tabernacle",
        "sknis",
        "naspa",
        "nia ",
        "nia's",
        "nevis island administration",
        "federation",
    )

    relevant_articles = []

    for article in articles:
        searchable_text = (
            article.get("title", "")
            + " "
            + article.get("summary", "")
        ).casefold()

        if any(term in searchable_text for term in local_terms):
            relevant_articles.append(article)

    print(
        "[RELEVANCE] St. Kitts-Nevis Observer: "
        f"{len(relevant_articles)} of {len(articles)} "
        "articles retained."
    )

    return relevant_articles


def fetch_rss_feed(url, country, source_name, language):
    """Retrieve and normalize articles from an RSS feed."""

    print(f"[RSS] Requesting {source_name}: {url}")

    headers = {
        "User-Agent": "Mozilla/5.0"
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

        title = clean_html(entry.get("title", "Untitled"))

        published_at = entry.get("published", "")

        if not published_at:
            published_at = entry.get("updated", "")

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

                    published_at = format_datetime(parsed_datetime)

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


def fetch_niue_government():
    """Retrieve media releases from the Government of Niue."""

    source_name = "Government of Niue"
    country = "Niue"
    language = "English"

    print(
        f"[WEB] Requesting {source_name}: "
        f"{NIUE_GOVERNMENT_URL}"
    )

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 Chrome/120.0 Safari/537.36"
        )
    }

    response = requests.get(
        NIUE_GOVERNMENT_URL,
        headers=headers,
        timeout=30,
    )

    response.raise_for_status()

    print(
        f"[WEB] {source_name}: HTTP {response.status_code}, "
        f"{len(response.content)} bytes received."
    )

    soup = BeautifulSoup(response.text, "html.parser")
    articles = []

    for details in soup.select(".media-line-details"):
        heading = details.find(["h2", "h3", "h4"])

        if not heading:
            continue

        link = heading.find_parent("a", href=True)

        if not link:
            continue

        title = clean_html(heading.get_text(" ", strip=True))

        article_url = urljoin(
            NIUE_GOVERNMENT_URL,
            link["href"],
        )

        date_element = details.select_one(".media-date")

        if not date_element:
            continue

        published_at = date_element.get_text(" ", strip=True)

        if not title or not article_url or not published_at:
            continue

        articles.append({
            "title": title,
            "url": article_url,
            "source": source_name,
            "published_at": published_at,
            "language": language,
            "source_country": country,
            "summary": "",
        })

    print(
        f"[WEB RESULT] {source_name}: "
        f"{len(articles)} articles retrieved."
    )

    for article in articles:
        try:
            article_response = requests.get(
                article["url"],
                headers=headers,
                timeout=20,
            )

            article_response.raise_for_status()

            article_soup = BeautifulSoup(
                article_response.text,
                "html.parser",
            )

            paragraphs = []

            for paragraph in article_soup.find_all("p"):
                if "media-date" in paragraph.get("class", []):
                    continue

                text = clean_html(
                    paragraph.get_text(" ", strip=True)
                )

                if text and len(text) > 30:
                    paragraphs.append(text)

            article["summary"] = " ".join(paragraphs)[:4000]

        except requests.RequestException as error:
            print(
                f"[WEB WARNING] Could not retrieve article "
                f"content: {article['title']}: {error}"
            )

    return articles


def fetch_google_news(country):
    """Discover news using Google News."""

    country_settings = get_country_language(country)
    country_code = country_settings["country_code"]

    preferred_language = country_settings.get(
        "language",
        country_settings.get("preferred_language", "English"),
    )

    if country.strip().casefold() == "niue":
        parameters = {
            "q": "Niue when:7d",
            "hl": "en-NU",
            "gl": "NU",
            "ceid": "NU:en",
        }

        url = (
            "https://news.google.com/rss/search?"
            + urlencode(parameters)
        )

        print(
            "[GOOGLE NEWS] Requesting Niue-specific "
            "seven-day search."
        )

        articles = fetch_rss_feed(
            url=url,
            country=country,
            source_name="Google News",
            language="English",
        )

        articles = filter_recent_articles(
            articles,
            "Google News - Niue Search",
        )

        niue_terms = (
            "niue",
            "niuean",
            "vagahau",
            "alofi",
        )

        relevant_articles = []

        for article in articles:
            searchable_text = (
                article.get("title", "")
                + " "
                + article.get("summary", "")
            ).casefold()

            if any(term in searchable_text for term in niue_terms):
                relevant_articles.append(article)

        print(
            f"[GOOGLE NEWS] Niue relevance filter: "
            f"{len(relevant_articles)} of "
            f"{len(articles)} articles retained."
        )

        return relevant_articles

    if country.strip().casefold() == "saint barthélemy":
        parameters = {
            "q": '"Saint-Barthélemy" "Outre-mer La 1ère" when:30d',
            "hl": "fr-FR",
            "gl": "FR",
            "ceid": "FR:fr",
        }

        url = (
            "https://news.google.com/rss/search?"
            + urlencode(parameters)
        )

        print(
            "[GOOGLE NEWS] Requesting Saint Barthélemy "
            "French-language 30-day search."
        )

        articles = fetch_rss_feed(
            url=url,
            country=country,
            source_name="Google News",
            language="French",
        )

        articles = filter_recent_articles(
            articles,
            "Google News - Saint Barthélemy Search",
            max_age_days=30,
        )

        saint_barthelemy_terms = (
            "saint-barthélemy",
            "saint barthélemy",
            "saint-barth",
            "saint barth",
        )

        relevant_articles = []

        for article in articles:
            searchable_text = (
                article.get("title", "")
                + " "
                + article.get("summary", "")
            ).casefold()

            if any(
                term in searchable_text
                for term in saint_barthelemy_terms
            ):
                relevant_articles.append(article)

        print(
            f"[GOOGLE NEWS] Saint Barthélemy relevance filter: "
            f"{len(relevant_articles)} of "
            f"{len(articles)} articles retained."
        )

        return relevant_articles

    # Saint Martin (French part) uses a dedicated French-language search.
    if country.strip().casefold() == "saint martin (french part)":
        parameters = {
            "q": '"Saint-Martin" (Marigot OR Grand-Case OR SXM) when:30d',
            "hl": "fr-FR",
            "gl": "FR",
            "ceid": "FR:fr",
        }

        url = (
            "https://news.google.com/rss/search?"
            + urlencode(parameters)
        )

        print(
            "[GOOGLE NEWS] Requesting Saint Martin "
            "French-language 30-day search."
        )

        articles = fetch_rss_feed(
            url=url,
            country=country,
            source_name="Google News",
            language="French",
        )

        articles = filter_recent_articles(
            articles,
            "Google News - Saint Martin Search",
            max_age_days=30,
        )

        saint_martin_terms = (
            "saint-martin",
            "saint martin",
            "marigot",
            "grand-case",
            "grand case",
            "sxm",
        )

        relevant_articles = []

        for article in articles:
            searchable_text = (
                article.get("title", "")
                + " "
                + article.get("summary", "")
            ).casefold()

            if any(
                term in searchable_text
                for term in saint_martin_terms
            ):
                relevant_articles.append(article)

        print(
            f"[GOOGLE NEWS] Saint Martin relevance filter: "
            f"{len(relevant_articles)} of "
            f"{len(articles)} articles retained."
        )

        return relevant_articles

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

    Niue also uses its government media releases webpage.

    Saint Kitts and Nevis Observer articles receive an
    additional local relevance filter.

    Google News is used only when no configured local
    source returns usable recent articles.
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

    if country.strip().casefold() == "niue":
        try:
            niue_articles = fetch_niue_government()

            recent_niue_articles = filter_recent_articles(
                niue_articles,
                "Government of Niue",
            )

            if recent_niue_articles:
                article_groups.append(recent_niue_articles)
            else:
                print(
                    "[WEB WARNING] Government of Niue "
                    "has no articles within the freshness limit."
                )

        except requests.RequestException as error:
            print(
                f"[WEB ERROR] Government of Niue: "
                f"{type(error).__name__}: {error}"
            )

        except Exception as error:
            print(
                f"[WEB ERROR] Unexpected error for "
                f"Government of Niue: "
                f"{type(error).__name__}: {error}"
            )

    # Retrieve and filter articles from configured local RSS feeds.
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

            # Apply the additional filter only to the Observer feed
            # for Saint Kitts and Nevis. SKNIS remains unchanged.
            if (
                country.strip().casefold() == "saint kitts and nevis"
                and source_name.strip().casefold()
                == "st. kitts-nevis observer"
            ):
                recent_articles = filter_saint_kitts_observer_articles(
                    recent_articles
                )

            if recent_articles:
                article_groups.append(recent_articles)
            else:
                print(
                    f"[RSS WARNING] {source_name}: "
                    "No recent relevant articles available."
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

    # Use Google News if no local sources provide recent articles.
    if not article_groups:
        print(
            f"[NEWS WARNING] No recent local articles "
            f"retrieved for {country}."
        )

        print("[NEWS] Activating Google News fallback.")

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
            f"[NEWS] Recent local sources succeeded. "
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
    print(f"Configured local RSS feeds: {len(sources)}")
    print(f"Article groups retrieved: {len(article_groups)}")
    print(f"Articles before deduplication: {len(articles)}")
    print(f"Articles after deduplication: {len(unique_articles)}")
    print(f"Articles returned: {len(final_articles)}")

    print("[NEWS SUMMARY] Publisher distribution:")

    for publisher, count in publisher_counts.items():
        print(f"  {publisher}: {count}")

    print("=" * 60 + "\n") 

    return final_articles
