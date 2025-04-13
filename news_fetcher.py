import os
import json
import requests
import logging
import trafilatura
from datetime import datetime
from flask import current_app
from app import db
from models import News, Category, Country
from googleapiclient.discovery import build
from utils import translate_text

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# API Keys
NEWS_API_KEY = os.environ.get("NEWS_API_KEY", "")
GNEWS_API_KEY = os.environ.get("GNEWS_API_KEY", "")

# News sources by country
news_sources = {
    'US': ['cnn', 'the-new-york-times', 'bbc-news'],
    'IN': ['the-times-of-india', 'the-hindu'],
    'PK': ['dawn-news', 'geo-news'],
    'SA': ['arab-news', 'saudi-gazette'],
    'LK': ['daily-news-lk', 'colombo-gazette']
}

# RSS feed URLs
rss_feeds = {
    'US': [
        'http://rss.cnn.com/rss/cnn_topstories.rss',
        'https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml'
    ],
    'IN': [
        'https://timesofindia.indiatimes.com/rssfeeds/1221656.cms',
        'https://www.thehindu.com/news/feeder/default.rss'
    ],
    'PK': [
        'https://www.dawn.com/feed',
        'https://www.geo.tv/rss/1/1'
    ],
    'SA': [
        'https://www.arabnews.com/rss.xml',
        'https://saudigazette.com.sa/feed'
    ],
    'LK': [
        'http://www.dailynews.lk/rss.xml',
        'https://colombogazette.com/feed/'
    ]
}

def fetch_from_newsapi(country_code):
    """Fetch news from NewsAPI based on country code"""
    try:
        url = f"https://newsapi.org/v2/top-headlines?country={country_code.lower()}&apiKey={NEWS_API_KEY}"
        response = requests.get(url)
        data = response.json()
        
        if response.status_code == 200 and data.get('status') == 'ok':
            articles = data.get('articles', [])
            logger.info(f"Fetched {len(articles)} articles from NewsAPI for {country_code}")
            return articles
        else:
            logger.error(f"Failed to fetch from NewsAPI: {data.get('message')}")
            return []
    except Exception as e:
        logger.error(f"Error fetching from NewsAPI: {str(e)}")
        return []

def fetch_from_gnews(country_code):
    """Fetch news from GNews based on country code"""
    try:
        url = f"https://gnews.io/api/v4/top-headlines?country={country_code.lower()}&token={GNEWS_API_KEY}"
        response = requests.get(url)
        data = response.json()
        
        if response.status_code == 200 and 'articles' in data:
            articles = data.get('articles', [])
            logger.info(f"Fetched {len(articles)} articles from GNews for {country_code}")
            return articles
        else:
            logger.error(f"Failed to fetch from GNews: {data.get('message', 'Unknown error')}")
            return []
    except Exception as e:
        logger.error(f"Error fetching from GNews: {str(e)}")
        return []

def scrape_website(url):
    """Scrape website content using trafilatura"""
    try:
        downloaded = trafilatura.fetch_url(url)
        text = trafilatura.extract(downloaded)
        if text:
            # Get first 500 characters as summary
            summary = text[:500] + "..." if len(text) > 500 else text
            return {
                "content": text,
                "summary": summary
            }
        return None
    except Exception as e:
        logger.error(f"Error scraping website {url}: {str(e)}")
        return None

def process_news_article(article, country_id, category_name="General"):
    """Process and add news article to database"""
    try:
        # Get or create category
        category = Category.query.filter_by(name=category_name).first()
        if not category:
            category = Category(name=category_name)
            db.session.add(category)
            db.session.commit()
        
        # Check if article already exists (by URL or title)
        existing = News.query.filter_by(source_url=article.get('url')).first()
        if not existing:
            existing = News.query.filter_by(title=article.get('title')).first()
        
        if existing:
            logger.debug(f"Article already exists: {article.get('title')}")
            return None
        
        # For articles without content, try to scrape the website
        if not article.get('content') and article.get('url'):
            scraped = scrape_website(article.get('url'))
            if scraped:
                article['content'] = scraped['content']
                if not article.get('description'):
                    article['description'] = scraped['summary']
        
        # Create news object
        news = News(
            title=article.get('title'),
            summary=article.get('description', ''),
            content=article.get('content', ''),
            image_url=article.get('urlToImage') or article.get('image'),
            source_url=article.get('url'),
            source_name=article.get('source', {}).get('name') or article.get('source', {}).get('name', 'Unknown'),
            published_at=article.get('publishedAt') if article.get('publishedAt') else datetime.utcnow(),
            category_id=category.id,
            country_id=country_id,
            is_auto_generated=True,
            is_published=True
        )
        
        db.session.add(news)
        db.session.commit()
        logger.info(f"Added news article: {news.title}")
        
        # Generate translations (can be async in production)
        try:
            translations = {}
            summary_en = news.summary
            title_en = news.title
            
            # Translate to other languages
            for lang_code in ['hi', 'ur', 'ar', 'si']:  # Hindi, Urdu, Arabic, Sinhala
                translations[lang_code] = {
                    'title': translate_text(title_en, lang_code),
                    'summary': translate_text(summary_en, lang_code)
                }
            
            news.translations = json.dumps(translations)
            db.session.commit()
            logger.info(f"Added translations for news ID: {news.id}")
        except Exception as e:
            logger.error(f"Error generating translations: {str(e)}")
        
        return news
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error processing news article: {str(e)}")
        return None

def fetch_news_for_country(country):
    """Fetch news for a specific country"""
    try:
        logger.info(f"Fetching news for {country.name}")
        
        # Fetch from NewsAPI
        articles = fetch_from_newsapi(country.code)
        
        # If NewsAPI fails or returns empty, try GNews
        if not articles:
            articles = fetch_from_gnews(country.code)
        
        # Process articles
        for article in articles:
            process_news_article(article, country.id)
        
        return len(articles)
    except Exception as e:
        logger.error(f"Error fetching news for {country.name}: {str(e)}")
        return 0

def fetch_all_news():
    """Fetch news for all countries"""
    try:
        logger.info("Starting automated news fetch")
        countries = Country.query.all()
        
        total_articles = 0
        for country in countries:
            count = fetch_news_for_country(country)
            total_articles += count
        
        logger.info(f"Completed news fetch, processed {total_articles} articles")
        return total_articles
    except Exception as e:
        logger.error(f"Error in fetch_all_news: {str(e)}")
        return 0

if __name__ == "__main__":
    # For testing purposes when run directly
    from app import app
    with app.app_context():
        fetch_all_news()
