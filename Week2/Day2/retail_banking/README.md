# Retail Banking — Complaints & Conduct Copilot

A retail-banking intelligence platform that helps complaint handlers triage cases, ground decisions in policy and past ombudsman precedent, and stay inside conduct-risk guardrails. 

**Built on FastAPI + Claude + Chroma/Voyage (backend) and Streamlit (frontend).**

See `PROJECT.md` for the full design.

## Run locally

You'll need two terminals — one for the backend, one for the frontend.

## Requirements:
Having python3.12 installed

### Terminal 1 — backend

```bash
cd retail_banking_backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Backend runs at `http://localhost:8000`.

### Terminal 2 — frontend

```bash
cd retail_banking_frontend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Frontend runs at `http://localhost:8501` and talks to the backend on port 8000.

## Environment variables

Set these in `retail_banking_backend/.env` before starting the backend:

```
ANTHROPIC_API_KEY=...
VOYAGE_API_KEY=...
```
