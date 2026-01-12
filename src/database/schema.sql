-- Company Information
CREATE TABLE IF NOT EXISTS companies (
    ticker TEXT PRIMARY KEY,
    company_name TEXT NOT NULL,
    sector TEXT NOT NULL,
    market_cap REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ESG Audit History
CREATE TABLE IF NOT EXISTS esg_audits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT NOT NULL,
    audit_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sec_sentiment REAL,
    news_sentiment REAL,
    sentiment_delta REAL,
    greenwashing_score REAL,
    risk_level TEXT,
    summary TEXT,
    FOREIGN KEY (ticker) REFERENCES companies(ticker)
);

-- News Articles
CREATE TABLE IF NOT EXISTS news_articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT NOT NULL,
    title TEXT NOT NULL,
    url TEXT,
    published_at TIMESTAMP,
    sentiment_score REAL,
    source TEXT,
    FOREIGN KEY (ticker) REFERENCES companies(ticker)
);

-- SEC Filings
CREATE TABLE IF NOT EXISTS sec_filings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT NOT NULL,
    filing_type TEXT,
    filing_date DATE,
    sentiment_score REAL,
    text_excerpt TEXT,
    url TEXT,
    FOREIGN KEY (ticker) REFERENCES companies(ticker)
);

-- Performance Metrics
CREATE TABLE IF NOT EXISTS stock_performance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT NOT NULL,
    date DATE,
    stock_return REAL,
    volatility REAL,
    FOREIGN KEY (ticker) REFERENCES companies(ticker)
);

-- Indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_audits_ticker ON esg_audits(ticker);
CREATE INDEX IF NOT EXISTS idx_audits_date ON esg_audits(audit_date);
CREATE INDEX IF NOT EXISTS idx_news_ticker ON news_articles(ticker);
CREATE INDEX IF NOT EXISTS idx_sec_ticker ON sec_filings(ticker);