# DataStraw — AI-Powered CX Reply Assistant

An AI-assisted customer support workspace that helps CX agents generate accurate, context-aware replies using customer conversations, order information, and brand-specific policies.

The system combines a FastAPI backend, Next.js frontend, PostgreSQL, vector search, and an LLM-powered RAG pipeline to turn a customer issue into an agent-ready response.

---

## Overview

Customer support agents often need to manually search through brand policies before responding to customers.

DataStraw streamlines this workflow:

```text
Customer Conversation
        ↓
Conversation Context
        ↓
Customer + Brand + Order + Messages
        ↓
Retrieve Relevant Brand Policies
        ↓
RAG Context
        ↓
LLM
        ↓
AI-Generated Reply
        ↓
Agent Reviews / Edits
        ↓
Approve Reply


Example

Customer:

My order arrived damaged. What can you do?

The system identifies the customer's latest message, retrieves the relevant Damaged Order Policy from the brand knowledge base, and generates a response based on that policy.

The agent can then:

Review the generated response
Edit it
Save the edited version
Approve the final response


Key Features
Conversation Workspace
View customer conversations
Conversation status management
Load complete conversation context
View customer information
View order information
View conversation messages
AI Reply Generation
Identify the latest customer message
Retrieve relevant brand knowledge
Generate a context-aware response using an LLM
Persist every reply generation
RAG-Based Knowledge Retrieval

Brand policies are retrieved based on semantic relevance.

The retrieved context can include policies such as:

Returns
Refunds
Shipping
Cancellation
Damaged orders
Agent Review Workflow

Generated responses are not automatically sent to customers.

The agent remains in control:

Generated
    ↓
Edit
    ↓
Save
    ↓
Approve
Reply Persistence

Each generation stores:

Customer message
Retrieved context
AI response
Edited response
Final response
Generation number
Model
Latency
Status
Approval timestamp
Architecture
┌──────────────────────────────────────────┐
│              Next.js Frontend            │
│                                          │
│  Conversation Workspace                  │
│  Customer Information                    │
│  Order Information                       │
│  AI Reply Editor                         │
└────────────────────┬─────────────────────┘
                     │ REST API
                     ▼
┌──────────────────────────────────────────┐
│              FastAPI Backend             │
│                                          │
│  Conversation APIs                       │
│  Reply Generation APIs                   │
│  Reply Editing                           │
│  Reply Approval                          │
│  Conversation Status                     │
└───────────────┬───────────────┬──────────┘
                │               │
                ▼               ▼
       ┌────────────────┐   ┌───────────────┐
       │  PostgreSQL    │   │ Vector Search │
       │                │   │               │
       │ Conversations  │   │ Brand KB      │
       │ Customers      │   │ Embeddings    │
       │ Orders         │   │ Retrieval     │
       │ Messages       │   │               │
       │ Reply History  │   └───────┬───────┘
       └────────────────┘           │
                                    ▼
                             ┌──────────────┐
                             │     LLM      │
                             │              │
                             │ Reply        │
                             │ Generation   │
                             └──────────────┘
Technology Stack
Frontend
Next.js
React
TypeScript
Tailwind CSS
Backend
Python
FastAPI
SQLAlchemy 2.0
Pydantic
Alembic
Database
PostgreSQL
Supabase PostgreSQL
AI / RAG
Sentence Transformers
Qdrant
Retrieval-Augmented Generation (RAG)
OpenRouter
LLM-based response generation
Development
Git
REST APIs
Async Python
Async SQLAlchemy
RAG Pipeline

The reply generation pipeline follows this flow:

Customer Message
       ↓
Conversation Context
       ↓
Identify Brand
       ↓
Retrieve Brand Knowledge
       ↓
Semantic Similarity Search
       ↓
Relevant Policy Context
       ↓
LLM Prompt
       ↓
AI Response
       ↓
Persist Generation

The model receives relevant brand policy context rather than generating a response purely from general knowledge.

This helps keep customer responses aligned with the brand's policies.

Reply Generation Lifecycle

Every generated response follows a controlled lifecycle.

generated
    │
    ▼
 edited
    │
    ▼
approved
Generated

The LLM creates the initial response.

Edited

The CX agent modifies the response when necessary.

Approved

The agent approves the final response.

The final response and approval timestamp are persisted in PostgreSQL.

API Flow
Conversations
List conversations
GET /api/conversations

Optional status filtering:

GET /api/conversations?status=open
Get conversation context
GET /api/conversations/{conversation_id}

This loads the conversation and its related context:

Conversation
├── Customer
├── Brand
├── Order
└── Messages
AI Reply
Generate reply
POST /api/conversations/{conversation_id}/reply

The request includes:

{
  "customer_message": "My order arrived damaged. What can you do?",
  "agent_id": "..."
}

The backend:

Loads the conversation
Retrieves relevant brand knowledge
Generates the AI response
Persists the generation
Returns the generated reply
Edit Reply
PATCH /api/conversations/replies/{reply_id}

The edited response is stored and the generation status becomes:

edited
Approve Reply
POST /api/conversations/replies/{reply_id}/approve

The final response is persisted and the status becomes:

approved
Conversation Status
PATCH /api/conversations/{conversation_id}/status

Example:

{
  "status": "open"
}
Database Model

The core entities are:

Brand
 │
 └── Knowledge Base Documents
          │
          └── Vector Retrieval

Customer
 │
 └── Conversation
       │
       ├── Messages
       ├── Order
       └── Reply Generations

Reply generations maintain the complete history of AI-assisted responses.

This makes the workflow traceable and allows the system to retain the distinction between:

AI Response
Edited Response
Final Response
Project Structure
datastraw/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes/
│   │   ├── core/
│   │   ├── db/
│   │   │   ├── models/
│   │   │   └── repositories/
│   │   ├── schemas/
│   │   └── services/
│   │
│   ├── alembic/
│   ├── requirements.txt
│   └── ...
│
├── frontend/
│   ├── app/
│   │   └── dashboard/
│   │       └── conversations/
│   ├── components/
│   │   ├── ConversationList.tsx
│   │   ├── ConversationPanel.tsx
│   │   ├── CustomerInfo.tsx
│   │   ├── ReplyEditor.tsx
│   │   └── StatusBadge.tsx
│   ├── lib/
│   │   └── api.ts
│   ├── package.json
│   └── ...
│
└── README.md
Getting Started
Prerequisites

Make sure the following are installed:

Python 3.11+
Node.js
npm
PostgreSQL / Supabase
Qdrant
Git
Backend Setup
cd backend

Create and activate a virtual environment:

Windows
python -m venv .venv
.\.venv\Scripts\Activate.ps1

Install dependencies:

pip install -r requirements.txt

Create your environment file:

.env

Configure the required environment variables.

Example:

DATABASE_URL=your_database_url

SUPABASE_JWT_SECRET=your_jwt_secret

QDRANT_URL=your_qdrant_url
QDRANT_API_KEY=your_qdrant_api_key
QDRANT_COLLECTION=your_collection

OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=your_model

EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

RAG_TOP_K=3
RAG_RELEVANCE_THRESHOLD=0.70

Run migrations:

python -m alembic upgrade head

Start the backend:

uvicorn app.main:app --reload

Backend:

http://127.0.0.1:8000

API documentation:

http://127.0.0.1:8000/docs
Frontend Setup

Open another terminal:

cd frontend

Install dependencies:

npm install

Start the development server:

npm run dev

Open:

http://localhost:3000/dashboard/conversations
Environment Variables

Never commit real secrets to Git.

The repository intentionally excludes:

.env
.env.local
node_modules/
.next/
.venv/

Use .env.example as a template for local configuration.

Example Workflow
Open the CX workspace.
Select a conversation.
Review customer and order context.
Review the customer's latest message.
Click Generate AI Reply.
The backend retrieves relevant brand policy context.
The LLM generates a response.
Review the response.
Edit if required.
Click Save Edit.
Click Approve Reply.
The final response is persisted.
Design Decisions
Agent-in-the-loop

AI-generated responses are never treated as automatically approved.

The CX agent has the final decision.

Brand-aware generation

Responses are grounded in brand-specific knowledge rather than relying only on the model's general knowledge.

Persistent generation history

Every generation is stored, allowing the system to track:

Customer Input
      ↓
Retrieved Context
      ↓
AI Response
      ↓
Agent Edit
      ↓
Final Response
Async backend

The backend uses asynchronous FastAPI and SQLAlchemy operations to support I/O-heavy workloads such as database access and AI service calls.

Current Scope

This implementation focuses on the core CX Reply Assistant workflow:

Conversation management
Context retrieval
Brand policy retrieval
AI reply generation
Agent editing
Reply approval
Persistence

The system is designed so additional capabilities such as authentication, analytics, additional knowledge sources, observability, and production deployment can be added independently.

Demo Scenario
Customer
My order arrived damaged. What can you do?
Retrieved Knowledge
Damaged Order Policy
AI

Generates a response based on the relevant brand policy.

Agent
Review → Edit → Save → Approve

This demonstrates the complete end-to-end CX workflow.

Repository

GitHub:

https://github.com/munavvarshaikh314/datastraw-cx-reply-assistant

Author

Munavvar Shaikh

AI & Backend Engineer

Built with FastAPI, Next.js, PostgreSQL, RAG, Qdrant, and LLMs.


### One thing I would change before committing

Because this README contains your GitHub URL, that's fine, but **don't put your actual API keys or Supabase credentials anywhere in it**.

Also, I intentionally used wording like **"designed so additional capabilities can be added"** rather than claiming features you haven't implemented. That's important in an interview assignment—reviewers can quickly tell when a README oversells the implementation.

Now create it from PowerShell:

```powershell
cd C:\dev\datastraw
notepad README.md