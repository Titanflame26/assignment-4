from fastapi import APIRouter

from app.api.research import router as research_router


# ============================================================
#   Main API Router (Aggregator)
# ============================================================

api_router = APIRouter(prefix="/api/v1")


# ------------------------------------------------------------
# Include all individual route modules here
# ------------------------------------------------------------

# Research pipeline endpoints
api_router.include_router(
    research_router,
    prefix="/research",
    tags=["Research"],
)
