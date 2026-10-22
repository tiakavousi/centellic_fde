# Retail Banking — Backend

FastAPI service powering the Complaints & Conduct Copilot. Serves structured
records (complaints, customers, products), Claude-generated summaries and
analysis, Azure AI Search-backed hybrid retrieval, and a tool-using agent.

**Two search backends — different purposes:**
- **Chroma** — local, offline, used only by the eval pipeline (`chunk_index.py`, `eval_retrieval.py`) to compare chunking strategies cheaply before committing to Azure.
- **Azure AI Search** — live API backend; hybrid BM25 + vector + semantic reranker. Receives the winning strategy's chunks after eval.

## Requirements

- Python 3.12
- An Anthropic API key, a Voyage AI API key, and an Azure AI Search resource

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
| `ANTHROPIC_MODEL` | Claude model id | yes | `claude-sonnet-4-6` |
| `MAX_TOKENS` | Max output tokens per LLM call | yes | `1024` |
| `MAX_RETRIES` | SDK retry count | yes | `2` |
| `MODEL_TIMEOUT` | SDK timeout in seconds | yes | `30` |
| `VOYAGEAI_API_KEY` | Voyage AI embeddings key | yes | `pa-...` |
| `VOYAGE_MODEL` | Voyage embedding model | yes | `voyage-3` |
| `AZURE_SEARCH_ENDPOINT` | Azure AI Search service URL | yes | `https://<name>.search.windows.net` |
| `AZURE_SEARCH_INDEX` | Index name | yes | `retail-banking-chunks` |
| `AZURE_SEMANTIC_CONFIG` | Semantic configuration name | yes | `retail-banking-semantic` |
| `RELEVANCE_FLOOR` | Minimum reranker score for grounded answers | yes | `1.5` |
| `TOP_K` | Number of chunks to retrieve | yes | `3` |
| `CHROMA_PATH` | Chroma persist directory (eval pipeline only) | eval only | `./chroma_store` |
| `ACK_WINDOW_DAYS` | SLA acknowledgement window in days | yes | `3` |
| `RESPONSE_WINDOW_DAYS` | SLA final response window in days | yes | `56` |

`.env` is gitignored. Share `.env.example` with new contributors.

## Run

```bash
uvicorn main:app --reload --port 8000
```

- API base: `http://localhost:8000`
- Interactive docs: `http://localhost:8000/docs`

## Build the search index

Run once after setup, and again whenever the document corpus changes:

```bash
python -m azure_build
```

This chunks all documents using the `sections_contextual` strategy, embeds them
with Voyage AI, and uploads them to Azure AI Search. The index is dropped and
rebuilt from scratch on each run.

## Tests

```bash
pytest                        # unit tests only
pytest -m integration         # also runs tests that call real APIs
```

## Layout

```
data/           synthetic seed data (customers, complaints, products, documents, corpus)
schemas/        Pydantic schemas for LLM structured output
prompts/        system prompt and user-prompt builders
routers/        FastAPI endpoints
main.py         app entrypoint
llm.py          Claude client
embedding.py    Voyage AI embedding client
chunking.py     chunking strategies (whole_document, fixed_words, sentence_packed, by_section)
chunk_index.py  Chroma-backed per-strategy indexes for offline eval
eval_set.py     labelled questions for retrieval and answer quality eval
eval_tools.py   pure scoring helpers (contains_evidence, keywords_present)
grounding.py    citation checker and refusal detection
eval_retrieval.py  score all strategies: Recall@k, MRR
azure_index.py  Azure AI Search index schema definition
azure_store.py  Azure AI Search client (build index, search)
azure_build.py  CLI entry point to build the search index
agent.py        tool-using agent loop
agent_tools.py  agent tool implementations
```
