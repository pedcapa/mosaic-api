from pydantic import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str
    openai_gpt_model: str = "gpt-4o"  # Modelo a usar
    openai_image_endpoint: str = "https://api.openai.com/v1/images/generations"
    openai_chat_endpoint: str = "https://api.openai.com/v1/chat/completions"

    class Config:
        env_file = ".env"


settings = Settings()
