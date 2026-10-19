
# import asyncio
# import json
# from pathlib import Path

# from services.embedding_service import embed_text
# from services.chroma_service import (
#     search_documents,
#     get_all_documents,
# )
# from services.rag_evaluation_service import (
#     precision_at_k,
#     recall_at_k,
# )

# BACKEND_DIR = Path(__file__).resolve().parents[1]
# DATASET_PATH = (
#     BACKEND_DIR / "tests" / "data" / "rag_evaluation_dataset.json"
# )

# K = 3


# def is_relevant(chunk: dict, item: dict) -> bool:
#     """Apply the dataset's source and keyword relevance rules."""
#     metadata = chunk.get("metadata") or {}
#     source = Path(metadata.get("source", "")).name.casefold()
#     expected_source = Path(item["relevant_source"]).name.casefold()

#     if source != expected_source:
#         return False

#     text = (chunk.get("text") or "").casefold()

#     return all(
#         keyword.casefold() in text
#         for keyword in item["relevant_keywords"]
#     )


# async def evaluate_question(item: dict, corpus: list[dict]) -> dict:
#     query_embedding = await asyncio.to_thread(
#         embed_text,
#         item["question"],
#         is_query=True,
#     )

#     retrieved = search_documents(query_embedding, limit=K)

#     retrieved_flags = [
#         is_relevant(chunk, item)
#         for chunk in retrieved
#     ]

#     # Estimate the number of relevant chunks in the full corpus.
#     relevant_corpus_chunks = [
#         chunk for chunk in corpus
#         if is_relevant(chunk, item)
#     ]

#     total_relevant = len(relevant_corpus_chunks)

#     precision = precision_at_k(retrieved_flags, K)

#     recall = (
#         recall_at_k(
#             retrieved_flags,
#             total_relevant=total_relevant,
#             k=K,
#         )
#         if total_relevant > 0
#         else None
#     )

#     return {
#         "id": item["id"],
#         "question": item["question"],
#         "retrieved_count": len(retrieved),
#         "relevant_retrieved": sum(retrieved_flags),
#         "total_relevant_estimate": total_relevant,
#         "precision_at_k": precision,
#         "recall_at_k": recall,
#     }


# async def main():
#     with DATASET_PATH.open("r", encoding="utf-8") as file:
#         dataset = json.load(file)

#     corpus = get_all_documents()

#     if not corpus:
#         print("ChromaDB contains no documents to evaluate.")
#         print("Upload the evaluation document and try again.")
#         return

#     print(f"Corpus chunks: {len(corpus)}")
#     print(f"Evaluating {len(dataset)} questions with K={K}\n")

#     results = []

#     for item in dataset:
#         result = await evaluate_question(item, corpus)
#         results.append(result)

#         print(f"Question: {result['question']}")
#         print(
#             f"Relevant retrieved: "
#             f"{result['relevant_retrieved']}/"
#             f"{result['retrieved_count']}"
#         )
#         print(f"Estimated relevant corpus chunks: "
#               f"{result['total_relevant_estimate']}")
#         print(f"Precision@{K}: {result['precision_at_k']:.3f}")

#         recall = result["recall_at_k"]
#         print(
#             f"Recall@{K}: "
#             f"{recall:.3f}" if recall is not None
#             else f"Recall@{K}: N/A (no relevant chunks identified)"
#         )
#         print("-" * 50)

#     # Macro averages: each question receives equal weight.
#     precision_avg = sum(
#         result["precision_at_k"] for result in results
#     ) / len(results)

#     valid_recalls = [
#         result["recall_at_k"]
#         for result in results
#         if result["recall_at_k"] is not None
#     ]

#     print("\nOVERALL RESULTS")
#     print(f"Mean Precision@{K}: {precision_avg:.3f}")

#     if valid_recalls:
#         recall_avg = sum(valid_recalls) / len(valid_recalls)
#         print(f"Mean Recall@{K}: {recall_avg:.3f}")
#     else:
#         print("Mean Recall: N/A")


# if __name__ == "__main__":
#     asyncio.run(main())




import asyncio
import json
import time
from pathlib import Path

from services.embedding_service import embed_text
from services.chroma_service import search_documents
from services.rag_evaluation_service import (
    precision_at_k,
    recall_at_k,
)

BACKEND_DIR = Path(__file__).resolve().parents[1]
DATASET_PATH = (
    BACKEND_DIR / "tests" / "data" / "rag_evaluation_dataset.json"
)

K_VALUES = (3, 5)


async def evaluate_question(item: dict) -> list[dict]:
    # Embed once per question so both K values use the same query vector.
    query_embedding = await asyncio.to_thread(
        embed_text,
        item["question"],
        is_query=True,
    )

    relevant_ids = set(item["relevant_chunk_ids"])
    question_results = []

    for k in K_VALUES:
        started = time.perf_counter()

        retrieved = search_documents(
            query_embedding,
            limit=k,
        )

        elapsed_ms = (time.perf_counter() - started) * 1000

        retrieved_flags = [
            chunk.get("id") in relevant_ids
            for chunk in retrieved
        ]

        precision = (
            precision_at_k(retrieved_flags, len(retrieved))
            if retrieved
            else 0.0
        )

        recall = recall_at_k(
            retrieved_flags,
            total_relevant=len(relevant_ids),
            k=k,
        )

        question_results.append(
            {
                "id": item["id"],
                "question": item["question"],
                "k": k,
                "returned": len(retrieved),
                "relevant_retrieved": sum(retrieved_flags),
                "precision": precision,
                "recall": recall,
                "latency_ms": elapsed_ms,
            }
        )

    return question_results


async def main():
    with DATASET_PATH.open("r", encoding="utf-8") as file:
        dataset = json.load(file)

    if not dataset:
        print("Evaluation dataset is empty.")
        return

    all_results = []

    print(f"Evaluation questions: {len(dataset)}")
    print(f"Comparing K values: {K_VALUES}\n")

    for item in dataset:
        results = await evaluate_question(item)
        all_results.extend(results)

        print(f"Question: {item['question']}")

        for result in results:
            print(
                f"  K={result['k']}: "
                f"retrieved={result['returned']}, "
                f"relevant={result['relevant_retrieved']}, "
                f"Precision={result['precision']:.3f}, "
                f"Recall={result['recall']:.3f}, "
                f"Search={result['latency_ms']:.2f} ms"
            )

        print("-" * 65)

    print("\nOVERALL RESULTS")

    for k in K_VALUES:
        results_for_k = [
            result for result in all_results
            if result["k"] == k
        ]

        count = len(results_for_k)

        mean_precision = sum(
            result["precision"] for result in results_for_k
        ) / count

        mean_recall = sum(
            result["recall"] for result in results_for_k
        ) / count

        mean_latency = sum(
            result["latency_ms"] for result in results_for_k
        ) / count

        print(
            f"K={k}: "
            f"Mean Precision@{k}={mean_precision:.3f}, "
            f"Mean Recall@{k}={mean_recall:.3f}, "
            f"Mean search latency={mean_latency:.2f} ms"
        )


if __name__ == "__main__":
    asyncio.run(main())

