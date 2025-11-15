"""
Graph Executor for the Research Pipeline
Builds and runs a LangGraph StateGraph depending on the chosen path.
"""

from typing import Dict, Any
from langgraph.graph import StateGraph, START, END

from app.services.graph.nodes import (
    search_node,
    extract_content_node,
    summarize_node,
    format_report_node,
)


# ------------------------------------------------------------
# BUILD GRAPH BASED ON SIMPLE OR COMPLEX PATH
# ------------------------------------------------------------
def build_graph(path: str):
    """
    Builds a StateGraph for either the simple or complex research path.
    """

    graph = StateGraph(name=f"{path}_research_graph")

    # Register nodes (but wiring depends on path)
    graph.add_node("search", search_node)
    graph.add_node("summarize", summarize_node)
    graph.add_node("format", format_report_node)

    if path == "complex":
        graph.add_node("extract", extract_content_node)

    # -----------------------------
    # Simple path wiring
    # START → search → summarize → format → END
    # -----------------------------
    if path == "simple":
        graph.add_edge(START, "search")
        graph.add_edge("search", "summarize")
        graph.add_edge("summarize", "format")
        graph.add_edge("format", END)

    # -----------------------------
    # Complex path wiring
    # START → search → extract → summarize → format → END
    # -----------------------------
    else:
        graph.add_edge(START, "search")
        graph.add_edge("search", "extract")
        graph.add_edge("extract", "summarize")
        graph.add_edge("summarize", "format")
        graph.add_edge("format", END)

    return graph.compile()


# ------------------------------------------------------------
# EXECUTE A GRAPH INSTANCE
# ------------------------------------------------------------
async def execute_graph(
    task_id: str,
    query: str,
    max_results: int,
    path: str,
    tools: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Executes the graph for the given task asynchronously.
    Returns the final state (summary, key_points, sources).
    """

    # Initial state passed into the graph
    initial_state = {
        "query": query,
        "max_results": max_results,
        "search_results": [],
        "extracted_texts": [],
        "summary": "",
        "key_points": [],
        "sources": [],
        "final": {},
    }

    # Build and compile the LangGraph workflow
    graph = build_graph(path)

    # Execute asynchronously
    final_state = await graph.ainvoke(
        initial_state,
        config={"metadata": {"task_id": task_id}},
        # context is passed to all nodes → tools + task_id
        context={"tools": tools, "task_id": task_id},
    )

    # final_state contains everything from the pipeline
    return final_state.get("final", {})
