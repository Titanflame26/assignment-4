from pydantic import BaseModel, Field, field_validator


class ResearchRequest(BaseModel):
    """
    Incoming request model for starting a research task.
    """

    query: str = Field(..., description="Topic or question to research.")
    max_results: int = Field(
        5,
        ge=1,
        le=10,
        description="Maximum number of web search results to process."
    )

    @field_validator("query")
    def validate_query(cls, v: str):
        cleaned = v.strip()
        if len(cleaned) < 3:
            raise ValueError("Query must be at least 3 characters long.")
        return cleaned
