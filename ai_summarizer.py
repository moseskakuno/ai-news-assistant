
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
14. Write the digest in English.
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
