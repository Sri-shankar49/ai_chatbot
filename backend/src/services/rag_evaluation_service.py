
def precision_at_k(relevant_flags: list[bool], k: int) -> float:
    """
    Calculate Precision@K.

    relevant_flags contains one boolean per retrieved chunk,
    ordered from most relevant-ranked to least relevant-ranked.
    """
    if k <= 0:
        raise ValueError("k must be greater than zero")

    top_k = relevant_flags[:k]
    relevant_count = sum(top_k)

    # Precision@K uses K as the denominator.
    return relevant_count / k


def recall_at_k(
    relevant_flags: list[bool],
    total_relevant: int,
    k: int,
) -> float:
    """
    Calculate Recall@K.

    total_relevant is the total number of known relevant chunks
    for this question in the evaluation dataset.
    """
    if k <= 0:
        raise ValueError("k must be greater than zero")

    if total_relevant <= 0:
        raise ValueError("total_relevant must be greater than zero")

    top_k = relevant_flags[:k]
    relevant_retrieved = sum(top_k)

    return relevant_retrieved / total_relevant
