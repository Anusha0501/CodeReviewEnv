"""Baseline inference for CodeReviewEnv using OpenAI client"""

import os
import json
import sys
from typing import Dict, Any, Optional
from openai import OpenAI
from env import CodeReviewEnv, Action, BugType

# Initialize OpenAI client using environment variables
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.groq.com/openai/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "llama3-8b-8192")
HF_TOKEN = os.getenv("HF_TOKEN")  # NO DEFAULT - must be provided

if not HF_TOKEN:
    raise ValueError("HF_TOKEN environment variable must be set")

client = OpenAI(
    base_url=API_BASE_URL,
    api_key=HF_TOKEN
)

# System prompt for the LLM
SYSTEM_PROMPT = """You are an expert code reviewer. Your task is to analyze code diffs and identify potential bugs or issues.

For each code diff, you must:
1. Determine if there is a bug present
2. If there's a bug, classify its type (syntax, logic, security, performance)
3. Provide a clear, concise comment explaining your analysis

Bug types:
- syntax: Syntax errors, type errors, invalid operations
- logic: Logical errors, off-by-one errors, incorrect algorithms
- security: Security vulnerabilities, injection risks, authentication issues
- performance: Performance issues, inefficient code, resource leaks

Respond in JSON format:
{
    "bug_detected": true/false,
    "bug_type": "syntax/logic/security/performance" or null,
    "reviewer_comment": "Your detailed analysis here"
}

Be thorough but concise. Focus on actual bugs, not style issues."""


def format_observation_prompt(observation: Dict[str, Any]) -> str:
    """Format observation into a prompt for the LLM"""
    prompt = f"""Code Review Analysis

File: {observation['file_name']}
Language: {observation['language']}
Context: {observation['context']}

Code Diff:
```
{observation['code_diff']}
```
"""
    
    if observation.get('previous_comments'):
        prompt += f"\nPrevious Comments:\n"
        for i, comment in enumerate(observation['previous_comments'], 1):
            prompt += f"{i}. {comment}\n"
    
    prompt += "\nAnalyze this code diff and provide your review in the specified JSON format."
    return prompt


def parse_llm_response(response_text: str) -> Dict[str, Any]:
    """Parse LLM response and extract action components"""
    try:
        # Try to parse as JSON
        action_data = json.loads(response_text)
        
        # Validate required fields
        if 'bug_detected' not in action_data:
            action_data['bug_detected'] = False
        
        if 'bug_type' not in action_data:
            action_data['bug_type'] = None
        
        if 'reviewer_comment' not in action_data:
            action_data['reviewer_comment'] = "No comment provided"
        
        # Validate bug_type enum
        if action_data['bug_type']:
            valid_types = ['syntax', 'logic', 'security', 'performance']
            if action_data['bug_type'] not in valid_types:
                action_data['bug_type'] = None
        
        return action_data
    
    except json.JSONDecodeError:
        # Fallback parsing if JSON fails
        return {
            "bug_detected": False,
            "bug_type": None,
            "reviewer_comment": "Failed to parse response"
        }


def run_episode(task_id: Optional[str] = None, difficulty: Optional[str] = None) -> Dict[str, Any]:
    """Run a single episode of the environment"""
    
    # Initialize environment
    env = CodeReviewEnv(task_id=task_id, difficulty=difficulty)
    
    # Get initial observation
    observation = env.reset(task_id=task_id, difficulty=difficulty)
    
    # Log start
    task_info = env.get_task_info()
    print(f"[START] task={task_info['task_id']} env=CodeReviewEnv model={MODEL_NAME}")
    
    step_count = 0
    rewards = []
    done = False
    success = False
    
    while not done and step_count < 5:
        step_count += 1
        
        # Format observation for LLM
        user_prompt = format_observation_prompt(observation.dict())
        
        try:
            # Call LLM
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,
                max_tokens=200
            )
            
            response_text = response.choices[0].message.content.strip()
            action_data = parse_llm_response(response_text)
            
            # Create action
            bug_type = None
            if action_data['bug_type']:
                bug_type = BugType(action_data['bug_type'])
            
            action = Action(
                reviewer_comment=action_data['reviewer_comment'],
                bug_detected=action_data['bug_detected'],
                bug_type=bug_type
            )
            
            # Step environment
            observation, reward, done, info = env.step(action)
            
            # Log step
            print(f"[STEP] step={step_count} action=\"{action.reviewer_comment[:50]}...\" reward={reward.score:.3f} done={done} error=None")
            
            rewards.append(reward.score)
            
            if done and reward.score >= 0.8:
                success = True
                
        except Exception as e:
            print(f"[STEP] step={step_count} action=\"Error\" reward=0.0 done=true error={str(e)}")
            break
    
    # Calculate final score
    final_score = sum(rewards) / len(rewards) if rewards else 0.0
    
    # Log end
    print(f"[END] success={success} steps={step_count} score={final_score:.3f} rewards={[f'{r:.3f}' for r in rewards]}")
    
    return {
        "success": success,
        "steps": step_count,
        "score": final_score,
        "rewards": rewards,
        "task_id": task_info['task_id']
    }


def main():
    """Main function for running inference"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run CodeReviewEnv inference")
    parser.add_argument("--task-id", type=str, help="Specific task ID to run")
    parser.add_argument("--difficulty", type=str, choices=["easy", "medium", "hard"], help="Difficulty level")
    parser.add_argument("--episodes", type=int, default=1, help="Number of episodes to run")
    
    args = parser.parse_args()
    
    results = []
    for episode in range(args.episodes):
        print(f"\n=== Episode {episode + 1} ===")
        result = run_episode(task_id=args.task_id, difficulty=args.difficulty)
        results.append(result)
    
    # Print summary
    if len(results) > 1:
        avg_score = sum(r['score'] for r in results) / len(results)
        success_rate = sum(1 for r in results if r['success']) / len(results)
        print(f"\n=== Summary ===")
        print(f"Episodes: {len(results)}")
        print(f"Average Score: {avg_score:.3f}")
        print(f"Success Rate: {success_rate:.3f}")


if __name__ == "__main__":
    main()
