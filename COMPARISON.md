# Tool Calling Approaches Comparison

## Overview

This document compares three different tool calling approaches for AgentBeats benchmarks, based on actual test results from the Math Quiz benchmark scenario.

**Test Date**: November 16, 2025  
**Test Model**: gpt-4o-mini (naive agent, no fine-tuning)  
**Test Runs**: 5 runs per approach  
**Test Results**: See `poc_test_results.json` for detailed data

---

## Quick Comparison Table

| Approach | Setup Time | Success Rate | Avg Response Time | Tool Accuracy | Complexity | Best For |
|----------|------------|--------------|-------------------|---------------|------------|----------|
| **PoC 1: Python Tools** | ~5 min | 100% | 20.9s | 100% | Low | Simple benchmarks, quick prototypes |
| **PoC 2: MCP Tools** | ~10 min | 100% | 23.9s | 100% | Medium | Shared tools, standardized operations |
| **PoC 4: Hybrid** | ~15 min | 100% | 26.8s | 100% | High | Production benchmarks, complex workflows |

---

## Test Results Summary

### PoC 1: Python Tools Only

**Test Results** (5 runs):
- ✅ Success Rate: **100%** (5/5 successful)
- ✅ Error Rate: **0%**
- ⏱️ Average Response Time: **20.9 seconds**
- ✅ Tool Calling Accuracy: **100%**
- ✅ All expected tools called in all runs

**Tools Used**:
- `generate_math_question()` - Python tool
- `evaluate_answer()` - Python tool
- `report_results()` - Python tool

**Example Response**:
```
The math quiz benchmark has been completed successfully. Here are the results:
- Question: What is 72 / 9?
- Your Answer: 8.0
- Evaluation: Correct!
- Score: 1.0
Result: PASS (score: 1.0)
```

### PoC 2: MCP Tools Only

**Test Results** (5 runs):
- ✅ Success Rate: **100%** (5/5 successful)
- ✅ Error Rate: **0%**
- ⏱️ Average Response Time: **23.9 seconds**
- ✅ Tool Calling Accuracy: **100%**
- ✅ All expected tools called in all runs

**Tools Used**:
- `generate_math_question()` - MCP tool
- `evaluate_answer()` - MCP tool
- `report_results()` - MCP tool

**Example Response**:
```
The math quiz benchmark has been completed successfully using MCP tools. Here are the results:
- Question: What is 10 + 4?
- Your Answer: 14
- Evaluation: Correct!
- Score: 1.0
Result: PASS (score: 1.0)
```

### PoC 4: Hybrid Approach

**Test Results** (5 runs):
- ✅ Success Rate: **100%** (5/5 successful)
- ✅ Error Rate: **0%**
- ⏱️ Average Response Time: **26.8 seconds**
- ✅ Tool Calling Accuracy: **100%**
- ✅ All expected tools called in all runs

**Tools Used**:
- `generate_math_question()` - Python tool (benchmark-specific)
- `evaluate_answer_mcp()` - MCP tool (standardized)
- `report_results_mcp()` - MCP tool (standardized)

**Example Response**:
```
The math quiz benchmark has been completed successfully using the hybrid approach. Here are the results:
- Question: What is 60 / 5?
- Your Answer: 12.0
- Evaluation: Correct!
- Score: 1.0
Result: PASS (score: 1.0)
```

---

## Detailed Analysis

### 1. Setup Complexity

#### PoC 1: Python Tools Only
**Setup Steps**:
1. Create Python file with `@ab.tool` decorated functions
2. Run agent with `--tool tools.py` flag
3. Done!

**Time**: ~5 minutes  
**Dependencies**: AgentBeats SDK only

#### PoC 2: MCP Tools Only
**Setup Steps**:
1. Create MCP server with FastMCP
2. Define tools using `@server.tool` decorator
3. Start MCP server (separate process)
4. Run agent with `--mcp http://localhost:9005/sse` flag

**Time**: ~10 minutes  
**Dependencies**: AgentBeats SDK, FastMCP, separate server process

#### PoC 4: Hybrid Approach
**Setup Steps**:
1. Create MCP server for standardized tools
2. Create Python file for benchmark-specific tools
3. Write detailed agent card with step-by-step workflow
4. Start MCP server (separate process)
5. Run agent with both `--tool tools.py` and `--mcp` flags

**Time**: ~15 minutes  
**Dependencies**: AgentBeats SDK, FastMCP, separate server process, detailed documentation

### 2. Performance Comparison

Based on actual test results:

| Metric | PoC 1 (Python) | PoC 2 (MCP) | PoC 4 (Hybrid) |
|--------|----------------|-------------|-----------------|
| **Fastest Run** | 18.6s | 20.9s | 24.4s |
| **Slowest Run** | 23.3s | 28.3s | 28.4s |
| **Average** | **20.9s** ⚡ | 23.9s | 26.8s |
| **Std Deviation** | ~1.7s | ~2.8s | ~1.5s |

**Key Finding**: Python-only approach is fastest, likely due to:
- No network overhead (tools in same process)
- Simpler tool discovery
- Direct function calls

