
# AI News Assistant 🌍

An AI-powered international news application that retrieves news from local publishers, processes articles, and generates AI-powered news summaries in multiple languages.

Users can select a country, explore available local news, generate individual article summaries, and create daily AI-powered news digests that can be downloaded as PDF documents.

## Features

### International News Discovery
- Select a country to explore its available news.
- Retrieve the latest news from configured local RSS feeds.
- Discover news from additional countries using Google News RSS as a fallback.
- Automatically determine a country's preferred news language.
- Choose the number of articles to retrieve.
- Remove duplicate articles.
- Display article headlines, publishers, publication information, and original source links.

### AI-Powered Summarization
- Generate individual AI-powered article summaries.
- Generate daily AI news digests from retrieved articles.
- Produce approximately 200-word individual article summaries.
- Generate summaries in multiple languages.
- Use extracted article text when publicly accessible.
- Fall back to available RSS information when full article extraction is unavailable.
- Avoid presenting unavailable full article content as though it were retrieved.

### PDF Downloads
- Download the current daily news digest as a PDF document.
- Download previously saved news digests as PDF documents.
- Generate PDF files dynamically using ReportLab.
- Format PDF documents with headings, paragraphs, and bullet points.
- Use country-specific titles in generated PDF documents.

### Database and Persistence
- Store retrieved articles in an SQLite database.
- Save generated daily news digests.
- Save individual article summaries.
- Retrieve previously saved articles.
- Load previously generated news digests.
- Reuse saved article summaries for the selected language.

## Technology Stack

- Python
- Streamlit
- OpenAI API
- SQLite
- ReportLab
- Requests
- Feedparser
- BeautifulSoup4
- Pandas
- PyCountry
- Python-dotenv

## Project Structure

```text
ai-news-assistant/
│
├── app.py
├── ai_summarizer.py
├── article_processor.py
├── content_extractor.py
├── country_service.py
├── deduplicator.py
├── language_service.py
├── news_database.py
├── news_discovery.py
├── pdf_generator.py
├── source_manager.py
│
├── requirements.txt
├── README.md
├── .gitignore
└── .env
```

Additional directories and files, such as the virtual environment and local SQLite database, are created locally and are not committed to GitHub.

## Currently Configured Countries and News Sources

| Country | Configured News Sources |
|---------|-------------------------|
| Germany | Deutschlandfunk |
| Kenya | Daily Nation, The Standard |

Additional countries can be selected through the application. Countries without configured local RSS feeds use Google News RSS as a discovery fallback where available.

News availability and the proportion of genuinely local publishers vary by country.

Additional local publishers can be configured through `source_manager.py`.

## Supported Summary Languages

- English
- German
- French
- Spanish
- Portuguese
- Arabic
- Hindi
- Japanese
- Chinese (Simplified)

The application automatically suggests a preferred language based on the selected country.

Users can also manually choose another supported summary language.

News discovery language and AI summary language are handled separately.

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/moseskakuno/ai-news-assistant.git

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

The `.env` file is excluded through `.gitignore`.

### 5. Run the application

```bash
streamlit run app.py
```

The application will open in your browser.

## How to Use the Application

1. Select a country.
2. Choose the number of articles to retrieve.
3. Select your preferred AI summary language.
4. Click **Fetch Latest News**.
5. Explore the retrieved news articles and original publisher links.
6. Expand an individual article's summary section to generate an AI-powered summary.
7. Click **Generate AI News Summary** to create a daily news digest.
8. Download the current news digest as a PDF.
9. Load previously saved news digests and download them as PDFs.

## Database

The application uses SQLite for local data persistence.

The database is automatically initialized when the application starts.

The database file is:

```text
news_assistant.db
```

The application stores:

- Retrieved news articles.
- Article titles and source URLs.
- Publisher information and publication dates.
- Generated individual article summaries.
- Generated daily news digests.
- Summary languages and timestamps.

Previously generated summaries and digests can be retrieved without generating them again.

## PDF Generation

PDF generation is implemented in `pdf_generator.py` using ReportLab.

The PDF generator converts daily news digest text into downloadable PDF documents.

Both current and previously saved news digests support PDF downloads.

Generated PDF documents are created dynamically in memory, so users do not need to store temporary PDF files on the server.

## News Sources and Content

The application uses configured RSS feeds and Google News RSS to discover news articles.

Where technically and legally permitted, the application attempts to extract publicly accessible article text.

Some publishers may restrict access through consent pages, authentication requirements, paywalls, or technical limitations.

When full article extraction is unavailable, the application uses the available RSS information where sufficient.

AI summaries are based only on the information supplied to the summarization process. They do not necessarily represent the complete content of the original articles.

Original publisher links are provided so users can consult the complete reporting.

News coverage depends on the availability, reliability, language, and accessibility of news sources.

Original news content remains the property of its respective publishers and is subject to their applicable copyright and usage terms.

## Deployment

The application is deployed using Streamlit Community Cloud.

The application requires:

- A GitHub repository.
- A valid OpenAI API key.
- The required Python dependencies.
- Streamlit Cloud secrets or environment configuration.

For deployment, configure the following secrets securely:

```toml
OPENAI_API_KEY = "your_openai_api_key"
OPENAI_MODEL = "your_available_model"
```

Never commit API keys or other credentials to the repository.

## Future Improvements

- Expand coverage to additional countries and verified local publishers.
- Improve international news discovery in local languages.
- Add topic-based news filtering.
- Add customizable date ranges.
- Introduce advanced news categorization.
- Improve article extraction and source validation.
- Add scheduled daily news digests.
- Introduce persistent cloud database storage.
- Add user accounts and personalized news preferences.
- Improve PDF formatting and customization.
- Add automated testing and monitoring.

## License and Usage Terms

**AI News Assistant** is an independent educational software project.

News data is obtained from the respective publishers through their publicly available RSS feeds and other discovery services. Original news content remains the property of its respective publishers and is subject to their applicable copyright, licensing, and usage terms.

Users should respect the applicable terms of the news discovery services and publishers.

The AI News Assistant is intended for educational and non-commercial use. Any commercial use is subject to applicable third-party licensing terms and the project owner's authorization.

© Moses Ochieng Akuno — [AI News Assistant](https://github.com/moseskakuno/ai-news-assistant). All rights reserved.
