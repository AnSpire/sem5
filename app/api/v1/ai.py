from fastapi import APIRouter, Depends
from app.services.ai import analyze_map


AIrouter = APIRouter(tags=["AI"])


@AIrouter.get("/analyze")
async def analyze():
    return analyze_map()




