# Complaints & Conduct Copilot
(This document is subject to change)

## Description

A retail-banking intelligence platform for complaint handlers and conduct-risk
teams. Banks receive thousands of customer complaints; regulators expect root
causes to be identified, vulnerable customers to be handled properly, and
redress outcomes to be consistent. This system helps handlers triage each
complaint, ground decisions in policy and past ombudsman precedent, and stay
inside the conduct-risk guardrails the bank sets.

Built on FastAPI + Claude + Chroma/Voyage + Streamlit, following the same
shape as the Firm Intelligence reference project but with a data model,
analysis schema, extra agent tool, refusal rule and UI feature specific to
retail banking.

## What the AI agent does

- **Classifies** each complaint into a typed schema: theme, severity,
  vulnerability concern, Consumer Duty risk, recommended next step, redress
  category, rationale, confidence.
- **Answers** free-text questions grounded in policy, regulator guidance and
  past ombudsman decisions — with citations, and refuses when no source
  clears the relevance floor or when the question asks for a specific
  redress amount.
- **Tools available to the agent:**
  1. `search_knowledge` — vector search over the document corpus.
  2. `find_similar_complaints` — surfaces historic complaints with matching
     theme/product to drive consistent outcomes.
- **Never** closes a complaint, sets a £ redress amount, or issues a binding
  remedy — it only recommends. Human sign-off is required.

## Data model (brief)

Two structured entities with a one-to-many relationship:
**one customer → many complaints.**

**`Customer`**
- `id`, `name`, `segment` (mass_market | premier | business),
  `vulnerability_flag` (bool), `tenure_years`

**`Complaint`**
- `id`, `customer_id` (FK → Customer), `product` (mortgage | credit_card |
  current_account | personal_loan | savings), `channel` (phone | branch |
  app | email | webform), `severity` (low | medium | high),
  `status` (open | in_review | resolved | escalated), `opened_date` (ISO),
  `summary` (short prose)

Query filters: complaints by `product` / `status` / `vulnerable_only`;
customers by `segment` / `vulnerability_flag`.

`opened_date` drives SLA aging; `vulnerability_flag` gates the refusal rule.

## Query flow (agent path)

1. **Request in** — `POST /agent/ask` with a question; FastAPI validates
   and loads config (model, iteration limit, relevance floor) from env.
2. **Agent loop starts** — Claude receives the question, the system prompt
   (refusal rules, tool contract) and the tool schemas for
   `search_knowledge` and `find_similar_complaints`.
3. **Tool: search_knowledge** — Voyage embeds the query, Chroma returns
   top-k docs, results below the relevance floor are dropped. Empty result
   → Claude must refuse.
4. **Tool: find_similar_complaints** — filters the complaints store by
   product / theme, joins customer for vulnerability, returns matching
   records.
5. **Iterate** — Claude may call tools multiple times. Loop exits on final
   answer or when `MAX_ITERATIONS` is reached (returns `completed: false`).
6. **Guardrails checked** — no £ redress amounts, no autonomous closure,
   refuse when no source clears the floor or when a vulnerable-customer
   question lacks the relevant policy doc.
7. **Response out** — `{ answer, citations, tool_calls, tokens,
   iterations, completed }`.
