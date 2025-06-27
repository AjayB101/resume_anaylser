from re import M
import stat
from langgraph.graph import START, StateGraph, END

from agents.resume_analyzer import extract_resume, resume_analyse
from agents.mock_evaluator import mock_interview_analyser
from agents.behavioral_retriever import BehaviourRetriver
from models.models import GraphState
# Orchestrator module
graph_builder = StateGraph(GraphState)
RESUME_ANALYZER_NODE = "resume_analyzer"
BEHAVIORAL_RETRIEVER_NODE = "behavioral_retriever"
MOCK_EVALUATOR_NODE = "mock_evaluator"


def resume_analyyser_node(state: GraphState) -> GraphState:
    extracted_resume_txt = extract_resume(state["file_path"],)
    state["resume_text"] = extracted_resume_txt
    agent_res = resume_analyse(extracted_resume_txt,
                               job_description=state["job_description"])
    state["resume_analysis"] = agent_res
    return state


def beahaviour_node(state: GraphState):
    behavioral_retriever = BehaviourRetriver()
    state["behavioral_questions"] = behavioral_retriever.get_q_and_a(
        state["job_description"])
    return state


def mock_evaluator_node(state: GraphState):
    # This node is not implemented yet, but can be used for future mock interview evaluations
    state["mock_response"] = mock_interview_analyser(
        state["resume_text"], state["answers"])
    return state


graph_builder.add_node(
    RESUME_ANALYZER_NODE,
    resume_analyyser_node,
)
graph_builder.add_node(
    BEHAVIORAL_RETRIEVER_NODE,
    beahaviour_node,
)
graph_builder.add_node(
    MOCK_EVALUATOR_NODE,
    mock_evaluator_node,
)


graph_builder.add_edge(START, RESUME_ANALYZER_NODE)


graph_builder.add_edge(RESUME_ANALYZER_NODE, BEHAVIORAL_RETRIEVER_NODE)


def should_run_mock(state: GraphState) -> str:
    if state["stage"] == "behavioral_questions":
        return END
    elif state["stage"] == "mock_evaluation" and state.get("answers"):
        return MOCK_EVALUATOR_NODE
    return END


graph_builder.add_conditional_edges(
    BEHAVIORAL_RETRIEVER_NODE,
    should_run_mock,
)

# Create separate graphs for better control


def create_behavioral_graph():
    """Graph that only runs resume analysis and behavioral questions"""
    builder = StateGraph(GraphState)

    builder.add_node(RESUME_ANALYZER_NODE, resume_analyyser_node)
    builder.add_node(BEHAVIORAL_RETRIEVER_NODE, beahaviour_node)

    builder.add_edge(START, RESUME_ANALYZER_NODE)
    builder.add_edge(RESUME_ANALYZER_NODE, BEHAVIORAL_RETRIEVER_NODE)
    builder.add_edge(BEHAVIORAL_RETRIEVER_NODE, END)

    return builder.compile()


def create_mock_evaluation_graph():
    """Graph that only runs mock evaluation"""
    builder = StateGraph(GraphState)

    builder.add_node(MOCK_EVALUATOR_NODE, mock_evaluator_node)
    builder.add_edge(START, MOCK_EVALUATOR_NODE)
    builder.add_edge(MOCK_EVALUATOR_NODE, END)

    return builder.compile()


# Create both graph instances
behavioral_graph = create_behavioral_graph()
mock_evaluation_graph = create_mock_evaluation_graph()
