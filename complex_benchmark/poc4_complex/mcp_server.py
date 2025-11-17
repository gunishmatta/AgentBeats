#!/usr/bin/env python3
"""
PoC 4: Hybrid Approach - MCP Server

MCP tools for standardized operations (evaluation, reporting, progress tracking).
These tools can be reused across different benchmarks.
"""

import time
from typing import Dict
from fastmcp import FastMCP

server = FastMCP("Standardized Benchmark Tools", version="1.0.0")

# Shared state module - both Python tools and MCP tools access this
# Since MCP server runs in separate process, we use file-based state sharing
import json
import os
import fcntl  # For file locking
from pathlib import Path

_STATE_FILE = Path(__file__).parent / ".task_state.json"

def _load_state(retry_count=3):
    """Load state from file (shared with Python tools process) with retries"""
    for attempt in range(retry_count):
        try:
            if _STATE_FILE.exists():
                # Check file age to ensure it's recent
                file_age = time.time() - os.path.getmtime(_STATE_FILE)
                if file_age > 60:  # File older than 60 seconds might be stale
                    print(f"Warning: State file is {file_age:.1f}s old")
                
                with open(_STATE_FILE, 'r') as f:
                    # Acquire shared lock for reading
                    try:
                        fcntl.flock(f.fileno(), fcntl.LOCK_SH)
                        data = json.load(f)
                        return data
                    finally:
                        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
            else:
                # File doesn't exist, wait and retry
                if attempt < retry_count - 1:
                    print(f"State file not found, waiting... (attempt {attempt + 1}/{retry_count})")
                    time.sleep(0.2)
        except (json.JSONDecodeError, IOError) as e:
            # File might be being written or corrupted
            if attempt < retry_count - 1:
                print(f"Error reading state file, retrying... (attempt {attempt + 1}/{retry_count})")
                time.sleep(0.2)
            else:
                print(f"Failed to load state after {retry_count} attempts: {e}")
        except Exception as e:
            print(f"Unexpected error loading state: {e}")
            break
    
    return {}

def _save_state(state):
    """Save state to file with file locking"""
    try:
        # Write to temp file first, then rename (atomic operation)
        temp_file = Path(str(_STATE_FILE) + ".tmp")
        with open(temp_file, 'w') as f:
            # Acquire exclusive lock
            try:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                json.dump(state, f, default=str, indent=2)
                f.flush()
                os.fsync(f.fileno())  # Force write to disk
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Atomic rename
        temp_file.replace(_STATE_FILE)
        
    except Exception as e:
        print(f"Error saving state: {e}")


@server.tool
def evaluate_step_response_mcp(task_id: str, step_id: int, answer: str) -> Dict:
    """
    Evaluate a response for a specific step (standardized evaluation tool).
    
    This is an MCP tool because evaluation logic can be standardized across benchmarks.
    
    Args:
        task_id: The task identifier
        step_id: The step number being evaluated
        answer: The answer provided by the blue agent
    
    Returns:
        Dictionary with evaluation results
    """
    # Load state from file (shared with Python tools) with retries
    _task_state = _load_state(retry_count=5)  # More retries for evaluation
    
    if not _task_state:
        return {"error": "Failed to load task state. Python tools may not have initialized yet. Please try again."}
    
    if task_id not in _task_state:
        return {
            "error": f"Task {task_id} not found. Available tasks: {list(_task_state.keys())}",
            "hint": "Make sure you called initialize_task first and used the returned task_id"
        }
    
    state = _task_state[task_id]
    
    # Handle step lookup - keys are always strings in JSON
    step_key = str(step_id)
    steps = state.get("steps", {})
    
    if step_key not in steps:
        return {
            "error": f"Step {step_id} not found",
            "available_steps": list(steps.keys()),
            "hint": f"Expected step key '{step_key}', but found: {list(steps.keys())}"
        }
    
    step = steps[step_key]
    expected = step["expected_answer"].lower().strip()
    provided = str(answer).lower().strip()
    
    # Check for exact match
    is_correct = expected == provided
    
    # Allow partial matches
    if not is_correct:
        is_correct = expected in provided or provided in expected
    
    # Calculate score
    if is_correct:
        score = float(step["points"])
        feedback = f"Correct! Step {step_id} completed."
    else:
        score = 0.0
        feedback = f"Incorrect. Expected: {step['expected_answer']}, Got: {answer}"
    
    # Update state
    if is_correct:
        if step_id not in state["completed_steps"]:
            state["completed_steps"].append(step_id)
        state["scores"][str(step_id)] = score
        state["current_step"] = step_id + 1
    
    # Save updated state back to file
    _task_state[task_id] = state
    _save_state(_task_state)
    
    return {
        "step_id": step_id,
        "is_correct": is_correct,
        "score": score,
        "max_points": step["points"],
        "feedback": feedback,
        "task_progress": len(state["completed_steps"]) / len(state["steps"])
    }


