import streamlit as st
from app.graph import build_graph
import time

st.set_page_config(page_title="Multi-Agent RAG Platform", layout="wide")
st.title("🏗️ Multi-Agent RAG Platform")
st.caption("LangGraph + 4 бизнес-конфига: юристы, логистика, медицина, недвижимость")

config_name = st.sidebar.selectbox("Бизнес-конфиг", 
    ["realestate", "law", "logistics", "medicine"])

doc_text = st.text_area("Документ (текст)", height=200,
    value="Setl Group открыла продажи ЖК Южно-Приморский. Старт продаж, эскроу, метро Южная.")

query = st.text_input("Вопрос", "Чем интересен объект? Какие риски?")

if st.button("Запустить граф"):
    graph = build_graph()
    cfg = {"configurable": {"thread_id": f"demo_{config_name}"}}
    
    t0 = time.time()
    result = graph.invoke(
        {"document_text": doc_text, "query": query, "config_name": config_name},
        config=cfg
    )
    elapsed = time.time() - t0
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Score", result.get("score", 0))
    col2.metric("Tokens", result.get("token_cost", 0))
    col3.metric("Time", f"{elapsed:.1f}s")
    
    st.subheader("Ответ")
    st.write(result.get("answer", ""))
    
    with st.expander("Технические детали"):
        st.json({
            "trace_id": result.get("trace_id"),
            "extracted_signals": result.get("extracted"),
            "review_ok": result.get("review_ok"),
            "confidence": result.get("confidence"),
            "chunks": len(result.get("chunks", []))
        })