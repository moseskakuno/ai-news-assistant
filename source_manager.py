
NEWS_SOURCES = {
    "Germany": [
        {
            "name": "Deutschlandfunk",
            "url": "https://www.deutschlandfunk.de/nachrichten-100.rss",
            "language": "German",
        }
    ],

    "Kenya": [
        {
            "name": "Daily Nation",
            "url": "https://nation.africa/kenya/rss.xml",
            "language": "English",
        },
        {
            "name": "The Standard",
            "url": "https://www.standardmedia.co.ke/rss/kenya.php",
            "language": "English",
        }
    ],
}


def get_sources(country):
    """Return the configured RSS sources for a country."""
    return NEWS_SOURCES.get(country, [])
