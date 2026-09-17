import os
from pathlib import Path

# Storage
DATA_DIR = Path(os.getenv("SECOND_BRAIN_DATA", "~/.second_brain")).expanduser()
CHROMA_DIR = DATA_DIR / "chroma"

# Embedding model
EMBEDDING_MODEL = "BAAI/bge-base-en-v1.5"
EMBEDDING_DIM = 768

# ChromaDB
COLLECTION_NAME = "screenshots"

# Search
DEFAULT_TOP_K = 3
MIN_CONFIDENCE = 0.50   # absolute floor — never show below 50%
SCORE_GAP_RATIO = 0.90  # relative floor — result must be ≥90% of the top score
MIN_TEXT_LENGTH = 10

# OCR
TESSERACT_CONFIG = "--psm 3"
SUPPORTED_EXTENSIONS = frozenset({
    ".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".tif", ".webp"
})

# API
API_HOST = "0.0.0.0"
API_PORT = 8000


