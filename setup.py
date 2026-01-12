#!/usr/bin/env python
"""
Setup script for ESG Intelligence Platform
Handles initial setup and verification
"""

import os
import sys
from pathlib import Path
import subprocess

def create_directories():
    """Create necessary directories"""
    directories = [
        'data/raw',
        'data/processed',
        'data/vector_store',
        'models/sentiment',
        'models/summarization'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created {directory}")

def verify_python_version():
    """Check Python version"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        sys.exit(1)
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} detected")

def install_requirements():
    """Install Python packages"""
    print("\n📦 Installing requirements (this may take a few minutes)...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Requirements installed")
    except subprocess.CalledProcessError:
        print("❌ Failed to install requirements")
        sys.exit(1)

def initialize_database():
    """Initialize SQLite database"""
    print("\n🗄️ Initializing database...")
    try:
        from src.database.db_manager import DatabaseManager
        db = DatabaseManager()
        print("✓ Database initialized")
        
        # Add sample companies
        import config
        for ticker, sector in config.SECTOR_MAPPING.items():
            company_names = {
                'AAPL': 'Apple Inc',
                'MSFT': 'Microsoft Corporation',
                'GOOGL': 'Alphabet Inc',
                'XOM': 'Exxon Mobil',
                'CVX': 'Chevron Corporation',
                'BP': 'BP plc',
                'TSLA': 'Tesla Inc',
                'F': 'Ford Motor Company',
                'JPM': 'JPMorgan Chase',
                'BAC': 'Bank of America',
                'JNJ': 'Johnson & Johnson',
                'PFE': 'Pfizer Inc'
            }
            db.add_company(ticker, company_names.get(ticker, ticker), sector)
        
        print("✓ Sample companies added")
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")

def create_env_file():
    """Create .env file if it doesn't exist"""
    if not Path('.env').exists():
        print("\n📝 Creating .env file...")
        with open('.env.example', 'r') as src:
            with open('.env', 'w') as dst:
                dst.write(src.read())
        print("✓ .env file created (please add your API keys)")
    else:
        print("✓ .env file exists")

def download_models():
    """Pre-download AI models"""
    print("\n🧠 Downloading AI models (this will take several minutes)...")
    print("   This is a one-time download (~2GB)")
    
    try:
        from transformers import AutoTokenizer, AutoModelForSequenceClassification
        from transformers import BartTokenizer, BartForConditionalGeneration
        import config
        
        # Download FinBERT
        print("   Downloading FinBERT...")
        AutoTokenizer.from_pretrained(config.SENTIMENT_MODEL, cache_dir='./models/sentiment')
        AutoModelForSequenceClassification.from_pretrained(config.SENTIMENT_MODEL, cache_dir='./models/sentiment')
        
        # Download BART
        print("   Downloading BART...")
        BartTokenizer.from_pretrained(config.SUMMARIZATION_MODEL, cache_dir='./models/summarization')
        BartForConditionalGeneration.from_pretrained(config.SUMMARIZATION_MODEL, cache_dir='./models/summarization')
        
        print("✓ Models downloaded successfully")
        
    except Exception as e:
        print(f"⚠️ Model download failed: {e}")
        print("   Models will be downloaded on first run")

def main():
    """Run setup process"""
    print("=" * 60)
    print("ESG Intelligence Platform - Setup")
    print("=" * 60)
    
    verify_python_version()
    create_directories()
    
    # Ask if user wants to install requirements
    response = input("\n📦 Install Python requirements? (y/n): ")
    if response.lower() == 'y':
        install_requirements()
    
    create_env_file()
    initialize_database()
    
    # Ask if user wants to download models now
    response = input("\n🧠 Download AI models now? (~2GB, recommended) (y/n): ")
    if response.lower() == 'y':
        download_models()
    
    print("\n" + "=" * 60)
    print("✅ Setup Complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. (Optional) Add API keys to .env file")
    print("2. Run: streamlit run app.py")
    print("3. Open browser to http://localhost:8501")
    print("\nFor help: Read README.md")
    print("=" * 60)

if __name__ == "__main__":
    main()