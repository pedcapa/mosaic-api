import httpx
from app.models.schemas import GPTRequest, GPTResponse
from app.core.config import settings

async def fetch_gpt_response(request: GPTRequest) -> GPTResponse:
    headers = {
        "Authorization": f"Bearer {settings.openai_api_key}",
        "Content-Type": "application/json"
    }
    system_prompt = (
        f"You are an assistant helping a {request.user_profile.learning_style} learner with {request.user_profile.disability}. "
        f"User is interested in {', '.join(request.user_profile.interests)}. "
        "Please provide the response in a structured JSON format as requested."
    )
    data = {
        "model": settings.openai_gpt_model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": request.prompt}
        ],
        "response_format": "json_object"
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(settings.openai_chat_endpoint, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
