from typing import Any, List, TypedDict

from pydantic import BaseModel


class ResumeScore(BaseModel):
    clarity: int
    relevance: int
    structure: int
    experience: int
    feedback: List[str]


class BehavioralQuestion(BaseModel):
    question: str
    answer: str
    source: str


class BehavioralQuestionsResponse(BaseModel):
    questions: List[BehavioralQuestion]


def success_response(data: Any) -> dict:
    return {"success": True, "data": data}


def error_response(message: str) -> dict:
    return {"success": False, "message": message}


class GraphState(TypedDict):
    resume_text: str
    job_description: str
    file_path: str
    resume_analysis: dict[bool, Any
                          ]
    behavioral_questions: dict[bool, Any] | None
