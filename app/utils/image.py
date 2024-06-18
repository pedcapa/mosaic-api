import httpx
from app.models.schemas import ImageRequest, ImageResponse
from app.core.config import settings


async def fetch_image_response(request: ImageRequest) -> ImageResponse:
    headers = {
        "Authorization": f"Bearer {settings.openai_api_key}",
        "Content-Type": "application/json"
    }
    user_profile = request.user_profile
    image_prompt = (
        f"Generate an image for a user with {user_profile.learning_style} learning style and {user_profile.disability}. "
        f"Include elements related to {', '.join(user_profile.interests)}. "
        f"Prompt: {request.prompt}"
    )
    data = {
        "prompt": image_prompt,
        "response_format": "json_object"
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(settings.openai_image_endpoint, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
