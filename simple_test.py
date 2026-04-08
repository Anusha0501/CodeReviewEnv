#!/usr/bin/env python3
"""Simple test to verify basic functionality"""

import sys
import os

print("=== CodeReviewEnv Simple Test ===")
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")

try:
    print("Testing imports...")
    from fastapi import FastAPI
    print("FastAPI imported successfully")
    
    from env import CodeReviewEnv
    print("CodeReviewEnv imported successfully")
    
    print("Testing environment creation...")
    env = CodeReviewEnv()
    print("Environment created successfully")
    
    print("Testing reset...")
    obs = env.reset()
    print("Reset successful")
    print(f"Observation type: {type(obs)}")
    
    print("Testing state...")
    state = env.state()
    print("State successful")
    print(f"State type: {type(state)}")
    
    print("=== ALL TESTS PASSED ===")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
