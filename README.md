# CloudDesk AI Support

A Tier-1 customer support AI agent for a fictional SaaS product, CloudDesk.
It classifies incoming questions, retrieves relevant knowledge-base content
with RAG, generates a grounded answer with Gemini, and escalates to a human
whenever it can't answer confidently -- rather than guessing.

## Architecture

```
Streamlit frontend  --HTTP-->  FastAPI backend  -->  SupportAgent
                                                        |
                                          +-------------+-------------+
                                          |             |             |
                                   TicketClassifier   RAGEngine    LLMService
                                   (keyword-based     (ChromaDB +  (Gemini)
                                    category router)   sentence-
                                                        transformers)
```

**Request flow (`backend/support_agent.py`):**

1. **Classify** the message into `billing` / `technical` / `account_access` /
   `unknown`, with a confidence score. Below a 0.70 confidence threshold, or
   `unknown`, escalate immediately -- don't bother searching the KB.
2. **Retrieve** the top-3 nearest FAQ entries from ChromaDB (cosine distance),
   filtering out anything above a relevance cutoff (`MAX_RELEVANT_DISTANCE`
   in `rag.py`). Irrelevant matches never reach the LLM.
3. **Generate** an answer with Gemini, grounded strictly in the retrieved
   context. The prompt requires the model to return an exact sentinel token
   (`NOT_FOUND_IN_KB`) if the context doesn't actually answer the question --
   this is checked deterministically rather than pattern-matching the model's
   free-text wording, which is what a fragile phrase-list approach would do.
4. Return `status: answered` (with sources) or `status: escalated` (with a
   human-support message) accordingly.

## Tech stack

- **Frontend:** Streamlit
- **Backend:** FastAPI + Uvicorn
- **Classification:** keyword-based scoring (no ML model -- see Assumptions)
- **Retrieval:** ChromaDB (persistent, cosine distance) +
  `sentence-transformers` (`all-MiniLM-L6-v2`) for embeddings
- **Generation:** Google Gemini (`google-genai` SDK)

## Setup

**1. Clone and create a virtual environment**

```bash
git clone <your-repo-url>
cd supervity-customer-support-ai
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux
```

**2. Install dependencies**

```bash
pip install -r requirements.txt
```

**3. Configure your API key**

Copy `.env.example` to `.env` and fill in your Gemini API key:

```bash
copy .env.example .env        # Windows
# cp .env.example .env        # macOS/Linux
```

```
GEMINI_API_KEY=your-key-here
```

**4. Build the knowledge base**

```bash
python scripts/ingest.py
```

This reads the FAQ content in `data/` and indexes it into a local
`chroma_db/` folder (git-ignored -- rebuild it locally, don't commit it).

**5. Run the backend**

```bash
uvicorn main:app --reload --port 8000
```

**6. Run the frontend** (separate terminal, same virtual environment)

```bash
streamlit run frontend/app.py
```

Open the URL Streamlit prints (typically `http://localhost:8501`).

## Assumptions made

- **Classification is keyword-based, not ML-based.** Given the scope, a
  transparent keyword-scoring classifier was used instead of training/hosting
  a separate intent-classification model. It's simple to reason about and
  fully explainable (`reason` field always says exactly which keywords
  matched), at the cost of being sensitive to phrasing it hasn't seen
  (e.g. "two-factor" with a hyphen vs "two factor" with a space needs to be
  listed explicitly).
- **The knowledge base is intentionally small (15 FAQ entries)** covering
  billing, technical, and account-access topics, as sample content for this
  exercise. The system's answer coverage is bounded by what's indexed --
  by design, it escalates rather than hallucinates on anything outside that
  set. See the tradeoff note in the demo video for more on this.
- **Confidence threshold (0.70)** and **RAG relevance cutoff (0.45 cosine
  distance)** were chosen based on manual testing against the actual sample
  data, not a formal tuning process. They're intentionally conservative --
  the system is designed to escalate rather than guess when uncertain.
- **Single-turn, stateless backend.** Each `/chat` call is independent; there
  is no multi-turn conversation memory on the backend (the frontend keeps
  chat history for display purposes only, it isn't sent back to the model).

## Known limitations

- Coverage is capped by the 15 indexed FAQ entries -- a well-formed,
  on-topic question with no matching KB entry will correctly escalate rather
  than answer, since the system is grounded-only by design (no fallback to
  the model's general knowledge).
- The sidebar's "Knowledge Base" / "Analytics" / "Settings" nav items in the
  frontend are placeholders for future pages, not yet functional.
- The right-hand "AI Support Status" panel shows static values (FAQ count,
  threshold) rather than live data pulled from the backend.
