from pathlib import Path

from tqdm import tqdm

from src import embedder, ocr, store
from src.config import DEFAULT_TOP_K, MIN_CONFIDENCE, SCORE_GAP_RATIO


class SecondBrain:
    def index(self, folder_path: str | Path, skip_existing: bool = True) -> dict:
        paths = ocr.scan_folder(Path(folder_path))
        new, skipped, failed = [], 0, 0

        for p in paths:
            if skip_existing and store.already_indexed(p):
                skipped += 1
                continue
            new.append(p)

        if not new:
            return {"indexed": 0, "skipped": skipped, "failed": failed}

        texts, valid_paths = [], []
        for p in tqdm(new, desc="OCR", unit="file"):
            text = ocr.extract_text(p)
            if ocr.is_indexable(text):
                texts.append(text)
                valid_paths.append(p)
            else:
                failed += 1

        if valid_paths:
            # BGE handles long noisy text well — embed full cleaned OCR.
            # Only strip lines that are pure noise (< 30% real letters).
            def _embed_text(p: Path, t: str) -> str:
                name = p.stem.replace("_", " ").replace("-", " ")
                clean = " ".join(
                    l.strip() for l in t.splitlines()
                    if len(l.strip()) >= 3
                    and sum(c.isalpha() for c in l.strip()) / len(l.strip()) > 0.3
                )
                return f"{name}\n{clean[:600]}"

            embed_inputs = [_embed_text(p, t) for p, t in zip(valid_paths, texts)]
            embeddings = embedder.embed_batch(embed_inputs)
            store.upsert(valid_paths, texts, embeddings)

        return {"indexed": len(valid_paths), "skipped": skipped, "failed": failed}

    def search(self, query: str, top_k: int = DEFAULT_TOP_K) -> list[dict]:
        if store.count() == 0:
            return []
        embedding = embedder.embed(query)
        candidate_k = min(store.count(), max(30, top_k * 15))
        hits = store.query(embedding, top_k=candidate_k)
        reranked = self._rerank(query, hits)
        if not reranked:
            return []
        # Adaptive threshold: whichever is higher wins.
        # If the best match scores 0.65, results below 0.585 are cut even if they
        # clear the 50% floor — this is what stops n8n from sneaking in on
        # every query just because it has dense, varied OCR text.
        threshold = max(MIN_CONFIDENCE, reranked[0]["score"] * SCORE_GAP_RATIO)
        return [h for h in reranked if h["score"] >= threshold][:top_k]

    def _rerank(self, query: str, hits: list[dict]) -> list[dict]:
        query_words = {w for w in query.lower().split() if len(w) > 2}
        for hit in hits:
            stem = hit["filename"].lower().replace("_", " ").replace("-", " ")
            file_words = set(stem.split())
            overlap = query_words & file_words
            if overlap:
                # Small nudge only — semantic score stays dominant
                hit["score"] *= 1 + 0.1 * len(overlap)
        return sorted(hits, key=lambda h: h["score"], reverse=True)
