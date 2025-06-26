class ToolPrompts:
    resume_analyzer_prompt = """
    You are an expert career coach evaluating resumes for job fit.

    Instructions:
    - Score the resume in three categories: clarity, relevance to the job description, and structure.
    - Give numeric scores out of 100 for each category.
    - Count the number of years of relevant experience.
    - Provide 2-3 specific improvement suggestions.

    Input Resume:
    {resume_text}

    Job Description:
    {job_description}

    instructions on how the output would be
    {format_instructions}
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
    Extract 5 behavioral interview questions and sample answers from the following content.
    I want the response in the following format:
    
    {format_instructions}

    Query:
    {query}
    no preamble or Explaination
    """
