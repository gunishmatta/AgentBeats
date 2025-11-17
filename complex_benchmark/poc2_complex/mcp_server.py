#!/usr/bin/env python3
"""
PoC 2: MCP Tools Only - Complex Benchmark

Multi-step task orchestration using only MCP tools via FastMCP server.
"""

import random
import time
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from fastmcp import FastMCP

server = FastMCP("Complex Benchmark MCP", version="1.0.0")

# In-memory state for tracking progress
_task_state = {}


@dataclass
class TaskStep:
    """Represents a single step in the multi-step task"""
    step_id: int
    question: str
    expected_answer: str
    hint: str
    dependencies: List[int]
    points: float


@server.tool
def initialize_task(task_name: str, battle_id: str = None) -> Dict:
    """
    Initialize a multi-step task challenge.
    
    Args:
        task_name: Name of the task (e.g., "security_audit", "code_review")
        battle_id: Optional battle identifier for tracking
    
    Returns:
        Dictionary containing:
        - task_id (str): Unique task identifier
        - task_name (str): Name of the task
        - total_steps (int): Number of steps in the task
        - steps (List[Dict]): List of step definitions
        - total_points (float): Total points available
    """
    global _task_state
    
    task_id = battle_id or f"task_{int(time.time())}"
    
    # Define 5 steps with dependencies
    steps = [
        TaskStep(
            step_id=1,
            question="What is the first step in a security audit?",
            expected_answer="reconnaissance",
            hint="Start by gathering information",
            dependencies=[],
            points=10.0
        ),
        TaskStep(
            step_id=2,
            question="What tool is commonly used for network scanning?",
            expected_answer="nmap",
            hint="A popular port scanner",
            dependencies=[1],
            points=15.0
        ),
        TaskStep(
            step_id=3,
            question="What is the most common web vulnerability?",
            expected_answer="sql injection",
            hint="Database-related attack",
            dependencies=[1, 2],
            points=20.0
        ),
        TaskStep(
            step_id=4,
            question="What HTTP status code indicates success?",
            expected_answer="200",
            hint="Two hundred",
            dependencies=[3],
            points=10.0
        ),
        TaskStep(
            step_id=5,
            question="What is the final step in a security audit?",
            expected_answer="reporting",
            hint="Document your findings",
            dependencies=[1, 2, 3, 4],
            points=25.0
        )
    ]
    
    # Initialize state
    _task_state[task_id] = {
        "task_id": task_id,
        "task_name": task_name,
        "steps": {s.step_id: asdict(s) for s in steps},
        "completed_steps": [],
        "scores": {},
        "start_time": time.time(),
        "current_step": 1
    }
    
    total_points = sum(s.points for s in steps)
    
    return {
        "task_id": task_id,
        "task_name": task_name,
        "total_steps": len(steps),
        "steps": [asdict(s) for s in steps],
        "total_points": total_points
    }


@server.tool
def get_current_step(task_id: str) -> Dict:
    """
    Get the current step that should be executed next.
    
    Args:
        task_id: The task identifier
    
    Returns:
        Dictionary with current step information and status
    """
    global _task_state
    
    if task_id not in _task_state:
        return {"error": f"Task {task_id} not found"}
    
    state = _task_state[task_id]
    current_step_id = state["current_step"]
    
    if current_step_id > len(state["steps"]):
        return {
            "status": "completed",
            "message": "All steps completed",
            "completed_steps": state["completed_steps"]
        }
    
    step = state["steps"][current_step_id]
    
    # Check dependencies
    dependencies_met = all(
        dep_id in state["completed_steps"]
        for dep_id in step["dependencies"]
    )
    
    return {
        "step_id": current_step_id,
        "question": step["question"],
        "hint": step["hint"],
        "points": step["points"],
        "dependencies_met": dependencies_met,
        "can_proceed": dependencies_met,
        "completed_steps": state["completed_steps"]
    }


