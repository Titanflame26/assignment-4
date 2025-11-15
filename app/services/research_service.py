import logging
from app.models.task_store import task_store
from app.models.response_models import ResearchResult

from app.services.graph.router import choose_path
from app.services.graph.executor import execute_graph

from app.tools.web_search_tool import WebSearchTool
from app.tools.content_extractor_tool import ContentExtractorTool
from app.tools.summarizer_tool import SummarizerTool

logger = logging.getLogger("research_service")


# --------------------------------------------------------------
# MAIN PIPELINE ENTRYPOINT — called from FastAPI background task
# --------------------------------------------------------------
async def start_research_pipeline(task_id: str, query: str, max_results: int):
    """
    Background task that executes the entire research pipeline.
    This is triggered by POST /research.
    """

    logger.info(f"[{task_id}] Starting research pipeline for query: {query}")
    task_store.update_progress(task_id, 5)

    try:
        # ----------------------------------------------------------
        # 1. Determine whether this is a simple or complex query
        # ----------------------------------------------------------
        path_type = choose_path(query)
        logger.info(f"[{task_id}] Routing to pipeline: {path_type}")

        # ----------------------------------------------------------
        # 2. Initialize tools (can share across nodes)
        # ----------------------------------------------------------
        web_search = WebSearchTool()
        extractor = ContentExtractorTool()
        summarizer = SummarizerTool()

        # ----------------------------------------------------------
        # 3. Execute graph (LangGraph-style orchestration)
        # ----------------------------------------------------------
        result_payload = await execute_graph(
            task_id=task_id,
            query=query,
            max_results=max_results,
            path=path_type,
            tools={
                "search": web_search,
                "extract": extractor,
                "summarize": summarizer,
            }
        )

        # ----------------------------------------------------------
        # 4. Format final result
        # ----------------------------------------------------------
        final_result = ResearchResult(
            topic=query,
            summary=result_payload["summary"],
            key_points=result_payload["key_points"],
            sources=result_payload["sources"]
        )

        task_store.set_result(task_id, final_result)
        logger.info(f"[{task_id}] Research pipeline completed successfully.")

    except Exception as e:
        # ----------------------------------------------------------
        # Handle any pipeline error gracefully
        # ----------------------------------------------------------
        logger.exception(f"[{task_id}] Research task failed due to error: {e}")
        task_store.set_error(task_id, str(e))

    finally:
        # Close tool sessions (aiohttp clients)
        try:
            await web_search.close()
            await extractor.close()
        except Exception:
            pass
