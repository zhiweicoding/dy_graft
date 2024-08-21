from fastapi import FastAPI

from dotenv import load_dotenv
from app.routers import upload, dy

# Load environment variables
load_dotenv()

app = FastAPI()

# 包含具体的路由器
app.include_router(upload.router, prefix="/upload", tags=["upload"])
app.include_router(dy.router, prefix="/dy", tags=["dy"])
app.include_router(dy.router, prefix="/db", tags=["db"])


@app.get("/")
async def health_check():
    return {"message": "hello"}
