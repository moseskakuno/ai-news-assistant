
# AI News Assistant 🌍

An AI-powered news application that retrieves news from configured local publishers, processes articles, and generates daily news summaries in multiple languages.

## Features

- Retrieve the latest news from configured RSS feeds.
- Select a country to explore its news.
- Choose the number of articles to retrieve.
- Generate AI-powered news summaries using OpenAI.
- Generate summaries in multiple languages.
- View original article headlines, publishers, publication information, and links.
- Store retrieved articles and generated summaries in an SQLite database.
- Retrieve previously saved articles and news digests.
- Download news digests as Markdown files.
- Remove duplicate articles.

## Technology Stack

- Python
- Streamlit
- OpenAI API
- SQLite
- Requests
- Feedparser
- BeautifulSoup
- Pandas

## Project Structure

```text
ai-news-assistant/
│
├── app.py
├── ai_summarizer.py
├── article_processor.py
├── deduplicator.py
├── language_service.py
├── news_database.py
├── news_discovery.py
├── source_manager.py
│
├── requirements.txt
├── README.md
├── .gitignore
└── .env
```

The SQLite database is created locally when the application starts.

## Currently Supported Countries

| Country | Configured News Sources |
|---------|-------------------------|
| Germany | Deutschlandfunk |

Additional countries and verified local news sources can be configured through `source_manager.py`.

## Supported Summary Languages

- English
- German
- French
- Spanish
- Portuguese
- Arabic
- Hindi
- Japanese

News availability and source language depend on the configured publishers.

## Installation

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd ai-news-assistant
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```dotenv
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=your_available_model
```

Never commit your `.env` file or expose your API key.

### 5. Run the application

```bash
streamlit run app.py
```

The application will open in your browser.

## Database

The application uses SQLite to store:

- Retrieved news articles.
- Article metadata and source URLs.
- Generated news digests.
- Summary languages and timestamps.

The database is created automatically as `news_assistant.db`.

## News Sources and Content

The application uses configured RSS feeds to discover news articles.

AI summaries are based on the information available in the supplied RSS summaries and metadata. They do not necessarily represent the full content of the original articles.

Original publisher links are provided so users can consult the complete reporting.

News coverage depends on the availability and reliability of configured RSS sources.

## Future Improvements

- Expand coverage to additional countries and publishers.
- Add topic-based news filtering.
- Add customizable date ranges.
- Improve multilingual news discovery.
- Introduce more advanced news categorization.
- Add persistent cloud database storage.
- Deploy the application online.

## License and Usage Terms

**AI News Assistant:** News data is provided by the respective publishers through their publicly available RSS feeds. All original news content remains the property of its respective publishers and is subject to their applicable copyright and usage terms.

The free AI News Assistant is intended for educational and non-commercial use. Commercial usage is subject to AI News Assistant's licensing and subscription terms.

© Moses Ochieng Akuno — [AI News Assistant](https://github.com/moseskakuno/ai-news-assistant). All rights reserved.
