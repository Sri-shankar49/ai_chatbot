
import json
from pathlib import Path


DATASET_PATH = (
    Path(__file__).parent
    / "data"
    / "rag_evaluation_dataset.json"
)


def test_evaluation_dataset_is_valid():
    assert DATASET_PATH.exists(), (
        f"Evaluation dataset not found: {DATASET_PATH}"
    )

    with DATASET_PATH.open("r", encoding="utf-8") as file:
        dataset = json.load(file)

    assert isinstance(dataset, list)
    assert len(dataset) >= 3

    required_fields = {
        "id",
        "question",
        "expected_answer",
        "relevant_keywords",
        "relevant_source",
    }

    ids = set()

    for item in dataset:
        assert required_fields.issubset(item.keys())
        assert item["id"] not in ids
        ids.add(item["id"])

        assert item["question"].strip()
        assert item["expected_answer"].strip()
        assert item["relevant_keywords"]
        assert item["relevant_source"].strip()


def test_evaluation_dataset_has_unique_ids():
    with DATASET_PATH.open("r", encoding="utf-8") as file:
        dataset = json.load(file)

    ids = [item["id"] for item in dataset]

    assert len(ids) == len(set(ids))
