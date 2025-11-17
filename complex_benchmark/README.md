# Complex Benchmark: Multi-Step Task Orchestration

This benchmark tests tool calling approaches on a more complex scenario than the simple math quiz. It simulates a multi-step orchestration task similar to Cybench but without requiring Docker or external dependencies.

## Benchmark Scenario

The green agent orchestrates a multi-step task with:
1. **Task Setup** - Initialize a multi-step challenge
2. **Step Execution** - Present each step sequentially to a blue agent
3. **Step Evaluation** - Evaluate the blue agent's response for each step
4. **Progress Tracking** - Track completion across all steps
5. **Final Reporting** - Generate comprehensive results

## Complexity Features

- **Multiple sequential steps** (5 steps with dependencies)
- **Agent-to-agent communication** (green talks to blue)
- **Progress tracking** across steps
- **Complex evaluation logic** (partial credit, dependencies)
- **State management** (tracking which steps are complete)
- **Error handling** (timeouts, failures, retries)

## Four Approaches

1. **PoC 1: Python Tools Only** (`poc1_complex/`)
2. **PoC 2: MCP Tools Only** (`poc2_complex/`)
3. **PoC 3: Text Descriptions Only** (`poc3_complex/`)
4. **PoC 4: Hybrid Approach** (`poc4_complex/`)

## Running the Benchmark

See individual PoC directories for setup instructions.

## Testing

### Prerequisites

1. Install dependencies:
```bash
pip install a2a httpx fastmcp agentbeats
```

2. Set environment variable:
```bash
export OPENAI_API_KEY="your-openai-api-key"
```

### Running Tests

1. **Start Agents Manually** (in separate terminals):

#### PoC 1: Python Tools Only
```bash
cd poc_tool_approaches/complex_benchmark/poc1_complex
agentbeats run green_agent_card.toml \
    --launcher_host 0.0.0.0 --launcher_port 9040 \
    --agent_host 0.0.0.0 --agent_port 9041 \
    --model_type openai --model_name gpt-4o-mini \
    --tool tools.py
```

#### PoC 2: MCP Tools Only
**Terminal 1** - Start MCP Server:
```bash
cd poc_tool_approaches/complex_benchmark/poc2_complex
python mcp_server.py
```

**Terminal 2** - Start Agent:
```bash
cd poc_tool_approaches/complex_benchmark/poc2_complex
agentbeats run green_agent_card.toml \
    --launcher_host 0.0.0.0 --launcher_port 9041 \
    --agent_host 0.0.0.0 --agent_port 9042 \
    --model_type openai --model_name gpt-4o-mini \
    --mcp http://localhost:9006/sse
```

#### PoC 4: Hybrid Approach
**Terminal 1** - Start MCP Server:
```bash
cd poc_tool_approaches/complex_benchmark/poc4_complex
python mcp_server.py
```

**Terminal 2** - Start Agent:
```bash
cd poc_tool_approaches/complex_benchmark/poc4_complex
agentbeats run green_agent_card.toml \
    --launcher_host 0.0.0.0 --launcher_port 9042 \
    --agent_host 0.0.0.0 --agent_port 9043 \
    --model_type openai --model_name gpt-4o-mini \
    --tool tools.py \
    --mcp http://localhost:9007/sse
```

2. **Run Test Script**:
```bash
cd poc_tool_approaches/complex_benchmark

# Test all PoCs with default model (gpt-4o-mini)
python test_complex_benchmark.py --runs 5 --poc all

# Test with newer GPT model
python test_complex_benchmark.py --runs 5 --poc all --model gpt-4o

# Test specific PoC
python test_complex_benchmark.py --runs 3 --poc 4 --model gpt-4o
```

### Test Options

```bash
# Test all PoCs
python test_complex_benchmark.py --runs 5 --poc all

# Test specific PoC
python test_complex_benchmark.py --runs 3 --poc 1
python test_complex_benchmark.py --runs 3 --poc 2
python test_complex_benchmark.py --runs 3 --poc 3  # Text descriptions only
python test_complex_benchmark.py --runs 3 --poc 4

# Custom output file
python test_complex_benchmark.py --runs 5 --output my_results.json
```

### What Gets Tested

The test script validates:
- **Tool Calling**: Detects if expected tools are called
- **Step Completion**: Tracks how many steps (out of 5) are completed
- **Final Score**: Extracts final score from results
- **Response Time**: Measures time to complete benchmark
- **Success Rate**: Percentage of runs that complete successfully

### Success Criteria

A successful run should:
- Call at least 4 out of 6 expected tools
- Complete at least 3 out of 5 steps (ideally 5/5)
- Generate a final score
- Complete within reasonable time (< 5 minutes)

### Output

Results are saved to `complex_benchmark_results.json` with:
- Summary metrics per PoC
- Detailed results for each run
- Tool calling accuracy
- Step completion rates
- Final scores
