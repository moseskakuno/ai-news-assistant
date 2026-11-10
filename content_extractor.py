
import requests

from bs4 import BeautifulSoup


def extract_article_content(url):
    """
    Extract readable article text from a publicly
    accessible news article.

    Returns an empty string if extraction fails or
    the retrieved page is not a genuine article.
    """

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (compatible; "
            "AI-News-Assistant/1.0)"
        )
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=15,
            allow_redirects=True,
        )

        response.raise_for_status()

        final_url = response.url.lower()

        # Reject common consent and login redirects.
        blocked_domains = [
            "consent.google.com",
            "accounts.google.com",
            "login.",
        ]

        if any(domain in final_url for domain in blocked_domains):
            print("Article extraction skipped: consent or login page.")
            return ""

        soup = BeautifulSoup(
            response.text,
            "html.parser",
        )

        page_title = (
            soup.title.get_text(" ", strip=True).lower()
            if soup.title
            else ""
        )

        # Reject common consent and access-denied pages.
        blocked_phrases = [
            "before you continue",
            "we use cookies",
            "consent required",
            "access denied",
            "sign in to continue",
        ]

        if any(phrase in page_title for phrase in blocked_phrases):
            print("Article extraction skipped: non-article page.")
            return ""

        # Remove elements that do not contain article content.
        for element in soup([
            "script",
            "style",
            "nav",
            "header",
            "footer",
            "aside",
            "form",
            "noscript",
        ]):
            element.decompose()

        # Look for the main article container.
        article = soup.find("article")

        if not article:
            article = soup.find("main")

        if not article:
            article = soup.body

        if not article:
            return ""

        # Extract paragraph text.
        paragraphs = article.find_all("p")

        content = "\n\n".join(
            paragraph.get_text(" ", strip=True)
            for paragraph in paragraphs
            if len(paragraph.get_text(strip=True)) > 40
        )

        content = content.strip()

        # Reject pages without enough article text.
        if len(content) < 200:
            print("Article extraction skipped: insufficient article text.")
            return ""

        return content

    except requests.RequestException as error:
        print(f"Could not retrieve article: {error}")
        return ""

    except Exception as error:
        print(f"Could not extract article content: {error}")
        return ""
