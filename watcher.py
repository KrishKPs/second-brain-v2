"""
Watches a folder for new screenshots and hits the /index endpoint automatically.

Usage:
    conda activate second
    python watcher.py                        # watches ~/Desktop/SC by default
    python watcher.py ~/Screenshots          # watch a different folder
"""

import argparse
import time
from pathlib import Path

import requests
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

from src.config import API_HOST, API_PORT, SUPPORTED_EXTENSIONS

API_BASE = f"http://{API_HOST if API_HOST != '0.0.0.0' else '127.0.0.1'}:{API_PORT}"
DEFAULT_WATCH_FOLDER = "~/Desktop/SC"


class ScreenshotHandler(FileSystemEventHandler):
    def __init__(self, folder: Path) -> None:
        self.folder = folder

    def on_created(self, event: FileSystemEvent) -> None:
        if event.is_directory:
            return
        path = Path(event.src_path)
        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            return
        print(f"[watcher] New file: {path.name}")
        self._index(path)

    def on_moved(self, event: FileSystemEvent) -> None:
        # macOS saves screenshots as a temp file then renames — catch the rename
        if event.is_directory:
            return
        path = Path(event.dest_path)
        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            return
        print(f"[watcher] New file (moved): {path.name}")
        self._index(path)

    def _index(self, path: Path) -> None:
        # Small delay so the file is fully written before OCR reads it
        time.sleep(0.5)
        try:
            resp = requests.post(
                f"{API_BASE}/index",
                json={"folder": str(self.folder)},
                timeout=120,
            )
            resp.raise_for_status()
            result = resp.json()
            print(
                f"[watcher] Indexed {result['indexed']} new, "
                f"skipped {result['skipped']}, "
                f"failed {result['failed']}"
            )
        except requests.exceptions.ConnectionError:
            print(f"[watcher] ERROR: API server not running at {API_BASE}")
            print(f"[watcher]   Start it with: uvicorn api.main:app --host 0.0.0.0 --port {API_PORT}")
        except Exception as e:
            print(f"[watcher] ERROR indexing {path.name}: {e}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Watch a folder and auto-index new screenshots")
    parser.add_argument(
        "folder",
        nargs="?",
        default=DEFAULT_WATCH_FOLDER,
        help=f"Folder to watch (default: {DEFAULT_WATCH_FOLDER})",
    )
    args = parser.parse_args()

    folder = Path(args.folder).expanduser().resolve()
    if not folder.is_dir():
        print(f"ERROR: {folder} is not a directory")
        raise SystemExit(1)

    handler = ScreenshotHandler(folder)
    observer = Observer()
    observer.schedule(handler, str(folder), recursive=False)
    observer.start()

    print(f"[watcher] Watching {folder}")
    print(f"[watcher] API server: {API_BASE}")
    print(f"[watcher] Press Ctrl+C to stop")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()
