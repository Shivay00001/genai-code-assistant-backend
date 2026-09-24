"""Real GenAI code-assistant API.

FastAPI backend with a real OpenAI-compatible LLM client (llm.py).
Endpoints: /complete, /explain, /fix. Without an API key every endpoint
returns an honest error instead of fabricated code.
"""
import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from llm import LLMError, chat

app = FastAPI(title="GenAI Code Assistant", version="1.0.0")


class CompleteRequest(BaseModel):
    prompt: str = Field(..., max_length=8000)
    language: str = "python"


class ExplainRequest(BaseModel):
    code: str = Field(..., max_length=20000)
    language: str = "python"


class FixRequest(BaseModel):
    code: str = Field(..., max_length=20000)
    error: str = Field("", max_length=4000)
    language: str = "python"


def _call(system: str, user: str) -> str:
    try:
        return chat(system, user)
    except LLMError as e:
        code = 503 if e.status is None else e.status
        raise HTTPException(code, str(e))


@app.get("/health")
def health():
    return {"status": "ok",
            "key_configured": bool(os.environ.get("OPENAI_API_KEY"))}


@app.post("/complete")
def complete(req: CompleteRequest):
    if not req.prompt.strip():
        raise HTTPException(400, "prompt must not be empty")
    system = (f"You are a senior {req.language} engineer. Complete the user's "
              "code/request with working, idiomatic code only. No explanations "
              "outside code comments.")
    return {"result": _call(system, req.prompt)}


@app.post("/explain")
def explain(req: ExplainRequest):
    if not req.code.strip():
        raise HTTPException(400, "code must not be empty")
    system = (f"You are a senior {req.language} engineer. Explain what the "
              "following code does, clearly and concisely: what it does, how "
              "it works, and any notable edge cases.")
    return {"result": _call(system, req.code)}


@app.post("/fix")
def fix(req: FixRequest):
    if not req.code.strip():
        raise HTTPException(400, "code must not be empty")
    system = (f"You are a senior {req.language} engineer. Fix the bug in the "
              "following code. Return the corrected full code, then a short "
              "note on what was wrong.")
    user = req.code + (f"\n\nReported error:\n{req.error}" if req.error else "")
    return {"result": _call(system, user)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8004)))
