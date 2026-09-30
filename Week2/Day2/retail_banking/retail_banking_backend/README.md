# Retail Banking — Backend

FastAPI service powering the Complaints & Conduct Copilot. Serves structured
records (complaints, customers, products), Claude-generated summaries and
analysis, Chroma/Voyage-backed retrieval, and a tool-using agent.

## Requirements

- Python 3.12
- An Anthropic API key and a Voyage API key

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Environment variables

Create a `.env` file in this folder:

```
ANTHROPIC_API_KEY=...
VOYAGE_API_KEY=...
```

## Run

```bash
uvicorn main:app --reload --port 8000
```

- API base: `http://localhost:8000`
- Interactive docs: `http://localhost:8000/docs`

## Tests

```bash
pytest
```

## Layout

```
data/           synthetic seed data (customers, complaints, products, documents)
routers/        FastAPI endpoints
main.py         app entrypoint
llm.py          Claude client
knowledge.py    Chroma + Voyage retrieval
agent.py        tool-using agent loop
```
