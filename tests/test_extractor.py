import pytest
from app.agents import extractor


def test_extractor_real_estate_signals():
    """Недвижимость: находит сигналы и считает скоринг."""
    state = {
        "config_name": "realestate",
        "retrieved": [
            "старт продаж, пресейл, эскроу в Сбербанке",
            "метро Южная в пешей доступности",
        ],
    }
    result = extractor(state)
    assert "positive" in result["extracted"]
    assert "risk" in result["extracted"]
    assert len(result["extracted"]["positive"]) >= 2  # старт продаж, пресейл, эскроу
    assert 0 <= result["score"] <= 100


def test_extractor_no_signals():
    """Если сигналов нет — score 0."""
    state = {"config_name": "realestate", "retrieved": ["просто текст без сигналов"]}
    result = extractor(state)
    assert result["score"] == 0
    assert len(result["extracted"]["positive"]) == 0


def test_extractor_law_signals():
    """Юристы: находит штрафы/неустойки."""
    state = {
        "config_name": "law",
        "retrieved": ["штраф за нарушение 0.1%, неустойка за просрочку оплаты"],
    }
    result = extractor(state)
    assert "штраф" in result["extracted"]["risk"] or "неустойка" in result["extracted"]["positive"]