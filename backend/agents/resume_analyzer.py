from itertools import chain
from models.models import ResumeScore, success_response, error_response
from prompts.tool_prompts import ToolPrompts
from llm import llm
import pdfplumber
import os
import docx2txt
from langchain_core.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser


def extract_resume(directory: str) -> str:
    if not os.path.exists(directory):
        raise FileNotFoundError(f"Directory not found: {directory}")

    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        file_path = os.path.join(directory, filename)

        if filename.lower().endswith('.pdf'):
            try:
                with pdfplumber.open(file_path) as pdf:
                    full_text = ''
                    for page in pdf.pages:
                        text = page.extract_text()
                        if text:
                            full_text += text + '\n'
                    return full_text.strip()
            except Exception as e:
                raise RuntimeError(
                    f"Failed to read PDF '{filename}': {str(e)}")

        elif filename.lower().endswith('.docx'):
            try:
                return docx2txt.process(file_path).strip()
            except Exception as e:
                raise RuntimeError(
                    f"Failed to read DOCX '{filename}': {str(e)}")

    raise ValueError(
        "No valid resume file (.pdf or .docx) found in the directory.")


def resume_analyse(resume_txt: str, job_description: str):
    try:

        parser = PydanticOutputParser(pydantic_object=ResumeScore)
        prompt = PromptTemplate(
            template=ToolPrompts.resume_analyzer_prompt,
            input_variables=["resume_text", "job_description"],
            partial_variables={"format_instructions": parser.get_format_instructions
                               ()})

        chain = prompt | llm | parser
        result = chain.invoke({
            "resume_text": resume_txt,
            "job_description": job_description
        })
        if not result.is_valid_resume and not result.is_valid_job_description:
            return error_response(result.validation_message or "The provided resume and job description is not valid.")
        elif not result.is_valid_resume:
            return error_response(result.validation_message or "The uploaded document is not a valid resume.")
        elif not result.is_valid_job_description:
            return error_response(result.validation_message or "The provided job description is not valid.")

        # Return success with resume analysis data
        return success_response({
            "clarity": result.clarity,
            "relevance": result.relevance,
            "structure": result.structure,
            "experience": result.experience,
            "feedback": result.feedback
        })

    except Exception as e:
        return error_response(str(e))
