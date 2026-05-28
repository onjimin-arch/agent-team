import os
import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse

from services.whisper_service import transcribe_audio

router = APIRouter()

ALLOWED_EXTENSIONS = {".mp3", ".wav", ".m4a", ".ogg", ".flac", ".webm"}
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE_MB", 50)) * 1024 * 1024
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "uploads"))


@router.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"지원하지 않는 파일 형식입니다. 허용 형식: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"파일 크기가 {os.getenv('MAX_FILE_SIZE_MB', 50)}MB를 초과합니다.",
        )

    UPLOAD_DIR.mkdir(exist_ok=True)
    tmp_path = UPLOAD_DIR / f"{uuid.uuid4()}{ext}"

    try:
        tmp_path.write_bytes(content)
        result = transcribe_audio(tmp_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"STT 변환 중 오류가 발생했습니다: {str(e)}")
    finally:
        if tmp_path.exists():
            tmp_path.unlink()

    return JSONResponse(content=result)
