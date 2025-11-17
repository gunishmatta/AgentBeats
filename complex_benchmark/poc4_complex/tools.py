#!/usr/bin/env python3
"""
PoC 4: Hybrid Approach - Complex Benchmark

Multi-step task orchestration combining:
- Python tools for benchmark-specific logic (task setup, step management)
- MCP tools for standardized operations (evaluation, reporting, progress tracking)
"""

import random
import time
import json
import os
import agentbeats as ab
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

# In-memory state for tracking progress
# Also write to file for MCP server to access (since it runs in separate process)
import fcntl  # For file locking on Unix systems

_task_state = {}
_STATE_FILE = Path(__file__).parent / ".task_state.json"

def _save_state():
    """Save state to file for MCP server access with file locking"""
    try:
        # Convert dataclass objects to dicts for JSON serialization
        serializable_state = {}
        for task_id, state in _task_state.items():
            serializable_state[task_id] = {
                "task_id": state.get("task_id"),
                "task_name": state.get("task_name"),
                "steps": {str(k): v for k, v in state.get("steps", {}).items()},
                "completed_steps": state.get("completed_steps", []),
                "scores": {str(k): v for k, v in state.get("scores", {}).items()},
                "start_time": state.get("start_time"),
                "current_step": state.get("current_step", 1),
                "_write_timestamp": time.time()  # Track when written
            }
        
        # Write to temp file first, then rename (atomic operation)
        temp_file = Path(str(_STATE_FILE) + ".tmp")
        with open(temp_file, 'w') as f:
            # Acquire exclusive lock
            try:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                json.dump(serializable_state, f, default=str, indent=2)
                f.flush()
                os.fsync(f.fileno())  # Force write to disk
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Atomic rename
        temp_file.replace(_STATE_FILE)
        
        # Small delay to ensure file system sync
        time.sleep(0.05)
        
    except Exception as e:
        print(f"Warning: Failed to save state: {e}")

def _load_state():
    """Load state from file with retries"""
    global _task_state
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            if _STATE_FILE.exists():
                with open(_STATE_FILE, 'r') as f:
                    # Acquire shared lock
                    try:
                        fcntl.flock(f.fileno(), fcntl.LOCK_SH)
                        loaded = json.load(f)
                    finally:
                        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                    
                    # Merge with in-memory state
                    for task_id, state in loaded.items():
                        if task_id not in _task_state:
                            _task_state[task_id] = state
                        else:
                            # Update existing state with file state (file is source of truth for MCP)
                            _task_state[task_id].update(state)
                    return
            else:
                # File doesn't exist yet, wait a bit
                if attempt < max_retries - 1:
                    time.sleep(0.1)
        except (json.JSONDecodeError, IOError) as e:
            # File might be being written, retry
            if attempt < max_retries - 1:
                time.sleep(0.1)
            else:
                print(f"Warning: Failed to load state after {max_retries} attempts: {e}")
        except Exception as e:
            print(f"Warning: Unexpected error loading state: {e}")
            break


@dataclass
class TaskStep:
    """Represents a single step in the multi-step task"""
    step_id: int
    question: str
    expected_answer: str
    hint: str
    dependencies: List[int]
    points: float


@ab.tool
def initialize_task(task_name: str, battle_id: str = None) -> Dict:
    """
    Initialize a multi-step task challenge (benchmark-specific).
    
    This is a Python tool because task initialization is specific to this benchmark.
    
    Args:
        task_name: Name of the task (e.g., "security_audit", "code_review")
        battle_id: Optional battle identifier for tracking
    
    Returns:
        dict with keys:
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
    # Convert steps to dict with string keys for JSON compatibility
    steps_dict = {}
    for s in steps:
        step_dict = asdict(s)
        steps_dict[str(s.step_id)] = step_dict
    
    _task_state[task_id] = {
        "task_id": task_id,
        "task_name": task_name,
        "steps": steps_dict,
        "completed_steps": [],
        "scores": {},
        "start_time": time.time(),
        "current_step": 1
    }
    
    # Save state for MCP server (critical - MCP server needs this!)
    _save_state()
    
    # Wait a moment to ensure file is written and available
    time.sleep(0.1)
    
    total_points = sum(s.points for s in steps)
    
    return {
        "task_id": task_id,
        "task_name": task_name,
        "total_steps": len(steps),
        "steps": [asdict(s) for s in steps],
        "total_points": total_points
    }


@ab.tool
def get_current_step(task_id: str) -> Dict:
    """
    Get the current step that should be executed next (benchmark-specific).
    
    This is a Python tool because step management is specific to this benchmark.
    
    Args:
        task_id: The task identifier
    
    Returns:
        dict with current step information and status
    """
    global _task_state
    
    # Reload state from file to get latest updates from MCP server
    _load_state()
    
    if task_id not in _task_state:
        return {"error": f"Task {task_id} not found"}
    
    state = _task_state[task_id]
    
    # Handle current_step - might be int or need conversion
    current_step_id = state.get("current_step", 1)
    if isinstance(current_step_id, str):
        current_step_id = int(current_step_id)
    
    steps = state.get("steps", {})
    if current_step_id > len(steps):
        return {
            "status": "completed",
            "message": "All steps completed",
            "completed_steps": state.get("completed_steps", [])
        }
    
    # Handle step lookup - keys might be strings from JSON
    step_key = str(current_step_id)
    if step_key not in steps:
        step_key = current_step_id
    
    if step_key not in steps:
        return {"error": f"Step {current_step_id} not found"}
    
    step = steps[step_key]
    
    # Check dependencies
    completed_steps = state.get("completed_steps", [])
    dependencies_met = all(
        dep_id in completed_steps
        for dep_id in step.get("dependencies", [])
    )
    
    result = {
        "step_id": current_step_id,
        "question": step.get("question", ""),
        "hint": step.get("hint", ""),
        "points": step.get("points", 0.0),
        "dependencies_met": dependencies_met,
        "can_proceed": dependencies_met,
        "completed_steps": completed_steps
    }
    
    # Save state for MCP server
    _save_state()
    
    return result


@ab.tool
def simulate_blue_agent_response(question: str, hint: str = "") -> str:
    """
    Simulate a response from a blue agent (benchmark-specific).
    
    In a real scenario, this would use talk_to_agent from MCP server.
    This is a Python tool for benchmark-specific simulation logic.
    
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

