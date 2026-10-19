
import re


def normalize_text(text: str) -> str:
    """Normalize text for simple, case-insensitive phrase matching."""
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    return " ".join(text.split())


def evaluate_answer(
    answer: str,
    required_keywords: list[str],
) -> dict:
    """
    Evaluate whether an answer contains the required phrases.

    This is a simple baseline metric, not a guarantee of factual correctness.
    """
    normalized_answer = normalize_text(answer)

    normalized_keywords = [
        normalize_text(keyword)
        for keyword in required_keywords
        if normalize_text(keyword)
    ]

    matched_keywords = [
        keyword
        for keyword in normalized_keywords
        if keyword in normalized_answer
    ]

    missing_keywords = [
        keyword
        for keyword in normalized_keywords
        if keyword not in normalized_answer
    ]

    total = len(normalized_keywords)
    score = len(matched_keywords) / total if total else 0.0

    return {
        "score": score,
        "passed": total > 0 and len(missing_keywords) == 0,
        "matched_keywords": matched_keywords,
        "missing_keywords": missing_keywords,
    }
