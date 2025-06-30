# Gap Fixer module

from langchain.prompts import PromptTemplate
from fire_crawl_services import FireCrawlService
from llm import llm
from prompts.tool_prompts import ToolPrompts
from models.models import ImprovementPlan, error_response, success_response
from langchain.output_parsers import PydanticOutputParser
from langchain.chains import LLMChain


def gap_fixer_agent(resume_dict: dict, evaluation_scores: dict, success_likelihood: dict) -> dict:

    try:
        parser = PydanticOutputParser(
            pydantic_object=ImprovementPlan,
        )
        template = PromptTemplate(
            template=ToolPrompts.gap_fixer_single_prompt_template_string,
            input_variables=["resume_strength_json",
                             "evaluation_scores_json", "success_likelihood_json"],
            partial_variables={
                "format_instructions": parser.get_format_instructions()}
        )
        gap_fixer_chain = LLMChain(
            llm=llm,
            prompt=template,
            output_parser=parser,
            verbose=True
        )
        gap_fixer_response = gap_fixer_chain.invoke({
            "resume_strength_json": resume_dict,
            "evaluation_scores_json": evaluation_scores,
            "success_likelihood_json": success_likelihood
        })
        improvemet_plan = gap_fixer_response["text"].dict()
        querys = []
        descriptions = []
        for plan in improvemet_plan["actionable_steps"][:3]:
            if plan["description"] and plan["search_query"]:
                querys.append(plan["search_query"])
                descriptions.append(plan["description"])

        fire_crawl = FireCrawlService()
        links = []
        for query in querys[:3]:
            search_res = fire_crawl.search(query, n_res=1)
            links .append(search_res.data[0]["url"])
        final_res = {
            "summary": improvemet_plan["overall_summary"],
            "improvements": descriptions,
            "links": links
        }
        return success_response(final_res)
    except Exception as e:
        print(f"❌ Error in gap fixer agent: {e}")
        return error_response(str(e))