@server.tool
def evaluate_step_response(task_id: str, step_id: int, answer: str) -> Dict:
    """
    Evaluate a response for a specific step.
    
    Args:
        task_id: The task identifier
        step_id: The step number being evaluated
        answer: The answer provided by the blue agent
    
    Returns:
        Dictionary with evaluation results
    """
    global _task_state
    
    if task_id not in _task_state:
        return {"error": f"Task {task_id} not found"}
    
    state = _task_state[task_id]
    
    if step_id not in state["steps"]:
        return {"error": f"Step {step_id} not found"}
    
    step = state["steps"][step_id]
    expected = step["expected_answer"].lower().strip()
    provided = str(answer).lower().strip()
    
    # Check for exact match
    is_correct = expected == provided
    
    # Allow partial matches
    if not is_correct:
        is_correct = expected in provided or provided in expected
    
    # Calculate score
    if is_correct:
        score = step["points"]
        feedback = f"Correct! Step {step_id} completed."
    else:
        score = 0.0
        feedback = f"Incorrect. Expected: {step['expected_answer']}, Got: {answer}"
    
    # Update state
    if is_correct:
        if step_id not in state["completed_steps"]:
            state["completed_steps"].append(step_id)
        state["scores"][step_id] = score
        state["current_step"] = step_id + 1
    
    return {
        "step_id": step_id,
        "is_correct": is_correct,
        "score": score,
        "max_points": step["points"],
        "feedback": feedback,
        "task_progress": len(state["completed_steps"]) / len(state["steps"])
    }


@server.tool
def get_task_progress(task_id: str) -> Dict:
    """
    Get the current progress of the task.
    
    Args:
        task_id: The task identifier
    
    Returns:
        Dictionary with progress information
    """
    global _task_state
    
    if task_id not in _task_state:
        return {"error": f"Task {task_id} not found"}
    
    state = _task_state[task_id]
    total_steps = len(state["steps"])
    completed = len(state["completed_steps"])
    total_score = sum(state["scores"].values())
    max_score = sum(s["points"] for s in state["steps"].values())
    
    elapsed_time = time.time() - state["start_time"]
    
    return {
        "task_id": task_id,
        "task_name": state["task_name"],
        "completed_steps": completed,
        "total_steps": total_steps,
        "progress_percentage": (completed / total_steps) * 100,
        "current_score": total_score,
        "max_score": max_score,
        "score_percentage": (total_score / max_score) * 100 if max_score > 0 else 0,
        "elapsed_time": elapsed_time,
        "completed_step_ids": state["completed_steps"]
    }


@server.tool
def simulate_blue_agent_response(question: str, hint: str = "") -> str:
    """
    Simulate a response from a blue agent (for testing purposes).
    
    Args:
        question: The question to ask
        hint: Optional hint for the question
    
    Returns:
        Simulated answer from blue agent
    """
    time.sleep(0.5)  # Simulate response time
    
    question_lower = question.lower()
    if "first step" in question_lower or "reconnaissance" in question_lower:
        return "reconnaissance"
    elif "network scanning" in question_lower or "nmap" in question_lower:
        return "nmap"
    elif "web vulnerability" in question_lower or "sql" in question_lower:
        return "sql injection"
    elif "status code" in question_lower or "200" in question_lower:
        return "200"
    elif "final step" in question_lower or "reporting" in question_lower:
        return "reporting"
    else:
        return "unknown"


@server.tool
def finalize_task(task_id: str) -> Dict:
    """
    Finalize the task and generate final report.
    
    Args:
        task_id: The task identifier
    
    Returns:
        Dictionary with final results and summary
    """
    global _task_state
    
    if task_id not in _task_state:
        return {"error": f"Task {task_id} not found"}
    
    state = _task_state[task_id]
    
    total_steps = len(state["steps"])
    completed = len(state["completed_steps"])
    total_score = sum(state["scores"].values())
    max_score = sum(s["points"] for s in state["steps"].values())
    elapsed_time = time.time() - state["start_time"]
    
    final_report = {
        "task_id": task_id,
        "task_name": state["task_name"],
        "status": "completed" if completed == total_steps else "partial",
        "final_score": total_score,
        "max_score": max_score,
        "score_percentage": (total_score / max_score) * 100 if max_score > 0 else 0,
        "completed_steps": completed,
        "total_steps": total_steps,
        "completion_percentage": (completed / total_steps) * 100,
        "elapsed_time": elapsed_time,
        "step_scores": state["scores"]
    }
    
    return final_report


if __name__ == "__main__":
    print("Starting Complex Benchmark MCP Server on localhost:9006")
    server.run(
        transport="sse",
        host="localhost",
        port=9006
    )

