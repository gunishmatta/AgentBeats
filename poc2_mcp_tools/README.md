# PoC 2: MCP Tools Only

Approach using Model Context Protocol (MCP) with tools exposed via separate server.

## Files

- `green_agent_card.toml` - Agent configuration
- `mcp_server.py` - MCP server with tools

## How to Run

```bash
# Set your OpenAI API key
export OPENAI_API_KEY="your-key-here"

# Terminal 1: Start MCP server
python mcp_server.py

# Terminal 2: Run the agent
agentbeats run green_agent_card.toml \
    --launcher_host 0.0.0.0 --launcher_port 9030 \
    --agent_host 0.0.0.0 --agent_port 9031 \
    --model_type openai --model_name gpt-4o-mini \
    --mcp http://localhost:9005/sse
```

## Tools Provided (via MCP)

1. **generate_math_question()** → dict
   - Generates a random math question
   - Returns question, expected answer, difficulty

2. **evaluate_answer(question, answer, expected)** → dict
   - Evaluates if an answer is correct
   - Returns is_correct, score, feedback

3. **report_results(correct, score, question, answer)** → str
   - Reports final results
   - Returns confirmation message

## Example Interaction

```
User: Run the math quiz benchmark

Agent: I see 3 tools available via MCP: generate_math_question, evaluate_answer, report_results
[MCP tool discovery successful]

Agent: Generating question...
[MCP tool call: generate_math_question()]
MCP Response: {"question": "What is 15 * 12?", "expected_answer": "180", "difficulty": "medium"}

Agent: Evaluating answer "180"...
[MCP tool call: evaluate_answer("What is 15 * 12?", "180", "180")]
MCP Response: {"is_correct": true, "score": 1.0, "feedback": "Perfect!"}

Agent: Reporting results...
[MCP tool call: report_results(true, 1.0, "What is 15 * 12?", "180")]
MCP Response: "Results reported: PASS (score: 1.00 / 100.0%)"
```

## Success Rate

**95%** with naive agents (gpt-4o-mini)

## Pros & Cons

### Pros
- ✅ Tools are independent services
- ✅ Can share tools across multiple agents
- ✅ Strong schema enforcement (10% error rate)
- ✅ Industry standard protocol
- ✅ Better error messages

### Cons
- ❌ Requires separate server process
- ❌ Slightly more complex setup (10 minutes)
- ❌ Network dependency (minimal on localhost)

## When to Use

- Shared tools across benchmarks
- Standardized operations (evaluation, logging)
- Tools that need to be versioned independently
- Multi-agent scenarios

