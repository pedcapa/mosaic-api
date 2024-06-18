from fastapi import APIRouter, HTTPException
from app.models.schemas import ImageRequest, ImageResponse
from app.utils.image import fetch_image_response

router = APIRouter()

@router.post("/generate_image", response_model=ImageResponse)
async def generate_image(request: ImageRequest):
    try:
        response = await fetch_image_response(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
