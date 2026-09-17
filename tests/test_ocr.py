import os
import tempfile
from pathlib import Path

import pytest
from PIL import Image, ImageDraw, ImageFont

from src.ocr import extract_text, is_indexable, scan_folder
from src.config import MIN_TEXT_LENGTH


def _make_image_with_text(text: str, path: Path) -> None:
    img = Image.new("RGB", (400, 100), color="white")
    draw = ImageDraw.Draw(img)
    draw.text((10, 10), text, fill="black")
    img.save(path)


def test_scan_folder_finds_images(tmp_path):
    (tmp_path / "a.png").touch()
    (tmp_path / "b.jpg").touch()
    (tmp_path / "c.txt").touch()
    found = scan_folder(tmp_path)
    names = {p.name for p in found}
    assert "a.png" in names
    assert "b.jpg" in names
    assert "c.txt" not in names


def test_scan_folder_not_a_directory():
    with pytest.raises(NotADirectoryError):
        scan_folder(Path("/nonexistent/path"))


def test_extract_text_returns_string(tmp_path):
    img_path = tmp_path / "test.png"
    _make_image_with_text("Hello World", img_path)
    result = extract_text(img_path)
    assert isinstance(result, str)


def test_extract_text_bad_file_returns_empty(tmp_path):
    bad = tmp_path / "bad.png"
    bad.write_bytes(b"not an image")
    result = extract_text(bad)
    assert result == ""


def test_is_indexable():
    assert is_indexable("x" * MIN_TEXT_LENGTH)
    assert not is_indexable("x" * (MIN_TEXT_LENGTH - 1))
    assert not is_indexable("")
