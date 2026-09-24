import os
from fastapi.testclient import TestClient

os.environ.pop("no_proxy", None)
os.environ.pop("NO_PROXY", None)

from main import app  # noqa: E402

client = TestClient(app)
DUMMY = "sk-dummy-invalid-key-for-testing"


def _with_dummy():
    os.environ["OPENAI_API_KEY"] = DUMMY


def _without_key():
    os.environ.pop("OPENAI_API_KEY", None)


def test_health():
    assert client.get("/health").status_code == 200


def test_complete_no_key_is_honest():
    _without_key()
    r = client.post("/complete", json={"prompt": "def fib(n):"})
    assert r.status_code == 503
    assert "OPENAI_API_KEY" in r.json()["detail"]


def test_explain_no_key_is_honest():
    _without_key()
    r = client.post("/explain", json={"code": "print('hi')"})
    assert r.status_code == 503


def test_fix_no_key_is_honest():
    _without_key()
    r = client.post("/fix", json={"code": "x = 1/0"})
    assert r.status_code == 503


def _assert_real_401(path, payload):
    _with_dummy()
    try:
        r = client.post(path, json=payload)
    finally:
        _without_key()
    # real HTTP client -> real provider -> honest 401
    assert r.status_code == 401, (path, r.status_code, r.text[:200])


def test_complete_dummy_key_real_401():
    _assert_real_401("/complete", {"prompt": "def fib(n):"})


def test_explain_dummy_key_real_401():
    _assert_real_401("/explain", {"code": "print('hi')"})


def test_fix_dummy_key_real_401():
    _assert_real_401("/fix", {"code": "x = 1/0", "error": "ZeroDivisionError"})


def test_empty_inputs_rejected():
    assert client.post("/complete", json={"prompt": " "}).status_code == 400
    assert client.post("/explain", json={"code": " "}).status_code == 400
    assert client.post("/fix", json={"code": " "}).status_code == 400
