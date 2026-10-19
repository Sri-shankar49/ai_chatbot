
from services.answer_quality_service import evaluate_answer


def test_correct_answer_passes():
    result = evaluate_answer(
        "Employees receive 20 days of annual leave per year.",
        ["20 days", "annual leave"],
    )

    assert result["passed"] is True
    assert result["score"] == 1.0
    assert result["missing_keywords"] == []


def test_different_wording_passes():
    result = evaluate_answer(
        "Staff get 20 days of annual leave each year.",
        ["20 days", "annual leave"],
    )

    assert result["passed"] is True
    assert result["score"] == 1.0


def test_incomplete_answer_fails():
    result = evaluate_answer(
        "Employees receive annual leave each year.",
        ["20 days", "annual leave"],
    )

    assert result["passed"] is False
    assert result["score"] == 0.5
    assert result["missing_keywords"] == ["20 days"]


def test_wrong_number_fails():
    result = evaluate_answer(
        "Employees receive 30 days of annual leave per year.",
        ["20 days", "annual leave"],
    )

    assert result["passed"] is False
    assert result["score"] == 0.5
    assert result["missing_keywords"] == ["20 days"]


def test_keyword_matching_is_case_insensitive():
    result = evaluate_answer(
        "EMPLOYEES RECEIVE 20 DAYS OF ANNUAL LEAVE.",
        ["20 days", "annual leave"],
    )

    assert result["passed"] is True


def test_empty_keyword_list_does_not_pass():
    result = evaluate_answer(
        "Any answer",
        [],
    )

    assert result["passed"] is False
    assert result["score"] == 0.0
