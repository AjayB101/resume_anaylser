from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from prompts.tool_prompts import ToolPrompts
from llm import llm  # Your Gemini or Groq LLM
from langchain.output_parsers import PydanticOutputParser
from models.models import OutcomeModel

parser = PydanticOutputParser(
    pydantic_object=OutcomeModel,
)
template = PromptTemplate(
    input_variables=["resume_avg", "mock_avg"],
    template=ToolPrompts.PREDICTOR_PROMPT,
    partial_variables={
        "format_instructions": parser.get_format_instructions()
    }
)
predictor_chain = LLMChain(
    llm=llm,
    prompt=template,
    output_parser=parser,
    verbose=True
)


def predict_outcome(resume_scores: dict, mock_scores: dict) -> dict:
    try:
        resume_scores = resume_scores["data"]
        mock_scores = mock_scores["data"]

        # Calculate averages
        resume_avg = (
            resume_scores['clarity'] + resume_scores['relevance'] + resume_scores['structure']) / 3
        mock_avg = (
            mock_scores['tone'] + mock_scores['confidence'] + mock_scores['relevance']) / 3

        # Prepare inputs for the prompt
        inputs = {
            "resume_response": resume_scores,
            "mock_response": mock_scores,
            "resume_avg": resume_avg,
            "mock_avg": mock_avg,

        }

        # Generate prediction justification
        prediction_justification = predictor_chain.run(inputs)
        pred_dict = prediction_justification.dict()

        return {
            "success": True,
            "score": pred_dict["score"],
            "justification": pred_dict["feedback"],
        }

    except Exception as e:
        print("❌ Error in outcome prediction:", e)
        return {"success": False, "message": str(e)}
