from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
from fastapi.responses import JSONResponse
import PyPDF2
import openai
import os
import json
from pathlib import Path

openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

UPLOAD_DIRECTORY = "./app/uploads/"
if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

gpt_model = "gpt-4o"

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
            model=gpt_model,
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
            model=gpt_model,
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


@app.post("/api/v1/generate_via_pdf")
async def generate_via_pdf(request: GPTRequest):
    user_profile = request.user_profile
    system_prompt = (
        f"You are assisting a user who prefers {user_profile.learning_style} learning style and has {user_profile.disability}. "
        f"The user is interested in topics such as {', '.join(user_profile.interests)}. "
        'The user will provide a PDF as a prompt, please provide the explanation in the response in a structured JSON format with following format: {"content": [{"type": "paragraph","text": ""},{"type": "image","text": ""},...]}'
        '1. Ensure the text in the "text" of the paragraph fields is in markdown format.'
        '2. The "text" field of the image should provide a detailed prompt for generate the image.'
    )

    pdf_reader = PyPDF2.PdfReader(request.prompt)
    text = ""

    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        text += page.extract_text()

    try:
        response = openai.chat.completions.create(
            model=gpt_model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ]
        )

        json_string = response.choices[0].message.content
        json_object = json.loads(json_string)

        return json_object
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/upload_file/")
async def upload_file(file: UploadFile = File(...)):
    # Crear el directorio si no existe
    Path(UPLOAD_DIRECTORY).mkdir(parents=True, exist_ok=True)

    # Construir la ruta completa donde se guardará el archivo
    file_location = os.path.join(UPLOAD_DIRECTORY, file.filename)

    # Escribir el archivo en el sistema de archivos
    with open(file_location, "wb+") as file_object:
        file_object.write(await file.read())

    # Devolver la ruta del archivo
    return JSONResponse(content={"filename": file.filename, "location": file_location})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
