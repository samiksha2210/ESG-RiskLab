import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
NEWS_API_KEY = os.getenv('NEWS_API_KEY', '')
SEC_API_KEY = os.getenv('SEC_API_KEY', '')

# Database
DATABASE_PATH = 'data/esg_intelligence.db'
VECTOR_STORE_PATH = 'data/vector_store'

# Model Configurations
SENTIMENT_MODEL = 'ProsusAI/finbert'
SUMMARIZATION_MODEL = 'facebook/bart-large-cnn'
EMBEDDING_MODEL = 'sentence-transformers/all-MiniLM-L6-v2'

# Sector Classifications
SECTOR_MAPPING = {
    'AAPL': 'Technology',
    'MSFT': 'Technology',
    'GOOGL': 'Technology',
    'XOM': 'Energy',
    'CVX': 'Energy',
    'BP': 'Energy',
    'TSLA': 'Automotive',
    'F': 'Automotive',
    'JPM': 'Finance',
    'BAC': 'Finance',
    'JNJ': 'Healthcare',
    'PFE': 'Healthcare'
}

# Risk Thresholds
RISK_THRESHOLDS = {
    'low': 0.3,
    'medium': 0.6,
    'high': 1.0
}

# Data Collection Settings
MAX_NEWS_ARTICLES = 20
NEWS_LOOKBACK_DAYS = 30

# RAG Settings
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
TOP_K_RESULTS = 5