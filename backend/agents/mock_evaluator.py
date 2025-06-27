# Mock Evaluator module
from typing import Any
from prompts.tool_prompts import ToolPrompts
from models.models import MockInterviewFeedback, success_response, error_response
from langchain_core.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from llm import llm


def mock_interview_analyser(resume_txt: str, answers: list[dict[str, Any]]) -> dict:
    try:
        parser = PydanticOutputParser(pydantic_object=MockInterviewFeedback)

        prompt_temp = PromptTemplate(
            template=ToolPrompts.mock_interview_prompt,
            input_variables=["resume_text", "answers"],
            partial_variables={
                "format_instructions": parser.get_format_instructions()
            }
        )

        chain = prompt_temp | llm | parser

        result = chain.invoke({
            "resume_text": resume_txt,
            "answers": answers
        })

        return success_response(result.dict())

    except Exception as e:
        print("❌ Error in mock interview analysis:", e)
        return error_response(f"Mock Interview Evaluation failed: {str(e)}")
