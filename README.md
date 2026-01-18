🌍 ESG Intelligence & Risk Platform
AI-Powered Greenwashing Detection & ESG Risk Analysis
📌 Overview

The ESG Intelligence & Risk Platform is an AI-driven system designed to detect corporate greenwashing by identifying discrepancies between what companies claim in official disclosures and how they are perceived publicly through media coverage.

By combining financial NLP models, retrieval-augmented generation (RAG), and ESG analytics, the platform enables investors, analysts, and regulators to assess Environmental, Social, and Governance (ESG) risks with greater transparency and confidence.

🚀 Key Features
🔍 Company-Level ESG Analysis

1.Analyze individual companies in real time using:
2.SEC Scraper – Extracts ESG-related disclosures from official 10-K filings
3.NewsAPI Integration – Collects relevant news articles for public sentiment analysis
4.Sentiment Delta (Greenwashing Risk Score) – Quantifies the gap between corporate claims and media sentiment
5.Executive Summary – AI-generated insights summarizing ESG risks and inconsistencies

📈 Sector Benchmarking

1.Compare a company’s ESG risk against industry peers
2.Visualize risk vs. performance quadrants
3.Identify outliers with unusually high greenwashing risk

📚 Document Q&A (RAG)

1.Chat directly with 10-K filings
2.Uses Retrieval-Augmented Generation (RAG) to provide precise, document-grounded answers
3.Enables targeted queries about:
4.Environmental commitments
5.Social responsibility
6.Governance policies

📋 Audit History & Tracking

Persistent storage of:

1.ESG risk scores
2.Sentiment deltas
3.Historical audits

Enables trend analysis and compliance tracking over time

🛠️ Technology Stack
🖥️ Frontend

Streamlit – Interactive dashboards and visual analytics

⚙️ Core Logic

Python
Pandas, NumPy

🤖 AI & Machine Learning Models

FinBERT – Financial sentiment analysis
BART – Abstractive text summarization
Sentence Transformers – Semantic embeddings for RAG workflows

🗄️ Databases

SQLite – Structured data (audits, historical records)
ChromaDB – Vector database for semantic search and document retrieval

🌐 External APIs

SEC-API – Access to official regulatory filings
NewsAPI – Media sentiment and coverage
LLaMA Cloud API (optional) – Enhanced LLM capabilities


🎯 Use Cases

Investors – Identify ESG risk and greenwashing exposure
Regulators – Monitor disclosure consistency and compliance
Analysts – Perform sector-level ESG benchmarking
Researchers – Study ESG sentiment and narrative divergence



