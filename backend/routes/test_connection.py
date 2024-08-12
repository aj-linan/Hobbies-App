from fastapi import APIRouter
from database import db

router = APIRouter()

@router.get("/test-connection")
async def test_connection():
    return {"status": "Connected to MongoDB Atlas!"}