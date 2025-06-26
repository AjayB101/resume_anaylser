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


def resume_analyse(file_path: str, job_description: str):
    try:
        extracted_resume_txt = extract_resume(file_path)
        if not extracted_resume_txt:
            return error_response(str("No content is present in pdf"))
        parser = PydanticOutputParser(pydantic_object=ResumeScore)
        prompt = PromptTemplate(
            template=ToolPrompts.resume_analyzer_prompt,
            input_variables=["resume_text", "job_description"],
            partial_variables={"format_instructions": parser.get_format_instructions
                               ()})

        chain = prompt | llm | parser
        res = chain.invoke({
            "resume_text": extracted_resume_txt,
            "job_description": job_description
        })
        return success_response(res.dict())

    except Exception as e:
        return error_response(str(e))
