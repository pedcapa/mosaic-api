import httpx
from app.models.schemas import ImageRequest, ImageResponse
from app.core.config import settings


async def fetch_image_response(request: ImageRequest) -> ImageResponse:
    headers = {
        "Authorization": f"Bearer {settings.openai_api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "prompt": request.prompt,
        "response_format": "json_object"
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(settings.openai_image_endpoint, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
