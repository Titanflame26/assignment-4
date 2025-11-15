from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.api.research import router as research_router
from app.tools.web_search_tool import WebSearchTool
from app.tools.content_extractor_tool import ContentExtractorTool
from app.api.router import api_router
logger = logging.getLogger("main")
logging.basicConfig(level=logging.INFO)

# Global shared resources
global_tools = {
    "web_search": None,
    "extractor": None,
}


# ============================================================
# Lifespan Context Manager (Modern FastAPI Startup/Shutdown)
# ============================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Logic that runs BEFORE the server starts handling requests,
    and AFTER the server finishes (shutdown).
    """

    # ----------------------------------------
    # STARTUP: Initialize shared resources
    # ----------------------------------------
    logger.info("🚀 Starting FastAPI app - initializing shared resources")

    global_tools["web_search"] = WebSearchTool()
    global_tools["extractor"] = ContentExtractorTool()

    yield  # <-- App runs here (receives requests)

    # ----------------------------------------
    # SHUTDOWN: Clean up resources
    # ----------------------------------------
    logger.info("🔻 Shutting down FastAPI - cleaning up resources")

    try:
        if global_tools["web_search"]:
            await global_tools["web_search"].close()
        if global_tools["extractor"]:
            await global_tools["extractor"].close()
    except Exception as e:
        logger.error(f"Error during shutdown cleanup: {e}")


# ============================================================
# FastAPI Application
# ============================================================
def create_app() -> FastAPI:
    app = FastAPI(
        title="LangGraph Research Assistant",
        version="1.0.0",
        description="A Multi-Step Research Pipeline using LangGraph + FastAPI",
        lifespan=lifespan,   # <-- Modern way to handle startup/shutdown
    )

    # CORS (optional)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )

    # Include API modules
    app.include_router(api_router)

    # Root endpoint
    @app.get("/", tags=["Health"])
    async def health_check():
        return {"status": "ok", "message": "Research Assistant API running"}

    return app


# ============================================================
# App instance for Uvicorn
# ============================================================
app = create_app()
