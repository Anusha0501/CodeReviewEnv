"""FastAPI server for CodeReviewEnv Hugging Face Spaces deployment"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import os
import sys

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from env import CodeReviewEnv, Action, Observation, Reward, BugType

# Initialize FastAPI app
app = FastAPI(
    title="CodeReviewEnv API",
    description="AI-Powered Code Review & Bug Detection Environment",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global environment instance
env: Optional[CodeReviewEnv] = None

# Request/Response models
class ResetRequest(BaseModel):
    task_id: Optional[str] = None
    difficulty: Optional[str] = None

class StepRequest(BaseModel):
    reviewer_comment: str
    bug_detected: bool
    bug_type: Optional[str] = None

class ResetResponse(BaseModel):
    observation: Dict[str, Any]
    task_info: Dict[str, Any]

class StepResponse(BaseModel):
    observation: Dict[str, Any]
    reward: Dict[str, Any]
    done: bool
    info: Dict[str, Any]

class TaskListResponse(BaseModel):
    tasks: Dict[str, Dict[str, Any]]

def get_env():
    """Get or initialize the environment"""
    global env
    if env is None:
        env = CodeReviewEnv()
    return env

@app.get("/")
async def root():
    """Root endpoint returning status"""
    return {
        "message": "CodeReviewEnv API",
        "version": "1.0.0",
        "status": "running",
        "environment": "CodeReviewEnv"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "environment": "CodeReviewEnv"}

@app.post("/reset", response_model=ResetResponse)
async def reset_environment(request: ResetRequest):
    """Reset the environment and return initial observation"""
    try:
        env = CodeReviewEnv(task_id=request.task_id, difficulty=request.difficulty)
        observation = env.reset(task_id=request.task_id, difficulty=request.difficulty)
        task_info = env.get_task_info()
        
        return ResetResponse(
            observation=observation.dict(),
            task_info=task_info
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/step", response_model=StepResponse)
async def step_environment(request: StepRequest):
    """Execute one step in the environment"""
    global env
    
    if env is None:
        raise HTTPException(status_code=400, detail="Environment not initialized. Call /reset first.")
    
    try:
        # Convert bug_type string to enum if provided
        bug_type = None
        if request.bug_type:
            try:
                bug_type = BugType(request.bug_type)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid bug_type: {request.bug_type}")
        
        # Create action
        action = Action(
            reviewer_comment=request.reviewer_comment,
            bug_detected=request.bug_detected,
            bug_type=bug_type
        )
        
        # Step environment
        observation, reward, done, info = env.step(action)
        
        return StepResponse(
            observation=observation.dict(),
            reward=reward.dict(),
            done=done,
            info=info
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/state")
async def get_state():
    """Get current environment state"""
    global env
    
    if env is None:
        raise HTTPException(status_code=400, detail="Environment not initialized. Call /reset first.")
    
    try:
        return env.state()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tasks", response_model=TaskListResponse)
async def list_tasks():
    """List all available tasks"""
    try:
        temp_env = CodeReviewEnv()
        tasks = temp_env.list_available_tasks()
        return TaskListResponse(tasks=tasks)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/task_info")
async def get_task_info():
    """Get information about the current task"""
    global env
    
    if env is None:
        raise HTTPException(status_code=400, detail="Environment not initialized. Call /reset first.")
    
    try:
        return env.get_task_info()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