### 3. Tool Discovery & Schema

#### PoC 1: Python Tools
- Tools discovered via Python introspection
- Type hints provide parameter guidance
- Docstrings provide descriptions
- **Pros**: Simple, fast, good IDE support
- **Cons**: No standardized schema, harder to share across benchmarks

#### PoC 2: MCP Tools
- Tools discovered via MCP protocol
- Strong schema enforcement (JSON Schema)
- Standardized tool descriptions
- **Pros**: Industry standard, reusable, better validation
- **Cons**: Network dependency, slightly slower

#### PoC 4: Hybrid
- Combines both approaches
- Python tools for benchmark-specific logic
- MCP tools for standardized operations
- **Pros**: Best of both worlds, clear separation
- **Cons**: Most complex setup

### 4. Agent Card Quality

#### PoC 1: Minimal Card
```toml
description = '''
## Your Role
You are the Math Quiz benchmark orchestrator.

## Task
Run a simple math quiz benchmark:
1. Generate a random math question using generate_math_question()
2. Evaluate the answer using evaluate_answer()
3. Report results using report_results()
'''
```
**Length**: ~15 lines  
**Detail Level**: Basic workflow

#### PoC 2: Basic Card
```toml
description = '''
## Your Role
You are the Math Quiz benchmark orchestrator using MCP tools.

## Workflow
1. Call generate_math_question() to get a question
2. Call evaluate_answer(question, answer, expected) to check
3. Call report_results(correct, score) to log results
'''
```
**Length**: ~12 lines  
**Detail Level**: Basic workflow

#### PoC 4: Detailed Card
```toml
description = '''
## Your Role
You are the Math Quiz benchmark orchestrator using the HYBRID APPROACH.

## Workflow - FOLLOW THESE STEPS IN ORDER

### Step 1: Generate Question
Call generate_math_question() to get a random math question.
[Detailed instructions with examples...]

### Step 2-3: Present & Get Answer
[Detailed instructions...]

### Step 4: Evaluate Answer
Call evaluate_answer_mcp(question, answer, expected) to evaluate.
[Detailed instructions with return format...]

### Step 5: Report Results
Call report_results_mcp(correct, score, question, answer) to log results.
[Detailed instructions...]

## Example Execution
[Complete example trace...]

## Error Handling
[Error handling guidance...]
'''
```
**Length**: ~130 lines  
**Detail Level**: Comprehensive with examples, error handling, best practices

**Key Finding**: All three approaches achieved 100% success rate, suggesting that even minimal cards work well when tools are properly defined. However, detailed cards provide better guidance for complex scenarios.

---

## Use Case Recommendations

### Use PoC 1: Python Tools Only When:
- ✅ Building simple, standalone benchmarks
- ✅ Quick prototyping and iteration needed
- ✅ Tools are benchmark-specific (not reusable)
- ✅ Speed is critical (lowest latency)
- ✅ Single agent deployment

**Example Scenarios**:
- Simple math/quiz benchmarks
- Single-use evaluation tools
- Rapid development cycles

### Use PoC 2: MCP Tools Only When:
- ✅ Tools need to be shared across multiple benchmarks
- ✅ Standardized operations (evaluation, logging, reporting)
- ✅ Multiple agents need same tools
- ✅ Want industry-standard protocol (MCP)

**Example Scenarios**:
- Shared evaluation frameworks
- Common logging/reporting tools
- Agent-to-agent communication
- Standardized benchmark infrastructure

### Use PoC 4: Hybrid Approach When:
- ✅ Production benchmarks requiring robustness
- ✅ Complex workflows with multiple steps
- ✅ Need both standardized and custom tools
- ✅ Maximum clarity and maintainability desired
- ✅ Long-term maintainability is important

**Example Scenarios**:
- Production benchmark suites
- Complex multi-step evaluations
- Benchmarks with both standard and custom operations
- Team-shared benchmark infrastructure

---

## Implementation Examples

### PoC 1: Python Tools

**tools.py**:
```python
import agentbeats as ab
import random

@ab.tool
def generate_math_question() -> dict:
    """Generate a random math question."""
    a = random.randint(1, 100)
    b = random.randint(1, 100)
    op = random.choice(['+', '-', '*', '/'])
    # ... implementation
    return {"question": f"What is {a} {op} {b}?", "expected_answer": str(result)}

@ab.tool
def evaluate_answer(question: str, answer: str, expected: str) -> dict:
    """Evaluate if an answer is correct."""
    is_correct = answer.strip() == expected.strip()
    return {"is_correct": is_correct, "score": 1.0 if is_correct else 0.0}

@ab.tool
def report_results(correct: bool, score: float) -> str:
    """Report the final results."""
    return f"Results reported: {'PASS' if correct else 'FAIL'} (score: {score})"
```

**Run Command**:
```bash
agentbeats run green_agent_card.toml \
    --tool tools.py \
    --model_type openai --model_name gpt-4o-mini
```

### PoC 2: MCP Tools

