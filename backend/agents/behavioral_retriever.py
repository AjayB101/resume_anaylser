# Behavioral Retriever module
from itertools import chain
from database.db import save_questions_if_new
from models.models import BehavioralQuestionsResponse, error_response, success_response
from fire_crawl_services import FireCrawlService
from prompts.tool_prompts import ToolPrompts
from llm import llm
from langchain_core.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser


class BehaviourRetriver:
    def __init__(self) -> None:
        self.fire_crawl = FireCrawlService()

    def search_query_generator(self, job_description: str) -> str:
        try:
            search_prompt_temp = ToolPrompts.serach_query_prompt
            search_prompt = PromptTemplate(
                template=search_prompt_temp,
                input_variables=["job_description"]
            )
            chain = search_prompt | llm
            serch_query_res = chain.invoke(
                {"job_description": job_description})
            if hasattr(serch_query_res, "content"):
                query_text = serch_query_res.content
            else:
                query_text = str(serch_query_res)
            if not isinstance(query_text, str) or query_text.strip() == "":
                raise ValueError(
                    "Search query generation failed or returned empty.")

            return query_text.strip()

        except Exception as e:
            print("❌ Search prompt error:", e)
            raise RuntimeError(e)

    def get_q_and_a(self, job_description: str) -> dict:
        try:
            # Step 1: Generate search query
            search_query = self.search_query_generator(job_description)

            # Step 2: Set up parser and prompt
            parser = PydanticOutputParser(
                pydantic_object=BehavioralQuestionsResponse)

            prompt = PromptTemplate(
                template=ToolPrompts.behavioural_q_and_a_prompt,
                input_variables=["query"],
                partial_variables={
                    "format_instructions": parser.get_format_instructions()
                }
            )

            # Step 3: Chain the call
            chain = prompt | llm | parser
            result = chain.invoke({"query": search_query})

            # Step 4: Return success
            if hasattr(result, "questions"):
                # convert pydantic to dict
                qna_list = [q.dict() for q in result.questions]
                save_questions_if_new(qna_list)

            # Step 5: Return success
            return success_response([q["question"] for q in result.dict().get("questions", [])])

        except Exception as e:
            return error_response(f"Unexpected error: {str(e)}")
