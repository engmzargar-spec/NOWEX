from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "NOWEX Platform",
        "timestamp": "2024-12-04T21:00:00Z"
    }