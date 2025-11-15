"""
Graph Nodes for the Research Pipeline
"""

from typing import Dict, Any, List
from app.models.task_store import task_store


# ------------------------------------------------------------
# NODE 1: Web Search
# ------------------------------------------------------------
async def search_node(state: Dict[str, Any], tools: Dict[str, Any], task_id: str):
    """
    Performs a web search for the given query.
    Updates:
        - state["search_results"]
        - task progress: 20%
    """
    query = state["query"]
    max_results = state["max_results"]

    search_tool = tools["search"]
    results = await search_tool.search(query, max_results)

    state["search_results"] = results
    task_store.update_progress(task_id, 20)

    return state


# ------------------------------------------------------------
# NODE 2: Extract Content (used only in complex path)
# ------------------------------------------------------------
async def extract_content_node(state: Dict[str, Any], tools: Dict[str, Any], task_id: str):
    """
    Fetches readable text from URLs.
    Updates:
        - state["extracted_texts"]
        - state["sources"]
        - progress: 45%
    """
    extractor = tools["extract"]
    search_results = state.get("search_results", [])

    extracted_texts: List[str] = []
    sources: List[Dict[str, str]] = []

    for result in search_results:
        url = result.get("url")
        if not url:
            continue

        try:
            text = await extractor.extract(url)
            extracted_texts.append(text)
            sources.append({"url": url, "title": result.get("title")})
        except Exception:
            # skip failed URLs gracefully
            continue

    state["extracted_texts"] = extracted_texts
    state["sources"] = sources

    task_store.update_progress(task_id, 45)
    return state


# ------------------------------------------------------------
# NODE 3: Summarization (used by both simple & complex paths)
# ------------------------------------------------------------
async def summarize_node(state: Dict[str, Any], tools: Dict[str, Any], task_id: str):
    """
    Summarizes either:
        - search result snippets (simple path)
        - extracted page text (complex path)
    Updates:
        - state["summary"]
        - state["key_points"]
        - progress: 80%
    """
    summarizer = tools["summarize"]

    if state.get("extracted_texts"):
        # Complex path
        combined_text = "\n\n".join(state["extracted_texts"])[:20000]
    else:
        # Simple path (fallback to snippets)
        snippets = [
            r.get("snippet", "") or r.get("title", "")
            for r in state.get("search_results", [])
        ]
        combined_text = "\n".join(snippets)[:5000]

    summary, key_points = await summarizer.summarize(combined_text)

    state["summary"] = summary
    state["key_points"] = key_points

    task_store.update_progress(task_id, 80)
    return state


# ------------------------------------------------------------
# NODE 4: Final Report Formatting
# ------------------------------------------------------------
async def format_report_node(state: Dict[str, Any], tools: Dict[str, Any], task_id: str):
    """
    Creates the final structured report format.
    Updates:
        - state["final"]
        - progress: 100%
    """
    state["final"] = {
        "summary": state.get("summary"),
        "key_points": state.get("key_points"),
        "sources": state.get("sources", []),
    }

    task_store.update_progress(task_id, 100)
    return state
