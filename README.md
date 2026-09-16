# ResearchMind

A lightweight multi-step AI research pipeline. Give it a topic, and it searches the web, scrapes the most relevant source, writes a structured report, and critiques its own output — all powered by Groq's `openai/gpt-oss-120b` model via LangChain.

Available as both a Streamlit web app and a command-line script.

## How it works

The pipeline runs four sequential steps:

1. **Search** — queries [Tavily](https://tavily.com) for recent, relevant results on the topic (titles, URLs, snippets).
2. **Reader** — picks the top URL from the search results and scrapes clean text content from it.
3. **Writer** — an LLM chain drafts a structured report (Introduction, Key Findings, Conclusion, Sources) from the combined search + scraped content.
4. **Critic** — a second LLM chain reviews the report and returns a score, strengths, areas to improve, and a one-line verdict.

Search and scrape are plain, deterministic function calls (not agent loops), which keeps the pipeline fast. Only the writer and critic steps make LLM calls that need generation.

## Project structure

```
.
├── app.py         # Streamlit web UI
├── pipeline.py    # CLI entry point — runs the full pipeline in the terminal
├── agents.py      # Search/reader functions + writer & critic LLM chains
├── tools.py       # web_search (Tavily) and scrape_url (requests + BeautifulSoup) tools
└── .env           # API keys (not committed)
```

## Setup

### 1. Install dependencies

```bash
pip install streamlit langchain langchain-groq langchain-core python-dotenv tavily-python requests beautifulsoup4 lxml rich
```

### 2. Add API keys

Create a `.env` file in the project root:

```
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
```

- Get a Groq API key at [console.groq.com](https://console.groq.com)
- Get a Tavily API key at [tavily.com](https://tavily.com)

## Usage

### Web app (Streamlit)

```bash
streamlit run app.py
```

Enter a topic, click **Run Research**, and watch the pipeline stages complete. The final report and critic feedback render below, with a download button for the report as a `.md` file.

### Command line

```bash
python pipeline.py
```

Enter a topic when prompted. Progress and results for each step print directly to the terminal.

## Tech stack

- **LLM**: `openai/gpt-oss-120b` via [Groq](https://groq.com) (fast inference)
- **Framework**: [LangChain](https://www.langchain.com/) (LCEL chains for writer/critic)
- **Search**: [Tavily](https://tavily.com)
- **Scraping**: `requests` + `BeautifulSoup`
- **UI**: [Streamlit](https://streamlit.io)

## Notes

- The reader step scrapes only the **first** URL found in the search results and truncates content to 3,000 characters to keep prompts and processing fast.
- `web_search` returns up to 5 results, each with a 300-character snippet.
- No agent frameworks (e.g. LangGraph, ReAct loops) are used — every step is a direct function or chain call, which keeps latency predictable and low.
