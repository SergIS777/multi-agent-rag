import os
import httpx

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODELS = ["meta-llama/llama-4-scout-17b-16e-instruct",
          "openai/gpt-oss-20b",
          "openai/gpt-oss-120b"]


def _post(key: str, payload: dict, timeout: int):
    proxy = os.getenv("LOCAL_PROXY", "")
    print(f"[LLM] proxy={proxy!r}")
    headers = {"Authorization": f"Bearer {key}",
               "Content-Type": "application/json"}
    if proxy:
        return httpx.post(GROQ_URL, headers=headers, json=payload,
                          timeout=timeout, proxy=proxy)
    return httpx.post(GROQ_URL, headers=headers, json=payload,
                      timeout=timeout, trust_env=False)


def call_llm(system: str, user: str, temperature: float = 0.2,
             timeout: int = 60) -> tuple:
    key = os.getenv("GROQ_API_KEY", "")
    if not key:
        print("[LLM] GROQ_API_KEY не задан")
        return "[FALLBACK] LLM недоступен. Ответ требует ручной проверки.", 0

    for model in MODELS:
        try:
            r = _post(key, {"model": model, "temperature": temperature,
                            "messages": [{"role": "system", "content": system},
                                         {"role": "user", "content": user}]},
                      timeout)
            if r.status_code in (400, 404) and "model" in r.text.lower():
                print(f"[LLM] модель {model} недоступна — пробую следующую")
                continue
            r.raise_for_status()
            data = r.json()
            return (data["choices"][0]["message"]["content"],
                    data.get("usage", {}).get("total_tokens", 0))
        except httpx.HTTPStatusError as e:
            print(f"[LLM ERROR] {model}: status={e.response.status_code} "
                  f"body={e.response.text[:200]}")
        except Exception as e:
            print(f"[LLM ERROR] {model}: {type(e).__name__}: {str(e)[:200]}")
            break
    return "[FALLBACK] LLM недоступен. Ответ требует ручной проверки.", 0