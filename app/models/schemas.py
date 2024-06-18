from pydantic import BaseModel
from typing import List, Dict, Any


class UserProfile(BaseModel):
    interests: List[str]
    learning_style: str  # "visual", "auditive", "reader"
    disability: str  # "ADHD", "autism", "dyslexia"


class GPTRequest(BaseModel):
    prompt: str
    user_profile: UserProfile


class GPTResponse(BaseModel):
    content: List[Dict[str, Any]]


class ImageRequest(BaseModel):
    prompt: str
    user_profile: UserProfile


class ImageResponse(BaseModel):
    url: str
