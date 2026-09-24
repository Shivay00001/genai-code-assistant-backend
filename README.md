# genai-code-assistant-backend

Real GenAI code-assistant API: FastAPI backend with a **real
OpenAI-compatible LLM client** (`llm.py`, httpx).

## What it does

- `POST /complete` — `{"prompt", "language"}` → code completion
- `POST /explain` — `{"code", "language"}` → plain-English explanation
- `POST /fix` — `{"code", "error", "language"}` → fixed code + what was wrong
- `GET /health` — includes `key_configured`

## API key

| Env var          | Purpose                      | Default                     |
|------------------|------------------------------|-----------------------------|
| `OPENAI_API_KEY` | **API key** for the LLM call | (unset)                     |
| `OPENAI_BASE_URL`| Compatible endpoint          | `https://api.openai.com/v1` |
| `OPENAI_MODEL`   | Model name                   | `gpt-4o-mini`               |

Without `OPENAI_API_KEY` every endpoint returns **HTTP 503** with a clear
message — the service never fabricates code. With an invalid key, the
provider's real 401 is surfaced.

## Run

```bash
pip install -r requirements.txt
OPENAI_API_KEY=sk-... uvicorn main:app --port 8004
```

## Tests

```bash
python -m pytest tests/ -q
```

Covers: honest 503 on all three endpoints without a key, real upstream 401
with a dummy key (proves genuine HTTP plumbing), empty-input rejection.
