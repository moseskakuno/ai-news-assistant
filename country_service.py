
import pycountry


# Country-specific news language and Google News edition settings.
# Keys use ISO 3166-1 alpha-2 country codes.
COUNTRY_LANGUAGES = {
    "DE": {"language": "German", "hl": "de-DE", "ceid_language": "de"},
    "KE": {"language": "English", "hl": "en-KE", "ceid_language": "en"},
    "UG": {"language": "English", "hl": "en-UG", "ceid_language": "en"},
    "JP": {"language": "Japanese", "hl": "ja-JP", "ceid_language": "ja"},
    "FR": {"language": "French", "hl": "fr-FR", "ceid_language": "fr"},
    "BR": {"language": "Portuguese", "hl": "pt-BR", "ceid_language": "pt-BR"},
    "ZA": {"language": "English", "hl": "en-ZA", "ceid_language": "en"},
    "US": {"language": "English", "hl": "en-US", "ceid_language": "en"},
    "GB": {"language": "English", "hl": "en-GB", "ceid_language": "en"},
    "CA": {"language": "English", "hl": "en-CA", "ceid_language": "en"},

    "KH": {
        "language": "Khmer",
        "hl": "km-KH",
        "gl": "KH",
        "ceid_language": "km",
    },
    "CM": {
        "language": "French",
        "hl": "fr-CM",
        "gl": "CM",
        "ceid_language": "fr",
    },
    "CV": {
        "language": "Portuguese",
        "hl": "pt-CV",
        "gl": "CV",
        "ceid_language": "pt",
    },

    "AU": {"language": "English", "hl": "en-AU", "ceid_language": "en"},
    "IN": {"language": "English", "hl": "en-IN", "ceid_language": "en"},
    "ES": {"language": "Spanish", "hl": "es-ES", "ceid_language": "es"},
    "MX": {"language": "Spanish", "hl": "es-MX", "ceid_language": "es"},
    "AR": {"language": "Spanish", "hl": "es-AR", "ceid_language": "es"},
    "PT": {"language": "Portuguese", "hl": "pt-PT", "ceid_language": "pt-PT"},
    "IT": {"language": "Italian", "hl": "it-IT", "ceid_language": "it"},
    "NL": {"language": "Dutch", "hl": "nl-NL", "ceid_language": "nl"},
    "BE": {"language": "Dutch", "hl": "nl-BE", "ceid_language": "nl"},
    "CH": {"language": "German", "hl": "de-CH", "ceid_language": "de"},
    "AT": {"language": "German", "hl": "de-AT", "ceid_language": "de"},
    "RU": {"language": "Russian", "hl": "ru-RU", "ceid_language": "ru"},
    "CN": {"language": "Chinese", "hl": "zh-CN", "ceid_language": "zh-CN"},
    "TW": {"language": "Chinese", "hl": "zh-TW", "ceid_language": "zh-TW"},
    "KR": {"language": "Korean", "hl": "ko-KR", "ceid_language": "ko"},
    "SA": {"language": "Arabic", "hl": "ar-SA", "ceid_language": "ar"},
    "EG": {"language": "Arabic", "hl": "ar-EG", "ceid_language": "ar"},
    "IQ": {"language": "Arabic", "hl": "ar-IQ", "gl": "IQ", "ceid_language": "ar"},
    "IL": {"language": "Hebrew", "hl": "he-IL", "gl": "IL", "ceid_language": "he"},
    "IR": {"language": "Persian", "hl": "fa-IR", "gl": "IR", "ceid_language": "fa"},

    # Africa
    "DZ": {"language": "French", "hl": "fr-FR", "gl": "DZ", "ceid_language": "fr"},
    "NG": {"language": "English", "hl": "en-NG", "ceid_language": "en"},
    "GH": {"language": "English", "hl": "en-GH", "ceid_language": "en"},
    "BY": {
        "language": "Russian",
        "hl": "ru-BY",
        "gl": "BY",
        "ceid_language": "ru",
    },
    "BJ": {
        "language": "French",
        "hl": "fr-BJ",
        "gl": "BJ",
        "ceid_language": "fr",
    },
    "BW": {
        "language": "English",
        "hl": "en-BW",
        "gl": "BW",
        "ceid_language": "en",
    },
    "BI": {
        "language": "French",
        "hl": "fr-BI",
        "gl": "BI",
        "ceid_language": "fr",
    },

    # Territories and islands
    "AS": {
        "language": "English",
        "hl": "en-AS",
        "gl": "AS",
        "ceid_language": "en",
    },
    "AI": {
        "language": "English",
        "hl": "en-AI",
        "gl": "AI",
        "ceid_language": "en",
    },
    "BM": {
        "language": "English",
        "hl": "en-BM",
        "gl": "BM",
        "ceid_language": "en",
    },
    "AW": {
        "language": "Papiamento",
        "hl": "pap-AW",
        "gl": "AW",
        "ceid_language": "en",
    },
    "AG": {
        "language": "English",
        "hl": "en-AG",
        "gl": "AG",
        "ceid_language": "en",
    },
    "BB": {
        "language": "English",
        "hl": "en-GB",
        "gl": "BB",
        "ceid_language": "en",
    },

    # Europe
    "IE": {"language": "English", "hl": "en-IE", "ceid_language": "en"},
    "NZ": {"language": "English", "hl": "en-NZ", "ceid_language": "en"},
    "PH": {"language": "English", "hl": "en-PH", "ceid_language": "en"},
    "PK": {"language": "English", "hl": "en-PK", "ceid_language": "en"},
    "BG": {
        "language": "Bulgarian",
        "hl": "bg-BG",
        "gl": "BG",
        "ceid_language": "bg",
    },
    "BN": {
        "language": "English",
        "hl": "en-BN",
        "gl": "BN",
        "ceid_language": "en",
    },
    "BA": {
        "language": "Bosnian",
        "hl": "bs-BA",
        "gl": "BA",
        "ceid_language": "bs",
    },
    "AL": {
        "language": "Albanian",
        "hl": "sq-AL",
        "gl": "AL",
        "ceid_language": "sq",
    },
    "AD": {
        "language": "Catalan",
        "hl": "ca-AD",
        "gl": "AD",
        "ceid_language": "ca",
    },
    "AM": {
        "language": "English",
        "hl": "en-AM",
        "gl": "AM",
        "ceid_language": "en",
    },
    "AZ": {
        "language": "Azerbaijani",
        "hl": "az-AZ",
        "gl": "AZ",
        "ceid_language": "az",
    },
    "UA": {"language": "Ukrainian", "hl": "uk-UA", "ceid_language": "uk"},
    "GR": {"language": "Greek", "hl": "el-GR", "ceid_language": "el"},
    "PL": {"language": "Polish", "hl": "pl-PL", "ceid_language": "pl"},
    "SE": {"language": "Swedish", "hl": "sv-SE", "ceid_language": "sv"},
    "NO": {"language": "Norwegian", "hl": "no", "ceid_language": "no"},
    "DK": {"language": "Danish", "hl": "da-DK", "ceid_language": "da"},
    "FI": {"language": "Finnish", "hl": "fi-FI", "ceid_language": "fi"},

    # Asia
    "BD": {"language": "Bengali", "hl": "bn-BD", "ceid_language": "bn"},
    "TH": {"language": "Thai", "hl": "th-TH", "ceid_language": "th"},
    "VN": {"language": "Vietnamese", "hl": "vi-VN", "ceid_language": "vi"},
    "ID": {"language": "Indonesian", "hl": "id-ID", "ceid_language": "id"},
    "TR": {"language": "Turkish", "hl": "tr-TR", "ceid_language": "tr"},
    "AF": {
        "language": "English",
        "hl": "en-US",
        "gl": "AF",
        "ceid_language": "en",
    },
"DO": {
    "language": "Spanish",
    "hl": "es-DO",
    "gl": "DO",
    "ceid_language": "es",
},
"GQ": {
    "language": "Spanish",
    "hl": "es-GQ",
    "gl": "GQ",
    "ceid_language": "es",
},
"ER": {
    "language": "English",
    "hl": "en-ER",
    "gl": "ER",
    "ceid_language": "en",
},
"EE": {
    "language": "Estonian",
    "hl": "et-EE",
    "gl": "EE",
    "ceid_language": "et",
},
"SZ": {
    "language": "English",
    "hl": "en-SZ",
    "gl": "SZ",
    "ceid_language": "en",
},
"ET": {
    "language": "Amharic",
    "hl": "am-ET",
    "gl": "ET",
    "ceid_language": "am",
},
"FK": {
    "language": "English",
    "hl": "en-FK",
    "gl": "FK",
    "ceid_language": "en",
},
    # South America
    "AO": {
        "language": "Portuguese",
        "hl": "pt-AO",
        "gl": "AO",
        "ceid_language": "pt-PT",
    },
    # Central African Republic
    "CF": {
    "language": "French",
    "hl": "fr-CF",
    "gl": "CF",
    "ceid_language": "fr",
},
    "TD": {
    "language": "French",
    "hl": "fr-TD",
    "gl": "TD",
    "ceid_language": "fr",
},
    "CN": {
    "language": "Chinese",
    "hl": "zh-CN",
    "gl": "CN",
    "ceid_language": "zh-Hans",
},
    "KM": {
    "language": "French",
    "hl": "fr-FR",
    "gl": "KM",
    "ceid_language": "fr",
},
    
"HR": {
    "language": "Croatian",
    "hl": "hr-HR",
    "gl": "HR",
    "ceid_language": "hr",
},

"CU": {
    "language": "Spanish",
    "hl": "es-CU",
    "gl": "CU",
    "ceid_language": "es",
},
"CY": {
    "language": "Greek",
    "hl": "el-CY",
    "gl": "CY",
    "ceid_language": "el",
},
"CZ": {
    "language": "Czech",
    "hl": "cs-CZ",
    "gl": "CZ",
    "ceid_language": "cs",
},
"DK": {
    "language": "Danish",
    "hl": "da-DK",
    "gl": "DK",
    "ceid_language": "da",
},
"DJ": {
    "language": "French",
    "hl": "fr-DJ",
    "gl": "DJ",
    "ceid_language": "fr",
},
"DM": {
    "language": "English",
    "hl": "en-DM",
    "gl": "DM",
    "ceid_language": "en",
},
    "PY": {"language": "Spanish", "hl": "es-PY", "ceid_language": "es"},
    "CL": {"language": "Spanish", "hl": "es-CL", "ceid_language": "es"},
    "PE": {"language": "Spanish", "hl": "es-PE", "ceid_language": "es"},
    "EC": {"language": "Spanish", "hl": "es-EC", "ceid_language": "es"},
    "BO": {"language": "Spanish", "hl": "es-BO", "ceid_language": "es"},
    "UY": {"language": "Spanish", "hl": "es-UY", "ceid_language": "es"},

    # Central America
    "PA": {"language": "Spanish", "hl": "es-PA", "ceid_language": "es"},
    "GT": {"language": "Spanish", "hl": "es-GT", "ceid_language": "es"},
    "HN": {"language": "Spanish", "hl": "es-HN", "ceid_language": "es"},
    "SV": {"language": "Spanish", "hl": "es-SV", "ceid_language": "es"},
    "NI": {"language": "Spanish", "hl": "es-NI", "ceid_language": "es"},
    "BZ": {"language": "English", "hl": "en-BZ", "ceid_language": "en"},

    # Caribbean
    "JM": {"language": "English", "hl": "en-JM", "ceid_language": "en"},
    "TT": {"language": "English", "hl": "en-TT", "ceid_language": "en"},
    
"FO": {
    "language": "Faroese",
    "hl": "fo-FO",
    "gl": "FO",
    "ceid_language": "fo",
},
"FJ": {
    "language": "English",
    "hl": "en-FJ",
    "gl": "FJ",
    "ceid_language": "en",
},
"FI": {
    "language": "Finnish",
    "hl": "fi-FI",
    "gl": "FI",
    "ceid_language": "fi",
},
"GF": {
    "language": "French",
    "hl": "fr-FR",
    "gl": "GF",
    "ceid_language": "fr",
},
"PF": {
    "language": "French",
    "hl": "fr-FR",
    "gl": "PF",
    "ceid_language": "fr",
},
"GA": {
    "language": "French",
    "hl": "fr-FR",
    "gl": "GA",
    "ceid_language": "fr",
},

"GM": {
    "language": "English",
    "hl": "en-GB",
    "gl": "GM",
    "ceid_language": "en",
},

"GE": {
    "language": "Georgian",
    "hl": "ka-GE",
    "gl": "GE",
    "ceid_language": "ka",
},

"GR": {
    "language": "Greek",
    "hl": "el-GR",
    "gl": "GR",
    "ceid_language": "el",
},

"GD": {
    "language": "English",
    "hl": "en-GD",
    "gl": "GD",
    "ceid_language": "en",
},
"GP": {
    "language": "French",
    "hl": "fr-FR",
    "gl": "GP",
    "ceid_language": "fr",
},
"GU": {
    "language": "English",
    "hl": "en-US",
    "gl": "GU",
    "ceid_language": "en",
},
"GG": {
    "language": "English",
    "hl": "en-GB",
    "gl": "GG",
    "ceid_language": "en",
},
"GN": {
    "language": "French",
    "hl": "fr-FR",
    "gl": "GN",
    "ceid_language": "fr",
},
"GW": {
    "language": "Portuguese",
    "hl": "pt-PT",
    "gl": "GW",
    "ceid_language": "pt",
},
"GY": {
    "language": "English",
    "hl": "en-GY",
    "gl": "GY",
    "ceid_language": "en",
},
"HT": {
    "language": "French",
    "hl": "fr-FR",
    "gl": "HT",
    "ceid_language": "fr",
},
    "HU": {
        "language": "Hungarian",
        "hl": "hu-HU",
        "gl": "HU",
        "ceid_language": "hu",
    },
        "IS": {
        "language": "Icelandic",
        "hl": "is-IS",
        "gl": "IS",
        "ceid_language": "is",
    },
    "JO": {"language": "Arabic", "hl": "ar-JO", "ceid_language": "ar"},
    "KZ": {"language": "Russian", "hl": "ru-KZ", "ceid_language": "ru"},
    "KW": {"language": "Arabic", "hl": "ar-KW", "ceid_language": "ar"},
    "KG": {"language": "Kyrgyz", "hl": "ky-KG", "ceid_language": "ky"},
    "LV": {
    "language": "Latvian",
    "hl": "lv-LV",
    "ceid_language": "lv",
},
    "LB": {
    "language": "Arabic",
    "hl": "ar-LB",
    "ceid_language": "ar",
},
    "LS": {
    "language": "English",
    "hl": "en-LS",
    "ceid_language": "en",
},
    "LR": {
    "language": "English",
    "hl": "en-LR",
    "ceid_language": "en",
},
    "LY": {
    "language": "Arabic",
    "hl": "ar-LY",
    "ceid_language": "ar",
},
    "LI": {
    "language": "German",
    "hl": "de-LI",
    "ceid_language": "de",
},
    "LT": {
    "language": "Lithuanian",
    "hl": "lt-LT",
    "ceid_language": "lt",
},
    "LU": {
    "language": "German",
    "hl": "de-LU",
    "ceid_language": "de",
},
    "MG": {
    "language": "French",
    "hl": "fr-FR",
    "ceid_language": "fr",
},
    "MY": {
    "language": "Malay",
    "hl": "ms-MY",
    "ceid_language": "ms",
},
  "ML": {
    "language": "French",
    "hl": "fr-FR",
    "ceid_language": "fr",
},
  "MT": {
    "language": "English",
    "hl": "en-GB",
    "ceid_language": "en",
},
      "MH": {
        "country": "Marshall Islands",
        "language": "English",
        "hl": "en-US",
        "ceid_language": "en",
    },
          "MQ": {
        "country": "Martinique",
        "language": "French",
        "hl": "fr-FR",
        "ceid_language": "fr",
    },
        "MR": {
        "country": "Mauritania",
        "language": "Arabic",
        "hl": "ar",
        "ceid_language": "ar",
    },
            "MU": {
        "country": "Mauritius",
        "language": "English",
        "hl": "en-US",
        "ceid_language": "en",
    },
        "YT": {
        "country": "Mayotte",
        "language": "French",
        "hl": "fr-FR",
        "ceid_language": "fr",
    },

}


