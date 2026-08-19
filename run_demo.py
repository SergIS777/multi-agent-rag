import time
import uuid
from app.graph import build_graph

DOC = """
Setl Group открыла продажи нового ЖК "Южно-Приморский" в Санкт-Петербурге.
Проектная декларация опубликована, эскроу-счета в Сбербанке.
Старт продаж, пресейл: цены от 5,2 млн руб. Субсидированная ипотека 6%, рассрочка.
Срок сдачи — 4 квартал 2027. Метро "Южная" в пешей доступности.
"""

def main():
    graph = build_graph()
    # Каждый запуск — новая сессия (Uuid вместо хардкода)
    thread_id = f"demo_{uuid.uuid4().hex[:8]}"
    cfg = {"configurable": {"thread_id": thread_id}}
    print(f"[SESSION] {thread_id}")

    print("=== 1. INGEST документа ===")
    r1 = graph.invoke({"document_text": DOC, "config_name": "realestate"}, config=cfg)
    print("chunks:", len(r1.get("chunks", [])))

    print("=== 2. QUERY ===")
    t0 = time.time()
    try:
        r2 = graph.invoke({"query": "Чем интересен объект? Какие риски?",
                           "config_name": "realestate"}, config=cfg)
    except Exception as e:
        print(f"[SYSTEM] LLM недоступен после 3 попыток: {type(e).__name__}. "
              "Честный отказ — данные не выдуманы.")
        return
    print("trace:", r2.get("trace_id"))
    print("score:", r2.get("score"), "| signals:", r2.get("extracted", {}).get("positive"))
    print("review_ok:", r2.get("review_ok"), "| tokens:", r2.get("token_cost"),
          "| cost: $%.6f" % r2.get("cost_usd", 0),
          "| %.1fs" % (time.time() - t0))
    print("--- ANSWER ---")
    print(r2.get("answer", "")[:800])

if __name__ == "__main__":
    main()