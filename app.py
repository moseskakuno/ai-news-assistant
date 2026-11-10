
import hashlib

import streamlit as st

from news_discovery import fetch_news
from article_processor import process_articles

from ai_summarizer import (
    generate_news_digest,
    generate_article_summary,
)

from content_extractor import extract_article_content

from country_service import (
    get_countries,
    get_country_language,
)

from language_service import get_supported_languages

from news_database import (
    initialize_database,
    save_articles,
    save_digest,
    get_articles,
    get_latest_digest,
    save_article_summary,
    get_article_summary,
)


# Page configuration
st.set_page_config(
    page_title="AI News Assistant",
    page_icon="🌍",
    layout="wide",
)


# Initialize the database
initialize_database()


# Application heading
st.title("🌍 AI News Assistant")

st.markdown(
    """
    ### Your daily international news overview

    Explore news from countries around the world.
    Available news sources depend on the selected country.
    Generate AI-powered summaries in your preferred language.
    """
)

st.divider()


# Country selection
available_countries = get_countries()

country = st.selectbox(
    "Select a country",
    available_countries,
    index=available_countries.index("Germany"),
    key="selected_country",
)


# Automatically determine the country's preferred language
country_settings = get_country_language(country)

preferred_language = country_settings["language"]

supported_languages = get_supported_languages()

if preferred_language not in supported_languages:
    preferred_language = "English"


# Update the default language when the country changes.
# Preserve a user's manual language choice while the country
# remains unchanged.
if st.session_state.get("_language_country") != country:

    st.session_state["selected_language"] = preferred_language

    st.session_state["_language_country"] = country

    # Clear country-specific displayed results when switching countries.
    st.session_state.pop("articles", None)
    st.session_state.pop("country", None)
    st.session_state.pop("digest", None)
    st.session_state.pop("digest_country", None)
    st.session_state.pop("digest_language", None)
    st.session_state.pop("previous_digest", None)


# Number of articles
max_articles = st.slider(
    "Number of articles",
    min_value=5,
    max_value=30,
    value=10,
)


# Summary language selection
# The selected language is initialized in session state above.
# No index parameter is needed here.
selected_language = st.selectbox(
    "Choose your news summary language",
    supported_languages,
    key="selected_language",
)

st.caption(
    f"Preferred language for {country}: {preferred_language}. "
    "You can choose another summary language."
)


# Fetch news
if st.button("Fetch Latest News", type="primary"):

    with st.spinner(f"Retrieving news from {country}..."):

        try:
            raw_articles = fetch_news(
                country,
                max_records=max_articles,
            )

            articles = process_articles(raw_articles)

            if not articles:

                st.session_state.pop("articles", None)
                st.session_state.pop("digest", None)

                st.warning(
                    f"No articles were found for {country}. "
                    "News sources may not yet be available "
                    "for this country. Please try again later."
                )

            else:

                # Save articles to the database
                saved_count = save_articles(articles)

                st.session_state["articles"] = articles
                st.session_state["country"] = country

                # Clear any previous digest
                st.session_state.pop("digest", None)

                st.success(
                    f"{len(articles)} articles retrieved. "
                    f"{saved_count} articles saved or updated "
                    "in the database."
                )

        except Exception as error:

            st.error(f"News retrieval failed: {error}")


