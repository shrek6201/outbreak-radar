import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import requests
import feedparser
import re
import os
import base64
from io import BytesIO
from PIL import Image
from datetime import datetime, timedelta, timezone
from collections import Counter
from time import mktime
from urllib.parse import quote, unquote

# ─── Favicon (embedded as base64 so HF Spaces CSP never blocks it) ───────────
_FAVICON_B64 = (
    "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"
)
_favicon_img = Image.open(BytesIO(base64.b64decode(_FAVICON_B64)))

# ─── Page config (must be first) ─────────────────────────────────────────────
st.set_page_config(
    page_title="OutbreakRadar",
    page_icon=_favicon_img,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS / Theme ─────────────────────────────────────────────────────────────
THEME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Oswald:wght@300;400;600&display=swap');

/* ── Base ── */
html, body, [class*="css"], .stApp {
    background-color: #0a0a08 !important;
    color: #d4cdb7 !important;
}
* { box-sizing: border-box; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #0c0c0a !important;
    border-right: 1px solid #1e1e16 !important;
}
[data-testid="stSidebar"] * { color: #d4cdb7 !important; }

/* ── Main container ── */
.main .block-container {
    padding: 0.6rem 1.2rem 2rem 1.2rem !important;
    max-width: 100% !important;
}

/* ── Headings ── */
h1, h2, h3, h4 {
    font-family: 'Oswald', sans-serif !important;
    color: #c8a84b !important;
    letter-spacing: 0.06em;
    font-weight: 600;
}

/* ── LIVE badge ── */
.live-badge {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    background: rgba(204,63,12,0.12);
    border: 1px solid rgba(204,63,12,0.6);
    border-radius: 3px;
    padding: 4px 11px 4px 9px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.72rem;
    color: #ff6535;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    margin-top: 2px;
}
.live-dot {
    width: 8px; height: 8px;
    background: #ff4500;
    border-radius: 50%;
    flex-shrink: 0;
    animation: blink 1.3s ease-in-out infinite;
}
@keyframes blink {
    0%,100% { opacity: 1; box-shadow: 0 0 6px #ff4500; }
    50%      { opacity: 0.35; box-shadow: none; }
}

/* ── Timestamp ── */
.timestamp {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.68rem;
    color: #4a4a3a;
    margin-top: 6px;
    letter-spacing: 0.03em;
}

/* ── Sidebar title ── */
.sidebar-title {
    font-family: 'Oswald', sans-serif;
    font-size: 1.55rem;
    font-weight: 600;
    color: #c8a84b !important;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    line-height: 1.15;
}
.sidebar-subtitle {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.62rem;
    color: #4a7c59 !important;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    margin-top: 5px;
}

/* ── Section headers ── */
.section-hdr {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: #4a4a3a;
    border-bottom: 1px solid #1e1e16;
    padding-bottom: 7px;
    margin-bottom: 12px;
}

/* ── Metric boxes ── */
.metric-row {
    display: flex;
    gap: 10px;
    margin: 6px 0 10px 0;
}
.metric-box {
    background: #0f0f0c;
    border: 1px solid #1e1e16;
    border-radius: 3px;
    padding: 9px 16px;
    min-width: 90px;
}
.metric-val {
    font-family: 'Share Tech Mono', monospace;
    font-size: 1.7rem;
    color: #c8a84b;
    line-height: 1;
}
.metric-lbl {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.6rem;
    color: #4a4a3a;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-top: 3px;
}

/* ── Alert cards (WHO) ── */
.alert-card {
    background: #0f0f0c;
    border: 1px solid #1e1e16;
    border-left: 3px solid #cc3f0c;
    border-radius: 2px;
    padding: 9px 13px;
    margin-bottom: 8px;
    transition: border-left-color 0.2s;
}
.alert-card:hover { border-left-color: #ff6535; }
.alert-date {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.62rem;
    color: #cc3f0c;
    letter-spacing: 0.08em;
    margin-bottom: 4px;
}
.alert-title a {
    font-family: 'Oswald', sans-serif;
    font-size: 0.83rem;
    font-weight: 400;
    color: #d4cdb7 !important;
    text-decoration: none;
    line-height: 1.35;
}
.alert-title a:hover { color: #c8a84b !important; }

/* ── News cards ── */
.news-card {
    background: #0f0f0c;
    border: 1px solid #1e1e16;
    border-left: 3px solid #4a7c59;
    border-radius: 2px;
    padding: 10px 13px;
    margin-bottom: 8px;
    transition: border-left-color 0.2s;
}
.news-card:hover { border-left-color: #c8a84b; }
.news-source {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.62rem;
    color: #4a7c59;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 5px;
}
.news-title {
    font-family: 'Oswald', sans-serif;
    font-size: 0.83rem;
    font-weight: 400;
    color: #d4cdb7;
    line-height: 1.35;
    margin-bottom: 5px;
}
.news-desc {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.65rem;
    color: #5a5a4a;
    line-height: 1.4;
    margin-bottom: 6px;
}
.news-link a {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.65rem;
    color: #c8a84b !important;
    text-decoration: none;
    letter-spacing: 0.05em;
}
.news-link a:hover { color: #e8c870 !important; }

/* ── Scrollable containers ── */
.scroll-box {
    max-height: 480px;
    overflow-y: auto;
    padding-right: 4px;
}
.scroll-box::-webkit-scrollbar { width: 3px; }
.scroll-box::-webkit-scrollbar-track { background: #0a0a08; }
.scroll-box::-webkit-scrollbar-thumb { background: #2a2a1e; border-radius: 2px; }

/* ── Empty state ── */
.empty-state {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.72rem;
    color: #2a2a1e;
    text-align: center;
    padding: 40px 20px;
    border: 1px dashed #1e1e16;
    border-radius: 3px;
    letter-spacing: 0.08em;
}

/* ── Divider ── */
.divider { border: none; border-top: 1px solid #1e1e16; margin: 0.8rem 0; }

/* ── Button ── */
.stButton > button {
    background: transparent !important;
    border: 1px solid #4a7c59 !important;
    color: #4a7c59 !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    border-radius: 2px !important;
    padding: 8px 0 !important;
    width: 100% !important;
    transition: all 0.18s !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 5px !important;
    line-height: 1 !important;
}
.stButton > button p {
    margin: 0 !important;
    line-height: 1 !important;
}
.stButton > button:hover {
    background: rgba(74,124,89,0.12) !important;
    border-color: #c8a84b !important;
    color: #c8a84b !important;
}

/* ── Selectbox ── */
.stSelectbox label { display: none !important; }
[data-baseweb="select"] > div {
    background: #111109 !important;
    border-color: #2a2a1e !important;
    border-radius: 2px !important;
}

/* ── Map ── */
.map-title {
    font-family: 'Oswald', sans-serif;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    color: #3a3a2e;
    margin-bottom: 4px;
}
.map-wrapper {
    border: 1px solid #1e1e16;
    border-radius: 3px;
    overflow: hidden;
    background: #0a0a08;
}

/* ── Intelligence Brief ── */
.intel-wrap {
    background: #0d0d0b;
    border: 1px solid #1e1e16;
    border-left: 3px solid #4a7c59;
    border-radius: 2px;
    padding: 10px 16px 10px 14px;
    margin-bottom: 10px;
}
.intel-label {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.6rem;
    color: #4a7c59;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-bottom: 7px;
}
.intel-items {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
    gap: 3px 24px;
}
.intel-item {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.67rem;
    color: #6a6a5a;
    line-height: 1.65;
}
.intel-item b { color: #c8a84b; font-weight: 400; }

/* ── Timeline ── */
.timeline-hdr {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.62rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #3a3a2e;
    margin: 10px 0 2px 0;
}

/* ── Hotspot leaderboard (sidebar) ── */
.hotspot-row {
    display: flex;
    align-items: center;
    gap: 7px;
    padding: 5px 0;
    border-bottom: 1px solid #141410;
    cursor: pointer;
    transition: background 0.15s;
}
.hotspot-row:hover { background: rgba(200,168,75,0.04); }
.hotspot-rank {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.58rem;
    color: #3a3a2e;
    width: 14px;
    flex-shrink: 0;
}
.hotspot-name {
    font-family: 'Oswald', sans-serif;
    font-size: 0.76rem;
    color: #d4cdb7;
    flex: 1;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.hotspot-bar-wrap {
    width: 44px;
    height: 3px;
    background: #1a1a14;
    border-radius: 2px;
    flex-shrink: 0;
}
.hotspot-bar {
    height: 3px;
    background: linear-gradient(90deg, #3a6645, #c8a84b);
    border-radius: 2px;
}
.hotspot-count {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.6rem;
    color: #c8a84b;
    min-width: 18px;
    text-align: right;
    flex-shrink: 0;
}

/* ── Disease tag pills ── */
.tag-row {
    display: flex;
    flex-wrap: wrap;
    gap: 5px;
    margin-bottom: 11px;
}
.tag-pill {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.6rem;
    padding: 3px 8px;
    border: 1px solid #2a2a1e;
    border-radius: 2px;
    color: #5a5a4a;
    letter-spacing: 0.07em;
    text-transform: uppercase;
    display: inline-block;
}
.tag-pill.hi { border-color: #4a7c59; color: #4a7c59; }
.tag-pill.hot { border-color: #c8a84b; color: #c8a84b; background: rgba(200,168,75,0.07); }

/* ── Credits ── */
.credits {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.6rem;
    color: #2a2a22;
    line-height: 1.7;
}
.credits span { color: #3a3a2e; }

/* ── Remove iframe borders (st.components iframes) ── */
iframe { border: none !important; display: block !important; }
</style>
"""

# ─── Disease vocabulary ───────────────────────────────────────────────────────
DISEASE_VOCAB: dict[str, list[str]] = {
    "COVID-19":      ["covid", "coronavirus", "sars-cov-2"],
    "Mpox":          ["mpox", "monkeypox"],
    "Dengue":        ["dengue"],
    "Cholera":       ["cholera"],
    "Ebola":         ["ebola"],
    "Avian Flu":     ["avian flu", "bird flu", "h5n1"],
    "Measles":       ["measles"],
    "Tuberculosis":  ["tuberculosis"],
    "Malaria":       ["malaria"],
    "Meningitis":    ["meningitis"],
    "Yellow Fever":  ["yellow fever"],
    "Marburg":       ["marburg"],
    "Polio":         ["poliovirus", "polio"],
    "Influenza":     ["influenza"],
    "Hepatitis":     ["hepatitis"],
    "Plague":        ["bubonic plague", "pneumonic plague"],
    "MERS":          ["mers-cov", "middle east respiratory"],
    "Rabies":        ["rabies"],
}

# ─── Country Mappings ─────────────────────────────────────────────────────────
COUNTRY_ISO3: dict[str, str] = {
    "Afghanistan": "AFG", "Albania": "ALB", "Algeria": "DZA", "Angola": "AGO",
    "Argentina": "ARG", "Armenia": "ARM", "Australia": "AUS", "Austria": "AUT",
    "Azerbaijan": "AZE", "Bahrain": "BHR", "Bangladesh": "BGD", "Belarus": "BLR",
    "Belgium": "BEL", "Benin": "BEN", "Bolivia": "BOL", "Bosnia": "BIH",
    "Bosnia and Herzegovina": "BIH", "Botswana": "BWA", "Brazil": "BRA",
    "Bulgaria": "BGR", "Burkina Faso": "BFA", "Burundi": "BDI",
    "Cambodia": "KHM", "Cameroon": "CMR", "Canada": "CAN",
    "Central African Republic": "CAF", "Chad": "TCD", "Chile": "CHL",
    "China": "CHN", "Colombia": "COL", "Comoros": "COM", "Congo": "COG",
    "Costa Rica": "CRI", "Croatia": "HRV", "Cuba": "CUB", "Cyprus": "CYP",
    "Czechia": "CZE", "Czech Republic": "CZE", "Denmark": "DNK",
    "Djibouti": "DJI", "Dominican Republic": "DOM", "Ecuador": "ECU",
    "Egypt": "EGY", "El Salvador": "SLV", "Equatorial Guinea": "GNQ",
    "Eritrea": "ERI", "Estonia": "EST", "Eswatini": "SWZ",
    "Ethiopia": "ETH", "Fiji": "FJI", "Finland": "FIN", "France": "FRA",
    "Gabon": "GAB", "Gambia": "GMB", "Georgia": "GEO", "Germany": "DEU",
    "Ghana": "GHA", "Greece": "GRC", "Guatemala": "GTM", "Guinea": "GIN",
    "Guinea-Bissau": "GNB", "Guyana": "GUY", "Haiti": "HTI",
    "Honduras": "HND", "Hungary": "HUN", "Iceland": "ISL", "India": "IND",
    "Indonesia": "IDN", "Iran": "IRN", "Iraq": "IRQ", "Ireland": "IRL",
    "Israel": "ISR", "Italy": "ITA", "Ivory Coast": "CIV", "Jamaica": "JAM",
    "Japan": "JPN", "Jordan": "JOR", "Kazakhstan": "KAZ", "Kenya": "KEN",
    "Kiribati": "KIR", "Kuwait": "KWT", "Kyrgyzstan": "KGZ", "Laos": "LAO",
    "Latvia": "LVA", "Lebanon": "LBN", "Liberia": "LBR", "Libya": "LBY",
    "Lithuania": "LTU", "Luxembourg": "LUX", "Madagascar": "MDG",
    "Malawi": "MWI", "Malaysia": "MYS", "Maldives": "MDV", "Mali": "MLI",
    "Malta": "MLT", "Marshall Islands": "MHL", "Mauritania": "MRT",
    "Mexico": "MEX", "Micronesia": "FSM", "Moldova": "MDA",
    "Mongolia": "MNG", "Montenegro": "MNE", "Morocco": "MAR",
    "Mozambique": "MOZ", "Myanmar": "MMR", "Namibia": "NAM", "Nepal": "NPL",
    "Netherlands": "NLD", "New Zealand": "NZL", "Nicaragua": "NIC",
    "Niger": "NER", "Nigeria": "NGA", "North Korea": "PRK",
    "North Macedonia": "MKD", "Norway": "NOR", "Oman": "OMN",
    "Pakistan": "PAK", "Palau": "PLW", "Palestine": "PSE", "Panama": "PAN",
    "Papua New Guinea": "PNG", "Paraguay": "PRY", "Peru": "PER",
    "Philippines": "PHL", "Poland": "POL", "Portugal": "PRT", "Qatar": "QAT",
    "Romania": "ROU", "Russia": "RUS", "Rwanda": "RWA",
    "Saudi Arabia": "SAU", "Senegal": "SEN", "Serbia": "SRB",
    "Sierra Leone": "SLE", "Singapore": "SGP", "Slovakia": "SVK",
    "Slovenia": "SVN", "Solomon Islands": "SLB", "Somalia": "SOM",
    "South Africa": "ZAF", "South Korea": "KOR", "South Sudan": "SSD",
    "Spain": "ESP", "Sri Lanka": "LKA", "Sudan": "SDN", "Suriname": "SUR",
    "Sweden": "SWE", "Switzerland": "CHE", "Syria": "SYR", "Taiwan": "TWN",
    "Tajikistan": "TJK", "Tanzania": "TZA", "Thailand": "THA", "Togo": "TGO",
    "Tonga": "TON", "Trinidad and Tobago": "TTO", "Tunisia": "TUN",
    "Turkey": "TUR", "Turkmenistan": "TKM", "Tuvalu": "TUV", "UAE": "ARE",
    "Uganda": "UGA", "Ukraine": "UKR", "United Arab Emirates": "ARE",
    "United Kingdom": "GBR", "United States": "USA", "Uruguay": "URY",
    "Uzbekistan": "UZB", "Vanuatu": "VUT", "Venezuela": "VEN",
    "Vietnam": "VNM", "Yemen": "YEM", "Zambia": "ZMB", "Zimbabwe": "ZWE",
    "DRC": "COD", "Democratic Republic of Congo": "COD",
    "Democratic Republic of the Congo": "COD",
    "Republic of Congo": "COG", "UK": "GBR", "US": "USA",
    "Cote d'Ivoire": "CIV", "Côte d'Ivoire": "CIV",
    "Timor-Leste": "TLS", "East Timor": "TLS", "Brunei": "BRN",
    "Cape Verde": "CPV", "Cabo Verde": "CPV", "Bhutan": "BTN",
    "Samoa": "WSM", "Nauru": "NRU", "Belize": "BLZ", "Kosovo": "XKX",
    "São Tomé and Príncipe": "STP",
}

# Build reverse map preferring the longest (most canonical) name per ISO3 code
# so "United States" wins over "US", "United Kingdom" over "UK", etc.
ISO3_TO_NAME: dict[str, str] = {}
for _name, _iso3 in COUNTRY_ISO3.items():
    if _iso3 not in ISO3_TO_NAME or len(_name) > len(ISO3_TO_NAME[_iso3]):
        ISO3_TO_NAME[_iso3] = _name

# ─── Data fetching ────────────────────────────────────────────────────────────

def _get_api_key() -> str:
    try:
        return st.secrets["NEWS_API_KEY"]
    except Exception:
        return os.environ.get("NEWS_API_KEY", "")


@st.cache_data(ttl=600, show_spinner=False)
def fetch_who_alerts() -> list[dict]:
    try:
        feed = feedparser.parse("https://www.who.int/rss-feeds/news-english.xml")
        alerts = []
        for entry in feed.entries[:60]:
            published = None
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                published = datetime.fromtimestamp(
                    mktime(entry.published_parsed), tz=timezone.utc
                )
            alerts.append({
                "title": entry.get("title", "").strip(),
                "link":  entry.get("link", ""),
                "published": published,
                "summary": entry.get("summary", ""),
            })
        return [a for a in alerts if a["title"]]
    except Exception:
        return []


@st.cache_data(ttl=600, show_spinner=False)
def fetch_newsapi_global(api_key: str) -> list[dict]:
    if not api_key:
        return []
    try:
        cutoff = (datetime.now() - timedelta(days=28)).strftime("%Y-%m-%d")
        resp = requests.get(
            "https://newsapi.org/v2/everything",
            params={
                "q": "(outbreak OR epidemic OR disease OR infection OR pathogen) AND (WHO OR health OR virus)",
                "from": cutoff,
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": 100,
                "apiKey": api_key,
            },
            timeout=12,
        )
        if resp.status_code == 200:
            return resp.json().get("articles", [])
        return []
    except Exception:
        return []


@st.cache_data(ttl=600, show_spinner=False)
def fetch_newsapi_country(country: str, api_key: str) -> list[dict]:
    if not api_key or not country:
        return []
    try:
        cutoff = (datetime.now() - timedelta(days=28)).strftime("%Y-%m-%d")
        resp = requests.get(
            "https://newsapi.org/v2/everything",
            params={
                "q": f'"{country}" AND (disease OR outbreak OR epidemic OR virus OR health OR infection)',
                "from": cutoff,
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": 20,
                "apiKey": api_key,
            },
            timeout=12,
        )
        if resp.status_code == 200:
            return resp.json().get("articles", [])
        return []
    except Exception:
        return []


# ─── Data processing ──────────────────────────────────────────────────────────

def _extract_countries(text: str) -> list[str]:
    tl = text.lower()
    return [n for n in COUNTRY_ISO3 if re.search(r"\b" + re.escape(n.lower()) + r"\b", tl)]


def build_country_df(who_alerts: list[dict], news_articles: list[dict]) -> pd.DataFrame:
    iso3_counts: dict[str, int] = {}
    iso3_name:   dict[str, str] = {}
    for alert in who_alerts:
        text = f"{alert.get('title','')} {alert.get('summary','')}"
        for c in _extract_countries(text):
            iso3 = COUNTRY_ISO3[c]
            iso3_counts[iso3] = iso3_counts.get(iso3, 0) + 2
            iso3_name.setdefault(iso3, c)
    for art in news_articles:
        text = f"{art.get('title','')} {art.get('description','')}"
        for c in _extract_countries(text):
            iso3 = COUNTRY_ISO3[c]
            iso3_counts[iso3] = iso3_counts.get(iso3, 0) + 1
            iso3_name.setdefault(iso3, c)
    if not iso3_counts:
        return pd.DataFrame(columns=["iso3", "country", "count"])
    df = pd.DataFrame([{"iso3": k, "country": iso3_name[k], "count": v}
                       for k, v in iso3_counts.items()])
    return df.sort_values("count", ascending=False).reset_index(drop=True)


def extract_disease_tags(
    global_news: list[dict], who_alerts: list[dict]
) -> list[tuple[str, int]]:
    """Return (disease, count) pairs sorted by frequency."""
    counts: Counter = Counter()
    texts = (
        [f"{a.get('title','')} {a.get('description','')}".lower() for a in global_news]
        + [f"{a.get('title','')} {a.get('summary','')}".lower() for a in who_alerts]
    )
    for text in texts:
        for disease, kws in DISEASE_VOCAB.items():
            if any(kw in text for kw in kws):
                counts[disease] += 1
    return [(d, c) for d, c in counts.most_common() if c >= 1]


def build_disease_chart(disease_tags: list[tuple[str, int]]) -> go.Figure:
    """Horizontal bar chart of top-8 disease mention counts."""
    if not disease_tags:
        fig = go.Figure()
        fig.update_layout(paper_bgcolor="#0a0a08", plot_bgcolor="#0a0a08",
                          height=160, margin=dict(l=0, r=0, t=10, b=0))
        return fig
    tags   = disease_tags[:8]
    labels = [d for d, _ in reversed(tags)]
    counts = [c for _, c in reversed(tags)]
    mx     = max(counts)
    colors = [
        f"rgba({int(12 + 188*(c/mx))},{int(31 + 105*(c/mx))},{int(18 + 14*(c/mx))},0.9)"
        for c in counts
    ]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=counts, y=labels,
        orientation="h",
        marker=dict(color=colors, line=dict(width=0)),
        hovertemplate="<b>%{y}</b><br>Mentions: %{x}<extra></extra>",
        text=counts,
        textposition="outside",
        textfont=dict(color="#5a5a4a", size=9, family="Share Tech Mono"),
    ))
    fig.update_layout(
        paper_bgcolor="#0a0a08", plot_bgcolor="#0a0a08",
        margin=dict(l=0, r=34, t=10, b=0), height=160,
        xaxis=dict(showgrid=True, gridcolor="#111109", zeroline=False, showline=False,
                   tickfont=dict(color="#3a3a2e", size=8, family="Share Tech Mono")),
        yaxis=dict(showgrid=False, zeroline=False, showline=False,
                   tickfont=dict(color="#9a9a7a", size=9, family="Share Tech Mono")),
        hoverlabel=dict(bgcolor="#111109", bordercolor="#4a7c59",
                        font=dict(color="#d4cdb7", size=11, family="Share Tech Mono")),
        bargap=0.28,
    )
    return fig


def generate_brief(
    who_alerts: list[dict],
    global_news: list[dict],
    country_df: pd.DataFrame,
    disease_tags: list[tuple[str, int]],
) -> list[str]:
    items: list[str] = []
    week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    recent_who = sum(1 for a in who_alerts if a.get("published") and a["published"] > week_ago)
    items.append(f"<b>{recent_who}</b> WHO alerts in the last 7 days")
    if not country_df.empty:
        top = country_df.iloc[0]
        items.append(f"<b>{top['country']}</b> leads with <b>{int(top['count'])}</b> mentions")
    if disease_tags:
        d, c = disease_tags[0]
        items.append(f"<b>{d}</b> most reported pathogen (<b>{c}</b> articles)")
    items.append(f"<b>{len(country_df)}</b> countries under active surveillance")
    items.append(f"<b>{len(global_news)}</b> global health articles indexed")
    return items


# ─── Chart builders ───────────────────────────────────────────────────────────

def build_map(df: pd.DataFrame) -> go.Figure:
    COLORSCALE = [
        [0.00, "#0d0d0a"], [0.10, "#141f14"], [0.25, "#1e3622"],
        [0.45, "#3a6645"], [0.65, "#7a6020"], [0.82, "#c8a84b"], [1.00, "#cc3f0c"],
    ]
    all_rows = {iso3: (name, 0) for name, iso3 in COUNTRY_ISO3.items()}
    for _, row in df.iterrows():
        all_rows[row["iso3"]] = (row["country"], int(row["count"]))
    full_df = pd.DataFrame(
        [{"iso3": k, "country": v[0], "count": v[1]} for k, v in all_rows.items()]
    )
    mx = max(int(full_df["count"].max()), 1)
    trace = go.Choropleth(
        locations=full_df["iso3"],
        z=full_df["count"],
        text=full_df["country"],
        customdata=full_df[["country", "count"]].values,
        colorscale=COLORSCALE,
        zmin=0, zmax=mx,
        showscale=True,
        colorbar=dict(
            title=dict(text="ALERTS", font=dict(color="#4a4a3a", size=9, family="Share Tech Mono"), side="right"),
            tickfont=dict(color="#4a4a3a", size=8, family="Share Tech Mono"),
            bgcolor="rgba(0,0,0,0)", bordercolor="#1e1e16", borderwidth=1,
            thickness=10, len=0.55, x=1.005, xpad=6,
        ),
        marker=dict(line=dict(color="#161610", width=0.5)),
        hovertemplate=(
            "<b style='font-family:Oswald'>%{customdata[0]}</b><br>"
            "<span style='font-family:Share Tech Mono;font-size:11px'>"
            "Outbreak Mentions: %{customdata[1]}</span><extra></extra>"
        ),
    )
    fig = go.Figure(trace)
    fig.update_layout(
        geo=dict(
            showframe=False, showcoastlines=True, coastlinecolor="#252518",
            showland=True, landcolor="#141410", showocean=True, oceancolor="#070708",
            showlakes=False, showrivers=False, showcountries=True,
            countrycolor="#1e1e16", projection_type="natural earth",
            bgcolor="#0a0a08", lataxis_range=[-60, 85],
        ),
        paper_bgcolor="#0a0a08", plot_bgcolor="#0a0a08",
        margin=dict(l=0, r=0, t=0, b=0), height=500,
        dragmode="pan", clickmode="event+select",
        hoverlabel=dict(bgcolor="#111109", bordercolor="#4a7c59",
                        font=dict(color="#d4cdb7", size=13, family="Oswald")),
    )
    return fig



# ─── HTML card helpers ────────────────────────────────────────────────────────

def _alert_card(title: str, link: str, date_str: str) -> str:
    return f"""
<div class="alert-card">
  <div class="alert-date">⬡ {date_str}</div>
  <div class="alert-title"><a href="{link}" target="_blank" rel="noopener">{title}</a></div>
</div>"""


def _news_card(source: str, title: str, desc: str, url: str, date_str: str) -> str:
    safe_desc = (desc[:115] + "…") if len(desc) > 115 else desc
    return f"""
<div class="news-card">
  <div class="news-source">{source} &nbsp;·&nbsp; {date_str}</div>
  <div class="news-title">{title}</div>
  <div class="news-desc">{safe_desc}</div>
  <div class="news-link"><a href="{url}" target="_blank" rel="noopener">→ Read full article</a></div>
</div>"""


def _hotspot_html(rank: int, country: str, count: int, max_count: int) -> str:
    pct = int(100 * count / max(max_count, 1))
    enc = quote(country)
    return f"""
<a href="?country={enc}" style="text-decoration:none;display:block;" title="Filter: {country}">
<div class="hotspot-row">
  <div class="hotspot-rank">{rank:02d}</div>
  <div class="hotspot-name">{country}</div>
  <div class="hotspot-bar-wrap"><div class="hotspot-bar" style="width:{pct}%"></div></div>
  <div class="hotspot-count">{count}</div>
</div>
</a>"""


def _tag_pills_html(disease_tags: list[tuple[str, int]], active: str | None) -> str:
    if not disease_tags:
        return ""
    pills = []
    top_count = disease_tags[0][1] if disease_tags else 1
    for i, (d, c) in enumerate(disease_tags[:12]):
        cls = "hot" if i == 0 else ("hi" if c >= top_count * 0.5 else "")
        pills.append(f'<span class="tag-pill {cls}">{d} <b style="opacity:0.6">·{c}</b></span>')
    return '<div class="tag-row">' + "".join(pills) + "</div>"


# ─── Main app ─────────────────────────────────────────────────────────────────

def main() -> None:
    st.markdown(THEME_CSS, unsafe_allow_html=True)
    st.components.v1.html(
        "<script>setTimeout(()=>window.parent.location.reload(),600000);</script>", height=0
    )

    api_key = _get_api_key()

    # ── Handle country selection via query param ────────────────────────────
    # Two sources write to ?country=X:
    #   • Hotspot rows  → <a href="?country=Brazil">   (full country name)
    #   • Map JS click  → <a href="?country=BRA">      (ISO3 code)
    _qp_country = st.query_params.get("country", "")
    if _qp_country:
        _decoded = unquote(_qp_country)
        # Resolve ISO3 → canonical name if needed
        if _decoded in ISO3_TO_NAME:
            _decoded = ISO3_TO_NAME[_decoded]
        if _decoded in COUNTRY_ISO3:
            st.session_state["country_dropdown"] = _decoded
        st.query_params.clear()

    # ── Session state ──────────────────────────────────────────────────────
    if "country_dropdown" not in st.session_state:
        st.session_state["country_dropdown"] = "— Global View —"

    # ── Fetch data FIRST so sidebar can use it ─────────────────────────────
    with st.spinner("Scanning global threat feeds…"):
        who_alerts   = fetch_who_alerts()
        global_news  = fetch_newsapi_global(api_key) if api_key else []
        country_df   = build_country_df(who_alerts, global_news)

    disease_tags = extract_disease_tags(global_news, who_alerts)
    brief_items  = generate_brief(who_alerts, global_news, country_df, disease_tags)

    # ── Sidebar ────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown(
            '<div class="sidebar-title">Outbreak<br>Radar</div>'
            '<div class="sidebar-subtitle">// Outbreak Intelligence</div>',
            unsafe_allow_html=True,
        )
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)

        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        st.markdown(
            '<div class="live-badge"><div class="live-dot"></div>LIVE</div>'
            f'<div class="timestamp">Refreshed: {now_str}</div>',
            unsafe_allow_html=True,
        )
        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("↻  Refresh Data"):
            st.cache_data.clear()
            st.rerun()

        st.markdown("<hr class='divider'>", unsafe_allow_html=True)

        # Country filter — only canonical names (longest name per ISO3),
        # so aliases like "UK", "US", "DRC" are excluded from the dropdown.
        st.markdown('<div class="section-hdr">Filter by Country</div>', unsafe_allow_html=True)
        canonical_countries = sorted(set(ISO3_TO_NAME.values()))
        sorted_countries = ["— Global View —"] + canonical_countries
        st.selectbox("Country", sorted_countries, key="country_dropdown")

        st.markdown("<hr class='divider'>", unsafe_allow_html=True)

        # Hotspots leaderboard
        st.markdown('<div class="section-hdr">Top Outbreak Hotspots</div>', unsafe_allow_html=True)
        if not country_df.empty:
            top8 = country_df.head(8)
            max_c = int(top8["count"].max())
            rows_html = "".join(
                _hotspot_html(i + 1, row["country"], int(row["count"]), max_c)
                for i, row in top8.iterrows()
            )
            st.markdown(rows_html, unsafe_allow_html=True)
        else:
            st.markdown('<div style="font-family:\'Share Tech Mono\',monospace;font-size:0.65rem;color:#3a3a2e;padding:8px 0">No data yet</div>', unsafe_allow_html=True)

        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        st.markdown(
            '<div class="credits"><span>Powered by:</span><br>'
            "· WHO Disease Outbreak News<br>· NewsAPI.org<br>· Plotly · Streamlit<br><br>"
            '<span>Coverage: last 28 days</span><br>Auto-refresh: every 10 min</div>',
            unsafe_allow_html=True,
        )

    # ── Derive filters ─────────────────────────────────────────────────────
    _raw = st.session_state.get("country_dropdown", "— Global View —")
    selected_country = None if _raw == "— Global View —" else _raw

    # Pills widget owns its own state via key "disease_pills_widget".
    # Read it from the previous run — no manual sync needed.
    active_disease: str | None = st.session_state.get("disease_pills_widget")

    # ── Metrics strip ──────────────────────────────────────────────────────
    n_who      = len(who_alerts)
    n_countries = len(country_df)
    n_news     = len(global_news)
    api_status = "CONNECTED" if api_key else "NO KEY"
    api_color  = "#4a7c59" if api_key else "#cc3f0c"

    st.markdown(f"""
    <div class="metric-row">
      <div class="metric-box"><div class="metric-val">{n_who}</div><div class="metric-lbl">WHO Alerts</div></div>
      <div class="metric-box"><div class="metric-val">{n_countries}</div><div class="metric-lbl">Countries Flagged</div></div>
      <div class="metric-box"><div class="metric-val">{n_news}</div><div class="metric-lbl">News Articles</div></div>
      <div class="metric-box"><div class="metric-val" style="font-size:0.85rem;color:{api_color};padding-top:4px">{api_status}</div><div class="metric-lbl">NewsAPI</div></div>
    </div>""", unsafe_allow_html=True)

    # ── Intelligence Brief ─────────────────────────────────────────────────
    items_html = "".join(f'<div class="intel-item">⬡ &nbsp;{item}</div>' for item in brief_items)
    st.markdown(f"""
    <div class="intel-wrap">
      <div class="intel-label">// Intel Brief</div>
      <div class="intel-items">{items_html}</div>
    </div>""", unsafe_allow_html=True)

    # ── Map hero ───────────────────────────────────────────────────────────
    st.markdown(
        '<div class="map-title">// GLOBAL OUTBREAK ACTIVITY MAP — LAST 28 DAYS</div>',
        unsafe_allow_html=True,
    )
    map_fig = build_map(country_df)
    st.markdown('<div class="map-wrapper">', unsafe_allow_html=True)
    st.plotly_chart(
        map_fig,
        use_container_width=True,
        config={
            "displayModeBar": True,
            "modeBarButtonsToRemove": ["select2d", "lasso2d", "autoScale2d", "toImage"],
            "displaylogo": False,
            "scrollZoom": True,
        },
        key="choropleth_map",
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Map click handler (JS → query param → session state) ───────────────
    # Renders at height=0 (invisible). Reaches into the parent Streamlit page,
    # attaches a native plotly_click listener to every .js-plotly-plot div,
    # and on a choropleth click navigates window.parent to ?country=ISO3.
    # The query-param handler above resolves ISO3 → country name.
    st.components.v1.html("""
<script>
(function () {
    function attach() {
        try {
            var divs = window.parent.document.querySelectorAll('.js-plotly-plot');
            divs.forEach(function (div) {
                if (div._mapClickBound) return;
                div._mapClickBound = true;
                div.on('plotly_click', function (evt) {
                    if (!evt || !evt.points || !evt.points.length) return;
                    var loc = evt.points[0].location;          // ISO3 for choropleth
                    if (loc && /^[A-Z]{2,3}$/.test(loc)) {
                        window.parent.location.href =
                            window.parent.location.origin +
                            window.parent.location.pathname +
                            '?country=' + encodeURIComponent(loc);
                    }
                });
            });
        } catch (e) {}
    }
    // Retry several times to survive Streamlit's async rendering
    [300, 700, 1400, 2500].forEach(function (ms) { setTimeout(attach, ms); });
})();
</script>
""", height=0)

    # ── Pathogen Activity Chart ────────────────────────────────────────────
    st.markdown(
        '<div class="timeline-hdr">// PATHOGEN ACTIVITY INDEX — CURRENT PERIOD</div>',
        unsafe_allow_html=True,
    )
    disease_fig = build_disease_chart(disease_tags)
    st.plotly_chart(
        disease_fig,
        use_container_width=True,
        config={"displayModeBar": False, "displaylogo": False},
        key="disease_chart",
    )

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    # ── Bottom panels ──────────────────────────────────────────────────────
    col_left, col_right = st.columns([1, 1], gap="medium")

    # ── WHO Alerts ─────────────────────────────────────────────────────────
    with col_left:
        week_ago = datetime.now(timezone.utc) - timedelta(days=7)
        new_this_week = sum(
            1 for a in who_alerts if a.get("published") and a["published"] > week_ago
        )
        badge = (
            f'&nbsp;<span style="font-family:\'Share Tech Mono\',monospace;'
            f'font-size:0.6rem;background:rgba(204,63,12,0.18);border:1px solid #cc3f0c;'
            f'border-radius:2px;padding:1px 6px;color:#ff6535;letter-spacing:0.06em;">'
            f'+{new_this_week} this week</span>'
            if new_this_week else ""
        )
        st.markdown(
            f'<div class="section-hdr">// Latest Global Alerts &nbsp;·&nbsp; WHO{badge}</div>',
            unsafe_allow_html=True,
        )
        top_alerts = who_alerts[:10]
        if top_alerts:
            cards = []
            for a in top_alerts:
                ds = a["published"].strftime("%d %b %Y") if a.get("published") else "—"
                cards.append(_alert_card(a["title"], a["link"], ds))
            st.markdown('<div class="scroll-box">' + "".join(cards) + "</div>",
                        unsafe_allow_html=True)
        else:
            st.markdown(
                '<div class="empty-state">WHO feed unavailable — check connection</div>',
                unsafe_allow_html=True,
            )

    # ── News Feed ──────────────────────────────────────────────────────────
    with col_right:
        label = selected_country or "Global"
        dis_label = f" · {active_disease}" if active_disease else ""

        # ✕ Clear reset — shown inline when any filter is active
        hdr_right = ""
        if selected_country or active_disease:
            hdr_right = (
                '&nbsp;&nbsp;<span style="font-family:\'Share Tech Mono\',monospace;'
                'font-size:0.6rem;color:#3a3a2e;letter-spacing:0.06em;" '
                'title="Use the sidebar dropdowns to reset">✕ filters active</span>'
            )
        st.markdown(
            f'<div class="section-hdr">// News Feed &nbsp;·&nbsp; {label}{dis_label}{hdr_right}</div>',
            unsafe_allow_html=True,
        )

        # Clickable disease pills — each press toggles the sidebar disease filter
        if disease_tags:
            pill_keys = [d for d, _ in disease_tags[:12]]
            # st.pills is available in Streamlit ≥ 1.40; we try it and fall back
            try:
                st.pills(
                    "disease",
                    options=pill_keys,
                    format_func=lambda d: f"{d}  ·{dict(disease_tags).get(d,'')}",
                    selection_mode="single",
                    key="disease_pills_widget",
                    label_visibility="collapsed",
                )
            except AttributeError:
                # Fallback: display-only pill HTML (sidebar selectbox still works)
                st.markdown(_tag_pills_html(disease_tags, active_disease), unsafe_allow_html=True)

        # Fetch articles — use the full pool before any slicing so the
        # disease filter can search across all articles, not just the first 15.
        if selected_country and api_key:
            articles = fetch_newsapi_country(selected_country, api_key)
        elif api_key:
            articles = global_news   # full pool; sliced to 15 below after filtering
        else:
            articles = []

        # Apply disease filter across the full pool
        if active_disease and articles:
            kws = [k.lower() for k in DISEASE_VOCAB.get(active_disease, [active_disease.lower()])]
            articles = [
                a for a in articles
                if any(kw in f"{a.get('title','')} {a.get('description','')}".lower() for kw in kws)
            ]

        if articles:
            cards = []
            for art in articles[:15]:
                src  = art.get("source", {}).get("name", "Unknown")
                ttl  = art.get("title", "No title")
                dsc  = art.get("description") or ""
                lnk  = art.get("url", "#")
                pub  = (art.get("publishedAt") or "")[:10]
                cards.append(_news_card(src, ttl, dsc, lnk, pub))
            st.markdown('<div class="scroll-box">' + "".join(cards) + "</div>",
                        unsafe_allow_html=True)
        elif not api_key:
            st.markdown(
                '<div class="empty-state">Set NEWS_API_KEY in .streamlit/secrets.toml</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="empty-state">No recent articles found for {label}{dis_label}.</div>',
                unsafe_allow_html=True,
            )


if __name__ == "__main__":
    main()
