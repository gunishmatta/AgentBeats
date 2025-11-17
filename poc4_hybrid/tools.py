#!/usr/bin/env python3
"""
PoC 4: Hybrid Approach - Python Tools

Benchmark-specific tools that need tight integration.
General tools (evaluate, report) are in MCP server.
"""

import random
import agentbeats as ab


@ab.tool
def generate_math_question() -> dict:
    """
    Generate a random math question.
    
    This is a benchmark-specific tool that creates questions
    based on the benchmark's requirements.
    
    Returns:
        dict with keys:
            - question (str): The math question
            - expected_answer (str): The correct answer
            - difficulty (str): easy, medium, or hard
    
    Example:
        >>> result = generate_math_question()
        >>> print(result)
        {
            "question": "What is 5 + 3?",
            "expected_answer": "8",
            "difficulty": "easy"
        }
    """
    operations = [
        ("easy", lambda: (random.randint(1, 10), random.randint(1, 10), "+")),
        ("medium", lambda: (random.randint(10, 50), random.randint(10, 50), "*")),
        ("hard", lambda: (random.randint(50, 100), random.randint(2, 10), "/")),
    ]
    
    difficulty, generator = random.choice(operations)
    num1, num2, op = generator()
    
    # Calculate expected answer
    if op == "+":
        expected = float(num1 + num2)
    elif op == "-":
        expected = float(num1 - num2)
    elif op == "*":
        expected = float(num1 * num2)
    elif op == "/":
        expected = round(num1 / num2, 2)
    else:
        expected = 0.0
    
    question = f"What is {num1} {op} {num2}?"
    
    return {
        "question": question,
        "expected_answer": str(expected),
        "difficulty": difficulty,
        "metadata": {
            "num1": num1,
            "num2": num2,
            "operation": op
        }
    }


# Note: evaluate_answer and report_results are in the MCP server
# This demonstrates the separation of concerns:
# - Benchmark-specific logic (question generation) → Python tools
# - Standardized operations (evaluation, reporting) → MCP tools

