from pathlib import Path
from PIL import Image
import pytesseract

from src.config import TESSERACT_CONFIG, SUPPORTED_EXTENSIONS, MIN_TEXT_LENGTH


def extract_text(image_path: Path) -> str:
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image, config=TESSERACT_CONFIG)
        return text.strip()
    except Exception as e:
        print(f"[OCR] Failed on {image_path.name}: {e}")
        return ""


def scan_folder(folder_path: Path) -> list[Path]:
    folder = Path(folder_path).expanduser().resolve()
    if not folder.is_dir():
        raise NotADirectoryError(f"{folder} is not a directory")
    return [
        p for p in folder.rglob("*")
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS
    ]


def is_indexable(text: str) -> bool:
    return len(text) >= MIN_TEXT_LENGTH
