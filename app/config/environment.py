import os
from pathlib import Path
from dotenv import load_dotenv


# ============================================================
#  Load .env file (if it exists)
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]  # project root
ENV_PATH = BASE_DIR / ".env"

if ENV_PATH.exists():
    load_dotenv(ENV_PATH)
else:
    print("[environment.py] No .env file found — using system environment variables.")


# ============================================================
#  Environment Helper Functions
# ============================================================

def env(key: str, default=None):
    """
    Fetch an environment variable.
    If not found, return the given default.
    """
    return os.getenv(key, default)


def require_env(key: str) -> str:
    """
    Fetch an environment variable.
    Raises a clear error if it does not exist.
    """
    value = os.getenv(key)
    if value is None:
        raise RuntimeError(f"Required environment variable '{key}' is missing.")
    return value


# ============================================================
#  Convenience Accessors (Optional)
# ============================================================

def get_gemini_key() -> str | None:
    return env("GEMINI_API_KEY", None)


def get_bing_key() -> str | None:
    return env("BING_API_KEY", None)


def get_ollama_url() -> str:
    return env("OLLAMA_URL", "http://localhost:11434")


def in_debug_mode() -> bool:
    return env("DEBUG", "false").lower() in ("1", "true", "yes", "y")
