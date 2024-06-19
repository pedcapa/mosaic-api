import httpx
from app.models.schemas import GPTRequest, GPTResponse
from app.core.config import settings


async def fetch_gpt_response(request: GPTRequest) -> GPTResponse:
    headers = {
        "Authorization": f"Bearer {settings.openai_api_key}",
        "Content-Type": "application/json"
    }
    user_profile = request.user_profile
    system_prompt = (
        f"You are assisting a user who prefers {user_profile.learning_style} learning style and has {user_profile.disability}. "
        f"The user is interested in topics such as {', '.join(user_profile.interests)}. "
        "Please provide the response in a structured JSON format with content sections that can include paragraphs, images descriptions, or additional structured data."
    )
    data = {
        "model": settings.openai_gpt_model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": request.prompt}
        ]
    }

    # Debug: print the payload being sent to the API
    print("Payload being sent to OpenAI API:", data)

    async with httpx.AsyncClient() as client:
        response = await client.post(settings.openai_chat_endpoint, headers=headers, json=data)

        # Debug: print the response status code and response body
        print("Response status code:", response.status_code)
        print("Response body:", response.text)

        response.raise_for_status()  # Esto lanzará una excepción si el código de estado HTTP no es 200-299

        return response.json()
