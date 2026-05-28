import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv

from routers import transcribe, minutes

load_dotenv()

app = FastAPI(title="회의록 자동 작성 앱", version="1.0.0")

app.include_router(transcribe.router, prefix="/api")
app.include_router(minutes.router, prefix="/api")

static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")

uploads_dir = Path(os.getenv("UPLOAD_DIR", "uploads"))
uploads_dir.mkdir(exist_ok=True)


@app.get("/")
async def root():
    return FileResponse(static_dir / "index.html")
