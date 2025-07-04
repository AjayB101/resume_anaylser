class ToolPrompts:
    resume_analyzer_prompt = """
You are an expert career coach and a meticulous document validator. Your job is to validate both the candidate's resume and the provided job description before performing an analysis.

STEP 1: VALIDATE THE RESUME
First, carefully analyze the 'Input Document' to determine if it is a valid resume/CV. Look for:
- Personal/contact information (name, email, phone)
- Professional experience or work history
- Education background
- A skills section
- Standard resume structure and professional language.

If the document is NOT a valid resume (e.g., a random article, book chapter, test document), you must stop and format the output for an invalid resume.

STEP 2: VALIDATE THE JOB DESCRIPTION
If the resume is valid, now analyze the 'Job Description' text. A valid job description should contain:
- A job title
- Company information or context
- A list of responsibilities or duties
- A list of qualifications, skills, or requirements.

If the text is NOT a valid job description, you must stop and format the output for an invalid job description.

STEP 3: FULL ANALYSIS (ONLY if both are valid)
If AND ONLY IF the document is a valid resume AND the text is a valid job description, then proceed to the full analysis:
- Set is_valid_resume: true
- Set is_valid_job_description: true
- Score the resume for clarity, relevance to the job description, and structure (0-100).
- Count the years of relevant experience mentioned in the resume.
- Provide 2-3 specific, actionable improvement suggestions.

Input Document:
{resume_text}

Job Description:
{job_description}

Format Instructions:
{format_instructions}

Your response MUST be in the following JSON format. Choose the format that matches your validation outcome:

- If the resume is INVALID:
{{
  "is_valid_resume": false,
  "is_valid_job_description": true,
  "validation_message": "This document does not appear to be a valid resume. Please upload a correctly formatted resume/CV.",
  "clarity": null,
  "relevance": null,
  "structure": null,
  "experience": null,
  "feedback": null
}}

- If the resume is VALID, but the job description is INVALID:
{{
  "is_valid_resume": true,
  "is_valid_job_description": false,
  "validation_message": "The provided text does not appear to be a valid job description. Please provide a complete job description with responsibilities and requirements.",
  "clarity": null,
  "relevance": null,
  "structure": null,
  "experience": null,
  "feedback": null
}}

- If BOTH the resume AND job description are VALID:
{{
  "is_valid_resume": true,
  "is_valid_job_description": true,
  "validation_message": null,
  "clarity": <int>,
  "relevance": <int>,
  "structure": <int>,
  "experience": <int>,
  "feedback": ["<string>", "<string>", ...]
}}

IMPORTANT: Be strict. Do not analyze invalid documents. The primary goal is accuracy no preamble or explainations.
"""

    serach_query_prompt = """
You are an expert at creating search queries for finding relevant behavioral interview questions.

Given the following job description, extract the key skills, technologies, responsibilities, and role requirements to create an optimized search query for finding behavioral interview questions.

Job Description:
{job_description}

Create a concise search query (maximum 10-15 words) that focuses on:
1. The primary role/position
2. Key technical skills mentioned
3. Important soft skills or responsibilities
4. Industry context if relevant

Format: Return only the search query, nothing else.

Example inputs and outputs:
- Input: "Software Engineer position requiring Java, Spring Boot, microservices..."
- Output: "software engineer behavioral interview questions Java Spring microservices"

- Input: "Data Scientist role with Python, machine learning, analytics..."
- Output: "data scientist behavioral interview questions Python machine learning"

Search Query:"""

    behavioural_q_and_a_prompt = """
    Extract 2 behavioral interview questions and sample answers from the following content.
    I want the response in the following format:

    {format_instructions}

    Query:
    {query}
    no preamble or Explaination
    """

    mock_interview_prompt = """
You are an expert interview evaluator. Your task is to analyze the candidate's resume and their answers to behavioral questions and provide a structured evaluation in JSON format.

**Candidate's Resume:**
{resume_text}

**Candidate's Interview Answers:**
{answers}

---
**Evaluation Criteria:**

1.  **Tone:** Evaluate the candidate's tone from their answers. Is it professional, enthusiastic, or passive? Assign a score from 0 (poor) to 100 (excellent).
2.  **Confidence:** Evaluate the candidate's confidence level. Do they sound sure of their answers and experiences? Assign a score from 0 (not confident) to 100 (very confident).
3.  **Relevance:** Evaluate the relevance of the candidate's answers to the questions asked. Are the answers on-topic and meaningful? Assign a score from 0 (irrelevant) to 100 (highly relevant).
    - If the answer is clearly invalid, placeholder-like (e.g., 'x', 'asdf'), or unrelated to the question, assign a **relevance score of 0**.
    - Invalid answers should also receive very low tone and confidence scores.
4.  **Total Marks:** Calculate the average of the tone, confidence, and relevance scores.
5.  **Feedback:** Based on your evaluation, provide a list of 2-3 clear, actionable feedback tips for the candidate to help them improve.

---
**Output Instructions:**

Return the final result strictly in the following JSON format:

```json
{{
    "tone": <int>,
    "confidence": <int>,
    "relevance": <int>,
    "total_marks": <float>,
    "feedback": [
        "<feedback 1>",
        "<feedback 2>",
        "<feedback 3>"
    ]
}}
"""

    PREDICTOR_PROMPT = """
You are an AI interview coach.

Based on the candidate's scores and feedback from their resume analysis and mock interview, predict the overall outcome of the candidate's interview performance.:
- Resume response from llm: {resume_response}
- Mock interview response from llm: {mock_response}
- Resume average score: {resume_avg}
- Mock interview average score: {mock_avg}




The response should be strictly  in the following format
{format_instructions}

example output format:
            ```json
            {{
                "score": 75,
                "feedback": "Focus on providing more STAR method examples in future interviews."
            }}
```
Predict the candidate's overall outcome and provide a justification for your prediction.
Your justification should be consolidated from the resume and mock interview scores and feedback and it should tell which area or skill lagging.
No preamble or explaination.
"""
    gap_fixer_single_prompt_template_string = """
You are an expert career coach and a professional "Gap Fixer" agent. Your task is to analyze a candidate's resume strengths, mock interview evaluation scores, and overall success likelihood to identify key areas for improvement.

Based on these insights, you will generate a personalized, human-readable improvement plan. Crucially, for each actionable step in the plan, you must also provide a list of precise web search queries that the candidate can use to find relevant learning resources and guidance online.

**Input Analysis Instructions:**
- **Resume Strength JSON:** Focus on specific areas like keyword matching, use of metrics, action verbs, and overall impact.
- **Evaluation Scores JSON:** Analyze scores for tone, confidence, and relevance, and derive insights from the specific feedback provided.
- **Success Likelihood JSON:** Understand the overall prediction and the high-level reasons for it.

**Candidate's Resume Strength Analysis:**
{resume_strength_json}

**Mock Interview Evaluation Scores:**
{evaluation_scores_json}

**Success Likelihood Prediction:**
{success_likelihood_json}

The output should be strictly based on the format instructions below. Do not include any explanation, commentary, or extra text—only return the final JSON object.

{format_instructions}

Output Format Example:
{{
  "overall_summary": "The candidate has a solid foundation but needs to enhance their resume with quantifiable achievements and improve interview confidence.",
  "actionable_steps": [
    {{
      "description": "Quantify achievements on resume bullet points to demonstrate impact.",
      "search_query": "quantify resume achievements"
    }},
    {{
      "description": "Practice interview questions using the STAR method.",
      "search_query": "STAR method interview examples"
    }},
    {{
      "description": "Improve technical communication by explaining projects clearly.",
      "search_query": "how to explain technical projects in interviews"
    }}
  ]
}}

"""
