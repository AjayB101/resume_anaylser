from typing import Any, List, TypedDict

from pydantic import BaseModel, Field


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
    answers: list[dict[str, Any]]
    mock_response: dict[bool, Any] | None
    stage: str


class MockInterviewFeedback(BaseModel):
    tone: int = Field(..., ge=0, le=100, description="Tone score out of 100")
    confidence: int = Field(..., ge=0, le=100,
                            description="Confidence score out of 100")
    relevance: int = Field(..., ge=0, le=100,
                           description="Relevance score out of 100")
    total_marks: int = Field(..., ge=0, le=100,
                             description="Average score based on confidence,relevance,tone score out of 100")
    feedback: List[str] = Field(...,
                                description="List of 2-3 actionable feedback tips")


class QAPair(BaseModel):
    question: str
    answer: str


class AnswersPayload(BaseModel):
    job_description: str
    resume_text: str
    answers: List[QAPair]
