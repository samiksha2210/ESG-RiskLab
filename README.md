🌍 ESG Intelligence & Risk Platform
AI-Powered Greenwashing Detection & ESG Risk Analysis
📌 Overview

The ESG Intelligence & Risk Platform is an AI-driven system designed to detect corporate greenwashing by identifying discrepancies between what companies claim in official disclosures and how they are perceived publicly through media coverage.

By combining financial NLP models, retrieval-augmented generation (RAG), and ESG analytics, the platform enables investors, analysts, and regulators to assess Environmental, Social, and Governance (ESG) risks with greater transparency and confidence.

🚀 Key Features
🔍 Company-Level ESG Analysis

Analyze individual companies in real time using:

SEC Scraper – Extracts ESG-related disclosures from official 10-K filings

NewsAPI Integration – Collects relevant news articles for public sentiment analysis

Sentiment Delta (Greenwashing Risk Score) – Quantifies the gap between corporate claims and media sentiment

Executive Summary – AI-generated insights summarizing ESG risks and inconsistencies

📈 Sector Benchmarking

Compare a company’s ESG risk against industry peers

Visualize risk vs. performance quadrants

Identify outliers with unusually high greenwashing risk

📚 Document Q&A (RAG)

Chat directly with 10-K filings

Uses Retrieval-Augmented Generation (RAG) to provide precise, document-grounded answers

Enables targeted queries about:

Environmental commitments

Social responsibility

Governance policies

📋 Audit History & Tracking

Persistent storage of:

ESG risk scores

Sentiment deltas

Historical audits

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

📦 Installation
1️⃣ Clone the Repository
git clone https://github.com/raghulpranxsh/ESG-Intelligence-and-Risk-Platform.git
cd ESG-Intelligence-and-Risk-Platform

2️⃣ Install Dependencies
pip install -r requirements.txt

3️⃣ Environment Setup

Create a .env file in the root directory (use .env.example as reference):

NEWS_API_KEY=your_newsapi_key
SEC_API_KEY=your_sec_api_key
LLAMA_CLOUD_API_KEY=your_llama_cloud_key   # Optional

▶️ Usage

Run the Streamlit application:

streamlit run app.py


Access the platform via your browser to begin ESG analysis.

📂 Project Structure
ESG-Intelligence-and-Risk-Platform/
│
├── app.py                 # Main Streamlit application
│
├── src/
│   ├── ai_models/          # Sentiment analysis, summarization, RAG
│   ├── data_collection/   # SEC & NewsAPI scrapers
│   ├── database/          # SQLite & ChromaDB utilities
│   ├── analytics/         # ESG metrics & visualizations
│
├── data/                  # PDFs, embeddings, local databases
├── requirements.txt
├── .env.example
└── README.md

🎯 Use Cases

Investors – Identify ESG risk and greenwashing exposure

Regulators – Monitor disclosure consistency and compliance

Analysts – Perform sector-level ESG benchmarking

Researchers – Study ESG sentiment and narrative divergence

