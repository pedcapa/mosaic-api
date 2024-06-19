from fastapi import FastAPI
from app.routers import gpt_endpoint, image_endpoint

app = FastAPI()

app.include_router(gpt_endpoint.router, prefix="/api/v1")
app.include_router(image_endpoint.router, prefix="/api/v1")


@app.get("/")
def read_root():
    return {"message": "Welcome to Galliard API!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
