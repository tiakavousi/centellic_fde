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
cp .env.example .env   # then fill in your keys
```

## Environment variables

| Variable | Purpose | Required | Example |
|---|---|---|---|
| `ANTHROPIC_API_KEY` | Claude API key | yes | `sk-ant-...` |
| `ANTHROPIC_MODEL_NAME` | Claude model id | yes | `claude-sonnet-4-6` |
| `MAX_TOKENS` | Max output tokens per LLM call | yes | `1024` |
| `MAX_RETRIES` | SDK retry count | yes | `2` |
| `MODEL_TIMEOUT` | SDK timeout in seconds | yes | `30` |
| `VOYAGE_API_KEY` | Voyage embeddings API key | yes | `pa-...` |
| `VOYAGE_MODEL` | Voyage embedding model | yes | `voyage-3` |
| `CHROMA_PATH` | Persistent Chroma directory | yes | `./chroma_store` |
| `CHROMA_COLLECTION` | Chroma collection name | yes | `retail_banking_docs` |
| `RELEVANCE_FLOOR` | Minimum score for grounded answers | yes | `0.6` |
| `TOP_K` | Number of docs to retrieve for grounded answers | yes | `3` |

`.env` is gitignored. Share `.env.example` with new contributors.

## Run

```bash
uvicorn main:app --reload --port 8000
```

- API base: `http://localhost:8000`
- Interactive docs: `http://localhost:8000/docs`

On first boot, index the document corpus:

```bash
curl -X POST http://localhost:8000/knowledge/index
```

## Tests

```bash
pytest
```

## Layout

```
data/           synthetic seed data (customers, complaints, products, documents)
schemas/        Pydantic schemas for LLM structured output
prompts/        system prompt and user-prompt builders
routers/        FastAPI endpoints
main.py         app entrypoint
llm.py          Claude client
knowledge.py    Chroma + Voyage retrieval
agent.py        tool-using agent loop
```
