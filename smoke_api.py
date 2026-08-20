import httpx

BASE = "http://127.0.0.1:8000"

DOC = ("Setl Group открыла продажи ЖК 'Южно-Приморский'. Пресейл, цены от 5,2 млн руб, "
       "эскроу в Сбербанке, метро Южная, сдача 4 кв 2027.")

print("health:", httpx.get(f"{BASE}/health", timeout=10).json())
ing = httpx.post(f"{BASE}/ingest",
                 json={"document_text": DOC, "config_name": "realestate"},
                 timeout=120).json()
print("ingest:", ing)
q = httpx.post(f"{BASE}/query",
               json={"query": "Чем интересен объект?", "config_name": "realestate",
                     "thread_id": ing["thread_id"]},
               timeout=120).json()
print("status:", q["status"])
print("answer:", (q.get("answer") or "")[:300])