@server.tool
def get_task_progress_mcp(task_id: str) -> Dict:
    """
    Get the current progress of the task (standardized progress tracking).
    
    This is an MCP tool because progress tracking can be standardized across benchmarks.
    
    Args:
        task_id: The task identifier
    
    Returns:
        Dictionary with progress information
    """
    # Load state from file (shared with Python tools)
    _task_state = _load_state()
    
    if task_id not in _task_state:
        return {"error": f"Task {task_id} not found. Available tasks: {list(_task_state.keys())}"}
    
    state = _task_state[task_id]
    total_steps = len(state["steps"])
    completed = len(state["completed_steps"])
    
    # Handle scores - keys might be strings from JSON
    scores = state.get("scores", {})
    total_score = sum(float(v) for v in scores.values())
    
    # Handle steps - keys might be strings from JSON
    steps = state.get("steps", {})
    max_score = sum(float(s.get("points", 0)) for s in steps.values())
    
    elapsed_time = time.time() - float(state.get("start_time", time.time()))
    
    return {
        "task_id": task_id,
        "task_name": state.get("task_name", "unknown"),
        "completed_steps": completed,
        "total_steps": total_steps,
        "progress_percentage": (completed / total_steps) * 100 if total_steps > 0 else 0,
        "current_score": total_score,
        "max_score": max_score,
        "score_percentage": (total_score / max_score) * 100 if max_score > 0 else 0,
        "elapsed_time": elapsed_time,
        "completed_step_ids": state.get("completed_steps", [])
    }


@server.tool
def finalize_task_mcp(task_id: str) -> Dict:
    """
    Finalize the task and generate final report (standardized reporting).
    
    This is an MCP tool because reporting can be standardized across benchmarks.
    
    Args:
        task_id: The task identifier
    
    Returns:
        Dictionary with final results and summary
    """
    # Load state from file (shared with Python tools)
    _task_state = _load_state()
    
    if task_id not in _task_state:
        return {"error": f"Task {task_id} not found. Available tasks: {list(_task_state.keys())}"}
    
    state = _task_state[task_id]
    
    total_steps = len(state.get("steps", {}))
    completed = len(state.get("completed_steps", []))
    
    # Handle scores - keys might be strings from JSON
    scores = state.get("scores", {})
    total_score = sum(float(v) for v in scores.values())
    
    # Handle steps - keys might be strings from JSON
    steps = state.get("steps", {})
    max_score = sum(float(s.get("points", 0)) for s in steps.values())
    elapsed_time = time.time() - float(state.get("start_time", time.time()))
    
    final_report = {
        "task_id": task_id,
        "task_name": state.get("task_name", "unknown"),
        "status": "completed" if completed == total_steps else "partial",
        "final_score": total_score,
        "max_score": max_score,
        "score_percentage": (total_score / max_score) * 100 if max_score > 0 else 0,
        "completed_steps": completed,
        "total_steps": total_steps,
        "completion_percentage": (completed / total_steps) * 100 if total_steps > 0 else 0,
        "elapsed_time": elapsed_time,
        "step_scores": scores
    }
    
    return final_report


if __name__ == "__main__":
    print("Starting Standardized Benchmark MCP Server on localhost:9007")
    server.run(
        transport="sse",
        host="localhost",
        port=9007
    )

