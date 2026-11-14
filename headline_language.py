
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException


# Make language detection reproducible.
DetectorFactory.seed = 0


def detect_headline_language(headline):
    """
    Detect the language of a news headline.

    Return an ISO language code such as 'en', 'de',
    'fr', or None when detection is uncertain.
    """

    if not headline or len(headline.strip()) < 15:
        return None

    try:
        language = detect(headline.strip())
        return language

    except LangDetectException:
        return None
