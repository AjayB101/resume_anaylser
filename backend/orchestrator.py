from langgraph.graph import START, StateGraph, END

from agents.resume_analyzer import resume_analyse
from agents.behavioral_retriever import BehaviourRetriver
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


def beahaviour_node(state: GraphState):
    behavioral_retriever = BehaviourRetriver()
    state["behavioral_questions"] = behavioral_retriever.get_q_and_a(
        state["job_description"])
    return state


graph_builder.add_edge(START, "resume_analyzer")
graph_builder.add_node(
    "behavioral_retriever",
    beahaviour_node,
)
graph_builder.add_edge("resume_analyzer", "behavioral_retriever")
graph_builder.add_edge("behavioral_retriever", END)

interview_graph = graph_builder.compile()
