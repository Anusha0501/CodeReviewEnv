"""FastAPI server for CodeReviewEnv deployment"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from env import CodeReviewEnv

def create_app():
    """Create FastAPI app instance"""
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

    @app.get("/")
    def root():
        """Root endpoint returning status"""
        return {"status": "running"}

    @app.get("/health")
    def health_check():
        """Health check endpoint"""
        return {"status": "healthy", "environment": "CodeReviewEnv"}

    @app.post("/reset")
    async def reset(request: Request):
        """Reset the environment and return initial observation"""
        try:
            # Try to parse JSON body, handle empty body gracefully
            try:
                data = await request.json()
            except:
                data = {}
            
            # Extract task_id safely
            task_id = data.get("task_id") if isinstance(data, dict) else None
            
            # Create environment and reset
            env = CodeReviewEnv(task_id=task_id)
            observation = env.reset(task_id=task_id) if task_id else env.reset()
            
            # Return observation as JSON (dict, not object)
            return observation.dict() if hasattr(observation, "dict") else observation
            
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    return app

# Required for FastAPI / uvicorn
app = create_app()

# Required for OpenEnv validator
def main():
    return app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860)
