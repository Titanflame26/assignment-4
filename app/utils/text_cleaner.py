import re


def clean_html(raw_html: str) -> str:
    """
    Remove HTML tags from text.
    """
    clean = re.sub(r"<[^>]+>", " ", raw_html)
    return normalize_whitespace(clean)


def normalize_whitespace(text: str) -> str:
    """
    Collapse multiple spaces/newlines into a single space.
    """
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def truncate(text: str, max_length: int = 20000) -> str:
    """
    Safely truncate text without breaking words in the middle.
    Useful before sending to an LLM.
    """
    if len(text) <= max_length:
        return text

    truncated = text[:max_length]

    # Avoid cutting a word in half
    last_space = truncated.rfind(" ")
    if last_space != -1:
        truncated = truncated[:last_space]

    return truncated.strip()
