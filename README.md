# 🦠 Outbreak Radar

> A real-time, outbreak intelligence dashboard that aggregates live disease news from the WHO and NewsAPI, visualises global activity on an interactive choropleth world map, and lets you drill into country and pathogen-level news feeds.

[![Live Demo](https://img.shields.io/badge/Live%20Demo-HuggingFace%20Spaces-yellow?logo=huggingface)](https://1shreyas-outbreakradar.hf.space)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.55-red?logo=streamlit)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## Features

| Feature | Description |
|---|---|
| 🗺️ **Interactive Choropleth Map** | Full-screen world map colour-coded by outbreak mention density over the last 28 days. Hover any country for name and alert count. |
| 📰 **Live News Feed** | Country-specific or global outbreak headlines from NewsAPI with source, date, and direct article links. Switch countries via the sidebar dropdown. |
| 💊 **Disease Filter Pills** | Clickable pathogen tags — Mpox · Dengue · Cholera · Ebola · Avian Flu · Measles · and more — that instantly filter the news feed. |
| 🚨 **Latest Global Alerts** | The 10 most recent WHO Disease Outbreak News items with dates and links, pulled live from the WHO RSS feed. |
| 📊 **Pathogen Activity Index** | Horizontal bar chart of the most-mentioned pathogens in the current 28-day window. |
| 🏆 **Top Outbreak Hotspots** | Ranked sidebar leaderboard of the 8 most-mentioned countries, each row a clickable country filter. |
| 🧠 **Intelligence Brief** | Auto-generated 5-point situational summary: WHO alert count, leading country, top pathogen, active surveillance coverage, and total articles indexed. |
| 🔴 **LIVE badge + auto-refresh** | Animated live indicator with last-refreshed timestamp. Page auto-refreshes every 10 minutes. |

---

## Tech Stack

| Layer | Library |
|---|---|
| UI framework | [Streamlit](https://streamlit.io) |
| Map & charts | [Plotly](https://plotly.com/python/) |
| Data wrangling | [Pandas](https://pandas.pydata.org) |
| Image handling | [Pillow](https://pillow.readthedocs.io) |
| WHO RSS feed | [feedparser](https://feedparser.readthedocs.io) |
| News headlines | [NewsAPI](https://newsapi.org) |
| HTTP | [Requests](https://requests.readthedocs.io) |

---

## Data Sources

- **WHO Disease Outbreak News** — live RSS feed at `https://www.who.int/rss-feeds/news-english.xml`
- **NewsAPI** — global English-language news filtered by outbreak/epidemic/pathogen keywords, last 28 days

---

## Running Locally

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/outbreakradar.git
cd outbreakradar
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Add your NewsAPI key

Create `.streamlit/secrets.toml` (this file is gitignored — never commit it):

```toml
NEWS_API_KEY = "your_newsapi_key_here"
```

Get a free key at [newsapi.org/register](https://newsapi.org/register).

### 4. Run

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`.

---

## Deploying to Hugging Face Spaces

1. Create a new Space at [huggingface.co/new-space](https://huggingface.co/new-space) — choose **Streamlit** as the SDK.
2. Push this repo to the Space:
   ```bash
   git remote add origin https://huggingface.co/spaces/YOUR_HF_USERNAME/outbreakradar
   git push origin main
   ```
3. In Space **Settings → Variables and secrets**, add:
   - **Name:** `NEWS_API_KEY` · **Value:** your NewsAPI key
4. The Space builds automatically (~2 min) and goes live at `https://YOUR_HF_USERNAME-outbreakradar.hf.space`.

---

## Project Structure

```
.
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── .streamlit/
│   └── config.toml         # Streamlit dark theme config
└── README.md
```

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `NEWS_API_KEY` | ✅ Yes | NewsAPI key — set via `.streamlit/secrets.toml` locally or Space secrets on HF |

---

## License

MIT
