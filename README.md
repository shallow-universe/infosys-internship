# 🕵️ Competitor Tracker + Ticket Resolution (RAG-Powered)

An **end-to-end competitor intelligence and ticket automation system** built with **FastAPI, SQLite, Google Sheets, and RAG (Retrieval-Augmented Generation)**.  

This project enables:  
- 📊 **Competitor tracking** (scraping, price/promo forecasting, sentiment analysis).  
- 🔔 **Smart alerts** (Slack integration).  
- 📑 **Google Sheets synchronization** (reporting + ticket logs).  
- 🧠 **RAG-powered Q&A** (contextual answers from product docs).  
- 🎫 **Ticket resolution workflow** (categorization → solution → update status).  

---

## 🚀 Features  

- **Scraping & ETL**  
  - Modular scrapers for competitor sites.  
  - Aggregator → normalize + store into SQLite.  

- **Analytics**  
  - Price/promo forecasting (basic predictor).  
  - Review sentiment analysis.  
  - Alerts (Slack notifications).  

- **Integrations**  
  - Google Sheets + BigQuery sync for reporting and ticket logs.  
  - RAG (Retrieval-Augmented Generation) pipeline for contextual Q&A.  

- **Ticket System**  
  - Auto-categorize tickets using LLM.  
  - Retrieve solutions from product documentation (RAG).  
  - Update ticket status back into Google Sheets.  

---

## 🗂 Project Structure  

competitor-tracker/
├─ .env # Secrets (SLACK_WEBHOOK_URL, GOOGLE_API_KEY, etc.)
├─ README.md # This file
├─ requirements.txt # Python dependencies
├─ main.py # FastAPI app + scheduler
├─ db.py # SQLite + SQLAlchemy models
├─ schemas.py # Pydantic schemas
├─ services/ # Core services
│ ├─ aggregator.py # ETL pipeline
│ ├─ predictor.py # Forecasting
│ ├─ sentiment.py # NLP sentiment analyzer
│ ├─ alerts.py # Slack alerts
│ └─ utils.py # Helpers
├─ scrapers/ # Site scrapers
│ ├─ base.py # Base class
│ ├─ example_shop.py # Example scraper
│ └─ adapters.py # Register sites
├─ data/
│ ├─ tracker.db # SQLite DB
│ └─ samples/ # Sample inputs
│ └─ seed_products.csv
├─ notebooks/
│ └─ EDA.ipynb # Jupyter exploration
└─ rag_pipeline/
├─ rag_faiss_gemini.py # RAG index + query pipeline
└─ loaders.py # File/pdf loaders



---

## ⚙️ Installation  

### 1. Setup Virtual Environment  

python -m venv myenv

source myenv/bin/activate


### 2. Install Dependencies  

pip install -r requirements.txt


`requirements.txt` includes:  

fastapi uvicorn sqlalchemy pydantic requests beautifulsoup4
gspread oauth2client pandas pandas-gbq
langchain langchain-community langchain-google-genai
faiss-cpu pypdf python-dotenv


---

## 🔑 Google Sheets Integration  

1. Enable **Google Sheets API** and **Google Drive API** on [Google Cloud Console](https://console.cloud.google.com).  
2. Create **Service Account** + download credentials → `credentials.json`.  
3. Share your target Google Sheet with the service account email.  
4. Example usage:  


import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

sheet = client.open("MyDatabaseSheet").sheet1
df = pd.DataFrame(sheet.get_all_records())
print(df.head())


---

## 🧠 RAG Pipeline  

Why RAG?  
- LLMs have **knowledge cutoffs** and may **hallucinate**.  
- RAG fetches **up-to-date, domain-specific data** and augments prompts before response generation.  

**Architecture**:  

Query → Retriever (FAISS/BM25) → Augment Prompt → LLM → Final Answer


Supported: PDFs, text, markdown, product docs.  

Run pipeline:  
python rag_pipeline/rag_faiss_gemini.py --docs ./my_docs --index-path ./faiss_index --rebuild

---

## 🎫 Ticket Workflow  

1. New ticket logged in Google Sheets:  

{
"ticket_id": "34vervewe3t",
"ticket_content": "I have issue with my phone",
"ticket_category": "",
"ticket_timestamp": "2025-08-22 00:00:00 IST",
"ticket_by": "email",
"ticket_status": "open"
}


2. LLM categorizes (e.g., `product_maintenance`).  
3. RAG retrieves **relevant docs** and suggests a solution.  
4. Solution + status updated back in Google Sheets.  

---

## 📡 Run the FastAPI Service  

uvicorn main:app --reload


- API Docs → [http://localhost:8000/docs](http://localhost:8000/docs)  
- Endpoints cover competitor data ingestion, ticket resolution, and RAG Q&A.  

---

## 📈 Roadmap  

- [x] Core scaffolding (FastAPI, DB, services).  
- [x] Google Sheets integration.  
- [ ] Add forecasting models for promotions.  
- [ ] Add multi-site competitor scrapers.  
- [ ] Deploy RAG pipeline with Gemini embeddings.  
- [ ] Ticket automation loop (categorize → resolve → update).  
- [ ] Dockerize + deploy on Google Cloud Run / Kubernetes.  

---

## 🤝 Contributing  

1. Fork the repo.  
2. Create a feature branch (`git checkout -b feature-x`).  
3. Commit changes.  
4. Submit PR.  

---

## 📜 License  

MIT License – feel free to use and adapt.  
