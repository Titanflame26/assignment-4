"""
Decides whether to route a research query through the simple
or complex research pipeline.

Simple Path  -> short, direct queries
Complex Path -> long or research-heavy queries
"""

import re


def choose_path(query: str) -> str:
    """
    Determine whether the query needs a simple or complex research flow.

    Rules:
    - If query is short (< 6 words), choose simple
    - If query contains research-heavy keywords, choose complex
    - Otherwise default to complex
    """

    cleaned = query.strip().lower()
    word_count = len(cleaned.split())

    # Rule 1: Short, direct queries → simple path
    if word_count <= 5:
        return "simple"

    # Rule 2: Research-heavy keywords → complex path
    research_keywords = [
        "impact", "future", "analysis", "deep dive",
        "research", "evaluate", "global", "comparison",
        "effects", "consequences", "overview"
    ]

    if any(kw in cleaned for kw in research_keywords):
        return "complex"

    # Rule 3: If question form is short → simple
    if re.match(r"^(what|who|when|where|define)\b", cleaned):
        if word_count <= 8:
            return "simple"

    # Default
    return "complex"
