import uuid
from langgraph.types import Command
from app.graph import build_graph

DOC = """
Договор №123 от 19.08.2026 между ООО "Ромашка" (Заказчик) и ИП Иванов (Исполнитель).
Сумма договора: 500 000 руб. Срок выполнения: 30 дней.
Штраф за нарушение сроков: 0.1% от суммы за каждый день просрочки.
Неустойка за просрочку оплаты: 0.05% от суммы за каждый день.
"""

def main():
    graph = build_graph()
    thread_id = f"law_test_{uuid.uuid4().hex[:8]}"
    cfg = {"configurable": {"thread_id": thread_id}}
    print(f"[SESSION] {thread_id}")

    print("=== 1. INGEST ===")
    graph.invoke({"document_text": DOC, "config_name": "law"}, config=cfg)
    print("ingest done")

    print("=== 2. QUERY (stream) ===")
    for event in graph.stream({"query": "Какие штрафы и неустойки?",
                               "config_name": "law"}, config=cfg):
        if "__interrupt__" in event:
            intr = event["__interrupt__"]
            if isinstance(intr, (list, tuple)):
                intr = intr[0]
            data = getattr(intr, "value", intr) or {}
            print("\n" + "=" * 50)
            print("=== ТРЕБУЕТСЯ ПОДТВЕРЖДЕНИЕ ЧЕЛОВЕКОМ ===")
            print("Сообщение:", data.get("message"))
            print("Score:", data.get("score"))
            print("Предпросмотр ответа:")
            print(str(data.get("answer_preview", ""))[:400])
            print("=" * 50)
        else:
            print(event)

    print("\n=== 3. APPROVE (resume) ===")
    result = graph.invoke(Command(resume={"action": "approve"}), config=cfg)
    print("review_ok:", result.get("review_ok"))
    print("Финальный ответ:")
    print(result.get("answer", "")[:500])

if __name__ == "__main__":
    main()