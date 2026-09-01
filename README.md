<div align="center">

# Multi-Agent RAG Platform

</div>

---

![License](https://img.shields.io/github/license/SergIS777/multi-agent-rag) ![Release](https://img.shields.io/github/v/release/SergIS777/multi-agent-rag) ![Tests](https://github.com/SergIS777/multi-agent-rag/actions/workflows/tests.yml/badge.svg)

---

![cover](docs/cover.png)

Платформа анализа документов на LangGraph: загрузил документ → задал вопрос →
получил проверенный ответ с цитатами, скорингом и стоимостью.
Бизнес-логика — в YAML-конфигах, код не меняется. Новый домен — 1 день.

---

## ДАШБОРД

https://multi-agent-rag777.streamlit.app/

![Живой прогон: документ → ответ с цитатами, cost и confidence](docs/demo-answer.png)

---

## Архитектура

## 📚 **Полная архитектурная документация** (arc42 + C4): [ARCHITECTURE.md](ARCHITECTURE.md)

---

## Возможности
- 🤖 9 агентов с анти-галлюцинациями (Reviewer-цикл ≤ 2)
- 🏢 4 домена из коробки + новый за 1 день без кода
- 🛡️ DLP до LLM: блокирует ПИИ до отправки в модель
- 💰 Cost control: лимит токенов, стоимость в $ за запрос
- 🔭 Наблюдаемость: trace_id + JSON-лог цепочки

---

## Быстрый старт

Установка:
```powershell
pip install langgraph langgraph-checkpoint-sqlite langchain-core fastembed chromadb httpx pyyaml fastapi uvicorn streamlit pypdf python-docx pytesseract PyMuPDF Pillow
```

Переменные окружения — **PowerShell (Windows)**:
```powershell
$env:GROQ_API_KEY="gsk_..."
$env:LOCAL_PROXY="http://user:pass@127.0.0.1:3067"   # только если нужен прокси
```

Переменные окружения — **bash (Linux/Mac)**:
```bash
export GROQ_API_KEY="gsk_..."
export LOCAL_PROXY="http://user:pass@127.0.0.1:3067"  # только если нужен прокси
```

Запуск (два окна + демо):
```powershell
uvicorn app.api:app --port 8000     # окно 1: API
streamlit run app/streamlit_app.py  # окно 2: витрина
python run_demo.py                  # или консольное демо
```
---

## ❓ Ответы на частые вопросы по проекту

Почему LangGraph, а не LangChain? Как работает анти-галлюцинации? Зачем DLP до LLM?

# → [FAQ.md](FAQ.md) — ответы на частые вопросы от работодателей и технических специалистов

---

## Лицензия
MIT

---

## Стек
- **AI/LLM:** LangGraph · LangChain · fastembed (эмбеддинги)
- **Векторная БД:** ChromaDB
- **Документы:** PyPDF · python-docx · PyMuPDF · Tesseract OCR · Pillow
- **API:** FastAPI · Uvicorn · httpx
- **UI:** Streamlit
- **Конфиги:** PyYAML
- **Тесты:** pytest (guard/extractor/cost)

## Автор: **Сергей Исаков** 

## Резюме на hh.ru  https://spb.hh.ru/resume/cabaf8c9ff07eccd210039ed1f4b75515a6f56

## Связаться с автором проекта sergeyhigh@gmail.com

## Другие проекты автора: 
- **https://github.com/SergIS777/ml-loop**
- **https://github.com/SergIS777/voicebot**
- **https://github.com/SergIS777/voicebot-analytics**

---
