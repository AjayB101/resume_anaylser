from re import M
import stat
from typing import Any
from langgraph.graph import START, StateGraph, END

from agents.resume_analyzer import extract_resume, resume_analyse
from agents.mock_evaluator import mock_interview_analyser
from agents.outcome_predictor import predict_outcome
from agents.behavioral_retriever import BehaviourRetriver
from agents.gap_fixer import gap_fixer_agent
from models.models import GraphState
# Orchestrator module
graph_builder = StateGraph(GraphState)
RESUME_ANALYZER_NODE = "resume_analyzer"
BEHAVIORAL_RETRIEVER_NODE = "behavioral_retriever"
MOCK_EVALUATOR_NODE = "mock_evaluator"
OUT_COME_NODE = "out_come_node"
GAP_FIXER_NODE = "gap_fixer_node"


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


def outcome_node(state: GraphState) -> GraphState:
    """
    This node is used to process the final outcome of the interview.
    It can be used to store or display the results.
    """
    # Here you can implement any logic you want to handle the outcome
    # For now, we will just return the state as is
    state["success_prediction"] = predict_outcome(
        state["resume_analysis"],
        state["mock_response"]
    )
    return state


def gap_fixer_node(state: GraphState) -> GraphState:
    res = gap_fixer_agent(
        state["resume_analysis"],
        state["mock_response"],
        state["success_prediction"]
    )
    state["gap_fixer"] = res
    return state


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
    builder.add_node(
        OUT_COME_NODE,
        outcome_node,
    )
    builder.add_node(
        GAP_FIXER_NODE,
        gap_fixer_node,
    )

    builder.add_node(MOCK_EVALUATOR_NODE, mock_evaluator_node)
    builder.add_edge(START, MOCK_EVALUATOR_NODE)
    builder.add_edge(START, MOCK_EVALUATOR_NODE)
    builder.add_edge(MOCK_EVALUATOR_NODE, OUT_COME_NODE)
    builder.add_edge(OUT_COME_NODE, GAP_FIXER_NODE)
    builder.add_edge(GAP_FIXER_NODE, END)

    return builder.compile()


# Create both graph instances
behavioral_graph = create_behavioral_graph()
mock_evaluation_graph = create_mock_evaluation_graph()
