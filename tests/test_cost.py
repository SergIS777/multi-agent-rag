import pytest
from app.agents import answerer


def test_cost_limit_blocks():
    """Если токенов уже больше лимита — честный отказ."""
    state = {
        "config_name": "cost_test",
        "retrieved": ["текст"],
        "token_cost": 5000,  # лимит 100
    }
    result = answerer(state)
    assert result["cost_blocked"] is True
    assert "[COST]" in result["answer"]
    assert "Превышен лимит" in result["answer"]


def test_cost_returns_usd():
    """Если в лимите — возвращает стоимость в $."""
    state = {
        "config_name": "realestate",
        "retrieved": ["текст документа"],
        "token_cost": 0,
        "query": "вопрос",
    }
    # Мокаем LLM чтобы не делать реальный запрос
    # (в реальном тесте нужен monkeypatch на call_llm)
    # Пока пропускаем этот тест, если нет mock
    pytest.skip("Требует mock для call_llm")