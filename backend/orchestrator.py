from langgraph.graph import START, StateGraph, END

from agents.resume_analyzer import resume_analyse
from models.models import GraphState
# Orchestrator module
graph_builder = StateGraph(GraphState)


def resume_analyyser_node(state: GraphState) -> GraphState:

    agent_res = resume_analyse(state["file_path"],
                               job_description=state["job_description"])
    state["resume_analysis"] = agent_res
    return state


graph_builder.add_node(
    "resume_analyzer",
    resume_analyyser_node,
)
graph_builder.add_edge(START, "resume_analyzer")
graph_builder.add_edge("resume_analyzer", END)
interview_graph = graph_builder.compile()
