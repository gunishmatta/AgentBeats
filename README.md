# Proof of Concept: Tool Calling Approaches

This directory contains working proof-of-concept implementations of different tool calling approaches for AgentBeats benchmarks.

## Quick Start

See **[COMPARISON.md](COMPARISON.md)** for detailed comparison and test results.

## Four Approaches

1. **PoC 1: Python Tools Only** (`poc1_python_tools/`) - Simple Python functions with `@ab.tool` decorator
2. **PoC 2: MCP Tools Only** (`poc2_mcp_tools/`) - Tools exposed via MCP server
3. **PoC 3: Text Descriptions Only** (`poc3_text_only/`) - No tools, agent simulates workflow
4. **PoC 4: Hybrid Approach** (`poc4_hybrid/`) - Combines MCP tools, Python tools, and detailed agent card

## 🏆 Latest Test Results

**Test Date:** November 17, 2025 | **Model:** gpt-4o-mini | **Runs:** 2 per PoC

| Approach | Success Rate | Avg Time | Tool Accuracy | Status |
|----------|-------------|----------|---------------|--------|
| **PoC 1: Python Tools** | **100%** ✅ | 26.8s | 100.0% | ⭐⭐⭐⭐⭐ |
| **PoC 2: MCP Tools** | **100%** ✅ | 25.8s | 100.0% | ⭐⭐⭐⭐⭐ |
| **PoC 3: Text Only** | **100%** ✅ | 2.7s | N/A | ⭐⭐⭐⭐ |
| **PoC 4: Hybrid** | **100%** ✅ | 30.5s | 100.0% | ⭐⭐⭐⭐⭐ |

### Key Findings

1. **All approaches achieved 100% success rate** - Including text-only!
2. **Text-only was surprisingly fastest** (2.7s) - Simple task, agent simulated well
3. **Tool-based approaches** provide validation and consistency (26-30s)
4. **Perfect tool accuracy** for all tool-based approaches (100%)

📄 **Full analysis:** See [COMPARISON.md](COMPARISON.md) and [RESULTS_SUMMARY.md](RESULTS_SUMMARY.md)

## Running the PoCs

### PoC 1: Python Tools Only (100% success)

```bash
cd poc1_python_tools
agentbeats run green_agent_card.toml \
    --launcher_host 0.0.0.0 --launcher_port 9030 \
    --agent_host 0.0.0.0 --agent_port 9031 \
    --model_type openai --model_name gpt-4o-mini \
    --tool tools.py
```

### PoC 2: MCP Tools Only (100% success)

**Terminal 1** - Start MCP Server:
```bash
cd poc2_mcp_tools
python mcp_server.py
```

**Terminal 2** - Start Agent:
```bash
cd poc2_mcp_tools
agentbeats run green_agent_card.toml \
    --launcher_host 0.0.0.0 --launcher_port 9031 \
    --agent_host 0.0.0.0 --agent_port 9032 \
    --model_type openai --model_name gpt-4o-mini \
    --mcp http://localhost:9005/sse
```

### PoC 3: Text Descriptions Only (100% success, fastest!)

```bash
cd poc3_text_only
agentbeats run green_agent_card.toml \
    --launcher_host 0.0.0.0 --launcher_port 9039 \
    --agent_host 0.0.0.0 --agent_port 9050 \
    --model_type openai --model_name gpt-4o-mini
```

### PoC 4: Hybrid Approach (100% success)

**Terminal 1** - Start MCP Server:
```bash
cd poc4_hybrid
python mcp_server.py
```

**Terminal 2** - Start Agent:
```bash
cd poc4_hybrid
agentbeats run green_agent_card.toml \
    --launcher_host 0.0.0.0 --launcher_port 9032 \
    --agent_host 0.0.0.0 --agent_port 9033 \
    --model_type openai --model_name gpt-4o-mini \
    --tool tools.py \
    --mcp http://localhost:9005/sse
```

## Testing

### Running Automated Tests

See `TEST_SCRIPT_README.md` for complete instructions.

Quick start:
1. Start agents manually (see above)
2. Run test script: `python test_poc_results.py --runs 10 --poc all`
3. Review results in `poc_test_results.json`

### Test Scripts

- **`test_poc_results.py`**: Main test script that sends queries and collects metrics
- **`run_poc_tests.py`**: Alternative test runner (more complex, auto-starts agents)

## Documentation

- **[COMPARISON.md](COMPARISON.md)** - Comprehensive comparison with actual test results
- **[TEST_SCRIPT_README.md](TEST_SCRIPT_README.md)** - Guide for running tests
- **`poc_test_results.json`** - Detailed test results data

## Recommendation

See [COMPARISON.md](COMPARISON.md) for detailed recommendations. In summary:

- **Simple benchmarks**: Use PoC 1 (Python Tools Only)
- **Shared tools**: Use PoC 2 (MCP Tools Only)
- **Production benchmarks**: Use PoC 4 (Hybrid Approach)

