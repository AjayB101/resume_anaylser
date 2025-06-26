import os
import shutil
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from tempfile import mkdtemp

from orchestrator import interview_graph

app = FastAPI(title="Interview Evaluation API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/run-interview-evaluation/")
async def run_pipeline(
    resume: UploadFile = File(...),
    job_description: str = Form(...),
    candidate_response: str = Form(...)  # unused for now
):
    try:
        # Save file to temp folder
        temp_dir = mkdtemp()
        filename = resume.filename or "uploaded_resume"
        file_path = os.path.join(temp_dir, filename)

        with open(file_path, "wb") as f:
            shutil.copyfileobj(resume.file, f)

        # Invoke the graph
        state = {
            "file_path": temp_dir,
            "job_description": job_description
        }

        result = interview_graph.invoke(state)
        return JSONResponse(content=result["resume_analysis"])

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"Server error: {str(e)}"}
        )
