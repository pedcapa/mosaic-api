from fastapi import APIRouter, HTTPException
from app.models.schemas import GPTRequest, GPTResponse
from app.utils.gpt import fetch_gpt_response

router = APIRouter()


@router.post("/gpt_response", response_model=GPTResponse)
async def gpt_response(request: GPTRequest):
    try:
        response = await fetch_gpt_response(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
