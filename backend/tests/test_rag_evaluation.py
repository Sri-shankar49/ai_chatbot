import pytest

from src.services.rag_service import filter_relevant_matches


@pytest.fixture
def sample_matches():
    return [
        {
            "id": "chunk-1",
            "text": "Annual leave allowance is 20 days.",
            "distance": 0.12,
        },
        {
            "id": "chunk-2",
            "text": "The office is located in Chennai.",
            "distance": 0.28,
        },
        {
            "id": "chunk-3",
            "text": "Unrelated product information.",
            "distance": 0.72,
        },
        {
            "id": "chunk-4",
            "text": "Missing distance metadata.",
            "distance": None,
        },
    ]


def test_keeps_relevant_matches(sample_matches):
    results = filter_relevant_matches(
        sample_matches,
        max_distance=0.35,
    )

    assert [item["id"] for item in results] == [
        "chunk-1",
        "chunk-2",
    ]


def test_rejects_irrelevant_matches(sample_matches):
    results = filter_relevant_matches(
        sample_matches,
        max_distance=0.35,
    )

    assert all(item["distance"] <= 0.35 for item in results)


def test_returns_empty_when_all_matches_are_irrelevant():
    matches = [
        {"id": "chunk-1", "distance": 0.80},
        {"id": "chunk-2", "distance": 0.95},
    ]

    assert filter_relevant_matches(
        matches,
        max_distance=0.35,
    ) == []


def test_accepts_match_exactly_at_threshold():
    matches = [
        {"id": "chunk-1", "distance": 0.35},
    ]

    assert len(
        filter_relevant_matches(matches, max_distance=0.35)
    ) == 1


def test_rejects_missing_distance():
    matches = [
        {"id": "chunk-1", "text": "Example"},
        {"id": "chunk-2", "distance": None},
    ]

    assert filter_relevant_matches(
        matches,
        max_distance=0.35,
    ) == []