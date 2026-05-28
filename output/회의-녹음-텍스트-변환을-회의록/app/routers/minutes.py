from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from services.claude_service import generate_minutes

router = APIRouter()


class MinutesRequest(BaseModel):
    transcript: str


@router.post("/minutes")
async def create_minutes(body: MinutesRequest):
    if not body.transcript.strip():
        raise HTTPException(status_code=400, detail="전사 텍스트가 비어 있습니다.")

    try:
        minutes = generate_minutes(body.transcript)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"회의록 생성 중 오류가 발생했습니다: {str(e)}")

    return JSONResponse(content={"minutes": minutes})
