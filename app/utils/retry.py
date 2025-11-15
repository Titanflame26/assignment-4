from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type


def default_retry(exceptions: tuple = (Exception,), attempts: int = 3):
    """
    A reusable retry decorator with sane defaults.
    
    Usage:
        @default_retry((HTTPError,), attempts=5)
        async def fetch_url(...):
            ...
    """
    return retry(
        stop=stop_after_attempt(attempts),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        retry=retry_if_exception_type(exceptions),
        reraise=True
    )
