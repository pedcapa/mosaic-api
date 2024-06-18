from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Union
import openai
import os

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

class ContentBlock(BaseModel):
    type: str
    text: Union[str, None] = None
    url: Union[str, None] = None
    description: Union[str, None] = None

class UserPrompt(BaseModel):
    prompt: str

class GeneratedResponse(BaseModel):
    content: List[ContentBlock]

@app.post("/generate-content/", response_model=GeneratedResponse)
async def generate_content(user_prompt: UserPrompt):
    prompt = user_prompt.prompt
    
    # Use the OpenAI API to generate content
    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": """ 
                 You are a content generator that creates structured articles with paragraphs and images based on user prompts. Return the response in the following JSON format: 

                    "{
                      \"content\": [
                        {
                          \"type\": \"paragraph\",
                          \"text\": \"\"
                        },
                        {
                          \"type\": \"image\",
                          \"description\": \"\"
                        },
                        {
                          \"type\": \"paragraph\",
                          \"text\": \"\"
                        }
                      ]
                    }"
                Each paragraph should contain relevant information based on the user's prompt, and each image should have a URL (use placeholders if necessary) and a description that explains the image. """},
                {"role": "user", "content": prompt}
            ]
        )
        generated_text = response.choices[0].message
        
        # Simulate splitting the generated text into content blocks
        # For a real implementation, you would need to parse the generated_text properly


        return {"content": generated_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)