from sentence_transformers import SentenceTransformer

from src.config import EMBEDDING_MODEL

_model: SentenceTransformer | None = None

# BGE models are instruction-tuned for retrieval — prefix queries only, not documents
_QUERY_PREFIX = "Represent this sentence for searching relevant passages: "


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model


def embed(text: str) -> list[float]:
    model = _get_model()
    vector = model.encode(_QUERY_PREFIX + text, normalize_embeddings=True)
    return vector.tolist()


def embed_batch(texts: list[str]) -> list[list[float]]:
    model = _get_model()
    vectors = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
    return [v.tolist() for v in vectors]
