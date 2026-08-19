import os
import httpx

key = os.getenv("GROQ_API_KEY", "")
proxy = os.getenv("LOCAL_PROXY", "")
h = {"Authorization": f"Bearer {key}"}

r = httpx.get("https://api.groq.com/openai/v1/models", headers=h,
              proxy=proxy, timeout=20)
print("GET /models:", r.status_code)

for m in ["openai/gpt-oss-20b", "openai/gpt-oss-120b"]:
    r2 = httpx.post("https://api.groq.com/openai/v1/chat/completions",
                    headers={**h, "Content-Type": "application/json"},
                    json={"model": m, "messages": [{"role": "user", "content": "hi"}]},
                    proxy=proxy, timeout=30)
    print(m, "->", r2.status_code, r2.text[:150])