**mcp_server.py**:
```python
from fastmcp import FastMCP
import random

server = FastMCP("Math Quiz Tools")

@server.tool
def generate_math_question() -> dict:
    """Generate a random math question."""
    # ... implementation
    return {"question": "...", "expected_answer": "..."}

@server.tool
def evaluate_answer(question: str, answer: str, expected: str) -> dict:
    """Evaluate if an answer is correct."""
    # ... implementation
    return {"is_correct": True, "score": 1.0}

@server.tool
def report_results(correct: bool, score: float) -> str:
    """Report the final results."""
    return f"Results reported: PASS (score: {score})"

if __name__ == "__main__":
    server.run(transport="sse", host="localhost", port=9005)
```

**Run Commands**:
```bash
# Terminal 1: Start MCP server
python mcp_server.py

# Terminal 2: Start agent
agentbeats run green_agent_card.toml \
    --mcp http://localhost:9005/sse \
    --model_type openai --model_name gpt-4o-mini
```

### PoC 4: Hybrid Approach

**tools.py** (Python tools):
```python
import agentbeats as ab
import random

@ab.tool
def generate_math_question() -> dict:
    """Generate a random math question (benchmark-specific)."""
    # ... implementation
    return {"question": "...", "expected_answer": "...", "difficulty": "..."}
```

**mcp_server.py** (MCP tools):
```python
from fastmcp import FastMCP

server = FastMCP("Standardized Benchmark Tools")

@server.tool
def evaluate_answer_mcp(question: str, answer: str, expected: str) -> dict:
    """Standardized evaluation tool."""
    # ... implementation
    return {"is_correct": True, "score": 1.0, "feedback": "..."}

@server.tool
def report_results_mcp(correct: bool, score: float, question: str, answer: str) -> str:
    """Standardized reporting tool."""
    # ... implementation
    return "Results reported: PASS (score: 1.0)"
```

**Run Commands**:
```bash
# Terminal 1: Start MCP server
python mcp_server.py

# Terminal 2: Start agent with both
agentbeats run green_agent_card.toml \
    --tool tools.py \
    --mcp http://localhost:9005/sse \
    --model_type openai --model_name gpt-4o-mini
```

---

## Key Findings

### 1. All Approaches Work Well
All three approaches achieved **100% success rate** with naive agents (gpt-4o-mini), demonstrating that:
- Tool calling is reliable across approaches
- Proper tool definitions are more important than approach choice
- Agent cards provide sufficient guidance

### 2. Performance Trade-offs
- **Python-only** is fastest (20.9s avg) due to no network overhead
- **MCP-only** adds ~3s overhead (23.9s avg) for network calls
- **Hybrid** adds ~6s overhead (26.8s avg) but provides best structure

### 3. Setup Complexity vs. Benefits
- **Simple benchmarks**: Python-only is sufficient
- **Shared tools**: MCP-only provides standardization
- **Production**: Hybrid provides best long-term maintainability

### 4. Agent Card Detail Matters Less Than Expected
Even minimal cards achieved 100% success, suggesting:
- Well-defined tools are more important than detailed cards
- Type hints and docstrings provide sufficient guidance
- Detailed cards help with complex workflows but aren't required for simple ones

---

## Recommendations

### For New Benchmarks

1. **Start Simple**: Use PoC 1 (Python Tools) for initial development
2. **Identify Reusability**: If tools will be shared, migrate to PoC 2 (MCP)
3. **Scale Up**: For production, use PoC 4 (Hybrid) for best structure

### For Existing Benchmarks

- **Python-only benchmarks**: Keep as-is if working well
- **Need shared tools**: Migrate to MCP for standardization
- **Complex workflows**: Consider hybrid approach for clarity

### For Teams

- **Standardize on MCP** for shared tools (evaluation, reporting, logging)
- **Use Python tools** for benchmark-specific logic
- **Document workflows** in agent cards (even if minimal)

---

## Test Methodology

Tests were conducted using:
- **Model**: gpt-4o-mini (OpenAI)
- **Runs per PoC**: 5
- **Test Query**: "Run the math quiz benchmark. Generate a question, evaluate an answer, and report the results."
- **Success Criteria**: Agent completes workflow, calls all expected tools, produces valid output
- **Metrics Collected**: Success rate, error rate, response time, tool calling accuracy

See `poc_test_results.json` for complete test data.

---

## Conclusion

All three approaches are viable and achieved 100% success rates in testing. The choice depends on:

1. **Simplicity vs. Structure**: Python-only is simplest; Hybrid provides best structure
2. **Speed vs. Reusability**: Python-only is fastest; MCP enables tool sharing
3. **Current vs. Future Needs**: Start simple, scale up as needed

**Recommendation**: Start with Python-only for new benchmarks, migrate to Hybrid for production systems requiring shared tools and long-term maintainability.

---

## References

- **Test Results**: `poc_test_results.json`
- **Test Script**: `test_poc_results.py`
- **Test Documentation**: `TEST_SCRIPT_README.md`
- **PoC Implementations**: `poc1_python_tools/`, `poc2_mcp_tools/`, `poc4_hybrid/`

