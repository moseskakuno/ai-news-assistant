
import pycountry


# Country-specific news language and Google News edition settings.
# The keys are ISO 3166-1 alpha-2 country codes.
COUNTRY_LANGUAGES = {
    "DE": {
        "language": "German",
        "hl": "de-DE",
        "ceid_language": "de",
    },
    "KE": {
        "language": "English",
        "hl": "en-KE",
        "ceid_language": "en",
    },
    "UG": {
        "language": "English",
        "hl": "en-UG",
        "ceid_language": "en",
    },
    "JP": {
        "language": "Japanese",
        "hl": "ja-JP",
        "ceid_language": "ja",
    },
    "FR": {
        "language": "French",
        "hl": "fr-FR",
        "ceid_language": "fr",
    },
    "BR": {
        "language": "Portuguese",
        "hl": "pt-BR",
        "ceid_language": "pt-BR",
    },
    "ZA": {
        "language": "English",
        "hl": "en-ZA",
        "ceid_language": "en",
    },
    "US": {
        "language": "English",
        "hl": "en-US",
        "ceid_language": "en",
    },
    "GB": {
        "language": "English",
        "hl": "en-GB",
        "ceid_language": "en",
    },
    "CA": {
        "language": "English",
        "hl": "en-CA",
        "ceid_language": "en",
    },
    "AU": {
        "language": "English",
        "hl": "en-AU",
        "ceid_language": "en",
    },
    "IN": {
        "language": "English",
        "hl": "en-IN",
        "ceid_language": "en",
    },
    "ES": {
        "language": "Spanish",
        "hl": "es-ES",
        "ceid_language": "es",
    },
    "MX": {
        "language": "Spanish",
        "hl": "es-MX",
        "ceid_language": "es",
    },
    "AR": {
        "language": "Spanish",
        "hl": "es-AR",
        "ceid_language": "es",
    },
    "PT": {
        "language": "Portuguese",
        "hl": "pt-PT",
        "ceid_language": "pt-PT",
    },
    "IT": {
        "language": "Italian",
        "hl": "it-IT",
        "ceid_language": "it",
    },
    "NL": {
        "language": "Dutch",
        "hl": "nl-NL",
        "ceid_language": "nl",
    },
    "BE": {
        "language": "Dutch",
        "hl": "nl-BE",
        "ceid_language": "nl",
    },
    "CH": {
        "language": "German",
        "hl": "de-CH",
        "ceid_language": "de",
    },
    "AT": {
        "language": "German",
        "hl": "de-AT",
        "ceid_language": "de",
    },
    "RU": {
        "language": "Russian",
        "hl": "ru-RU",
        "ceid_language": "ru",
    },
    "CN": {
        "language": "Chinese",
        "hl": "zh-CN",
        "ceid_language": "zh-CN",
    },
    "TW": {
        "language": "Chinese",
        "hl": "zh-TW",
        "ceid_language": "zh-TW",
    },
    "KR": {
        "language": "Korean",
        "hl": "ko-KR",
        "ceid_language": "ko",
    },
    "SA": {
        "language": "Arabic",
        "hl": "ar-SA",
        "ceid_language": "ar",
    },
    "EG": {
        "language": "Arabic",
        "hl": "ar-EG",
        "ceid_language": "ar",
    },
    "NG": {
        "language": "English",
        "hl": "en-NG",
        "ceid_language": "en",
    },
    "GH": {
        "language": "English",
        "hl": "en-GH",
        "ceid_language": "en",
    },
    "IE": {
        "language": "English",
        "hl": "en-IE",
        "ceid_language": "en",
    },
    "NZ": {
        "language": "English",
        "hl": "en-NZ",
        "ceid_language": "en",
    },
    "PH": {
        "language": "English",
        "hl": "en-PH",
        "ceid_language": "en",
    },
    "PK": {
        "language": "English",
        "hl": "en-PK",
        "ceid_language": "en",
    },
    "BD": {
        "language": "Bengali",
        "hl": "bn-BD",
        "ceid_language": "bn",
    },
    "TH": {
        "language": "Thai",
        "hl": "th-TH",
        "ceid_language": "th",
    },
    "VN": {
        "language": "Vietnamese",
        "hl": "vi-VN",
        "ceid_language": "vi",
    },
    "ID": {
        "language": "Indonesian",
        "hl": "id-ID",
        "ceid_language": "id",
    },
    "TR": {
        "language": "Turkish",
        "hl": "tr-TR",
        "ceid_language": "tr",
    },
    "GR": {
        "language": "Greek",
        "hl": "el-GR",
        "ceid_language": "el",
    },
    "PL": {
        "language": "Polish",
        "hl": "pl-PL",
        "ceid_language": "pl",
    },
    "SE": {
        "language": "Swedish",
        "hl": "sv-SE",
        "ceid_language": "sv",
    },
    "NO": {
        "language": "Norwegian",
        "hl": "no",
        "ceid_language": "no",
    },
    "DK": {
        "language": "Danish",
        "hl": "da-DK",
        "ceid_language": "da",
    },
    "FI": {
        "language": "Finnish",
        "hl": "fi-FI",
        "ceid_language": "fi",
    },
    "UA": {
        "language": "Ukrainian",
        "hl": "uk-UA",
        "ceid_language": "uk",
    },
        "BB": {
        "hl": "en-GB",
        "gl": "BB",
        "ceid": "BB:en",
    },
}


def get_countries():
    """Return an alphabetically sorted list of countries."""

    countries = sorted(
        pycountry.countries,
        key=lambda country: country.name
    )

    return [country.name for country in countries]


def get_country_code(country_name):
    """Return the ISO 3166-1 alpha-2 code for a country."""

    country = pycountry.countries.get(name=country_name)

    if country is None:
        raise ValueError(
            f"Country not found: {country_name}"
        )

    return country.alpha_2


def get_country_details(country_name):
    """Return a country's name and ISO country codes."""

    country = pycountry.countries.get(name=country_name)

    if country is None:
        raise ValueError(
            f"Country not found: {country_name}"
        )

    return {
        "name": country.name,
        "alpha_2": country.alpha_2,
        "alpha_3": country.alpha_3,
        "numeric": country.numeric,
    }


def get_country_language(country_name):
    """
    Return the preferred news language and Google News
    edition settings for a country.

    Countries without a specific mapping use English
    as a fallback.
    """

    country_code = get_country_code(country_name)

    settings = COUNTRY_LANGUAGES.get(
        country_code,
        {
            "language": "English",
            "hl": "en-US",
            "ceid_language": "en",
        },
    )

    return {
        "country": country_name,
        "country_code": country_code,
        **settings,
    }
