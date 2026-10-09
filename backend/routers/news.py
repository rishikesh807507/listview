from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.database import get_db
from backend.models import News
from backend.data_providers.news_provider import NewsProvider

router = APIRouter(prefix="/news", tags=["News"])

@router.get("")
def get_news(
    symbol: Optional[str] = None,
    category: Optional[str] = None,
    sentiment: Optional[str] = None,
    refresh: bool = False,
    db: Session = Depends(get_db)
):
    if refresh:
        provider = NewsProvider()
        items = provider.fetch_rss_news()
        for item in items:
            existing = db.query(News).filter(News.title == item["title"]).first()
            if not existing:
                from datetime import datetime
                db.add(News(
                    title=item["title"],
                    source=item["source"],
                    published_at=datetime.fromisoformat(item["published_at"]),
                    url=item.get("url"),
                    related_stock=item.get("related_stock"),
                    category=item.get("category", "Markets"),
                    sentiment=item.get("sentiment", "Neutral"),
                    sentiment_score=item.get("sentiment_score", 0.0),
                    summary=item.get("summary")
                ))
        db.commit()

    query = db.query(News)
    if symbol:
        query = query.filter(News.related_stock == symbol.upper().strip())
    if category and category.lower() != "all":
        query = query.filter(News.category.ilike(f"%{category}%"))
    if sentiment and sentiment.lower() != "all":
        query = query.filter(News.sentiment.ilike(sentiment))

    articles = query.order_by(News.published_at.desc()).limit(30).all()
    return {
        "count": len(articles),
        "articles": articles,
        "disclaimer": "News sentiment scores are derived from open-source linguistic rules and should not be treated as factual financial guidance."
    }
