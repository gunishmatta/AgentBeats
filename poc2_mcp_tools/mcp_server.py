#!/usr/bin/env python3
"""
PoC 2: MCP Tools Only

Math quiz tools exposed via MCP server using fastmcp.
"""

import random
from typing import Dict
from fastmcp import FastMCP

server = FastMCP("Math Quiz MCP", version="1.0.0")


@server.tool
def generate_math_question() -> Dict:
    """
    Generate a random math question.
    
    Returns:
        Dictionary containing:
        - question (str): The math question
        - expected_answer (str): The correct answer
        - difficulty (str): easy, medium, or hard
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
        "difficulty": difficulty
    }


@server.tool
def evaluate_answer(question: str, answer: str, expected: str) -> Dict:
    """
    Evaluate if an answer is correct.
    
    Args:
        question: The math question that was asked
        answer: The agent's answer
        expected: The expected correct answer
    
    Returns:
        Dictionary containing:
        - is_correct (bool): Whether the answer is correct
        - score (float): Score from 0.0 to 1.0
        - feedback (str): Feedback message
    """
    # Normalize answers
    answer_normalized = str(answer).strip().lower()
    expected_normalized = str(expected).strip().lower()
    
    # Check for exact match
    if answer_normalized == expected_normalized:
        return {
            "is_correct": True,
            "score": 1.0,
            "feedback": "Perfect! The answer is correct."
        }
    
    # Try parsing as numbers for close matches
    try:
        answer_num = float(answer_normalized)
        expected_num = float(expected_normalized)
        
        # Allow small rounding differences
        if abs(answer_num - expected_num) < 0.01:
            return {
                "is_correct": True,
                "score": 0.95,
                "feedback": "Correct! (minor rounding difference)"
            }
    except (ValueError, TypeError):
        pass
    
    return {
        "is_correct": False,
        "score": 0.0,
        "feedback": f"Incorrect. Expected: {expected}, Got: {answer}"
    }


@server.tool
def report_results(correct: bool, score: float, question: str = "", answer: str = "") -> str:
    """
    Report the final benchmark results.
    
    Args:
        correct: Whether the answer was correct
        score: The score achieved (0.0 to 1.0)
        question: Optional - the question that was asked
        answer: Optional - the answer that was given
    
    Returns:
        Confirmation message string
    """
    result = {
        "status": "PASS" if correct else "FAIL",
        "score": score,
        "correct": correct
    }
    
    if question:
        result["question"] = question
    if answer:
        result["answer"] = answer
    
    print("=" * 50)
    print("BENCHMARK RESULTS (MCP)")
    print("=" * 50)
    for key, value in result.items():
        print(f"{key}: {value}")
    print("=" * 50)
    
    return f"Results reported: {result['status']} (score: {score})"


if __name__ == "__main__":
    print("Starting Math Quiz MCP Server on localhost:9005")
    server.run(
        transport="sse",
        host="localhost",
        port=9005
    )

