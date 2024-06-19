import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    openai_api_key: str = os.getenv("OPENAI_API_KEY")
    openai_gpt_model: str = "gpt-4o"  # Modelo a usar
    openai_image_endpoint: str = "https://api.openai.com/v1/images/generations"
    openai_chat_endpoint: str = "https://api.openai.com/v1/chat/completions"


settings = Settings()
