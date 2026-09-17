import logging
import os
from pathlib import Path

os.environ["ANONYMIZED_TELEMETRY"] = "False"

import chromadb
from chromadb.config import Settings

logging.getLogger("chromadb.telemetry").setLevel(logging.CRITICAL)

from src.config import CHROMA_DIR, COLLECTION_NAME, DEFAULT_TOP_K


def _get_collection() -> chromadb.Collection:
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(
        path=str(CHROMA_DIR),
        settings=Settings(anonymized_telemetry=False),
    )
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def _batch(paths, texts, embeddings, collection, method):
    collection.__getattribute__(method)(
        ids=[str(p) for p in paths],
        documents=texts,
        embeddings=embeddings,
        metadatas=[
            {
                "filename": p.name,
                "path": str(p),
                "char_count": len(t),
                "modified": p.stat().st_mtime,
            }
            for p, t in zip(paths, texts)
        ],
    )


def add(paths: list[Path], texts: list[str], embeddings: list[list[float]]) -> None:
    collection = _get_collection()
    _batch(paths, texts, embeddings, collection, "add")


def upsert(paths: list[Path], texts: list[str], embeddings: list[list[float]]) -> None:
    """Delete existing entries then re-add so embeddings actually update."""
    collection = _get_collection()
    ids = [str(p) for p in paths]
    existing = collection.get(ids=ids)["ids"]
    if existing:
        collection.delete(ids=existing)
    _batch(paths, texts, embeddings, collection, "add")


def query(embedding: list[float], top_k: int = DEFAULT_TOP_K) -> list[dict]:
    collection = _get_collection()
    results = collection.query(
        query_embeddings=[embedding],
        n_results=min(top_k, collection.count() or 1),
        include=["documents", "metadatas", "distances"],
    )
    hits = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        hits.append({"text": doc, "score": max(0.0, 1 - dist), **meta})
    return hits


def count() -> int:
    return _get_collection().count()


def already_indexed(path: Path) -> bool:
    collection = _get_collection()
    result = collection.get(ids=[str(path)])
    return len(result["ids"]) > 0
