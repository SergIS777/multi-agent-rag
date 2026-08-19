from typing import TypedDict

class PlatformState(TypedDict, total=False):
    # вход
    document_text: str        # сырой текст документа
    query: str                # вопрос пользователя
    config_name: str          # какой бизнес-конфиг
    # обработка
    chunks: list              # чанки документа
    retrieved: list           # релевантные чанки
    extracted: dict           # извлечённые сущности/сигналы
    score: int                # скоринг 0-100 (недвижимость)
    answer: str               # ответ
    citations: list           # цитаты (chunk_id)
    confidence: float         # уверенность 0-100
    review_ok: bool           # Reviewer пропустил
    review_attempts: int      # попытки ревью
    pii_blocked: bool         # DLP заблокировал запрос
    # наблюдаемость
    trace_id: str
    token_cost: int           # суммарные токены