import os
import httpx

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODELS = ["meta-llama/llama-4-scout-17b-16e-instruct",
          "openai/gpt-oss-20b",
          "openai/gpt-oss-120b"]


class LLMUnavailableError(Exception):
    """Временный сбой (сеть/429/5xx) — RetryPolicy повторит ноду."""


def _post(key: str, payload: dict, timeout: int):
    proxy = os.getenv("LOCAL_PROXY", "")
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

    transient = None
    for model in MODELS:
        try:
            r = _post(key, {"model": model, "temperature": temperature,
                            "messages": [{"role": "system", "content": system},
                                         {"role": "user", "content": user}]},
                      timeout)
            # модель недоступна/снята — пробуем следующую
            if r.status_code in (400, 404) and "model" in r.text.lower():
                print(f"[LLM] модель {model} недоступна — пробую следующую")
                continue
            # ключ/права — постоянная ошибка, ретраи бесполезны
            if r.status_code in (401, 403):
                print(f"[LLM ERROR] {model}: status={r.status_code} (ключ/права)")
                return "[FALLBACK] LLM недоступен. Ответ требует ручной проверки.", 0
            # rate limit / серверные — временные
            if r.status_code in (429, 500, 502, 503, 529):
                transient = f"{model}: HTTP {r.status_code}"
                print(f"[LLM RETRYABLE] {transient}")
                continue
            r.raise_for_status()
            data = r.json()
            return (data["choices"][0]["message"]["content"],
                    data.get("usage", {}).get("total_tokens", 0))
        except httpx.TransportError as e:  # сеть/таймаут — временный сбой
            transient = f"{model}: {type(e).__name__}"
            print(f"[LLM RETRYABLE] {transient}")
            break  # сеть общая для всех моделей
        except httpx.HTTPStatusError as e:
            print(f"[LLM ERROR] {model}: status={e.response.status_code} "
                  f"body={e.response.text[:200]}")
    if transient:
        raise LLMUnavailableError(transient)  # подхватит RetryPolicy
    return "[FALLBACK] LLM недоступен. Ответ требует ручной проверки.", 0