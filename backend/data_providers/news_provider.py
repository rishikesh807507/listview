import logging
import feedparser
from typing import List, Dict, Any, Optional
from datetime import datetime
from backend.data_providers.base_provider import BaseProvider

logger = logging.getLogger("NewsProvider")

# Popular free public RSS feeds in India (No API Key Required)
FREE_RSS_FEEDS = [
    {"source": "LiveMint Markets", "url": "https://www.livemint.com/rss/markets"},
    {"source": "Economic Times Markets", "url": "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms"},
    {"source": "Business Standard", "url": "https://www.business-standard.com/rss/markets-106.rss"}
]

# Lexicons for financial sentiment classification
POSITIVE_KEYWORDS = {
    "growth", "surge", "gain", "profit", "bull", "jump", "record", "higher",
    "rally", "upgrade", "outperform", "expand", "soar", "dividend", "acquisition",
    "beat", "strong", "positive", "boom", "uptrend", "resilient", "expansion"
}
NEGATIVE_KEYWORDS = {
    "fall", "drop", "loss", "slump", "bear", "down", "penalty", "deficit",
    "decline", "downgrade", "underperform", "crash", "plunge", "fraud", "scam",
    "weak", "lower", "negative", "investigation", "probe", "selloff", "inflation"
}

def analyze_sentiment(text: str) -> tuple[str, float]:
    """
    Open-source rule-based financial sentiment analyzer.
    Zero external paid AI API used.
    Returns (SentimentLabel, ScoreBetween -1 and +1).
    """
    if not text:
        return "Neutral", 0.0
    
    words = text.lower().split()
    pos_count = sum(1 for w in words if any(kw in w for kw in POSITIVE_KEYWORDS))
    neg_count = sum(1 for w in words if any(kw in w for kw in NEGATIVE_KEYWORDS))
    total = pos_count + neg_count
    
    if total == 0:
        return "Neutral", 0.0
    
    score = round((pos_count - neg_count) / total, 2)
    if score > 0.15:
        return "Positive", score
    elif score < -0.15:
        return "Negative", score
    else:
        return "Neutral", score

class NewsProvider(BaseProvider):
    """
    Free News Provider using public RSS Feeds and Open-Source Sentiment Analysis.
    Never relies on paid financial news APIs.
    """
    def __init__(self):
        super().__init__("Public Financial RSS Feeds")

    def health_check(self) -> bool:
        return True

    def fetch_rss_news(self) -> List[Dict[str, Any]]:
        """Fetch latest market news from public RSS feeds."""
        items = []
        for feed_info in FREE_RSS_FEEDS:
            try:
                feed = feedparser.parse(feed_info["url"])
                for entry in feed.entries[:5]:  # Take top 5 from each
                    title = entry.get("title", "")
                    summary = entry.get("summary", "")
                    full_text = f"{title} {summary}"
                    sentiment, score = analyze_sentiment(full_text)
                    
                    # Detect related stock if mentioned
                    related = None
                    for ticker in ["RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK", "BHARTIARTL", "TATAMOTORS", "ITC", "LT", "SUNPHARMA"]:
                        if ticker.lower() in full_text.lower():
                            related = ticker
                            break

                    items.append({
                        "title": title,
                        "source": feed_info["source"],
                        "published_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S"),
                        "url": entry.get("link", ""),
                        "related_stock": related,
                        "category": "Markets",
                        "sentiment": sentiment,
                        "sentiment_score": score,
                        "summary": summary[:300] if summary else ""
                    })
            except Exception as e:
                logger.warning(f"Error parsing RSS feed {feed_info['url']}: {e}")
        
        return items
