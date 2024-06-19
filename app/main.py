from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from pathlib import Path
import openai
import os
import json


# Configura la clave API de OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()


# Modelos de datos para las solicitudes
class UserProfile(BaseModel):
    interests: list[str]
    learning_style: list[str]
    disability: list[str]


class GPTRequest(BaseModel):
    prompt: str
    user_profile: UserProfile


class ImageRequest(BaseModel):
    prompt: str
    user_profile: UserProfile

class AudioRequest(BaseModel):
    prompt: str


# respuesta personalizada
@app.post("/api/v1/gpt_response")
async def get_gpt_response(request: GPTRequest):
    user_profile = request.user_profile
    system_prompt = (
        f"You are assisting a user who prefers {user_profile.learning_style} learning style and has {user_profile.disability}. "
        f"The user is interested in topics such as {', '.join(user_profile.interests)}. "
        'Please provide the response in a structured JSON format with following format: {"content": [{"type": "paragraph","text": ""},{"type": "image","description": ""},...]}'
        '1. Ensure the text in the "text" fields is in markdown format.'
        '2. The "description" field of the image should provide a detailed prompt for generate the image.'
    )

    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            response_format={ "type": "json_object" },
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": request.prompt}
            ]
        )

        json_string = response.choices[0].message.content
        json_object = json.loads(json_string)

        return json_object
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# generar imagen
@app.post("/api/v1/generate_image")
async def generate_image(request: ImageRequest):
    user_profile = request.user_profile
    image_prompt = (
        f"Generate an image for a user with {user_profile.learning_style} learning style and {user_profile.disability}. "
        f"Include elements related to {', '.join(user_profile.interests)}. "
        f"Prompt: {request.prompt}"
    )

    try:
        response = openai.images.generate(
            model="dall-e-3",
            prompt=image_prompt,
            n=1,
            quality="standard"
        )
        return {"url": response.data[0].url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/generate_audio")
async def generate_audio(request: AudioRequest):
    audio_prompt = request.prompt

    speech_file_path = Path(__file__).parent / "speech.mp3"
    response = openai.audio.speech.create(
    model="tts-1",
    voice="alloy",
    input=audio_prompt
    )
    response.stream_to_file(speech_file_path)



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
