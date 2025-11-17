# PoC Test Script - Usage Guide

This directory contains scripts to run actual tests.

## Quick Start

### 1. Install Dependencies

```bash
# Make sure you have agentbeats installed
pip install agentbeats

# Install A2A client for testing
pip install a2a httpx
```

### 2. Set Environment Variable

```bash
export OPENAI_API_KEY="your-openai-api-key-here"
```

### 3. Start Agents Manually

You need to start each PoC's agent in separate terminals before running tests.

#### PoC 1: Python Tools Only

```bash
cd poc_tool_approaches/poc1_python_tools

agentbeats run green_agent_card.toml \
    --launcher_host 0.0.0.0 --launcher_port 9030 \
    --agent_host 0.0.0.0 --agent_port 9031 \
    --model_type openai --model_name gpt-4o-mini \
    --tool tools.py
```

#### PoC 2: MCP Tools Only

**Terminal 1** - Start MCP Server:
```bash
cd poc_tool_approaches/poc2_mcp_tools
python mcp_server.py
```

**Terminal 2** - Start Agent:
```bash
cd poc_tool_approaches/poc2_mcp_tools

agentbeats run green_agent_card.toml \
    --launcher_host 0.0.0.0 --launcher_port 9031 \
    --agent_host 0.0.0.0 --agent_port 9032 \
    --model_type openai --model_name gpt-4o-mini \
    --mcp http://localhost:9005/sse
```

#### PoC 4: Hybrid Approach

**Terminal 1** - Start MCP Server:
```bash
cd poc_tool_approaches/poc4_hybrid
python mcp_server.py
```

**Terminal 2** - Start Agent:
```bash
cd poc_tool_approaches/poc4_hybrid

agentbeats run green_agent_card.toml \
    --launcher_host 0.0.0.0 --launcher_port 9032 \
    --agent_host 0.0.0.0 --agent_port 9033 \
    --model_type openai --model_name gpt-4o-mini \
    --tool tools.py \
    --mcp http://localhost:9005/sse
```

### 4. Run Tests

Once all agents are running, execute the test script:

```bash
cd poc_tool_approaches

# Test all PoCs
python test_poc_results.py --runs 10 --poc all

# Test specific PoC
python test_poc_results.py --runs 5 --poc 1
python test_poc_results.py --runs 5 --poc 2
python test_poc_results.py --runs 5 --poc 4
```

## Script Options

```bash
python test_poc_results.py --help
```

Options:
- `--runs N`: Number of test runs per PoC (default: 5)
- `--poc {1,2,4,all}`: Which PoC to test (default: all)
- `--output FILE`: Output file for results (default: poc_test_results.json)

## What Gets Tested

For each PoC, the script:

1. **Sends Test Query**: Sends a standardized query asking the agent to run the benchmark
2. **Collects Response**: Captures the agent's response via A2A protocol
3. **Analyzes Tool Calls**: Detects which tools were called
4. **Measures Metrics**:
   - Success rate (completes workflow)
   - Error rate (fails or incomplete)
   - Tool calling accuracy (expected vs actual tools)
   - Response time
   - Common error types

## Output

The script generates:

1. **Console Output**: Real-time progress and summary
2. **JSON Report**: Detailed results in `poc_test_results.json`

### Example Output

```
================================================================================
TEST RESULTS SUMMARY
================================================================================

PoC 1: Python Tools
------------------------------------------------------------
  Total Runs:        10
  Successful:        8 (80.0%)
  Failed:            2 (20.0%)
  Avg Response Time: 3.45s
  Tool Accuracy:     85.0%
  Common Errors:
    - tool_calling_incomplete: 2

PoC 2: MCP Tools
------------------------------------------------------------
  Total Runs:        10
  Successful:        9 (90.0%)
  Failed:            1 (10.0%)
  Avg Response Time: 3.12s
  Tool Accuracy:     93.3%
  Common Errors:
    - tool_calling_incomplete: 1

PoC 4: Hybrid
------------------------------------------------------------
  Total Runs:        10
  Successful:        10 (100.0%)
  Failed:            0 (0.0%)
  Avg Response Time: 2.98s
  Tool Accuracy:     100.0%
```

## Metrics Explained

### Success Rate
Percentage of runs where the agent:
- Successfully completed the workflow
- Called all expected tools
- Produced valid output

### Error Rate
Percentage of runs that failed due to:
- Incomplete tool calls
- Request timeouts
- Agent unavailability

### Tool Calling Accuracy
Percentage of expected tools that were actually called:
- 100% = All expected tools called
- 80%+ = Most tools called (acceptable)
- <80% = Missing critical tools

### Response Time
Average time for agent to complete the benchmark workflow.

## Troubleshooting

### Agent Not Available
```
❌ Agent not available at http://localhost:9031
   Please start the agent first!
```

**Solution**: Make sure the agent is running in a separate terminal.

### MCP Server Not Running
If testing PoC 2 or PoC 4, make sure the MCP server is running first.

### Timeout Errors
If you see timeout errors:
- Check that agents are actually running
- Verify ports are not in use
- Try increasing timeout in script

### Import Errors
If you see import errors:
```bash
pip install a2a httpx
```

## Interpreting Results

### Good Results
- ✅ Success rate > 90%
- ✅ Tool accuracy > 90%
- ✅ Low error rate (< 10%)

### Needs Improvement
- ⚠️ Success rate 70-90%
- ⚠️ Tool accuracy 70-90%
- ⚠️ Error rate 10-30%

### Poor Results
- ❌ Success rate < 70%
- ❌ Tool accuracy < 70%
- ❌ Error rate > 30%

## Next Steps

After running tests:

1. **Review JSON Report**: Check `poc_test_results.json` for detailed results
2. **Compare PoCs**: See which approach performs best
3. **Identify Issues**: Look at common errors to improve agent cards
4. **Iterate**: Update agent cards or tools based on findings

## Notes

- Tests require agents to be running before execution
- Each test run sends a real query to the agent
- Results may vary based on model and API conditions
- For consistent results, run multiple times and average

