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

## Automated Testing

### Running `test_complex_benchmark.py`

This script automatically starts agents, runs the complex benchmark, and collects metrics.

**Prerequisites:**
```bash
pip install a2a httpx fastmcp agentbeats
export OPENAI_API_KEY="your-key"
```

**Usage:**
```bash
cd poc_tool_approaches/complex_benchmark

# Test all PoCs (auto-starts agents)
python test_complex_benchmark.py --runs 5 --poc all

# Test specific PoC
python test_complex_benchmark.py --runs 3 --poc 1  # Python tools
python test_complex_benchmark.py --runs 3 --poc 2  # MCP tools
python test_complex_benchmark.py --runs 3 --poc 3  # Text only
python test_complex_benchmark.py --runs 3 --poc 4  # Hybrid

# Use different model
python test_complex_benchmark.py --runs 5 --model gpt-4o

# Custom output file
python test_complex_benchmark.py --runs 5 --output my_results.json
```

**Output:** Results saved to `complex_benchmark_results.json` with success rates, step completion, scores, and tool accuracy.

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