# Alternative country names mapped to pycountry's official names.
COUNTRY_ALIASES = {
    "Cape Verde": "Cabo Verde",
    "Bolivia": "Bolivia, Plurinational State of",
    "Tanzania": "Tanzania, United Republic of",
    "Falkland Islands": "Falkland Islands (Malvinas)",
    "The Gambia": "Gambia",
    "Iran": "Iran, Islamic Republic of",
}


def _get_country(country_name):
    """Look up a country, supporting common alternative names."""

    lookup_name = COUNTRY_ALIASES.get(country_name, country_name)
    country = pycountry.countries.get(name=lookup_name)

    if country is None:
        raise ValueError(f"Country not found: {country_name}")

    return country


def get_countries():
    """Return an alphabetically sorted list of countries."""

    countries = sorted(
        pycountry.countries,
        key=lambda country: country.name
    )

    return [country.name for country in countries]


def get_country_code(country_name):
    """Return the ISO 3166-1 alpha-2 code for a country."""

    country = _get_country(country_name)
    return country.alpha_2


def get_country_details(country_name):
    """Return a country's name and ISO country codes."""

    country = _get_country(country_name)

    return {
        "name": country_name,
        "alpha_2": country.alpha_2,
        "alpha_3": country.alpha_3,
        "numeric": country.numeric,
    }


def get_country_language(country_name):
    """
    Return the preferred news language and Google News edition
    settings for a country.

    Countries without a specific mapping use English as fallback.
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
