import sqlite3

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import RetryPolicy

from app.state import PlatformState
from app import agents
from app.config_loader import load_config

_checkpointer = None

RETRY_LLM = RetryPolicy(max_attempts=3, initial_interval=1.0, backoff_factor=2.0)


def get_checkpointer() -> SqliteSaver:
    global _checkpointer
    if _checkpointer is None:
        conn = sqlite3.connect("checkpoints.sqlite", check_same_thread=False)
        _checkpointer = SqliteSaver(conn)
        _checkpointer.setup()
    return _checkpointer


def review_router(state: dict) -> str:
    if state.get("review_ok"):
        return "end"
    if state.get("review_attempts", 0) >= 2:
        return "end"
    return "retry"


def needs_human_review(state: dict) -> str:
    cfg = load_config(state.get("config_name", "realestate"))
    if cfg.get("human_review"):
        return "human"
    return "reviewer"


def build_graph():
    g = StateGraph(PlatformState)

    g.add_node("guard", agents.guard)
    g.add_node("ingestor", agents.ingestor)
    g.add_node("indexer", agents.indexer)
    g.add_node("retriever", agents.retriever)
    g.add_node("extractor", agents.extractor)
    g.add_node("answerer", agents.answerer, retry_policy=RETRY_LLM)
    g.add_node("summarizer", agents.summarizer, retry_policy=RETRY_LLM)
    g.add_node("reviewer", agents.reviewer)
    g.add_node("human_review", agents.human_review)

    g.add_edge(START, "guard")
    g.add_conditional_edges("guard", agents.route,
                            {"end": END,
                             "query": "retriever",
                             "summarize": "summarizer",
                             "ingest": "ingestor"})

    g.add_edge("ingestor", "indexer")
    g.add_edge("indexer", END)

    g.add_edge("retriever", "extractor")
    g.add_edge("extractor", "answerer")
    g.add_conditional_edges("answerer", needs_human_review,
                            {"human": "human_review",
                             "reviewer": "reviewer"})

    g.add_conditional_edges("reviewer", review_router,
                            {"end": END, "retry": "answerer"})

    g.add_edge("human_review", END)
    g.add_edge("summarizer", "reviewer")

    return g.compile(checkpointer=get_checkpointer())