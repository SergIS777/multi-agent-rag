import io
import os

import streamlit as st
import httpx

# Секреты Streamlit Cloud -> env (для Groq)
for _k in ("GROQ_API_KEY", "LOCAL_PROXY"):
    if _k not in os.environ:
        try:
            if _k in st.secrets:
                os.environ[_k] = str(st.secrets[_k])
        except Exception:
            pass

API = os.getenv("API_URL", "http://127.0.0.1:8000")
CONFIGS = ["realestate", "law", "logistics", "medicine"]

st.set_page_config(page_title="Multi-Agent RAG Platform", layout="wide")
st.title("🤖 Multi-Agent RAG Platform")
st.caption("LangGraph + 4 бизнес-конфига + FastAPI + OCR")


def _api_alive() -> bool:
    try:
        return httpx.get(f"{API}/health", timeout=1.5).status_code == 200
    except Exception:
        return False


USE_API = _api_alive()

_graph = None


def get_graph():
    global _graph
    if _graph is None:
        from app.graph import build_graph
        _graph = build_graph()
    return _graph


st.sidebar.success(f"Режим: {'API' if USE_API else 'прямой граф (in-process)'}")


def _ocr_pdf(doc) -> str:
    import pytesseract
    from PIL import Image
    if os.name == "nt":
        pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    out = []
    for page in doc:
        pix = page.get_pixmap(dpi=200)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        try:
            out.append(pytesseract.image_to_string(img, lang="rus+eng"))
        except Exception:
            out.append(pytesseract.image_to_string(img, lang="eng"))
    return "\n".join(out)


def extract_text(uploaded) -> str:
    name = uploaded.name.lower()
    data = uploaded.read()
    if name.endswith(".pdf"):
        import fitz
        doc = fitz.open(stream=data, filetype="pdf")
        text = "".join(page.get_text() for page in doc)
        if len(text.strip()) < 50:
            try:
                st.info("Похоже на скан — включаю OCR (может занять минуту)...")
                text = _ocr_pdf(doc)
            except Exception as e:
                st.error(f"OCR недоступен в этом окружении: {e}")
        return text
    if name.endswith(".docx"):
        import docx
        d = docx.Document(io.BytesIO(data))
        return "\n".join(par.text for par in d.paragraphs)
    return data.decode("utf-8", errors="ignore")


def run_ingest(doc: str, config: str) -> dict:
    if USE_API:
        return httpx.post(f"{API}/ingest",
                          json={"document_text": doc, "config_name": config},
                          timeout=300).json()
    g = get_graph()
    thread_id = f"st_{uuid4()}"
    cfg = {"configurable": {"thread_id": thread_id}}
    r = g.invoke({"document_text": doc, "config_name": config}, config=cfg)
    return {"thread_id": thread_id, "chunks": len(r.get("chunks", []))}


def run_query(query: str, config: str, thread_id: str) -> dict:
    if USE_API:
        return httpx.post(f"{API}/query",
                          json={"query": query, "config_name": config,
                                "thread_id": thread_id}, timeout=120).json()
    g = get_graph()
    cfg = {"configurable": {"thread_id": thread_id}}
    g.invoke({"query": query, "config_name": config}, config=cfg)
    st_state = g.get_state(cfg)
    if st_state.next:
        intr = {}
        if st_state.tasks and st_state.tasks[0].interrupts:
            intr = st_state.tasks[0].interrupts[0].value
        return {"status": "awaiting_human", "thread_id": thread_id, "interrupt": intr}
    r = st_state.values
    return {"status": "done", "thread_id": thread_id,
            "answer": r.get("answer"), "score": r.get("score"),
            "extracted": r.get("extracted"), "review_ok": r.get("review_ok"),
            "review_attempts": r.get("review_attempts"),
            "confidence": r.get("confidence"),
            "token_cost": r.get("token_cost"), "cost_usd": r.get("cost_usd")}


def run_resume(thread_id: str, action: str) -> dict:
    if USE_API:
        return httpx.post(f"{API}/resume",
                          json={"thread_id": thread_id, "action": action},
                          timeout=120).json()
    from langgraph.types import Command
    g = get_graph()
    cfg = {"configurable": {"thread_id": thread_id}}
    g.invoke(Command(resume={"action": action}), config=cfg)
    r = g.get_state(cfg).values
    return {"status": "done", "answer": r.get("answer"),
            "review_ok": r.get("review_ok"),
            "review_attempts": r.get("review_attempts"),
            "confidence": r.get("confidence"),
            "token_cost": r.get("token_cost"), "cost_usd": r.get("cost_usd")}


def uuid4() -> str:
    import uuid
    return uuid.uuid4().hex[:8]


config = st.sidebar.selectbox("Бизнес-конфиг", CONFIGS)
st.sidebar.info(f"Режим домена: {'автоматический' if config == 'realestate' else 'с подтверждением'}")

col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("📄 Документ")
    uploaded = st.file_uploader("Прикрепи файл (.txt / .md / .pdf / .docx)",
                                type=["txt", "md", "pdf", "docx"])
    if uploaded:
        doc = extract_text(uploaded)
        st.text_area("Содержимое файла", doc, height=200, disabled=True)
    else:
        doc = st.text_area("Или вставь текст", height=200,
                           value=("Setl Group открыла продажи ЖК 'Южно-Приморский'. "
                                  "Пресейл, цены от 5,2 млн руб, эскроу в Сбербанке, "
                                  "метро Южная, сдача 4 кв 2027."))

with col2:
    st.subheader("❓ Вопрос")
    query = st.text_input("Вопрос по документу",
                          value="Чем интересен объект? Какие риски?")

if st.button("🚀 Получить ответ", type="primary"):
    if not doc.strip() or not query.strip():
        st.error("Заполни документ и вопрос")
    else:
        with st.spinner("Загрузка → поиск → генерация ответа..."):
            ing = run_ingest(doc, config)
            q = run_query(query, config, ing["thread_id"])
        st.session_state.result = q

if "result" in st.session_state:
    r = st.session_state.result

    if r.get("status") == "awaiting_human":
        st.warning("⚠️ Чувствительный домен: нужно подтверждение человека")
        intr = r.get("interrupt", {})
        st.markdown(f"**Предпросмотр ответа:**\n\n{intr.get('answer_preview', '')}")
        st.caption(f"Score: {intr.get('score')} | Signals: {intr.get('signals')}")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ Подтвердить"):
                st.session_state.result = run_resume(r["thread_id"], "approve")
                st.rerun()
        with c2:
            if st.button("❌ Отклонить"):
                st.session_state.result = run_resume(r["thread_id"], "reject")
                st.rerun()
    else:
        st.subheader("📊 Ответ")
        answer = r.get("answer") or "—"
        if "заблокирован DLP" in answer:
            st.warning(answer)
        else:
            st.markdown(answer)
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Score", r.get("score"))
        m2.metric("Tokens", r.get("token_cost"))
        m3.metric("Cost", f"${(r.get('cost_usd') or 0):.6f}")
        m4.metric("Confidence", f"{(r.get('confidence') or 0):.0f}%")
        with st.expander("Детали (trace, сигналы, review)"):
            st.json({k: r.get(k) for k in
                     ["trace_id", "extracted", "review_ok", "review_attempts"]})