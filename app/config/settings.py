from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Gemini API key (optional)
    GEMINI_API_KEY: str | None = None

    # Bing Search key (optional)
    BING_API_KEY: str | None = None

    # Ollama server URL
    OLLAMA_URL: str = "http://localhost:11434"

    # Max search results default
    DEFAULT_MAX_RESULTS: int = 5

    class Config:
        env_file = ".env"
        extra = "allow"


# Instantiate global settings
settings = Settings()
