from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import pandas as pd
from pathlib import Path
import sys

# Add src to path
sys.path.append(str(Path(__file__).parent))

from src.data_collection.sec_scraper import SECScraper
from src.data_collection.news_scraper import NewsScraper
from src.ai_models.sentiment_analyzer import SentimentAnalyzer
from src.ai_models.summarizer import ESGSummarizer
from src.ai_models.rag_engine import RAGEngine
from src.database.db_manager import DatabaseManager
from src.analytics.visualizations import ESGVisualizations
import config

# Page configuration
st.set_page_config(
    page_title="ESG Intelligence Platform",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = False
    st.session_state.models_loaded = False

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .risk-high { color: #d62728; font-weight: bold; }
    .risk-medium { color: #ff7f0e; font-weight: bold; }
    .risk-low { color: #2ca02c; font-weight: bold; }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

def load_models():
    """Load AI models once and cache them"""
    with st.spinner("🧠 Loading AI models (this may take a minute on first run)..."):
        sentiment_analyzer = SentimentAnalyzer()
        summarizer = ESGSummarizer()
        rag_engine = RAGEngine()
        db_manager = DatabaseManager()
    return sentiment_analyzer, summarizer, rag_engine, db_manager

def main():
    # Header
    st.markdown('<h1 class="main-header">🌍 ESG Intelligence & Risk Platform</h1>', unsafe_allow_html=True)
    st.markdown("*AI-Powered Greenwashing Detection & ESG Risk Analysis*")
    
    # Load models
    if not st.session_state.models_loaded:
        try:
            sentiment_analyzer, summarizer, rag_engine, db_manager = load_models()
            st.session_state.sentiment_analyzer = sentiment_analyzer
            st.session_state.summarizer = summarizer
            st.session_state.rag_engine = rag_engine
            st.session_state.db_manager = db_manager
            st.session_state.models_loaded = True
            st.success("✅ AI models loaded successfully!")
        except Exception as e:
            st.error(f"Error loading models: {e}")
            st.stop()
    
    # Sidebar
    st.sidebar.title("📊 Navigation")
    page = st.sidebar.radio("Select Page", [
        "🔍 Company Analysis",
        "📈 Sector Benchmark",
        "📚 Document Q&A (RAG)",
        "📋 Audit History",
        "ℹ️ About"
    ])
    
    if page == "🔍 Company Analysis":
        company_analysis_page()
    elif page == "📈 Sector Benchmark":
        sector_benchmark_page()
    elif page == "📚 Document Q&A (RAG)":
        rag_page()
    elif page == "📋 Audit History":
        audit_history_page()
    else:
        about_page()

def company_analysis_page():
    st.header("🔍 Company ESG Risk Analysis")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        ticker = st.text_input("Enter Stock Ticker", "TSLA").upper()
    
    with col2:
        company_name = st.text_input("Company Name", "Tesla Inc")
    
    if st.button("🚀 Run Analysis", type="primary", use_container_width=True):
        run_company_analysis(ticker, company_name)

def run_company_analysis(ticker, company_name):
    """Execute full ESG analysis pipeline"""
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Step 1: Data Collection
        status_text.text("📡 Collecting data from SEC and NewsAPI...")
        progress_bar.progress(20)
        
        sec_scraper = SECScraper()
        news_scraper = NewsScraper()
        
        sec_data = sec_scraper.get_esg_disclosure(ticker)
        news_data = news_scraper.get_company_news(ticker, company_name)
        
        # Step 2: Sentiment Analysis
        status_text.text("🧠 Analyzing sentiment with FinBERT...")
        progress_bar.progress(40)
        
        sentiment_analyzer = st.session_state.sentiment_analyzer
        news_titles = [article['title'] for article in news_data]
        
        risk_analysis = sentiment_analyzer.calculate_sentiment_delta(sec_data['text'], news_titles)
        
        # Step 3: Generate Summary
        status_text.text("✍️ Generating executive summary with BART...")
        progress_bar.progress(60)
        
        summarizer = st.session_state.summarizer
        executive_summary = summarizer.generate_executive_summary(
            risk_analysis, sec_data['text'], news_titles
        )
        
        # Step 4: Save to Database
        status_text.text("💾 Saving audit results...")
        progress_bar.progress(80)
        
        db_manager = st.session_state.db_manager
        sector = config.SECTOR_MAPPING.get(ticker, 'Other')
        
        db_manager.add_company(ticker, company_name, sector)
        db_manager.save_audit(
            ticker, risk_analysis['sec_sentiment'], risk_analysis['news_sentiment'],
            risk_analysis['sentiment_delta'], risk_analysis['greenwashing_score'],
            risk_analysis['risk_level'], executive_summary
        )
        
        # Save news articles
        for article in news_data:
            article_sentiment = sentiment_analyzer.analyze_text(article['title'])
            article['sentiment'] = article_sentiment['score']
        
        db_manager.save_news_articles(ticker, news_data)
        
        progress_bar.progress(100)
        status_text.text("✅ Analysis complete!")
        
        # Display Results
        display_analysis_results(ticker, risk_analysis, executive_summary, news_data, sec_data)
        
    except Exception as e:
        st.error(f"Error during analysis: {e}")

def display_analysis_results(ticker, risk_analysis, summary, news_data, sec_data):
    """Display comprehensive analysis results"""
    st.success("### 📊 Analysis Results")
    
    # Risk Overview
    col1, col2, col3, col4 = st.columns(4)
    
    risk_level = risk_analysis['risk_level']
    
    with col1:
        st.metric("Greenwashing Risk", f"{risk_analysis['greenwashing_score']:.2f}", delta=risk_level)
    with col2:
        st.metric("SEC Sentiment", f"{risk_analysis['sec_sentiment']:.2f}")
    with col3:
        st.metric("News Sentiment", f"{risk_analysis['news_sentiment']:.2f}")
    with col4:
        st.metric("Sentiment Delta", f"{risk_analysis['sentiment_delta']:.2f}")
    
    # Executive Summary
    st.markdown(f"""
    <div class="metric-card">
        <h4>📝 Executive Summary</h4>
        <p>{summary}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Visualizations
    st.subheader("📊 Visual Analytics")
    tab1, tab2, tab3 = st.tabs(["Sentiment Gauge", "Comparison", "News Distribution"])
    
    viz = ESGVisualizations()
    
    with tab1:
        fig = viz.create_sentiment_gauge(risk_analysis['greenwashing_score'], risk_level)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        fig = viz.create_sentiment_comparison(risk_analysis['sec_sentiment'], risk_analysis['news_sentiment'])
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        sentiments = [st.session_state.sentiment_analyzer.analyze_text(article['title'])['score'] for article in news_data]
        fig = viz.create_sentiment_histogram(sentiments)
        st.plotly_chart(fig, use_container_width=True)
    
    # News Details
    with st.expander("📰 View News Articles"):
        for i, article in enumerate(news_data[:10], 1):
            st.markdown(f"**{i}. {article['title']}**")
            st.caption(f"Source: {article['source']} | {article['published_at']}")
            if article.get('url'):
                st.markdown(f"[Read more]({article['url']})")
            st.divider()

def sector_benchmark_page():
    st.header("📈 Sector Benchmark Analysis")
    
    db_manager = st.session_state.db_manager
    sector_stats = db_manager.get_sector_stats()
    
    if sector_stats.empty:
        st.info("No sector data available yet. Run some company analyses first!")
        return
    
    viz = ESGVisualizations()
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Risk by Sector")
        fig = viz.create_sector_benchmark(sector_stats)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Sector Statistics")
        st.dataframe(sector_stats, use_container_width=True)
    
    st.subheader("📍 Risk vs Performance Quadrant")
    latest_audits = db_manager.get_latest_audits(100)
    
    if not latest_audits.empty:
        latest_per_company = latest_audits.groupby('ticker').first().reset_index()
        fig = viz.create_risk_quadrant(latest_per_company)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Need more company data for quadrant analysis")

def rag_page():
    st.header("📚 Document Q&A - RAG System")
    st.markdown("*Chat with 10-K filings using Retrieval-Augmented Generation*")
    
    rag_engine = st.session_state.rag_engine
    
    # Show indexed companies
    indexed = rag_engine.list_indexed_companies()
    if indexed:
        st.success(f"📚 Currently Indexed: {', '.join(indexed)}")
    else:
        st.info("ℹ️ No documents indexed yet. Upload a PDF below to get started.")
    
    # File upload section
    st.subheader("📤 Upload Document")
    uploaded_file = st.file_uploader("Upload 10-K PDF Filing", type=['pdf'])
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        ticker = st.text_input("Company Ticker for RAG", "TSLA").upper()
    
    with col2:
        if uploaded_file:
            if st.button("📥 Index Document", type="primary", use_container_width=True):
                with st.spinner("📖 Processing document... This may take 1-2 minutes..."):
                    # Save temporarily
                    temp_path = f"data/temp_{ticker}.pdf"
                    with open(temp_path, 'wb') as f:
                        f.write(uploaded_file.getvalue())
                    
                    # Show progress
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # Extract text
                    status_text.text("📄 Extracting text from PDF...")
                    progress_bar.progress(30)
                    text = rag_engine.load_pdf(temp_path)
                    
                    if not text:
                        st.error("❌ Failed to extract text from PDF. Please check the file.")
                    else:
                        st.info(f"📊 Extracted {len(text)} characters from PDF")
                        
                        # Index
                        status_text.text("🧠 Creating embeddings and indexing...")
                        progress_bar.progress(60)
                        
                        success = rag_engine.index_document(
                            ticker, text,
                            {'filename': uploaded_file.name, 
                             'upload_date': pd.Timestamp.now().isoformat()}
                        )
                        
                        progress_bar.progress(100)
                        
                        if success:
                            st.success(f"✅ Successfully indexed {uploaded_file.name} for {ticker}!")
                            
                            # Show stats
                            stats = rag_engine.get_document_stats(ticker)
                            if stats:
                                st.info(f"📊 Created {stats['chunk_count']} searchable chunks")
                        else:
                            st.error("❌ Failed to index document. Please try again.")
    
    # Divider
    st.markdown("---")
    
    # Query interface
    st.subheader("💬 Ask Questions About the Document")
    
    # Example questions
    with st.expander("💡 Example Questions"):
        st.markdown("""
        - What are their 2030 carbon goals?
        - What renewable energy investments are mentioned?
        - What are the main environmental risks?
        - How much did emissions change?
        - What is their climate strategy?
        - What are the sustainability targets?
        """)
    
    question = st.text_input(
        "Enter your question about the 10-K filing",
        "What are their 2030 carbon goals?",
        help="Ask specific questions about ESG commitments, goals, or risks"
    )
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_button = st.button("🔍 Search Document", type="primary", use_container_width=True)
    
    with col2:
        num_results = st.selectbox("Results", [3, 5, 10], index=1)
    
    if search_button:
        if not question.strip():
            st.warning("⚠️ Please enter a question")
        else:
            with st.spinner(f"🔍 Searching {ticker} document..."):
                result = rag_engine.query_document(ticker, question, k=num_results)
                
                # Display answer
                st.markdown("### 💡 Answer")
                
                if "⚠️" in result['answer'] or "Error" in result['answer']:
                    st.warning(result['answer'])
                else:
                    st.success(result['answer'])
                
                # Display sources
                if result['sources']:
                    st.markdown("### 📄 Retrieved Sections")
                    st.caption(f"Found {len(result['sources'])} relevant sections")
                    
                    for i, source in enumerate(result['sources'], 1):
                        with st.expander(f"📌 Section {i} - Relevance: {source['relevance_score']:.3f}"):
                            st.text_area(
                                f"Content (Chunk {source['chunk_id']})",
                                source['content'],
                                height=200,
                                key=f"source_{i}"
                            )
                else:
                    st.info("ℹ️ No source sections were retrieved. The document may not contain information about this topic.")
    
    # Document management
    st.markdown("---")
    st.subheader("📊 Indexed Documents")
    
    if indexed:
        for ticker_name in indexed:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                stats = rag_engine.get_document_stats(ticker_name)
                if stats:
                    st.info(f"**{ticker_name}**: {stats['chunk_count']} chunks indexed")
                else:
                    st.info(f"**{ticker_name}**: Indexed")
            
            with col2:
                if st.button(f"Query {ticker_name}", key=f"query_{ticker_name}"):
                    st.session_state.current_ticker = ticker_name
    else:
        st.caption("No documents indexed yet. Upload a PDF above to get started.")
    
    # Help section
    with st.expander("❓ How to Use"):
        st.markdown("""
        ### How the RAG System Works
        
        1. **Upload a 10-K PDF**: Click "Browse files" and select a company's 10-K filing
        2. **Index the Document**: Click "Index Document" to process it (takes 1-2 minutes)
        3. **Ask Questions**: Type natural language questions about the document
        4. **Get Answers**: The AI searches the document and returns relevant information
        
        ### Tips for Best Results
        
        - **Be specific**: "What are the 2030 carbon reduction targets?" works better than "Tell me about carbon"
        - **Use numbers**: Questions about specific years, percentages, or amounts work well
        - **Check sources**: Always review the retrieved sections to verify the answer
        - **Try variations**: If you don't get good results, rephrase your question
        
        ### What Makes This Special
        
        This isn't just keyword search - it uses:
        - **Semantic Understanding**: Finds relevant content even if exact words don't match
        - **Vector Embeddings**: Converts text to mathematical representations
        - **ChromaDB**: Stores and searches millions of text chunks efficiently
        """)

# Add this function to your app.py (if not already there)
import pandas as pd

def audit_history_page():
    st.header("📋 Audit History & Trends")
    
    db_manager = st.session_state.db_manager
    ticker = st.text_input("Enter ticker to view history", "TSLA").upper()
    
    if st.button("📊 Load History"):
        history = db_manager.get_audit_history(ticker)
        
        if history.empty:
            st.info(f"No audit history found for {ticker}")
        else:
            viz = ESGVisualizations()
            fig = viz.create_time_series(history)
            st.plotly_chart(fig, use_container_width=True)
            
            st.subheader("📝 Audit Records")
            st.dataframe(history, use_container_width=True)
    
    st.subheader("🌐 Recent Audits (All Companies)")
    recent = db_manager.get_latest_audits(20)
    
    if not recent.empty:
        st.dataframe(recent[['ticker', 'company_name', 'sector', 
                             'greenwashing_score', 'risk_level', 
                             'audit_date']], use_container_width=True)

def about_page():
    st.header("ℹ️ About This Platform")
    
    st.markdown("""
    ## 🌍 ESG Intelligence & Risk Platform
    
    ### What This System Does
    
    This platform uses **AI and Machine Learning** to detect corporate greenwashing by analyzing
    the gap between what companies **claim** (SEC filings) and what the **media reports** (news coverage).
    
    ### 🔬 Technical Architecture
    
    #### 1. **Data Engineering**
    - **SEC Scraper**: Extracts ESG disclosures from official 10-K filings
    - **NewsAPI Integration**: Collects real-time news coverage
    - **SQLite Database**: Stores audit history and time-series data
    
    #### 2. **AI/ML Models**
    - **FinBERT** (Sentiment Analysis): Specialized BERT model for financial text
    - **BART** (Summarization): Generates human-readable executive summaries
    - **Sentence Transformers** (Embeddings): Powers the RAG system
    
    #### 3. **Advanced Analytics**
    - **Sentiment Delta Calculation**: Core greenwashing detection algorithm
    - **Sector Benchmarking**: Compare companies against industry peers
    - **Risk Quadrant Matrix**: Maps performance vs. risk
    - **Time-Series Tracking**: Monitor trends over time
    
    #### 4. **RAG (Retrieval-Augmented Generation)**
    - **ChromaDB**: Vector database for semantic search
    - **LangChain**: Orchestration framework
    - **Document Chunking**: Smart text segmentation
    - **Semantic Search**: Find relevant information in 200+ page documents
    
    ### 📊 How It Works
    
    1. **Data Collection**: Scrape SEC filings and news articles
    2. **Sentiment Analysis**: FinBERT analyzes tone of both sources
    3. **Delta Calculation**: Compare SEC positivity vs. news negativity
    4. **Risk Scoring**: Calculate greenwashing probability (0-1 scale)
    5. **Summarization**: BART generates 2-sentence explanation
    6. **Visualization**: Create interactive dashboards
    7. **Storage**: Save results for trend analysis
    
    ### 🎯 Use Cases
    
    - **Investors**: Identify ESG risks before investing
    - **Analysts**: Automate ESG due diligence
    - **Journalists**: Investigate greenwashing claims
    - **Regulators**: Monitor corporate disclosures
    
    ### 🚀 Tech Stack
    
    - **Languages**: Python, SQL
    - **AI/ML**: Transformers, PyTorch, Hugging Face
    - **RAG**: LangChain, ChromaDB, Sentence Transformers
    - **Data Science**: Pandas, NumPy, Plotly
    - **Database**: SQLite (relational), ChromaDB (vector)
    - **Web Framework**: Streamlit
    
    ---
    
    *This platform compresses what a team of junior analysts does over a week 
    into a single AI-powered dashboard that runs in seconds.*
    """)

if __name__ == "__main__":
    main()