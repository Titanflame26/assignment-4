from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.models.request_models import ResearchRequest
from app.models.task_store import task_store
from app.services.research_service import start_research_pipeline

import uuid

router = APIRouter(
    tags=["Research"],
)


# -------------------------------------------------------------
# POST /research → Start research task
# -------------------------------------------------------------
@router.post("/", summary="Start a new research task")
async def start_research(
    req: ResearchRequest,
    background_tasks: BackgroundTasks
):
    # Generate a unique task_id
    task_id = str(uuid.uuid4())

    # Store the task as pending
    task_store.create_task(task_id, query=req.query)

    # Run the pipeline asynchronously via background task
    background_tasks.add_task(
        start_research_pipeline,
        task_id=task_id,
        query=req.query,
        max_results=req.max_results
    )

    return {
        "task_id": task_id,
        "status": "started",
        "message": "Research task has been created."
    }


# -------------------------------------------------------------
# GET /research/{task_id} → Check status of research task
# -------------------------------------------------------------
@router.get("/{task_id}", summary="Get status/results of a research task")
async def get_research_status(task_id: str):
    status = task_store.get_status(task_id)

    if not status:
        raise HTTPException(status_code=404, detail="Task ID not found.")

    return status
