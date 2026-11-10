
NEWS_SOURCES = {
    "Germany": [
        {
            "name": "Deutschlandfunk",
            "url": "https://www.deutschlandfunk.de/nachrichten-100.rss",
            "language": "German",
        }
    ]
}


def get_sources(country):
    """Return the configured RSS sources for a country."""
    return NEWS_SOURCES.get(country, [])
