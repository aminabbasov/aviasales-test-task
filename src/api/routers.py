from fastapi import APIRouter

from api.controllers import router as via_router


router = APIRouter(prefix="/api/v1", tags=["API"])
router.include_router(via_router, prefix="/via")