# Display retrieved articles
if "articles" in st.session_state:

    articles = st.session_state["articles"]

    selected_country = st.session_state["country"]

    st.divider()

    st.subheader(
        f"Latest News from {selected_country}"
    )

    st.caption(
        f"{len(articles)} articles retrieved"
    )

    for index, article in enumerate(articles, start=1):

        with st.container():

            st.markdown(
                f"### {article['title']}"
            )

            st.write(
                f"**Publisher:** {article['source']}"
            )

            st.write(
                f"**Published:** "
                f"{article.get('published_at') or 'Unknown'}"
            )

            if article.get("summary"):

                st.write(article["summary"])

            st.markdown(
                f"[Read original article]({article['url']})"
            )

            # Create a stable identifier for this article.
            article_id = hashlib.sha256(
                article["url"].encode("utf-8")
            ).hexdigest()[:16]

            # Individual AI article summary
            with st.expander(
                "📖 Read AI-generated article summary"
            ):

                try:

                    # Check whether a summary already exists
                    # for this article and selected language.
                    saved_summary = get_article_summary(
                        article["url"],
                        selected_language,
                    )

                    if saved_summary:

                        st.markdown(
                            saved_summary["content"]
                        )

                        st.caption(
                            "Previously generated summary "
                            f"({selected_language})."
                        )

                    else:

                        st.caption(
                            "Generate an approximately 200-word "
                            "summary of this article."
                        )

                        if st.button(
                            "Generate Article Summary",
                            key=f"summarize_{article_id}",
                        ):

                            with st.spinner(
                                "Extracting article and generating summary..."
                            ):

                                # Try to retrieve the original article text.
                                extracted_content = (
                                    extract_article_content(
                                        article["url"]
                                    )
                                )

                                # Prepare the article information
                                # for the AI summarizer.
                                summary_article = article.copy()

                                if extracted_content:

                                    summary_article["content"] = (
                                        extracted_content
                                    )

                                    summary_article["content_type"] = (
                                        "full_article_text"
                                    )

                                else:

                                    # Fall back to the RSS summary.
                                    summary_article["content"] = (
                                        article.get("summary", "")
                                    )

                                    summary_article["content_type"] = (
                                        "rss_summary"
                                    )

                                # Generate the individual summary.
                                generated_summary = (
                                    generate_article_summary(
                                        summary_article,
                                        language=selected_language,
                                    )
                                )

                                # Save the summary in SQLite.
                                save_article_summary(
                                    article["url"],
                                    selected_language,
                                    generated_summary,
                                )

                            st.success(
                                "Article summary generated and saved."
                            )

                            st.markdown(generated_summary)

                            if not extracted_content:

                                st.caption(
                                    "Note: Full article text could not "
                                    "be retrieved. The summary was "
                                    "based on the available RSS "
                                    "information, if sufficient."
                                )

                except Exception as error:

                    st.error(
                        f"Could not generate or retrieve "
                        f"the article summary: {error}"
                    )

            st.divider()


    # AI news digest
    st.subheader("🤖 AI Daily News Digest")

    if st.button("Generate AI News Summary"):

        with st.spinner(
            "Analyzing articles and preparing your digest..."
        ):

            try:

                digest = generate_news_digest(
                    articles,
                    selected_country,
                    language=selected_language,
                )

                # Save the generated digest to the database
                save_digest(
                    selected_country,
                    selected_language,
                    digest,
                    len(articles),
                )

                st.session_state["digest"] = digest

                st.session_state["digest_country"] = (
                    selected_country
                )

                st.session_state["digest_language"] = (
                    selected_language
                )

                st.success(
                    "Your news digest was generated and saved."
                )

            except Exception as error:

                st.error(
                    f"AI summarization failed: {error}"
                )


    # Display and download digest
    if "digest" in st.session_state:

        st.markdown(
            st.session_state["digest"]
        )

        st.download_button(
            label="Download News Digest",
            data=st.session_state["digest"],
            file_name="daily_news_digest.md",
            mime="text/markdown",
        )


# Previously saved articles
st.divider()

with st.expander("View Previously Saved Articles"):

    try:

        saved_articles = get_articles(
            country,
            limit=50,
        )

        if saved_articles:

            st.caption(
                f"{len(saved_articles)} saved articles for {country}"
            )

            for article in saved_articles:

                st.markdown(
                    f"**{article['title']}**"
                )

                st.caption(
                    f"{article['source']} | "
                    f"{article.get('published_at') or 'Unknown'}"
                )

                st.markdown(
                    f"[Read original article]({article['url']})"
                )

                st.divider()

        else:

            st.info(
                "No saved articles are available for this country yet."
            )

    except Exception as error:

        st.error(
            f"Could not retrieve saved articles: {error}"
        )


# Previously saved digest
st.subheader("📚 Previous News Digest")

if st.button("Load Latest Saved Digest"):

    try:

        previous_digest = get_latest_digest(
            country,
            selected_language,
        )

        if previous_digest:

            st.session_state["previous_digest"] = (
                previous_digest
            )

        else:

            st.session_state.pop("previous_digest", None)

            st.info(
                "No saved digest was found for this "
                "country and language."
            )

    except Exception as error:

        st.error(
            f"Could not load the previous digest: {error}"
        )


if "previous_digest" in st.session_state:

    previous_digest = st.session_state["previous_digest"]

    st.markdown(
        f"**Country:** {previous_digest['country']}"
    )

    st.markdown(
        f"**Language:** {previous_digest['language']}"
    )

    st.markdown(
        f"**Articles summarized:** "
        f"{previous_digest['article_count']}"
    )

    st.markdown(
        f"**Created:** {previous_digest['created_at']}"
    )

    st.markdown(previous_digest["content"])

    st.download_button(
        label="Download Previous Digest",
        data=previous_digest["content"],
        file_name="previous_news_digest.md",
        mime="text/markdown",
    )


# Footer
st.divider()

st.caption(
    "AI News Assistant | News availability varies by country "
    "and source. Always consult original articles for "
    "full reporting and context."
)
