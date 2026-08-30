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
- 📄 Ввод: txt / md / pdf (включая сканы через OCR) / docx
- 🤖 9 агентов-нод: Guard (DLP), Ingestor, Indexer, Retriever, Extractor,
  Answerer, Summarizer, Reviewer, Human-in-the-loop
- 🏢 4 конфига: realestate (автомат), law / logistics / medicine (подтверждение человеком)
- 🛡️ Анти-галлюцинации: Reviewer-цикл (≤ 2), честный fallback
- 💰 Cost control: лимит токенов на запрос, стоимость в $
- 🔭 Наблюдаемость: trace_id + JSON-лог цепочки (нода → latency → токены)
- 🔁 Надёжность: RetryPolicy (3 попытки, backoff), SqliteSaver

## Как работает (расшифровка схемы)

| Нода на картинке | Что делает |
|---|---|
| DOCUMENT INPUT | принимает txt/md/pdf/docx; сканы → Tesseract OCR |
| GUARD DLP | блокирует ПИИ (телефоны +7/8(, email, СНИЛС, ИНН, паспорт) ДО вызова LLM |
| INDEXER | чанки 600 символов (overlap 100) → эмбеддинги fastembed → ChromaDB |
| RETRIEVER | векторный поиск top-3 релевантных чанков |
| EXTRACTOR | детерминированный скоринг из YAML: сигналы × веса, без LLM — предсказуемо и бесплатно |
| ANSWERER LLM | ответ СТРОГО по контексту с цитатами [0][1]; лимит токенов на запрос |
| REVIEWER | анти-галлюцинации: отклоняет fallback и пустые ответы, ≤ 2 доработок |
| HUMAN APPROVAL | interrupt/resume: юристы/логистика/медицина — человек подтверждает ответ кнопкой |
| ANSWER | ответ + метрики: score, tokens, cost $, confidence, trace_id |

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
docs/           decisions.md + cover.png (обложка)
tests/          pytest-юниты (guard/extractor/cost)
run_demo.py     консольное демо
smoke_api.py    живая проверка API (нужен запущенный сервер)
```

## Статус
✅ Ядро работает (realestate/law проверены живыми прогонами)
🚧 Growth points: персистентная векторная БД, Langfuse, docker/k8s — см. docs/decisions.md