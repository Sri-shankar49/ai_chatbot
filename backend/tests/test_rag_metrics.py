
import pytest

from services.rag_evaluation_service import (
    precision_at_k,
    recall_at_k,
)


def test_precision_at_k():
    retrieved = [True, False, True, True, False]

    assert precision_at_k(retrieved, 5) == pytest.approx(0.6)


def test_recall_at_k():
    retrieved = [True, False, True, True, False]

    assert recall_at_k(
        retrieved,
        total_relevant=6,
        k=5,
    ) == pytest.approx(0.5)


def test_precision_uses_only_top_k():
    retrieved = [True, False, False, True, True]

    assert precision_at_k(retrieved, 3) == pytest.approx(1 / 3)


def test_recall_uses_only_top_k():
    retrieved = [True, False, True, True, False]

    assert recall_at_k(
        retrieved,
        total_relevant=4,
        k=2,
    ) == pytest.approx(0.25)


def test_precision_rejects_zero_k():
    with pytest.raises(ValueError):
        precision_at_k([True, False], 0)


def test_recall_rejects_zero_relevant_chunks():
    with pytest.raises(ValueError):
        recall_at_k([True, False], total_relevant=0, k=2)
