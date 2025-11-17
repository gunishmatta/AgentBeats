# PoC 3: Text Descriptions Only (Complex Benchmark)

This PoC tests whether an agent can complete the complex multi-step orchestration benchmark using ONLY text descriptions, without any callable tools (Python or MCP).

## Approach

- **No Python tools** (@ab.tool)
- **No MCP tools**
- **No external tools at all**
- Only detailed text instructions in the agent card

## How It Works

The agent card provides:
1. Complete task description (5 steps with dependencies)
2. All questions and expected answers
3. Workflow instructions to simulate tool calling
4. Expected output format

The agent must:
1. Read and understand the instructions
2. Simulate the entire workflow in text
3. Process each step sequentially
4. Track progress manually
5. Generate final report

## Files

- `green_agent_card.toml` - Agent configuration with detailed instructions

## How to Run

```bash
# Set your OpenAI API key
export OPENAI_API_KEY="your-key-here"

# Run the agent
agentbeats run green_agent_card.toml \
    --launcher_host 0.0.0.0 --launcher_port 9033 \
    --agent_host 0.0.0.0 --agent_port 9044 \
    --model_type openai --model_name gpt-4o-mini
```

## Testing

Use the automated test script:

```bash
cd poc_tool_approaches/complex_benchmark
python test_complex_benchmark.py --runs 5 --poc 3
```

## Expected Behavior

**If successful:**
- Agent follows instructions exactly
- Completes all 5 steps in order
- Provides the correct answers (given in instructions)
- Tracks progress accurately
- Generates comprehensive final report

**Challenges:**
- No automated validation (agent must self-validate)
- Easy for agent to skip steps
- No enforcement of workflow
- Relies entirely on agent following instructions
- Higher cognitive load than callable tools

## Success Criteria

1. Mentions all 5 steps
2. Provides correct answer for each step
3. Tracks progress (1/5, 2/5, etc.)
4. Reports final score of 80.0
5. Shows completion status

## Comparison with Other PoCs

| Feature | PoC 1 (Python) | PoC 2 (MCP) | PoC 3 (Text) | PoC 4 (Hybrid) |
|---------|---------------|-------------|--------------|----------------|
| Tool Definition | @ab.tool | MCP server | None | Both |
| Setup Complexity | Low | Medium | **Lowest** | High |
| Agent Guidance | High | High | **Medium** | High |
| Validation | Automatic | Automatic | **Manual** | Automatic |
| State Management | Built-in | Built-in | **Manual** | Both |

## Expected Performance

Based on simple math quiz results:
- **Simple tasks:** ~40% success (very poor)
- **Complex tasks:** Expected < 20% (too complex without tools)

This approach is expected to struggle with:
- Multi-step coordination
- Dependency management
- State tracking
- Consistent execution

## Use Cases

Text-only approach is useful for:
- Understanding agent capabilities without tools
- Testing instruction-following
- Rapid prototyping of workflows
- Documentation and examples

**Not recommended for:**
- Production benchmarks
- Complex multi-step tasks
- Tasks requiring validation
- Tasks with external dependencies

