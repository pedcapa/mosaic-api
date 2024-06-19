from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from pathlib import Path
import openai
import os
import json
import requests

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


class QuizzRequest(BaseModel):
    content: list


class FileName(BaseModel):
    file: str


# respuesta personalizada
@app.post("/api/v1/gpt_response")
async def get_gpt_response(request: GPTRequest):
    user_profile = request.user_profile
    system_prompt = (
        f"You are assisting a user who prefers {user_profile.learning_style} learning style and has {user_profile.disability}. "
        f"The user is interested in topics such as {', '.join(user_profile.interests)}. "
        'Please provide the response in a structured JSON format with following format: {"content": [{"type": "paragraph","text": ""},{"type": "image","text": ""},...]}'
        '1. Ensure the text in the "text" of the paragraph fields is in markdown format.'
        '2. The "text" field of the image should provide a detailed prompt for generate the image.'
    )

    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
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


# quizz
@app.post("/api/v1/generate_quizz")
async def generate_quizz(request: QuizzRequest):
    content = json.dumps(request.content)
    system_prompt = (
        f"You are going to generate 5 questions for a user. The questions are going to be generated from a reference content. That content is in the prompt."
        'Please provide the response in a structured JSON format with following format: "[{\"question_number\": 1, \"question_text\": \"example_question_text\", \"options\": {\"example_option_1\": true, \"example_option_2\": false, \"example_option_3\": false}}, ...]"'
        '1. Ensure the text in the fields is in the right format.'
        '2. The first option will always be true and the last two will always be false.'
    )

    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": content}
            ]
        )

        json_string = response.choices[0].message.content
        json_object = json.loads(json_string)

        return json_object
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/speech_to_text")
async def speech_to_text(file_name: FileName):
    audio_file = open(file_name.file, "rb")
    transcript = openai.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file
    )

    return transcript


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
