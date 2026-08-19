import re
import uuid
from app.config_loader import load_config

PII_PATTERNS = [
    r"\+?\d[\d\s\-\(\)]{10,15}",
    r"\b[\w.\-]+@[\w\-]+\.\w{2,}\b",
    r"\bСНИЛС\b", r"\bИНН\b",
]

_model = None
_collection = None

def _get_model():
    global _model
    if _model is None:
        from fastembed import TextEmbedding
        supported = [m["model"] for m in TextEmbedding.list_supported_models()]
        prefs = [
            "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            "paraphrase-multilingual-MiniLM-L12-v2",
        ]
        name = next((p for p in prefs if p in supported), None)
        if name is None:
            name = next((m for m in supported if "multi" in m.lower()), None)
        if name is None:
            name = supported[0]
        print("EMBED MODEL:", name)
        _model = TextEmbedding(name)
    return _model

def _get_collection():
    global _collection
    if _collection is None:
        import chromadb
        client = chromadb.EphemeralClient()
        _collection = client.get_or_create_collection("docs")
    return _collection

def chunk_text(text: str, size: int = 600, overlap: int = 100) -> list:
    chunks, start = [], 0
    while start < len(text):
        chunks.append(text[start:start + size])
        start += size - overlap
    return chunks

# --- 1. GUARD (DLP) ---
def guard(state: dict) -> dict:
    text = f"{state.get('query', '')} {state.get('document_text', '')}"
    for p in PII_PATTERNS:
        if re.search(p, text, re.I):
            return {"pii_blocked": True,
                    "answer": "Запрос заблокирован DLP-фильтром: обнаружены персональные данные."}
    return {"pii_blocked": False,
            "trace_id": state.get("trace_id") or uuid.uuid4().hex[:12]}

# --- 2. INGESTOR ---
def ingestor(state: dict) -> dict:
    return {"document_text": re.sub(r"\s+", " ", state.get("document_text", "")).strip()}

# --- 3. INDEXER ---
def indexer(state: dict) -> dict:
    chunks = chunk_text(state.get("document_text", ""))
    if not chunks:
        return {"chunks": []}
    emb = [e.tolist() for e in _get_model().embed(chunks)]
    col = _get_collection()
    col.upsert(ids=[f"chunk_{i}" for i in range(len(chunks))],
               embeddings=emb, documents=chunks)
    return {"chunks": chunks}

# --- 4. RETRIEVER ---
def retriever(state: dict) -> dict:
    q = state.get("query", "")
    try:
        emb = list(_get_model().embed([q]))[0].tolist()
        res = _get_collection().query(query_embeddings=[emb], n_results=3)
        retrieved = res["documents"][0]
    except Exception:
        words = q.lower().split()[:3]
        retrieved = [c for c in state.get("chunks", [])
                     if any(w in c.lower() for w in words)][:3]
    return {"retrieved": retrieved}

# --- 5. EXTRACTOR (детерминированный скоринг из конфига, как в n8n) ---
def extractor(state: dict) -> dict:
    cfg = load_config(state.get("config_name", "realestate"))
    text = " ".join(state.get("retrieved", [])).lower()
    sc = cfg["scoring"]
    pos = [s for s in cfg["extraction_rules"]["signals_positive"] if s.lower() in text]
    risk = [s for s in cfg["extraction_rules"]["signals_risk"] if s.lower() in text]
    score = 0
    if pos:
        score += min(sc["positive_max"], len(pos) * 7)
    if risk:
        score -= min(abs(sc["risk_max"]), len(risk) * 6)
    score = max(0, min(100, score))
    return {"extracted": {"positive": pos, "risk": risk}, "score": score}

# --- 6. ANSWERER (LLM-карточка с цитатами) ---
def answerer(state: dict) -> dict:
    from app.llm import call_llm
    cfg = load_config(state.get("config_name", "realestate"))
    context = "\n---\n".join(f"[{i}] {c}" for i, c in enumerate(state.get("retrieved", [])))
    system = ("Ты аналитик рынка недвижимости Санкт-Петербурга. Отвечай СТРОГО по контексту, "
              "цитируй источники в формате [0], [1]. Если ответа в контексте нет — скажи прямо.")
    user = (f"Конфиг: {cfg['description']}\nКонтекст:\n{context}\n\n"
            f"Вопрос: {state.get('query', '')}\nАвтоскоринг: {state.get('score', 0)}/100")
    text, tokens = call_llm(system, user)
    return {"answer": text, "token_cost": state.get("token_cost", 0) + tokens}

# --- 7. SUMMARIZER ---
def summarizer(state: dict) -> dict:
    from app.llm import call_llm
    text, tokens = call_llm("Сделай резюме документа в 3-5 предложениях.",
                            state.get("document_text", "")[:4000])
    return {"answer": text, "token_cost": state.get("token_cost", 0) + tokens}

# --- 8. REVIEWER (ловит галлюцинации и fallback) ---
def reviewer(state: dict) -> dict:
    answer = state.get("answer", "")
    attempts = state.get("review_attempts", 0) + 1
    ok = ("[FALLBACK]" not in answer) and len(answer) > 50
    return {"review_ok": ok, "review_attempts": attempts,
            "confidence": 80.0 if ok else 30.0}

# --- 9. ORCHESTRATOR (роутинг) ---
def route(state: dict) -> str:
    if state.get("pii_blocked"):
        return "end"
    if state.get("query"):
        return "query"
    return "ingest"

# --- 10. HUMAN-IN-THE-LOOP (для law/medicine) ---
def human_review(state: dict) -> dict:
    """Остановка графа для подтверждения человеком (config-driven)."""
    from langgraph.types import interrupt
    answer = state.get("answer", "")
    decision = interrupt({
        "message": "Требуется подтверждение ответа",
        "answer_preview": answer[:500],
        "score": state.get("score", 0),
        "signals": state.get("extracted", {})
    })
    # decision = {"action": "approve"} или {"action": "reject"}
    if decision.get("action") == "approve":
        return {"review_ok": True, "confidence": 95.0}
    return {"review_ok": False, "answer": "Ответ отклонён пользователем."}