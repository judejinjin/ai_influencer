"""
Fetches trending food-safety and nutrition news from Google News RSS.
"""
import feedparser
from src.config import DATA_DIR

# Google News RSS search queries — no API key needed
GOOGLE_NEWS_QUERIES = [
    "food safety recall",
    "FDA food regulation",
    "ultra processed food health",
    "food additive banned",
    "obesity epidemic USA",
    "toxic food ingredients",
]


def fetch_trending_news(days: int = 7, max_results: int = 20) -> list[dict]:
    """
    Fetch recent food-safety news from Google News RSS (free, no API key).
    Grok is used later in the pipeline for *analyzing* the news context.
    """
    articles = _fetch_from_google_rss(max_results)
    articles = _deduplicate(articles)
    articles.sort(key=lambda a: a.get("date", ""), reverse=True)
    return articles[:max_results]


def _fetch_from_google_rss(max_per_query: int = 5) -> list[dict]:
    """Fetch from Google News RSS feeds (free, no API key)."""
    articles = []
    for query in GOOGLE_NEWS_QUERIES:
        feed_url = (
            f"https://news.google.com/rss/search?q={query.replace(' ', '+')}"
            f"&hl=en-US&gl=US&ceid=US:en"
        )
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:max_per_query]:
                articles.append({
                    "title": entry.get("title", ""),
                    "summary": entry.get("summary", ""),
                    "source": entry.get("source", {}).get("title", "Google News"),
                    "url": entry.get("link", ""),
                    "date": (
                        entry.get("published", "")[:10]
                        if entry.get("published")
                        else ""
                    ),
                    "origin": "google_rss",
                })
        except Exception as e:
            print(f"⚠️  Error fetching RSS for '{query}': {e}")
    return articles


def _deduplicate(articles: list[dict]) -> list[dict]:
    """Remove near-duplicate articles based on title similarity."""
    seen_titles: set[str] = set()
    unique = []
    for a in articles:
        key = a["title"].lower()[:50]
        if key not in seen_titles:
            seen_titles.add(key)
            unique.append(a)
    return unique


def format_for_prompt(articles: list[dict], count: int = 5) -> str:
    """Format news articles into an LLM-injectable string."""
    lines = ["TRENDING FOOD SAFETY NEWS:"]
    for a in articles[:count]:
        lines.append(
            f"  • [{a['date']}] {a['title']} (Source: {a['source']})\n"
            f"    Summary: {a['summary']}"
        )
    return "\n".join(lines)
