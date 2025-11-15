from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class ResearchResult(BaseModel):
    """
    Final packaged output after the research pipeline completes.
    """
    topic: str = Field(..., description="Original research topic or query.")
    summary: str = Field(..., description="Main summarized findings.")
    key_points: list[str] = Field(default_factory=list, description="Bullet-point summary of main insights.")
    sources: list[Dict[str, str]] = Field(
        default_factory=list,
        description="List of source URLs with optional titles/snippets."
    )


class ResearchStatus(BaseModel):
    """
    Represents the current status of an async research task.
    Returned by GET /research/{task_id}.
    """

    task_id: str = Field(..., description="Unique ID of the research task.")
    status: str = Field(..., description="pending | running | completed | failed")
    progress: float = Field(..., description="Progress percentage from 0 to 100.")
    
    result: Optional[ResearchResult] = Field(
        None, 
        description="The final output if the task is completed."
    )

    error: Optional[str] = Field(
        None, 
        description="Error message if the task failed."
    )
