import sqlite3

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver

from app.state import PlatformState
from app import agents

# --- Checkpointer: singleton, соединение живёт весь процесс (шаг 6 спеки) ---
_checkpointer = None


def get_checkpointer() -> SqliteSaver:
    """SqliteSaver с персистентным файлом: состояние переживает перезапуск,
    сбои можно replay-ить. Соединение открывается один раз."""
    global _checkpointer
    if _checkpointer is None:
        conn = sqlite3.connect("checkpoints.sqlite", check_same_thread=False)
        _checkpointer = SqliteSaver(conn)
        _checkpointer.setup()  # создаёт таблицы, если их нет
    return _checkpointer


def review_router(state: dict) -> str:
    """Reviewer решил: END или вернуть Answerer на доработку (лимит 2)."""
    if state.get("review_ok"):
        return "end"
    if state.get("review_attempts", 0) >= 2:
        return "end"  # честно: не удалось верифицировать
    return "retry"


def build_graph():
    g = StateGraph(PlatformState)

    g.add_node("guard", agents.guard)
    g.add_node("ingestor", agents.ingestor)
    g.add_node("indexer", agents.indexer)
    g.add_node("retriever", agents.retriever)
    g.add_node("extractor", agents.extractor)
    g.add_node("answerer", agents.answerer)
    g.add_node("summarizer", agents.summarizer)
    g.add_node("reviewer", agents.reviewer)

    g.add_edge(START, "guard")
    g.add_conditional_edges("guard", agents.route,
                            {"end": END,
                             "query": "retriever",
                             "summarize": "summarizer",
                             "ingest": "ingestor"})

    # ingest-ветка
    g.add_edge("ingestor", "indexer")
    g.add_edge("indexer", END)

    # query-ветка с Reviewer-циклом
    g.add_edge("retriever", "extractor")
    g.add_edge("extractor", "answerer")
    g.add_edge("answerer", "reviewer")
    g.add_conditional_edges("reviewer", review_router,
                            {"end": END, "retry": "answerer"})

    # summarize-ветка
    g.add_edge("summarizer", "reviewer")

    return g.compile(checkpointer=get_checkpointer())