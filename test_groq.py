import os
import httpx

key = os.getenv("GROQ_API_KEY", "")
print("key present:", bool(key), "| len:", len(key))

for model in ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]:
    try:
        r = httpx.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}",
                     "Content-Type": "application/json"},
            json={"model": model,
                  "messages": [{"role": "user", "content": "hi"}]},
            timeout=30,
        )
        print(model, "-> status:", r.status_code)
        print(r.text[:400])
    except Exception as e:
        print(model, "-> EXCEPTION:", type(e).__name__, str(e)[:200])
    print("---")