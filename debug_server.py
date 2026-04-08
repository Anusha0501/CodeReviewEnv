#!/usr/bin/env python3
"""Debug server for Hugging Face Spaces deployment"""

import os
import sys

print("=== DEBUG: CodeReviewEnv Server Startup ===")
print(f"Python path: {sys.path}")
print(f"Current directory: {os.getcwd()}")
print(f"Files in current directory: {os.listdir('.')}")

try:
    print("Testing basic imports...")
    import fastapi
    print(f"FastAPI version: {fastapi.__version__}")
    
    import uvicorn
    print(f"Uvicorn available: True")
    
    print("Testing env package import...")
    sys.path.insert(0, os.getcwd())
    from env import CodeReviewEnv
    print("CodeReviewEnv imported successfully")
    
    print("Testing environment creation...")
    env = CodeReviewEnv()
    print("Environment created successfully")
    
    print("Creating FastAPI app...")
    from fastapi import FastAPI
    app = FastAPI(title="Debug CodeReviewEnv")
    
    @app.get("/")
    async def root():
        return {"message": "Debug server is running", "status": "ok"}
    
    @app.post("/reset")
    async def reset():
        try:
            env = CodeReviewEnv()
            obs = env.reset()
            return {"observation": obs.dict(), "status": "success"}
        except Exception as e:
            return {"error": str(e), "status": "error"}
    
    print("Starting server...")
    if __name__ == "__main__":
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=7860)
    
except Exception as e:
    print(f"ERROR during startup: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
