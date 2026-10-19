
from google import genai

from config.settings import (
    GOOGLE_API_KEY,
    GEMINI_EMBEDDING_MODEL,
    EMBEDDING_DIMENSIONS,
)


def embed_text(text: str, *, is_query: bool = False) -> list[float]:
    if not GOOGLE_API_KEY:
        raise RuntimeError("GOOGLE_API_KEY is not configured.")

    text = text.strip()
    if not text:
        raise ValueError("Cannot embed empty text.")

    client = genai.Client(api_key=GOOGLE_API_KEY)

    try:
        if is_query:
            instructed_text = (
                "task: search result | query: " + text
            )
        else:
            instructed_text = (
                "task: search result | document: " + text
            )

        response = client.models.embed_content(
            model=GEMINI_EMBEDDING_MODEL,
            contents=instructed_text,
            config={
                "output_dimensionality": EMBEDDING_DIMENSIONS,
            },
        )

        if not response.embeddings:
            raise RuntimeError("Gemini returned no embeddings.")

        vector = response.embeddings[0].values

        if vector is None or len(vector) != EMBEDDING_DIMENSIONS:
            raise RuntimeError("Gemini returned an unexpected vector size.")

        return list(vector)

    finally:
        client.close()
