# Firm Intelligence UI

A Streamlit front-end for the Firm Intelligence API. Provides tabs to ask
questions, run semantic search, and stream firm summaries.

## Setup

```bash
cd firm-intelligence-ui
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

Make sure the API is running first (see `../firm-intelligence-api/README.md`).

```bash
source .venv/bin/activate
streamlit run app.py
```

Then open the URL Streamlit prints (default: <http://localhost:8501>).

## Configuration

By default the UI talks to `http://127.0.0.1:8000`. Override with:

```bash
API_BASE=http://127.0.0.1:8000 streamlit run app.py
```
