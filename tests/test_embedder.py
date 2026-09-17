from src.embedder import embed, embed_batch
from src.config import EMBEDDING_DIM


def test_embed_returns_correct_dim():
    vec = embed("hello world")
    assert len(vec) == EMBEDDING_DIM


def test_embed_is_normalized():
    import math
    vec = embed("some text for testing normalization")
    magnitude = math.sqrt(sum(x ** 2 for x in vec))
    assert abs(magnitude - 1.0) < 1e-5


def test_embed_batch_length():
    texts = ["first sentence", "second sentence", "third sentence"]
    vecs = embed_batch(texts)
    assert len(vecs) == len(texts)
    assert all(len(v) == EMBEDDING_DIM for v in vecs)


def test_similar_texts_closer_than_unrelated():
    import math

    def cosine(a, b):
        dot = sum(x * y for x, y in zip(a, b))
        mag_a = math.sqrt(sum(x ** 2 for x in a))
        mag_b = math.sqrt(sum(x ** 2 for x in b))
        return dot / (mag_a * mag_b)

    v1 = embed("connection refused socket error")
    v2 = embed("socket connection failed")
    v3 = embed("banana smoothie recipe")

    assert cosine(v1, v2) > cosine(v1, v3)
