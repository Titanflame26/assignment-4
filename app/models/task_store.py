from typing import Dict, Any, Optional
from threading import Lock
from .response_models import ResearchStatus, ResearchResult


class TaskStore:
    """
    Simple thread-safe in-memory task store.
    """

    def __init__(self):
        self._tasks: Dict[str, Dict[str, Any]] = {}
        self._lock = Lock()

    # -------------------------------------------------------
    # Create a new task
    # -------------------------------------------------------
    def create_task(self, task_id: str, query: str):
        with self._lock:
            self._tasks[task_id] = {
                "task_id": task_id,
                "status": "pending",
                "progress": 0.0,
                "query": query,
                "result": None,
                "error": None,
            }

    # -------------------------------------------------------
    # Update task progress
    # -------------------------------------------------------
    def update_progress(self, task_id: str, progress: float):
        with self._lock:
            if task_id in self._tasks:
                self._tasks[task_id]["progress"] = progress
                self._tasks[task_id]["status"] = "running"

    # -------------------------------------------------------
    # Mark completed
    # -------------------------------------------------------
    def set_result(self, task_id: str, result: ResearchResult):
        with self._lock:
            if task_id in self._tasks:
                self._tasks[task_id]["status"] = "completed"
                self._tasks[task_id]["progress"] = 100.0
                self._tasks[task_id]["result"] = result

    # -------------------------------------------------------
    # Mark failed
    # -------------------------------------------------------
    def set_error(self, task_id: str, message: str):
        with self._lock:
            if task_id in self._tasks:
                self._tasks[task_id]["status"] = "failed"
                self._tasks[task_id]["error"] = message

    # -------------------------------------------------------
    # Get task info
    # -------------------------------------------------------
    def get_status(self, task_id: str) -> Optional[ResearchStatus]:
        with self._lock:
            data = self._tasks.get(task_id)
            if not data:
                return None

            return ResearchStatus(
                task_id=data["task_id"],
                status=data["status"],
                progress=data["progress"],
                result=data["result"],
                error=data["error"],
            )

    # -------------------------------------------------------
    # Task exists?
    # -------------------------------------------------------
    def exists(self, task_id: str) -> bool:
        with self._lock:
            return task_id in self._tasks


# Global instance (import anywhere)
task_store = TaskStore()
