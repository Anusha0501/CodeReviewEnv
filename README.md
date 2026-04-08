# CodeReviewEnv: AI-Powered Code Review & Bug Detection Environment

A production-grade OpenEnv environment that simulates a developer reviewing code diffs and identifying bugs, issues, and improvements using AI.

## 🎯 Problem Description

CodeReviewEnv addresses the real-world challenge of automated code review in software development. It trains AI agents to analyze git diffs, detect bugs, classify issues, and provide meaningful feedback - skills essential for maintaining code quality in modern development workflows.

## 🌍 Real-World Use Case

This environment simulates the daily work of a code reviewer who must:
- Analyze pull requests and code changes
- Identify potential bugs and security vulnerabilities
- Classify issues by type (syntax, logic, security, performance)
- Provide constructive feedback to developers
- Balance thoroughness with efficiency

## 🏗️ Architecture

### Environment Components

- **Observation Space**: Code diff, file metadata, context, and review history
- **Action Space**: Reviewer comments, bug detection flags, and bug classification
- **Reward System**: Deterministic scoring with partial rewards for nuanced feedback

### Task Structure

The environment includes 5 predefined tasks across 3 difficulty levels:

#### Easy Tasks
- **Off-by-One Error**: Loop indexing bug in mathematical function
- **Clean Refactoring**: Function renaming (no bugs)

#### Medium Tasks  
- **Null Check Missing**: AttributeError potential in user data processing
- **Clean Improvement**: Email validation enhancement (no bugs)

#### Hard Tasks
- **SQL Injection**: Security vulnerability through string interpolation

## 🎮 Action & Observation Space

### Observation
```python
{
    "code_diff": "Git-style diff string",
    "file_name": "example.py",
    "language": "python", 
    "context": "Function description",
    "previous_comments": ["Previous review comments"],
    "step_count": 1
}
```

### Action
```python
{
    "reviewer_comment": "Detailed analysis of the code",
    "bug_detected": true,
    "bug_type": "logic"  # syntax, logic, security, performance
}
```

## 🏆 Reward Design

The deterministic grader provides nuanced scoring:

- **Correct Detection**: +0.5 points
- **Correct Classification**: +0.2 points  
- **Good Explanation**: +0.3 points
- **False Positives**: -0.2 points

**Total Score**: 0.0 to 1.0 (partial rewards enabled)

## 🚀 Setup Instructions

### Local Development

1. **Clone and Install**:
```bash
git clone <repository>
cd code_reviewai
pip install -r requirements.txt
```

2. **Environment Variables**:
```bash
export HF_TOKEN="your_huggingface_token"
export API_BASE_URL="https://api.groq.com/openai/v1"  # optional
export MODEL_NAME="llama3-8b-8192"  # optional
```

3. **Run Inference**:
```bash
# Run specific task
python inference.py --task-id easy_off_by_one

# Run by difficulty
python inference.py --difficulty medium --episodes 5

# Run random tasks
python inference.py --episodes 10
```

4. **Start Server**:
```bash
python main.py
# or
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Docker Deployment

1. **Build Image**:
```bash
docker build -t codereview-env .
```

2. **Run Container**:
```bash
docker run -p 8000:8000 -e HF_TOKEN=your_token codereview-env
```

### Hugging Face Spaces

1. **Deploy to Hugging Face**:
   - Connect repository to Hugging Face Spaces
   - Set `HF_TOKEN` secret in Space settings
   - Docker Space will automatically build and deploy

## 📊 API Endpoints

### Environment Control
- `POST /reset` - Reset environment with optional task selection
- `POST /step` - Execute one review step
- `GET /state` - Get current environment state
- `GET /health` - Health check endpoint

### Task Management
- `GET /tasks` - List all available tasks
- `GET /task_info` - Get current task information

### Example Usage

```python
import requests

# Reset environment
response = requests.post("http://localhost:8000/reset", json={
    "task_id": "easy_off_by_one"
})
observation = response.json()["observation"]

# Submit review
response = requests.post("http://localhost:8000/step", json={
    "reviewer_comment": "There's an off-by-one error in the loop",
    "bug_detected": True,
    "bug_type": "logic"
})
reward = response.json()["reward"]
print(f"Score: {reward['score']:.3f}")
```

## 📈 Baseline Performance

Expected baseline scores using Llama3-8b:

| Task | Difficulty | Baseline Score |
|------|------------|----------------|
| easy_off_by_one | Easy | 0.65 |
| medium_null_check | Medium | 0.58 |
| hard_sql_injection | Hard | 0.42 |
| clean_easy | Easy | 0.78 |
| clean_medium | Medium | 0.71 |

## 🧪 Testing & Validation

### Run Environment Tests
```bash
python -c "
from env import CodeReviewEnv
env = CodeReviewEnv(task_id='easy_off_by_one')
obs = env.reset()
print('Environment initialized successfully')
print(f'Task: {env.get_task_info()[\"task_id\"]}')
"
```

### Validate OpenEnv Compliance
```bash
openenv validate
```

## 🔧 Configuration

### Environment Variables
- `HF_TOKEN`: Hugging Face API token (required)
- `API_BASE_URL`: LLM API base URL (default: Groq)
- `MODEL_NAME`: LLM model name (default: llama3-8b-8192)

### Custom Tasks
Add new tasks in `env/tasks.py` following the `TaskConfig` schema:

```python
NEW_TASK = TaskConfig(
    task_id="custom_task",
    difficulty="medium",
    code_diff="...",
    file_name="example.py",
    language="python",
    context="Task description",
    has_bug=True,
    bug_type=BugType.SECURITY,
    bug_description="Security vulnerability"
)
```

## 🎯 Learning Objectives

This environment helps AI agents develop:
- **Code Analysis**: Understanding syntax and semantics across languages
- **Bug Detection**: Identifying various types of software defects
- **Security Awareness**: Recognizing common vulnerabilities
- **Communication Skills**: Providing clear, actionable feedback
- **Decision Making**: Balancing thoroughness with efficiency

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add new tasks or improve existing ones
4. Update tests and documentation
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenEnv framework for environment specification
- FastAPI for serving infrastructure
- Pydantic for data validation
- OpenAI for LLM integration

---

**Built with ❤️ for the AI research community**
