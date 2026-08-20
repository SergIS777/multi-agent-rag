# Multi-Agent RAG Platform

Платформа анализа документов на LangGraph: загрузил документ → задал вопрос →
получил проверенный ответ с цитатами, скорингом и стоимостью.
Бизнес-логика — в YAML-конфигах, код не меняется. Новый домен — 1 день.

## Возможности
- 📄 Ввод: txt / md / pdf (включая сканы через OCR) / docx
- 🤖 9 агентов-нод: Guard (DLP), Ingestor, Indexer, Retriever, Extractor,
  Answerer, Summarizer, Reviewer, Human-in-the-loop
- 🏢 4 конфига: realestate (автомат), law / logistics / medicine (подтверждение человеком)
- 🛡️ Анти-галлюцинации: Reviewer-цикл (≤ 2), честный fallback
- 💰 Cost control: лимит токенов на запрос, стоимость в $
- 🔭 Наблюдаемость: trace_id + JSON-лог цепочки (нода → latency → токены)
- 🔁 Надёжность: RetryPolicy (3 попытки, backoff), SqliteSaver

## Архитектура

```mermaid
graph TD
    START --> guard
    guard -->|ingest| ingestor --> indexer --> END
    guard -->|query| retriever --> extractor --> answerer
    guard -->|end| END
    answerer -->|human| human_review --> END
    answerer -->|reviewer| reviewer
    reviewer -->|retry| answerer
    reviewer -->|end| END
    summarizer --> reviewer
```

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

## Структура
```
app/            агенты-ноды, граф, state, llm-слой, observability, api, витрина
configs/        4 бизнес-конфига + cost_test (YAML)
docs/           decisions.md — ключевые решения и уроки
run_demo.py     консольное демо
test_*.py       проверки (law human-in-the-loop, cost, api)
```

## Статус
✅ Ядро работает (realestate/law проверены живыми прогонами)
🚧 Growth points: персистентная векторная БД, Langfuse, docker/k8s — см. docs/decisions.md