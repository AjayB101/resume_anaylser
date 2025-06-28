import os
import shutil
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from tempfile import mkdtemp
import json
import uuid
from typing import Dict, Any
from models.models import AnswersPayload
from orchestrator import behavioral_graph, mock_evaluation_graph

app = FastAPI(title="Interview Evaluation API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session store (use Redis/database in production)
session_store: Dict[str, Dict[str, Any]] = {}


@app.post("/run-interview-evaluation/")
async def run_pipeline(
    resume: UploadFile = File(...),
    job_description: str = Form(...),

):
    """
    First API call - generates behavioral questions
    """
    try:
        # Generate unique session ID
        session_id = str(uuid.uuid4())

        # Save file to temp folder
        temp_dir = mkdtemp()
        filename = resume.filename or "uploaded_resume"
        file_path = os.path.join(temp_dir, filename)

        with open(file_path, "wb") as f:
            shutil.copyfileobj(resume.file, f)

        # Use the behavioral graph (only runs resume analysis + behavioral questions)
        state = {
            "file_path": temp_dir,
            "job_description": job_description,
        }

        result = behavioral_graph.invoke(state)

        # Store ALL necessary data for the second API call
        session_store[session_id] = {
            "file_path": temp_dir,
            "job_description": job_description,
            "resume_analysis": result.get("resume_analysis"),
            # This is now extracted in the orchestrator
            "resume_text": result.get("resume_text", ""),
            "behavioral_questions": result.get("behavioral_questions"),

        }

        # Return questions with session ID
        behavioral_questions = result.get("behavioral_questions", {})

        # Ensure we return the questions in the expected format
        if behavioral_questions.get("success"):
            response_data = {
                "success": True,
                "data": behavioral_questions.get("data", []),
                "session_id": session_id
            }
        else:
            response_data = {
                "success": False,
                "message": behavioral_questions.get("message", "Failed to generate questions"),
                "session_id": session_id
            }

        return JSONResponse(content=response_data)

    except Exception as e:
        print(f"❌ Error during pipeline execution: {e}")

        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"Server error: {str(e)}"}
        )


@app.post("/submit-mock-answers/")
async def submit_mock_answers(
    session_id: str = Form(...),
    answers: str = Form(...)
):
    """
    Second API call - evaluates mock interview answers
    Expects `answers` as JSON string: '[{"question": "...", "answer": "..."}, ...]'
    """
    try:
        # Retrieve session data
        if session_id not in session_store:
            raise HTTPException(
                status_code=400,
                detail="Invalid or expired session ID"
            )

        session_data = session_store[session_id]

        # Parse answers from JSON string
        try:
            parsed_answers = json.loads(answers)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=400,
                detail="Invalid JSON format for answers"
            )

        # Validate that we have the required resume_text
        if not session_data.get("resume_text"):
            raise HTTPException(
                status_code=400,
                detail="Resume text not found in session. Please restart the interview process."
            )

        # Prepare state for mock evaluation graph
        state = {
            "resume_text": session_data["resume_text"],
            "answers": parsed_answers,

            "job_description": session_data["job_description"],
            "resume_analysis": session_data["resume_analysis"],
            "behavioral_questions": session_data["behavioral_questions"],
            "success_prediction": {},
        }

        # Use the mock evaluation graph
        result = mock_evaluation_graph.invoke(state)
        mock_response = result.get("mock_response", {})

        # Clean up session after successful evaluation
        temp_dir = session_store[session_id]["file_path"]
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        del session_store[session_id]

        # Return the evaluation results
        if mock_response.get("success"):
            return JSONResponse(content={
                "success": True,
                "feedback": mock_response.get("data", {})
            })
        else:
            return JSONResponse(content={
                "success": False,
                "message": mock_response.get("message", "Mock evaluation failed")
            })

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in mock interview evaluation: {e}")

        # Clean up session on error
        if session_id in session_store:
            temp_dir = session_store[session_id]["file_path"]
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            del session_store[session_id]

        raise HTTPException(
            status_code=500, detail=f"Evaluation error: {str(e)}")


@app.delete("/cleanup-session/{session_id}")
async def cleanup_session(session_id: str):
    """Optional endpoint to manually clean up sessions"""
    try:
        if session_id in session_store:
            temp_dir = session_store[session_id]["file_path"]
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            del session_store[session_id]
            return {"message": "Session cleaned up successfully"}
        else:
            raise HTTPException(status_code=404, detail="Session not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Interview Evaluation API is running"}


@app.get("/session/{session_id}")
async def get_session_info(session_id: str):
    """Debug endpoint to check session data"""
    if session_id not in session_store:
        raise HTTPException(status_code=404, detail="Session not found")

    session_data = session_store[session_id]
    return {
        "session_id": session_id,
        "has_resume_analysis": bool(session_data.get("resume_analysis")),
        "has_resume_text": bool(session_data.get("resume_text")),
        "has_behavioral_questions": bool(session_data.get("behavioral_questions")),
        "job_description_length": len(session_data.get("job_description", ""))
    }
