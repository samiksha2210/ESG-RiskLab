import sqlite3
import pandas as pd
from datetime import datetime
from pathlib import Path
import config

class DatabaseManager:
    def __init__(self, db_path=config.DATABASE_PATH):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database with schema"""
        with sqlite3.connect(self.db_path) as conn:
            schema_path = Path(__file__).parent / 'schema.sql'
            with open(schema_path, 'r') as f:
                conn.executescript(f.read())
    
    def add_company(self, ticker, company_name, sector, market_cap=None):
        """Add or update company information"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT OR REPLACE INTO companies (ticker, company_name, sector, market_cap)
                VALUES (?, ?, ?, ?)
            ''', (ticker, company_name, sector, market_cap))
    
    def save_audit(self, ticker, sec_sentiment, news_sentiment, 
                   sentiment_delta, greenwashing_score, risk_level, summary):
        """Save ESG audit results"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO esg_audits 
                (ticker, sec_sentiment, news_sentiment, sentiment_delta, 
                 greenwashing_score, risk_level, summary)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (ticker, sec_sentiment, news_sentiment, sentiment_delta,
                  greenwashing_score, risk_level, summary))
    
    def save_news_articles(self, ticker, articles):
        """Save news articles with sentiment"""
        with sqlite3.connect(self.db_path) as conn:
            for article in articles:
                conn.execute('''
                    INSERT INTO news_articles 
                    (ticker, title, url, published_at, sentiment_score, source)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (ticker, article['title'], article.get('url'), 
                      article.get('published_at'), article.get('sentiment'), 
                      article.get('source')))
    
    def save_sec_filing(self, ticker, filing_type, filing_date, 
                        sentiment_score, text_excerpt, url):
        """Save SEC filing information"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO sec_filings 
                (ticker, filing_type, filing_date, sentiment_score, text_excerpt, url)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (ticker, filing_type, filing_date, sentiment_score, 
                  text_excerpt, url))
    
    def get_audit_history(self, ticker):
        """Retrieve audit history for a company"""
        query = '''
            SELECT audit_date, greenwashing_score, risk_level, 
                   sec_sentiment, news_sentiment
            FROM esg_audits
            WHERE ticker = ?
            ORDER BY audit_date DESC
        '''
        return pd.read_sql_query(query, sqlite3.connect(self.db_path), 
                                 params=(ticker,))
    
    def get_sector_stats(self):
        """Get aggregated statistics by sector"""
        query = '''
            SELECT c.sector, 
                   AVG(e.greenwashing_score) as avg_risk,
                   COUNT(DISTINCT e.ticker) as company_count,
                   AVG(e.news_sentiment) as avg_sentiment
            FROM companies c
            JOIN esg_audits e ON c.ticker = e.ticker
            WHERE e.audit_date >= date('now', '-30 days')
            GROUP BY c.sector
        '''
        return pd.read_sql_query(query, sqlite3.connect(self.db_path))
    
    def get_latest_audits(self, limit=10):
        """Get most recent audits across all companies"""
        query = '''
            SELECT e.*, c.company_name, c.sector
            FROM esg_audits e
            JOIN companies c ON e.ticker = c.ticker
            ORDER BY e.audit_date DESC
            LIMIT ?
        '''
        return pd.read_sql_query(query, sqlite3.connect(self.db_path), 
                                 params=(limit,))
    
    def get_news_for_ticker(self, ticker, days=30):
        """Get recent news for a ticker"""
        query = '''
            SELECT title, sentiment_score, published_at, url, source
            FROM news_articles
            WHERE ticker = ? AND published_at >= date('now', '-' || ? || ' days')
            ORDER BY published_at DESC
        '''
        return pd.read_sql_query(query, sqlite3.connect(self.db_path),
                                 params=(ticker, days))