# File: server.py
# (Place this file in your 'my-new-project' root folder)

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, Literal
import uvicorn
from pydantic import BaseModel
import uuid

# Import our compiled graph from the 'src' folder
# (Adjust the import if your project structure is different)
from src.agent.graph import graph as app

# This will store the 'state' of each conversation
# In production, you'd use a real database (like Redis or Postgres)
thread_states = {}

# --- Define API Models ---
class StartRequest(BaseModel):
    mcq_input: Dict[str, str]

class ResumeRequest(BaseModel):
    thread_id: str
    approval_response: Literal["approve", "reject"]

# --- Initialize FastAPI ---
api = FastAPI()
api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows your HTML file to talk to this server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@api.post("/api/start_engagement")
async def start_engagement(request: StartRequest):
    """
    Endpoint 1: Starts a new graph (thread)
    """
    # Create a unique ID for this engagement
    thread_id = str(uuid.uuid4())
    
    # This is the "config" object that tells LangGraph which thread we're working on
    thread_config = {"configurable": {"thread_id": thread_id}}
    
    # Get the MCQ data from the request
    input_data = {"mcq_input": request.mcq_input}
    
    # Run the graph. It will run until the first "Interrupt"
    graph_state = app.invoke(input_data, thread_config)
    
    # Save the thread config so we can resume it later
    thread_states[thread_id] = thread_config
    
    # Return the Thread ID and the current state (which includes the plan)
    return {"thread_id": thread_id, "current_state": graph_state}

@api.post("/api/resume_engagement")
async def resume_engagement(request: ResumeRequest):
    """
    Endpoint 2: Resumes a graph that was interrupted
    """
    # Get the thread ID from the request
    thread_id = request.thread_id
    
    # Find the saved config for this thread
    thread_config = thread_states.get(thread_id)
    if not thread_config:
        return {"error": "Thread not found"}, 404
    
    # This is the new input (the human's decision)
    input_data = {"approval_response": request.approval_response}
    
    # Run the graph *again* on the *same thread*. It will resume.
    final_state = app.invoke(input_data, thread_config)
    
    # Clean up (optional)
    del thread_states[thread_id]
    
    return {"status": "complete", "final_state": final_state}

@api.get("/", response_class=HTMLResponse)
async def get_frontend():
    """
    Serves the main HTML file
    """
    return FileResponse('index.html')

if __name__ == "__main__":
    print("--- Starting FastAPI Server for ACIP Red Team ---")
    uvicorn.run(api, host="127.0.0.1", port=8000)