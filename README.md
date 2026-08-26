# Aster & Row Reliable RAG Support Agent

A compact support agent built for the Crossword Engineering AI internship take-home. The design prioritizes groundedness, safe abstention, document precedence, order-tool privacy, multi-turn context, deterministic evaluation, and observable execution.

## What is included
- RAG over all supplied Markdown knowledge-base documents.
- Metadata-aware retrieval that prefers active official customer documents and rejects draft/superseded content as authority.
- A sanitized `lookup_order` function over `data/orders.json`.
- Session-scoped multi-turn memory.
- Prompt-injection resistance by treating retrieved text and tool output as untrusted data.
- Explicit abstention and human-handoff behavior for conflicts, missing evidence, privacy requests, and unsupported actions.
- Deterministic regression tests and evaluation runner covering all visible cases plus five original cases.
- Structured debug logging with retrieval metadata and sanitized tool results.

## Architecture
`main.py` -> `Agent` -> routing -> `Retriever` or `OrderLookup` -> grounded response -> sources/handoff.

Retrieval uses a lightweight TF-IDF-style lexical index with metadata/authority boosts. This keeps the submission reproducible and dependency-light. An LLM provider can be added behind the response-generation boundary without changing the safety, retrieval, or tool contracts.

## Setup
```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

Optional API configuration is documented in `.env.example`. The evaluation suite does not require an API key.

## Run
```bash
python main.py --debug
```

Try a cited policy question, `Where is ORD-1007 and when should it arrive?`, a multi-turn Canada question, and the conflicting Breeze Tumbler dishwasher question.

## Evaluation
```bash
pytest -q
python evaluation/run_evaluation.py
```

The supplied visible suite contains 15 behavior-level cases. Five additional original cases are in `evaluation/custom-cases.json`.

Final deterministic evaluation result: **20/20 cases passed** locally, covering all 15 supplied cases plus five original regression cases. Run the command above to reproduce it.

### Evaluation categories
Retrieval, groundedness, multi-source grounding, conversation, tool use, tool reliability, privacy, prompt security, abstention, source conflict, and safety.

## Bug diary
1. **Legacy policy outranked current policy.** Root cause: lexical similarity ignored document status. Fix: active official documents receive an authority boost and superseded/draft documents are excluded from customer authority. Regression: `test_current_return_policy`.
2. **Cancelled orders exposed stale delivery data.** Root cause: raw order data contains a historical ETA. Fix: `OrderLookup` clears carrier/tracking/ETA for cancelled or returned states. Regression: `test_cancelled_eta_not_stale`.
3. **Internal order fields could leak.** Root cause: an early prototype returned the whole order object. Fix: explicit customer-safe field allowlist. Regression: `test_order_tool_sanitizes`.
4. **Migration content looked instruction-like.** Root cause: retrieved text was treated as authority. Fix: metadata filtering plus an application-level security boundary. Regression: `test_prompt_injection_is_data`.
5. **Two active official Breeze Tumbler sources conflict.** Root cause: ranking could silently select one. Fix: explicit conflict detection and human confirmation. Regression: `test_source_conflict`.

## Known limitations
- Retrieval is lexical rather than dense-vector semantic retrieval. For this small corpus it is deterministic and transparent; production should use hybrid dense + lexical retrieval with offline retrieval evaluation.
- The current response layer uses deterministic grounded templates to keep evaluation reproducible. A production version should place an LLM behind the same grounded-context and safety contracts.
- The mock order tool assumes possession of the order ID is sufficient authentication, matching the assignment.
- No production ticketing or cancellation/refund action tool exists, so the agent never claims those actions were completed.

## AI coding tools
AI assistance was used to structure implementation, tests, and documentation. Human review remains responsible for the submitted code. One incomplete suggestion was an early design that would have passed raw order objects to the model. It was rejected because it violated the assignment's privacy requirement. The final implementation uses an explicit safe-field allowlist.

## Demo
Record a 2–4 minute terminal demo showing: one cited knowledge-base answer, one order lookup, one multi-turn conversation, one refusal/conflict handoff, and the evaluation suite running. ![Agent demo](media/demo.gif)

## Security
Never commit `.env` or API keys. API credentials must be supplied through environment variables and never placed in source code, README files, logs, or the repository.
