# Firm Intelligence API

A FastAPI service for querying a small in-memory dataset of law firms and their people, generating LLM-powered summaries and structured analyses of individual firms, and running semantic search over a corpus of firm-related documents.

## Stack

- **FastAPI** for the HTTP layer
- **Anthropic Claude** (`claude-haiku-4-5`) for firm summaries, structured analysis, and grounded Q&A
- **Voyage AI** (`voyage-3-lite`) for document embeddings used by the knowledge search

## Setup

```bash
cd firm-intelligence-api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install anthropic python-dotenv     # not yet pinned in requirements.txt
```

Create `.env.local` in the project root:

```
ANTHROPIC_API_KEY=sk-ant-...
VOYAGE_API_KEY=...
```

`.env.local` is git-ignored — never commit real keys.

## Run

```bash
source .venv/bin/activate
uvicorn main:app --reload --port 8000
```

Interactive docs: <http://localhost:8000/docs>

## Endpoints

### Health
- `GET /health`

### Firms (`routers/firms.py`)
- `GET /firms` — list all firms; optional `?jurisdiction=` and `?min_revenue=` filters
- `GET /firms/{id}` — fetch one firm (404 if missing)
- `GET /firms/{id}/benchmarks` — revenue per lawyer, profit per equity partner
- `POST /firms` — add a firm (supports `Idempotency-Key` header)
- `PUT /firms/{id}` — replace a firm
- `DELETE /firms/{id}` — remove a firm

### People (`routers/people.py`)
- `GET /people` — list all people; optional `?firm_id=` filter
- `GET /people/{id}` — fetch one person
- `POST /people` — add a person (validates that `firm_id` exists)

### Insights (`routers/insights.py`) — Claude-backed
- `POST /firms/{id}/summary` — two-paragraph natural-language summary
- `POST /firms/{id}/structured_analysis` — JSON: tier, strengths, risks, headcount efficiency
- `GET  /firms/{id}/summary/estimate` — input-token estimate before you spend
- `GET  /firms/{id}/summary/stream` — streamed summary (text/plain)
- `POST /firms/search` — semantic search shortcut over the document corpus

### Knowledge (`routers/knowledge.py`) — Voyage-backed RAG
- `POST /knowledge/index` — embed the corpus and populate the in-memory index (costs tokens; call deliberately)
- `POST /knowledge/search` — vector search: `{ "question": "...", "top_k": 3 }`
- `GET  /knowledge/ask` — retrieve + generate grounded answer (WIP)

## Notes

- **Index lifecycle**: `/knowledge/search` requires the index to exist. Call `POST /knowledge/index` once after startup, or restart the server after changing `documents.py`.
- **Data is in-memory**: firms, people, and the vector index all reset on restart.
- **Model versions** are pinned in `llm.py` (`MODEL`) and `knowledge.py` (`EMBED_MODEL`).


## Sample questions the system can be asked: 
- "Which firm has the strongest disputes position, and how does that compare with current UK lateral hiring trends?"
- "Identify firms with international ambitions, then explain whether the corpus contains evidence that those strategies are succeeding."
