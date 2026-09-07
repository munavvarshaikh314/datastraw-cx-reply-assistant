# Datastraw CX Reply Assistant

**Live app:** [https://datastraw-cx-reply-assistant.vercel.app/dashboard/conversations](https://datastraw-cx-reply-assistant.vercel.app/dashboard/conversations)


An AI-assisted reply tool for customer support agents. An agent opens a conversation, sees the customer's message alongside their order and brand context, and generates a draft reply grounded in that brand's policy knowledge base. The agent edits, regenerates, or approves — nothing goes to a customer without a human deciding it should.

## How it works

```
Customer Message
       │
       ▼
┌──────────────────────┐
│ FastAPI Reply API    │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────────────┐
│ Deterministic Eligibility    │
│ Check                        │
│                               │
│ delivery_date + brand's      │
│ configured refund window     │
└──────────────┬────────────────┘
               │
        ┌──────┴───────┐
        │              │
   Ineligible/       Eligible /
   Ambiguous         Normal case
        │              │
        ▼              ▼
 Safe response   ┌─────────────────┐
 (LLM not        │ Retrieve Brand  │
  called)         │ Knowledge       │
                 │                 │
                 │ Qdrant +        │
                 │ brand_id filter │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │ OpenRouter LLM  │
                 │                 │
                 │ Context +       │
                 │ conversation +  │
                 │ policy decision │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │ AI Guardrails   │
                 │ + Output        │
                 │ Validation      │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │ AI Reply        │
                 │                 │
                 │ Edit → Approve  │
                 └────────┬────────┘
                          │
                          ▼
                    PostgreSQL
                    AI reply/log
```

Two distinct guardrail layers, not one: the **eligibility check** above runs before the LLM and can bypass it entirely; **output validation** runs after generation regardless of which path was taken, as a second, independent check on the actual text before it reaches the agent.

## The eligibility guardrail

The brief's own example is the reason this exists: a customer who received an order 20 days ago asking for a refund, against a policy with a 7-day change-of-mind window and a 30-day defective-item window. An LLM asked to reason about that from a system prompt alone can — and in early testing here, did — get the date math wrong or answer with more confidence than the data supports.

So eligibility isn't left to the model. `app/services/eligibility.py` computes it in code from the order's real delivery date and the brand's actual policy window, before the LLM is ever called:

- **Eligible** → normal grounded generation proceeds, with the verdict attached to context so the reply stays consistent with it.
- **Not eligible** → the LLM is bypassed entirely; a fixed policy-accurate response is returned.
- **Ambiguous** (e.g. outside the change-of-mind window but inside the defective-item window, with no defect status on record) → the LLM is bypassed with a response asking the customer for the missing detail, rather than guessing either way.

The verdict is persisted alongside the retrieved context on every generation, so the audit trail shows not just what the agent saw, but why.

## Reply lifecycle

Every generation — including regenerations — is its own row, numbered per conversation (`generation_number`), never an overwrite of a prior one:

```
generated → edited (optional) → approved
```

Regenerate calls the same generation pipeline as the initial "Generate Reply" — same retrieval, same guardrail, same persistence — producing a new row rather than mutating the last one.

## Architecture

```
                         ┌──────────────────────────┐
                         │        Agent/User        │
                         │      Web Browser         │
                         └────────────┬─────────────┘
                                      │
                                      ▼
                  ┌──────────────────────────────────┐
                  │       Next.js Frontend            │
                  │                                   │
                  │  • Conversation Dashboard         │
                  │  • Conversation History           │
                  │  • AI Reply Generation             │
                  │  • Edit / Regenerate / Approve     │
                  └──────────────┬───────────────────┘
                                 │ REST API
                                 ▼
                  ┌──────────────────────────────────┐
                  │          FastAPI Backend          │
                  │                                   │
                  │  Conversation API                 │
                  │  Reply API                        │
                  │  Status Management                 │
                  │  AI Orchestration                  │
                  └──────────────┬───────────────────┘
                                 │
                 ┌───────────────┼────────────────┐
                 │               │                │
                 ▼               ▼                ▼
       ┌────────────────┐ ┌───────────────┐ ┌─────────────────┐
       │   PostgreSQL   │ │    Qdrant     │ │   OpenRouter    │
       │    Supabase    │ │ Vector Store  │ │      LLM        │
       │                │ │               │ │                 │
       │ • Brands       │ │ • Brand KB    │ │ • Generate      │
       │ • Customers    │ │ • Embeddings  │ │   reply         │
       │ • Conversations│ │ • Documents   │ │                 │
       │ • Messages     │ │ • Policies    │ │                 │
       │ • Orders       │ │               │ │                 │
       │ • AI Replies   │ │               │ │                 │
       └────────────────┘ └───────────────┘ └─────────────────┘
                                 ▲
                                 │
                         ┌───────┴────────┐
                         │  Embedding     │
                         │    Service     │
                         │ Sentence-      │
                         │ Transformers   │
                         └────────────────┘
```

## Tech stack

- **Frontend:** Next.js, React, TypeScript, Tailwind CSS
- **Backend:** Python, FastAPI, SQLAlchemy 2.0 (async), Pydantic, Alembic
- **Database:** PostgreSQL (Supabase-hosted)
- **AI / RAG:** Qdrant, Sentence Transformers embeddings, OpenRouter

## Setup

**Backend**
```bash
cd backend
python -m venv .venv && .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
# copy .env.example to .env and fill in real values
python -m alembic upgrade head
uvicorn app.main:app --reload
```
Runs at `http://127.0.0.1:8000`, docs at `/docs`.

**Frontend**
```bash
cd frontend
npm install
npm run dev
```
Runs at `http://localhost:3000/dashboard/conversations`.

**Environment variables** — see `.env.example`. Never commit real secrets; `.env`, `.env.local`, `node_modules/`, `.next/`, `.venv/` are gitignored.

## Key API endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/conversations` | List conversations, optional `?status=` filter |
| GET | `/api/conversations/{id}` | Full context: customer, brand, order, messages |
| POST | `/api/conversations/{id}/reply` | Generate (or regenerate) a reply |
| PATCH | `/api/conversations/replies/{id}` | Save an edit |
| POST | `/api/conversations/replies/{id}/approve` | Approve the final response |
| PATCH | `/api/conversations/{id}/status` | Update conversation status |

## Design decisions

- **Agent-in-the-loop, always.** No generated reply is ever sent automatically; approval is a manual, logged action.
- **Eligibility is deterministic, not prompted.** See above — this is the single most important decision in the project, and the one place correctness can't depend on the model's judgment.
- **Every generation is retained, not just the final one.** `generated → edited → approved`, with `generation_number` per conversation, so the full history — including abandoned regenerations — is queryable.
- **No authentication in this build**, by design: single implicit agent context, appropriate for this scope. Brand-scoped JWT auth is the documented next step (see system design doc) rather than something skipped silently.

## Current scope

Built and tested: conversation workspace, brand/order/customer context loading, Qdrant-based policy retrieval, the deterministic eligibility guardrail, LLM-based reply generation, edit, regenerate, approve, and full audit persistence (customer message, retrieved context + verdict, AI response, edited response, final response, timestamps).

Not built, and deliberately out of scope for this exercise: authentication, multi-tenant row-level security, observability/monitoring, and production deployment hardening. These are addressed as forward-looking design decisions in the accompanying system design document, not implemented here.

## AI usage disclosure

AI tools were used throughout this build. In the interest of being specific rather than just checking a box:

- **Claude** was used for architecture discussion, code scaffolding (schema, edge/API functions, the eligibility module), and reviewing generated code before merging it.
- **[Add any other tools you actually used — Copilot, ChatGPT, etc. — with a one-line example of how, or remove this bullet if it was Claude only.]**

**A concrete instance of AI-generated code being wrong, caught during review:** an early version of the reply-generation service called a guardrail-validation function on the AI's output, but never fetched or passed the customer's order into that code path. The function *looked* like it was checking refund eligibility — it had the right name, the right shape, and the code compiled and ran fine — but with no order in scope, it was structurally incapable of doing the date-based eligibility math the brief's example requires. It would have shipped as a guardrail that didn't guard anything. Caught by tracing the actual data flow into the function, not by testing it against a failing case.

**A second instance:** the initial refund-detection logic only matched explicit keywords like "refund" and "money back." Tested against the brief's own example message — "the bottle is broken. What can I do?" — it wouldn't have triggered the eligibility check at all, since that message contains none of those words. Fixed by broadening detection to damage/complaint language, and by manually testing the exact example message from the brief before considering the guardrail done.

## Repository

[https://github.com/munavvarshaikh314/datastraw-cx-reply-assistant]

**Author:** Munavvar Shaikh
