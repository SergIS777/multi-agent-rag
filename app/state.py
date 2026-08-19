from typing import TypedDict


class PlatformState(TypedDict, total=False):
    """Общая память графа: каждый агент читает и дописывает свои поля."""

    # --- входы ---
    document_text: str
    query: str
    config_name: str

    # --- Guard (DLP) ---
    pii_blocked: bool
    trace_id: str

    # --- Ingestor / Indexer ---
    chunks: list

    # --- Retriever / Extractor ---
    retrieved: list
    extracted: dict
    score: int

    # --- Answerer / Summarizer ---
    answer: str
    citations: list
    token_cost: int
    cost_usd: float
    cost_blocked: bool

    # --- Reviewer ---
    review_ok: bool
    review_attempts: int
    confidence: float