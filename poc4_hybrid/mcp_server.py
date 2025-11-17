#!/usr/bin/env python3
"""
PoC 4: Hybrid Approach - MCP Tools

Standardized tools that can be reused across multiple benchmarks.
These handle evaluation and reporting in a consistent way.
"""

from typing import Dict
from fastmcp import FastMCP

server = FastMCP("Math Quiz Hybrid MCP", version="1.0.0")


@server.tool
def evaluate_answer_mcp(question: str, answer: str, expected: str) -> Dict:
    """
    Evaluate if an answer is correct.
    
    This is a standardized evaluation tool that can be used across
    multiple benchmarks. It provides consistent scoring logic.
    
    Args:
        question: The math question that was asked
        answer: The agent's answer to evaluate
        expected: The expected correct answer
    
    Returns:
        Dictionary containing:
        - is_correct (bool): Whether the answer is correct
        - score (float): Score from 0.0 to 1.0
        - feedback (str): Human-readable feedback message
        - details (dict): Additional evaluation details
    
    Example:
        >>> result = evaluate_answer_mcp("What is 5+3?", "8", "8")
        >>> print(result)
        {
            "is_correct": True,
            "score": 1.0,
            "feedback": "Perfect! The answer is correct.",
            "details": {"exact_match": True}
        }
    """
    # Normalize answers (remove spaces, convert to lowercase)
    answer_normalized = str(answer).strip().lower()
    expected_normalized = str(expected).strip().lower()
    
    details = {
        "original_answer": answer,
        "normalized_answer": answer_normalized,
        "expected_normalized": expected_normalized
    }
    
    # Check for exact match
    if answer_normalized == expected_normalized:
        return {
            "is_correct": True,
            "score": 1.0,
            "feedback": "Perfect! The answer is correct.",
            "details": {**details, "exact_match": True}
        }
    
    # Try parsing as numbers for close matches
    try:
        answer_num = float(answer_normalized)
        expected_num = float(expected_normalized)
        
        difference = abs(answer_num - expected_num)
        
        # Allow small rounding differences
        if difference < 0.01:
            return {
                "is_correct": True,
                "score": 0.95,
                "feedback": "Correct! (minor rounding difference accepted)",
                "details": {
                    **details,
                    "exact_match": False,
                    "numeric_difference": difference
                }
            }
        
        # Partial credit for close answers
        if difference < 1.0:
            return {
                "is_correct": False,
                "score": 0.5,
                "feedback": f"Close, but not quite right. Off by {difference}",
                "details": {
                    **details,
                    "exact_match": False,
                    "numeric_difference": difference
                }
            }
    except (ValueError, TypeError):
        details["parse_error"] = "Could not parse answer as number"
    
    return {
        "is_correct": False,
        "score": 0.0,
        "feedback": f"Incorrect. Expected: {expected}, Got: {answer}",
        "details": details
    }


@server.tool
def report_results_mcp(
    correct: bool, 
    score: float, 
    question: str = "", 
    answer: str = "",
    benchmark_name: str = "Math Quiz"
) -> str:
    """
    Report the final benchmark results in a standardized format.
    
    This tool provides consistent reporting across all benchmarks.
    In a real system, this would log to a database or monitoring system.
    
    Args:
        correct: Whether the answer was correct
        score: The score achieved (0.0 to 1.0)
        question: Optional - the question that was asked
        answer: Optional - the answer that was given
        benchmark_name: Optional - name of the benchmark
    
    Returns:
        str: Confirmation message with result summary
    
    Example:
        >>> msg = report_results_mcp(True, 1.0, "What is 5+3?", "8")
        >>> print(msg)
        "Results reported: PASS (score: 1.0)"
    """
    result = {
        "benchmark": benchmark_name,
        "status": "PASS" if correct else "FAIL",
        "score": score,
        "correct": correct,
        "percentage": f"{score * 100:.1f}%"
    }
    
    if question:
        result["question"] = question
    if answer:
        result["answer"] = answer
    
    # In a real system, you would:
    # 1. Log to database
    # 2. Send to monitoring system
    # 3. Update leaderboard
    # 4. Trigger notifications
    
    print("=" * 60)
    print(f"BENCHMARK RESULTS - {benchmark_name} (HYBRID APPROACH)")
    print("=" * 60)
    for key, value in result.items():
        print(f"{key.upper()}: {value}")
    print("=" * 60)
    
    # Return summary message
    status_emoji = "✅" if correct else "❌"
    return (
        f"{status_emoji} Results reported: {result['status']} "
        f"(score: {score:.2f} / {result['percentage']})"
    )


@server.tool
def get_benchmark_info() -> Dict:
    """
    Get information about available benchmarks.
    
    This demonstrates MCP's ability to provide metadata and discovery.
    
    Returns:
        Dictionary with benchmark information
    """
    return {
        "name": "Math Quiz Hybrid",
        "version": "1.0.0",
        "description": "Hybrid approach combining MCP and Python tools",
        "capabilities": {
            "evaluation": "standardized across benchmarks",
            "reporting": "consistent format and logging",
            "question_generation": "benchmark-specific via Python tools"
        },
        "tools": {
            "mcp_tools": [
                "evaluate_answer_mcp",
                "report_results_mcp",
                "get_benchmark_info"
            ],
            "python_tools": [
                "generate_math_question"
            ]
        }
    }


if __name__ == "__main__":
    print("Starting Math Quiz Hybrid MCP Server on localhost:9005")
    print("This server provides standardized evaluation and reporting tools")
    print("Benchmark-specific tools are provided via Python @ab.tool")
    server.run(
        transport="sse",
        host="localhost",
        port=9005
    )

