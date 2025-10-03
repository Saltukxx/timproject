from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .api.routes import router as analysis_router

app = FastAPI(title="Maeva TCO Analyzer", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analysis_router)

_STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
_INDEX_FILE = _STATIC_DIR / "index.html"

if _STATIC_DIR.exists():
    app.mount("/", StaticFiles(directory=_STATIC_DIR, html=True), name="frontend")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/{full_path:path}")
async def spa_fallback(full_path: str) -> FileResponse:
    if _INDEX_FILE.exists():
        return FileResponse(_INDEX_FILE)
    raise HTTPException(status_code=404, detail="Not Found")
