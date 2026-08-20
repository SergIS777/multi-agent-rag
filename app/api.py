import uuid

from fastapi import FastAPI
from pydantic import BaseModel
from langgraph.types import Command

from app.graph import build_graph

app = FastAPI(title="Multi-Agent RAG Platform", version="0.2.0")

_graph = None


def get_graph():
    global _graph
    if _graph is None:
        _graph = build_graph()
    return _graph


class IngestRequest(BaseModel):
    document_text: str
    config_name: str = "realestate"


class QueryRequest(BaseModel):
    query: str
    config_name: str = "realestate"
    thread_id: str | None = None


class ResumeRequest(BaseModel):
    thread_id: str
    action: str = "approve"


@app.get("/health")
def health():
    return {"status": "ok", "version": "0.2.0"}


@app.post("/ingest")
def ingest(req: IngestRequest):
    graph = get_graph()
    thread_id = f"api_{uuid.uuid4().hex[:8]}"
    cfg = {"configurable": {"thread_id": thread_id}}
    r = graph.invoke({"document_text": req.document_text,
                      "config_name": req.config_name}, config=cfg)
    return {"thread_id": thread_id,
            "chunks": len(r.get("chunks", [])),
            "trace_id": r.get("trace_id")}


@app.post("/query")
def query(req: QueryRequest):
    graph = get_graph()
    thread_id = req.thread_id or f"api_{uuid.uuid4().hex[:8]}"
    cfg = {"configurable": {"thread_id": thread_id}}
    graph.invoke({"query": req.query, "config_name": req.config_name}, config=cfg)
    st = graph.get_state(cfg)
    if st.next:  # граф остановился: human-in-the-loop ждёт человека
        intr = {}
        if st.tasks and st.tasks[0].interrupts:
            intr = st.tasks[0].interrupts[0].value
        return {"status": "awaiting_human", "thread_id": thread_id, "interrupt": intr}
    r = st.values
    return {"status": "done", "thread_id": thread_id,
            "trace_id": r.get("trace_id"),
            "answer": r.get("answer"),
            "score": r.get("score"),
            "extracted": r.get("extracted"),
            "review_ok": r.get("review_ok"),
            "review_attempts": r.get("review_attempts"),  # ← ШАГ 12: полировка
            "confidence": r.get("confidence"),
            "token_cost": r.get("token_cost"),
            "cost_usd": r.get("cost_usd"),
            "cost_blocked": r.get("cost_blocked")}


@app.post("/resume")
def resume(req: ResumeRequest):
    graph = get_graph()
    cfg = {"configurable": {"thread_id": req.thread_id}}
    graph.invoke(Command(resume={"action": req.action}), config=cfg)
    r = graph.get_state(cfg).values
    return {"status": "done",
            "answer": r.get("answer"),
            "review_ok": r.get("review_ok"),
            "review_attempts": r.get("review_attempts"),  # ← ШАГ 12: полировка
            "confidence": r.get("confidence"),
            "token_cost": r.get("token_cost"),
            "cost_usd": r.get("cost_usd"),
            "cost_blocked": r.get("cost_blocked")}