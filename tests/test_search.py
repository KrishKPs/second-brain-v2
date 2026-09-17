import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from src import store
from src.config import CHROMA_DIR


@pytest.fixture(autouse=True)
def isolated_chroma(tmp_path, monkeypatch):
    """Point ChromaDB at a temp dir so tests don't touch the real DB."""
    chroma_tmp = tmp_path / "chroma"
    monkeypatch.setattr("src.store.CHROMA_DIR", chroma_tmp)
    monkeypatch.setattr("src.config.CHROMA_DIR", chroma_tmp)
    yield
    if chroma_tmp.exists():
        shutil.rmtree(chroma_tmp)


def _fake_path(name: str, tmp_path: Path) -> Path:
    p = tmp_path / name
    p.write_text("placeholder")
    return p


def test_count_empty():
    assert store.count() == 0


def test_add_and_count(tmp_path):
    from src.embedder import embed
    paths = [_fake_path("a.png", tmp_path)]
    texts = ["socket connection refused error"]
    embeddings = [embed(texts[0])]
    store.add(paths, texts, embeddings)
    assert store.count() == 1


def test_already_indexed(tmp_path):
    from src.embedder import embed
    p = _fake_path("b.png", tmp_path)
    text = "pricing page with orange button"
    store.add([p], [text], [embed(text)])
    assert store.already_indexed(p)
    assert not store.already_indexed(tmp_path / "nonexistent.png")


def test_query_returns_results(tmp_path):
    from src.embedder import embed
    p = _fake_path("c.png", tmp_path)
    text = "fatal error: null pointer dereference"
    emb = embed(text)
    store.add([p], [text], [emb])

    hits = store.query(embed("null pointer error"), top_k=1)
    assert len(hits) == 1
    assert hits[0]["filename"] == "c.png"
    assert 0 <= hits[0]["score"] <= 1
