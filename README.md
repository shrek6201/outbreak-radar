---
title: OutbreakRadar
emoji: 🦠
colorFrom: green
colorTo: red
sdk: streamlit
sdk_version: 1.55.0
app_file: app.py
pinned: false
---

# 🦠 OutbreakRadar

A real-time, dark-themed outbreak intelligence dashboard that aggregates live disease news from the WHO and NewsAPI, visualises global activity on an interactive choropleth map, and lets you drill into country- and pathogen-level news feeds.

---

## Features

- **Interactive Choropleth Map** — full-screen world map colour-coded by outbreak mention density over the last 28 days. Hover for country name and alert count. Click any country to filter the news feed instantly.
- **Live News Feed** — country-specific or global outbreak headlines pulled from NewsAPI, with source, date, and direct article links.
- **Disease Filter Pills** — clickable tags (Mpox · Dengue · Cholera · Ebola · Avian Flu · …) that filter the news feed by pathogen in one click.
- **Latest Global Alerts** — the 10 most recent WHO Disease Outbreak News items with dates and links.
- **Pathogen Activity Index** — horizontal bar chart showing the most-mentioned pathogens in the current data window.
- **Top Outbreak Hotspots** — ranked sidebar leaderboard of the 8 most-mentioned countries with clickable rows.
- **Intelligence Brief** — auto-generated 5-point summary: WHO alert count, top country, top pathogen, surveillance coverage, and total articles indexed.
- **LIVE badge + auto-refresh** — animated live indicator and automatic page refresh every 10 minutes.

---

## Tech Stack

| Layer | Library |
|---|---|
| UI framework | [Streamlit](https://streamlit.io) |
| Map & charts | [Plotly](https://plotly.com/python/) |
| Data wrangling | [Pandas](https://pandas.pydata.org) |
| WHO RSS feed | [feedparser](https://feedparser.readthedocs.io) |
| News headlines | [NewsAPI](https://newsapi.org) |

---

## Data Sources

- **WHO Disease Outbreak News** — `https://www.who.int/rss-feeds/news-english.xml`
- **NewsAPI** — global English-language news, filtered by outbreak/epidemic/pathogen keywords, last 28 days

---

## Running Locally

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/global-disease-tracker.git
cd global-disease-tracker
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Add your NewsAPI key

Create `.streamlit/secrets.toml`:

```toml
NEWS_API_KEY = "your_newsapi_key_here"
```

Get a free key at [newsapi.org](https://newsapi.org/register).

### 4. Run

```bash
streamlit run app.py
```

---

## Deploying to Hugging Face Spaces

1. Create a new Space at [huggingface.co/new-space](https://huggingface.co/new-space) — choose **Streamlit** as the SDK.
2. Push this repo to the Space.
3. In the Space settings → **Variables and secrets**, add:
   - **Name:** `NEWS_API_KEY`
   - **Value:** your NewsAPI key
4. The Space builds automatically and goes live.

---

## Project Structure

```
.
├── app.py               # Main Streamlit application
├── requirements.txt     # Python dependencies
├── .streamlit/
│   └── config.toml      # Streamlit theme config
└── README.md
```

---

## License

MIT
