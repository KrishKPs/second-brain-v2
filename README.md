# Second Brain: Semantic Screenshot Search

Search your screenshots by meaning. Type `"that socket error message"` or `"the pricing page with the orange button"` and get the exact screenshot back, instead of digging through `Screenshot 2024-03-15 at 2.43.11 PM.png`.

**Fully local and offline.** No API keys, no cloud, no per-query cost. Your screenshots never leave your machine.

## Pipeline

```
Screenshot → OCR → Embed → Store → Search
```

1. **OCR:** Tesseract extracts text from the image
2. **Embed:** `all-MiniLM-L6-v2` turns the text into a 384-dimension vector
3. **Store:** ChromaDB (HNSW index) persists vectors and metadata locally
4. **Search:** the query is embedded the same way and matched by cosine similarity

A `watchdog` watcher indexes new screenshots automatically as they appear.

## Run it

Requires [Tesseract](https://github.com/tesseract-ocr/tesseract) (`brew install tesseract`).

```bash
pip install -r requirements.txt

# CLI
python cli.py index ~/Screenshots/
python cli.py search "that socket error message"

# Web UI + API on http://localhost:8000
uvicorn api.main:app --reload

# Auto-index a folder as screenshots are added
python watcher.py ~/Screenshots/
```

Data is stored in `~/.second_brain` (override with `SECOND_BRAIN_DATA`, see `.env.example`).

### Docker

```bash
SCREENSHOTS_FOLDER=~/Screenshots docker compose up --build
```

This runs the API and the folder watcher together, mounting your folder read-only.

## API

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/index` | Index a folder |
| `POST` | `/search` | Semantic search |
| `GET` | `/image` | Serve a matched screenshot |
| `GET` | `/health` | Health check |

## Tests

```bash
python -m pytest tests/
```

## Stack

Python · Tesseract · sentence-transformers · ChromaDB · FastAPI · watchdog · Docker
