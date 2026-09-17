from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from src.brain import SecondBrain
from src.config import DEFAULT_TOP_K, SUPPORTED_EXTENSIONS

app = FastAPI(title="Second Brain", description="Semantic screenshot search")
brain = SecondBrain()


class IndexRequest(BaseModel):
    folder: str
    reindex: bool = False


class SearchRequest(BaseModel):
    query: str
    top_k: int = DEFAULT_TOP_K


@app.get("/")
def serve_ui():
    return FileResponse("static/index.html")


@app.get("/image")
def serve_image(path: str):
    p = Path(path).expanduser().resolve()
    if not p.exists() or not p.is_file() or p.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(p)


@app.post("/index")
def index(req: IndexRequest) -> dict:
    folder = Path(req.folder).expanduser()
    if not folder.is_dir():
        raise HTTPException(status_code=400, detail=f"Not a directory: {folder}")
    return brain.index(folder, skip_existing=not req.reindex)


@app.post("/search")
def search(req: SearchRequest) -> list[dict]:
    return brain.search(req.query, top_k=req.top_k)


@app.get("/health")
def health() -> dict:
    from src import store
    return {"status": "ok", "indexed": store.count()}
