
import streamlit as st

from news_discovery import fetch_news
from article_processor import process_articles
from ai_summarizer import generate_news_digest
from source_manager import NEWS_SOURCES
from language_service import get_supported_languages
from news_database import (
    initialize_database,
    save_articles,
    save_digest,
    get_articles,
    get_latest_digest,
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

    Start with verified news feeds, with more countries coming soon.
    Generate AI-powered summaries in your preferred language.
    """
)

st.divider()


# Country selection
available_countries = list(NEWS_SOURCES.keys())

country = st.selectbox(
    "Select a country",
    available_countries,
)

max_articles = st.slider(
    "Number of articles",
    min_value=5,
    max_value=30,
    value=10,
)

selected_language = st.selectbox(
    "Choose your news summary language",
    get_supported_languages(),
    index=0,
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
                st.warning(
                    "No articles were found. "
                    "Please try again later."
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

    for article in articles:

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
                st.session_state["digest_country"] = selected_country
                st.session_state["digest_language"] = selected_language

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
    "AI News Assistant | News sourced from configured "
    "publishers. Always consult original articles for "
    "full reporting and context."
)
