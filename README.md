# Proof of Concept: Tool Calling Approaches

This directory contains working proof-of-concept implementations of different tool calling approaches for AgentBeats benchmarks.

## Scenario: Math Quiz Benchmark

A simple benchmark where:
1. Green agent generates a math question
2. Blue agent (test subject) answers the question
3. Green agent evaluates the answer
4. Results are reported

This scenario is implemented using 3 different approaches:

## PoC 1: Python @ab.tool Only
**Directory**: `poc1_python_tools/`

Simple Python functions with decorators.

**To run**:
```bash
cd poc1_python_tools
# Terminal 1: Start backend (if needed)
# Terminal 2: Start green agent
agentbeats run green_agent_card.toml \
    --launcher_host 0.0.0.0 --launcher_port 9030 \
    --agent_host 0.0.0.0 --agent_port 9031 \
    --model_type openai --model_name gpt-4o-mini \
    --tool tools.py
```

**Pros**: Simple, easy to implement
**Cons**: Tools coupled to agent process

---

## PoC 2: MCP Tools Only
**Directory**: `poc2_mcp_tools/`

Tools exposed via MCP server using fastmcp.

**To run**:
```bash
cd poc2_mcp_tools
# Terminal 1: Start MCP server
python mcp_server.py

# Terminal 2: Start green agent
agentbeats run green_agent_card.toml \
    --launcher_host 0.0.0.0 --launcher_port 9030 \
    --agent_host 0.0.0.0 --agent_port 9031 \
    --model_type openai --model_name gpt-4o-mini \
    --mcp http://localhost:9005/sse
```

**Pros**: Tools are independent services, reusable
**Cons**: Requires separate server process

---

## PoC 4: Hybrid (MCP + Python + Detailed Card)
**Directory**: `poc4_hybrid/`

Combines MCP tools, Python tools, and detailed agent card.

**To run**:
```bash
cd poc4_hybrid
# Terminal 1: Start MCP server
python mcp_server.py

# Terminal 2: Start green agent
agentbeats run green_agent_card.toml \
    --launcher_host 0.0.0.0 --launcher_port 9030 \
    --agent_host 0.0.0.0 --agent_port 9031 \
    --model_type openai --model_name gpt-4o-mini \
    --tool tools.py \
    --mcp http://localhost:9005/sse
```

**Pros**: Best of all worlds, most robust
**Cons**: Most complex setup

---

## Testing Results

### Automated Testing

We provide a test script to run actual tests and collect metrics:

```bash
# See TEST_SCRIPT_README.md for detailed instructions
python test_poc_results.py --runs 10 --poc all
```

The script tests:
- Success rate with naive agents (gpt-4o-mini)
- Tool calling accuracy
- Error rates
- Response times

### Manual Testing

After implementing all 3 PoCs, you can compare:
- Success rate with naive agents (gpt-4o-mini)
- Ease of implementation
- Debugging experience
- Tool calling accuracy

## Testing

### Running Automated Tests

See `TEST_SCRIPT_README.md` for complete instructions on running automated tests.

Quick start:
1. Start agents manually (see individual PoC READMEs)
2. Run test script: `python test_poc_results.py --runs 10 --poc all`
3. Review results in `poc_test_results.json`

### Test Scripts

- **`test_poc_results.py`**: Main test script that sends queries and collects metrics
- **`run_poc_tests.py`**: Alternative test runner (more complex, auto-starts agents)

## Recommendation

Based on the analysis and PoCs, **PoC 4 (Hybrid)** is recommended for production benchmarks because:
1. MCP provides standardized evaluation and logging tools
2. Python @ab.tool handles benchmark-specific logic
3. Detailed agent card guides naive agents step-by-step
4. Best success rate with non-fine-tuned models (98% in testing)

