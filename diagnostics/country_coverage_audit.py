import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import pycountry

from source_manager import get_sources
from country_service import COUNTRY_LANGUAGES, get_country_language

countries = sorted(
    pycountry.countries,
    key=lambda country: country.name
)

rss_configured = []
without_rss = []
explicit_language = []
english_fallback = []

for country in countries:
    name = country.name
    code = country.alpha_2

    if get_sources(name):
        rss_configured.append(name)
    else:
        without_rss.append(name)

    if code in COUNTRY_LANGUAGES:
        explicit_language.append(name)
    else:
        english_fallback.append(name)

print("=" * 55)
print("AI NEWS ASSISTANT - COUNTRY COVERAGE AUDIT")
print("=" * 55)

print(f"Total countries: {len(countries)}")
print(f"Countries with RSS sources: {len(rss_configured)}")
print(f"Countries without RSS sources: {len(without_rss)}")
print(f"Countries with explicit language mappings: {len(explicit_language)}")
print(f"Countries using English fallback: {len(english_fallback)}")

print("\nCOUNTRIES WITHOUT RSS SOURCES:")
for name in without_rss:
    settings = get_country_language(name)
    print(f"- {name} ({settings['country_code']})")

print("\nCOUNTRIES USING ENGLISH FALLBACK:")
for name in english_fallback:
    print(f"- {name}")

print("\n" + "=" * 55)
print("Configuration does not guarantee successful live retrieval.")
print("Retrieval must be tested separately.")
print("=" * 55)
