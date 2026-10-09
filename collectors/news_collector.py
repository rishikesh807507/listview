import logging
from datetime import datetime
from backend.database import SessionLocal
from backend.models import News
from backend.data_providers.news_provider import NewsProvider

logger = logging.getLogger("NewsCollector")

def collect_news():
    """Polls free RSS feeds and saves new items with sentiment classification."""
    db = SessionLocal()
    provider = NewsProvider()
    try:
        items = provider.fetch_rss_news()
        added = 0
        for item in items:
            existing = db.query(News).filter(News.title == item["title"]).first()
            if not existing:
                news_obj = News(
                    title=item["title"],
                    source=item["source"],
                    published_at=datetime.fromisoformat(item["published_at"]),
                    url=item.get("url"),
                    related_stock=item.get("related_stock"),
                    category=item.get("category", "Markets"),
                    sentiment=item.get("sentiment", "Neutral"),
                    sentiment_score=item.get("sentiment_score", 0.0),
                    summary=item.get("summary"),
                    created_at=datetime.utcnow()
                )
                db.add(news_obj)
                added += 1
        db.commit()
        print(f"[NewsCollector] Processed {len(items)} RSS items, added {added} new articles.")
    except Exception as e:
        print(f"[NewsCollector Error] {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    collect_news()
