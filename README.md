# Multi-Agent RAG Platform

![License](https://img.shields.io/github/license/SergIS777/multi-agent-rag) ![Release](https://img.shields.io/github/v/release/SergIS777/multi-agent-rag) ![Tests](https://github.com/SergIS777/multi-agent-rag/actions/workflows/tests.yml/badge.svg)

![cover](docs/cover.png)

Платформа анализа документов на LangGraph: загрузил документ → задал вопрос →
получил проверенный ответ с цитатами, скорингом и стоимостью.
Бизнес-логика — в YAML-конфигах, код не меняется. Новый домен — 1 день.

## ДАШБОРД

https://multi-agent-rag777.streamlit.app/

![Живой прогон: документ → ответ с цитатами, cost и confidence](docs/demo-answer.png)

## Возможности
- 🤖 9 агентов с анти-галлюцинациями (Reviewer-цикл ≤ 2)
- 🏢 4 домена из коробки + новый за 1 день без кода
- 🛡️ DLP до LLM: блокирует ПИИ до отправки в модель
- 💰 Cost control: лимит токенов, стоимость в $ за запрос
- 🔭 Наблюдаемость: trace_id + JSON-лог цепочки

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
