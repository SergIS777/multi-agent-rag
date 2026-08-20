import pytest
from app.agents import guard


def test_guard_blocks_phone():
    """Реальный телефон +7 блокируется."""
    state = {"query": "звони +7 999 123-45-67", "document_text": ""}
    result = guard(state)
    assert result["pii_blocked"] is True
    assert "DLP" in result["answer"]


def test_guard_blocks_phone_8():
    """Телефон с 8 тоже блокируется."""
    state = {"query": "номер 8(495)1234567", "document_text": ""}
    result = guard(state)
    assert result["pii_blocked"] is True


def test_guard_allows_blueprints():
    """Чертёжные размеры НЕ блокируются (false positive фикс)."""
    state = {"query": "", "document_text": "размеры 1530 3020 2570 710 3120, цены 3,48 15,53"}
    result = guard(state)
    assert result["pii_blocked"] is False
    assert "trace_id" in result


def test_guard_allows_clean_text():
    """Чистый текст проходит."""
    state = {"query": "какие риски?", "document_text": "проектная декларация, эскроу"}
    result = guard(state)
    assert result["pii_blocked"] is False