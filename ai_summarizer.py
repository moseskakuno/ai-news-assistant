
import os

from dotenv import load_dotenv
from openai import OpenAI
from language_service import get_language_instruction


# Load environment variables
load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("OPENAI_MODEL")


# Validate configuration
if not API_KEY:
    raise ValueError("OPENAI_API_KEY is missing from .env")

if not MODEL:
    raise ValueError("OPENAI_MODEL is missing from .env")


# Initialize OpenAI client
client = OpenAI(api_key=API_KEY)


def generate_article_summary(article, language="English"):
    """
    Generate an individual AI-powered summary of a news article.

    Prefer extracted article text. Use the RSS summary only
    when full article text is unavailable.
    """

    title = article.get("title", "Untitled")
    publisher = article.get("source", "Unknown")
    published_at = article.get("published_at", "Unknown")
    article_url = article.get("url", "")

    article_content = (
        article.get("content")
        or article.get("summary")
        or ""
    ).strip()

    content_type = article.get("content_type", "unknown")

    if not article_content:
        return (
            "A detailed summary is unavailable because "
            "no article text or RSS summary could be retrieved."
        )

    # Avoid presenting a short RSS snippet as a full article summary.
    if content_type == "rss_summary" and len(article_content) < 500:
        return (
            "A detailed summary is unavailable because the publisher "
            "did not provide enough article text. "
            "Please consult the original article for further details."
        )

    language_instruction = get_language_instruction(language)

    instructions = f"""
You are a professional international news journalist.

Create an accurate, readable summary of the supplied news article.

Requirements:

1. Aim for approximately 200 words when sufficient article
   information is available.
2. Use only facts explicitly stated in the supplied material.
3. Never invent names, dates, statistics, quotations, events,
   explanations, or background information.
4. Do not use external knowledge or assumptions.
5. Preserve the meaning and context of the original reporting.
6. Explain the main development and its reported significance
   only when the supplied text supports that explanation.
7. Use a neutral, factual, professional journalistic tone.
8. Do not reproduce long passages from the original article.
9. Do not create information that is absent from the source.
10. If the supplied information is limited, write a shorter
    summary rather than adding unsupported details.
11. Do not claim that the full article was available unless
    full article text was actually supplied.
12. Do not include a fabricated conclusion or prediction.

{language_instruction}
"""

    try:
        response = client.responses.create(
            model=MODEL,
            instructions=instructions,
            input=f"""
Summarize the following news article.

Headline: {title}
Publisher: {publisher}
Publication date: {published_at}
Original URL: {article_url}
Information type: {content_type}

Available article information:

{article_content}
"""
        )

        return response.output_text.strip()

    except Exception as error:
        raise RuntimeError(
            f"Could not generate the article summary: {error}"
        ) from error


def generate_news_digest(articles, country, language="English"):
    """
    Generate an AI-powered news digest using supplied
    article metadata and RSS summaries.
    """

    if not articles:
        return "No articles are available for summarization."

    news_items = []

    for index, article in enumerate(articles, start=1):
        news_items.append(
            f"""
Article {index}
Headline: {article['title']}
Publisher: {article['source']}
Published: {article.get('published_at', 'Unknown')}
Available information: {article.get('summary', '')}
Information type: {article.get('content_type', 'unknown')}
Original URL: {article['url']}
"""
        )

    news_context = "\n".join(news_items)

    instructions = """
You are a professional international news editor.

Create a clear, factual daily news digest using only the
information explicitly provided in the supplied articles.

Requirements:

1. Organize the news into meaningful topic sections.
2. Explain important developments in clear language.
3. Do not invent or add facts, dates, names, quotes,
   statistics, or other details.
4. Use only information explicitly present in the
   supplied article metadata and RSS summaries.
5. Do not use external knowledge, assumptions, or
   inference to complete missing information.
6. Do not expand people's names or titles unless the
   supplied information explicitly provides them.
7. Do not treat information in a headline as proof of
   additional details not present in the supplied material.
8. Preserve the original article URLs exactly.
9. Identify the publisher for every story.
10. If information is insufficient, clearly say so.
11. Use a neutral, factual, professional tone.
12. Avoid repeating the same story.
13. Make clear that the digest is based on RSS summaries,
    not necessarily full articles.
"""

    language_instruction = get_language_instruction(language)
    instructions = instructions + "\n" + language_instruction

    try:
        response = client.responses.create(
            model=MODEL,
            instructions=instructions,
            input=f"""
Prepare a daily news digest for {country}.

Here are the available news articles:

{news_context}

Use only the supplied information.
"""
        )

        return response.output_text

    except Exception as error:
        raise RuntimeError(
            f"Could not generate the AI news digest: {error}"
        ) from error
