import uuid
from app.graph import build_graph

DOC = "Тестовый объект: продажа, цена 5 млн руб, риск — срок сдачи."

def main():
    graph = build_graph()
    cfg = {"configurable": {"thread_id": f"cost_{uuid.uuid4().hex[:8]}"}}
    graph.invoke({"document_text": DOC, "config_name": "cost_test"}, config=cfg)
    r = graph.invoke({"query": "Чем интересен?", "config_name": "cost_test"}, config=cfg)
    print("answer:", r.get("answer"))
    print("token_cost:", r.get("token_cost"), "| cost_blocked:", r.get("cost_blocked"))

if __name__ == "__main__":
    main()