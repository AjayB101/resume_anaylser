# Behavioral Retriever module
from itertools import chain
from database.db import get_qna_by_category, save_qna_for_category
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
            if query_text.startswith('"') and query_text.endswith('"'):
                query_text = query_text[1:-1]
            return query_text.strip()

        except Exception as e:
            print("❌ Search prompt error:", e)
            raise RuntimeError(e)

    def get_q_and_a(self, job_description: str) -> dict:
        try:
            # Step 1: Infer category from job description
            category = self.infer_category_from_job_description(
                job_description)

            # Step 2: Check for cached questions by category
            cached_qs_by_category = get_qna_by_category(category)
            if cached_qs_by_category:
                print(
                    f"✅ Found {len(cached_qs_by_category)} cached questions for category '{category}'")
                return success_response([q["question"] for q in cached_qs_by_category])

            print(
                f"🤖 No cached questions found for category '{category}', proceeding with LLM call")

            # Step 3: Generate search query
            search_query = self.search_query_generator(job_description)

            # Step 4: Set up parser and prompt
            parser = PydanticOutputParser(
                pydantic_object=BehavioralQuestionsResponse)

            prompt = PromptTemplate(
                template=ToolPrompts.behavioural_q_and_a_prompt,
                input_variables=["query"],
                partial_variables={
                    "format_instructions": parser.get_format_instructions()
                }
            )

            # Step 5: Chain the call
            chain = prompt | llm | parser
            result = chain.invoke({"query": search_query})

            # Step 6: Process and save results
            if hasattr(result, "questions"):
                # Convert pydantic to dict and add category
                qna_list = []
                for q in result.questions:
                    qna_dict = q.dict()
                    # Add category to each question
                    qna_dict["category"] = category
                    qna_list.append(qna_dict)

                # Save questions with category information
                save_qna_for_category(qna_list, min_count=2)

                # Step 7: Return success with question list
                return success_response([q["question"] for q in qna_list])
            else:
                # Fallback if no questions attribute
                result_dict = result.dict() if hasattr(result, "dict") else {}
                questions = result_dict.get("questions", [])
                return success_response([q["question"] for q in questions])

        except Exception as e:
            print(f"❌ Error in get_q_and_a: {e}")
            return error_response(f"Unexpected error: {str(e)}")

    def infer_category_from_job_description(self, jd: str) -> str:
        """
        Infer the category from job description for better question caching.
        """
        jd_lower = jd.lower()

        if "python" in jd_lower:
            return "python"
        elif "data structure" in jd_lower or "algorithm" in jd_lower or "dsa" in jd_lower:
            return "dsa"
        elif "machine learning" in jd_lower or "ml" in jd_lower or "ai" in jd_lower:
            return "ml"
        elif "react" in jd_lower or "javascript" in jd_lower or "frontend" in jd_lower:
            return "frontend"
        elif "node.js" in jd_lower or "express" in jd_lower or "backend" in jd_lower:
            return "backend"
        elif "database" in jd_lower or "sql" in jd_lower or "mongodb" in jd_lower:
            return "database"
        elif "devops" in jd_lower or "aws" in jd_lower or "docker" in jd_lower or "kubernetes" in jd_lower:
            return "devops"
        elif "product manager" in jd_lower or "pm" in jd_lower:
            return "product_management"
        elif "data analyst" in jd_lower or "analytics" in jd_lower:
            return "data_analysis"
        else:
            return "general"
