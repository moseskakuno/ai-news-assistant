
import re
import unicodedata

from urllib.parse import (
    urlsplit,
    urlunsplit,
    parse_qsl,
    urlencode,
)


def normalize_url(url):
    """Normalize an article URL to help identify duplicates."""

    if not url:
        return ""

    try:
        parts = urlsplit(url.strip())

        # Remove common tracking parameters.
        tracking_parameters = {
            "utm_source",
            "utm_medium",
            "utm_campaign",
            "utm_term",
            "utm_content",
            "fbclid",
            "gclid",
        }

        query_parameters = [
            (key, value)
            for key, value in parse_qsl(parts.query)
            if key.lower() not in tracking_parameters
        ]

        hostname = (parts.hostname or "").lower()

        if hostname.startswith("www."):
            hostname = hostname[4:]

        port = parts.port

        netloc = hostname

        if port and not (
            (parts.scheme.lower() == "https" and port == 443)
            or (parts.scheme.lower() == "http" and port == 80)
        ):
            netloc = f"{hostname}:{port}"

        path = parts.path.rstrip("/")

        return urlunsplit(
            (
                parts.scheme.lower(),
                netloc,
                path,
                urlencode(query_parameters),
                "",
            )
        )

    except (ValueError, TypeError):
        return url.strip()


def normalize_title(title):
    """Normalize headlines for duplicate comparison."""

    if not title:
        return ""

    title = unicodedata.normalize("NFKC", title)

    title = title.casefold()

    title = re.sub(r"[^\w\s]", " ", title)

    title = re.sub(r"\s+", " ", title)

    return title.strip()


def deduplicate_articles(articles):
    """
    Remove duplicate articles while preserving their original order.

    Articles are considered duplicates when:
    - Their normalized URLs match, or
    - Their normalized headlines and publishers match.
    """

    unique_articles = []

    seen_urls = set()
    seen_headlines = set()

    for article in articles:
        url = normalize_url(article.get("url", ""))

        title = normalize_title(article.get("title", ""))

        source = normalize_title(article.get("source", ""))

        headline_key = (source, title)

        if url and url in seen_urls:
            continue

        if title and headline_key in seen_headlines:
            continue

        if url:
            seen_urls.add(url)

        if title:
            seen_headlines.add(headline_key)

        unique_articles.append(article)

    return unique_articles
