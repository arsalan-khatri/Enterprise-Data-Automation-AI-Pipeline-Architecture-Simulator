# Enterprise Data Automation & AI Triage Pipeline

An end-to-end automated data engineering and machine learning pipeline designed to eliminate manual data entry bottlenecks, parse unstructured text streams using Large Language Models (LLMs), and dynamically prioritize incoming enterprise support queries with real-time SQL database lookups and Power BI analytics.

---

## 🚀 Project Overview

Modern businesses and customer support centers are flooded with thousands of unstructured text queries daily. Manual triaging causes operational delays, data siloing, and missed high-priority client issues.

This project simulates a **production-grade enterprise helpdesk backend** that automates the entire flow — from raw data ingestion and synthetic data balancing to AI-driven sentiment analysis, database enrichment, and predictive priority classification.

---

## 🛠️ Project Structure & Architecture

```text
D:.
│   shop.html               # E-commerce frontend storefront for placing orders
│   support.html            # Helpdesk ticket submission interface
│
├───data
│   ├───final_data
│   │       customer_tickets_balanced.csv  # Balanced dataset used for model training
│   │
│   ├───processed
│   │       check_data.py                  # Data auditing & validation script
│   │       create-dataset.py              # Synthetic dataset generator
│   │       data_labling.py                # Rule-based sentiment and priority tagger
│   │       final_dataset.py               # Data balancing script
│   │
│   └───raw
│           customer_tickets.csv           # Initial raw customer ticket logs
│           customer_tickets_labeled.csv   # Intermediate labeled dataset
│
├───FastAPIs
│       main.py             # Core FastAPI backend (Database setup, REST endpoints, logic)
│
├───llm
│       schema_llm_pipeline.py  # Gemini LLM integration & Smart Fallback parser
│
└───ml
    │   machine_learning.py     # Random Forest model training & evaluation script
    │   selftesting.py          # Script for running live manual predictions
    │   verify_model.py         # Cross-validation and rigorous model testing script
    │
    └───saved_models
            label_encoders.pkl  # Saved categorical feature encoders
            priority_model.pkl  # Trained Random Forest classifier
```

---

## 🔴 The Business Problem

- **Operational Bottlenecks:** Manually reading and categorizing thousands of support tickets wastes hundreds of staff hours.
- **Delayed VIP Response:** High-value clients or urgent financial failures often get buried behind low-priority tickets.
- **Disconnected Data:** Unstructured text messages lack relational context (e.g., customer tier status, lifetime order value, and past complaints).

---

## 🟢 The Solution & Architecture Flow

1. **Automated Data Ingestion:** Customers place orders or submit support tickets through clean web interfaces (`shop.html` & `support.html`), which directly write into a relational SQL Server database.
2. **Dynamic DB Lookups:** When a ticket is received, the FastAPI backend queries the database in real-time to pull the customer's lifetime order value, tier status (Regular, Premium, VIP), and previous complaint history.
3. **AI-Powered Parsing:** Incoming messages are sent to an LLM pipeline (`schema_llm_pipeline.py`) powered by Google Gemini to extract intent, category, and sentiment.
4. **Predictive Classification:** A trained Scikit-Learn Random Forest model (`priority_model.pkl`) evaluates the dynamic database metrics alongside the LLM sentiment to assign a precise priority level (Critical, High, Medium, Low).
5. **Business Visualization:** Processed data is structured and piped into Power BI dashboards to provide stakeholders with live visibility into system bottlenecks, departmental loads, and customer trends.

---

## 🌟 Key Features & Business Impact

- **Zero Manual Triaging:** Fully automated ingestion and tagging of raw customer interactions into structured SQL records.
- **Smart Prioritization Matrix:** Instantly flags high-risk or VIP client complaints as *"Critical,"* ensuring immediate intervention.
- **Robust API Security & Validation:** Built-in duplicate ticket detection (spam prevention) and strict customer ID authorization gates.
- **Actionable Analytics Ready:** Clean, analysis-ready datasets and schemas optimized for Power BI reporting and data warehousing.

---

## ⚠️ Core Challenges Overcome

- **API Rate Limits & Failures:** Enterprise systems cannot fail when external AI APIs time out. Engineered a "Smart Fallback Analyzer" that instantly falls back to a rule-based NLP parser if the primary LLM API encounters quotas or network drops.
- **Real-World Data Imbalance:** Real support logs are heavily skewed towards low-priority or neutral queries. Wrote a custom synthetic data generator (`final_dataset.py`) to balance the dataset across all priority classes, preventing model bias during training.
- **Bridging Unstructured & Structured Data:** Seamlessly unified raw natural language strings with relational SQL metrics (order values and historical complaints) into a single predictive feature array.

---

## ⚙️ Tech Stack

| Category | Technologies |
|---|---|
| **Backend** | Python, FastAPI, Uvicorn, Pydantic, SQLAlchemy, PyODBC |
| **Database** | Microsoft SQL Server (MSSQL) |
| **Machine Learning & AI** | Scikit-Learn, Pandas, NumPy, Google Gemini API, Joblib |
| **Frontend** | HTML5, CSS3, JavaScript (Fetch API) |
| **Analytics** | Power BI, Advanced Excel Data Modeling |

---

## 🔧 Getting Started & Running Locally

**1. Clone the repository:**
```bash
git clone https://github.com/arsalan-khatri/Enterprise-Data-Automation-AI-Pipeline-Architecture-Simulator
cd enterprise-ai-data-pipeline
```

**2. Install dependencies:**
```bash
pip install fastapi uvicorn pandas scikit-learn sqlalchemy pyodbc joblib google-genai
```

**3. Run the FastAPI server:**
```bash
cd FastAPIs
uvicorn main:app --reload
```

**4. Access the application:**
- Open `shop.html` in your browser to simulate store checkouts.
- Open `support.html` to test the automated AI support helpdesk and priority prediction.
