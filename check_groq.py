import os, httpx
key = os.getenv("GROQ_API_KEY", "")
print(f"Key len: {len(key)}, starts: {key[:10] if key else 'EMPTY'}")
try:
    r = httpx.post("https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {key}"},
        json={"model": "llama-3.1-8b-instant", "messages": [{"role":"user","content":"hi"}]},
        timeout=30)
    print(f"STATUS: {r.status_code}")
    print(f"BODY: {r.text[:500]}")
except Exception as e:
    print(f"EXCEPTION: {type(e).__name__}: {e}")