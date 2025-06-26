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
