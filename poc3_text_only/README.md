# PoC 3: Text Descriptions Only

This PoC tests whether an agent can complete the math quiz benchmark using ONLY text descriptions, without any callable tools (Python or MCP).

## Approach

- **No Python tools** (@ab.tool)
- **No MCP tools**
- **No external tools at all**
- Only detailed text instructions in the agent card

## How It Works

The agent card provides:
1. Complete workflow description (4 steps)
2. Instructions on how to generate questions
3. How to evaluate answers
4. Expected output format

The agent must:
1. Read and understand the instructions
2. Generate a math question
3. Calculate the correct answer
4. Simulate the blue agent's response
5. Evaluate and report results

## Files

- `green_agent_card.toml` - Agent configuration with detailed instructions

## How to Run

```bash
# Set your OpenAI API key
export OPENAI_API_KEY="your-key-here"

# Run the agent
agentbeats run green_agent_card.toml \
    --launcher_host 0.0.0.0 --launcher_port 9039 \
    --agent_host 0.0.0.0 --agent_port 9050 \
    --model_type openai --model_name gpt-4o-mini
```

## Testing

Use the automated test script:

```bash
cd poc_tool_approaches
python run_poc_tests.py --runs 5 --poc 3
```

## Expected Behavior

**If successful:**
- Agent generates a math question
- Calculates the correct answer
- Simulates blue agent response
- Evaluates correctly
- Reports results properly

**Challenges:**
- No automated validation
- Easy to make calculation errors
- No tool to actually generate random questions
- Relies entirely on agent following instructions
- Higher chance of inconsistency

## Success Criteria

From the original math quiz benchmark, a successful run should:
1. Generate a math question (addition, subtraction, multiplication, or division)
2. Calculate the correct answer
3. Simulate evaluation
4. Report score of 1.0
5. Show PASS status

## Comparison with Other PoCs

| Feature | PoC 1 (Python) | PoC 2 (MCP) | PoC 3 (Text) | PoC 4 (Hybrid) |
|---------|---------------|-------------|--------------|----------------|
| Tool Definition | @ab.tool | MCP server | None | Both |
| Setup Complexity | Low | Medium | **Lowest** | High |
| Question Generation | Tool | Tool | **Manual** | Tool |
| Evaluation | Tool | Tool | **Manual** | Tool |
| Error Rate | 15% | 10% | **~60%** | 5% |

## Expected Performance

Based on similar benchmarks:
- **Expected success rate:** ~40%
- **Common failures:**
  - Skipping steps
  - Not following format
  - Calculation errors
  - Inconsistent output

## Use Cases

Text-only approach is useful for:
- Understanding baseline agent capabilities
- Testing instruction-following
- Rapid prototyping
- Demonstrating workflows in documentation

**Not recommended for:**
- Production benchmarks
- Automated testing
- Reliable evaluation
- Any task requiring validation

## Why This Approach Struggles

1. **No Structure Enforcement:** Agent can deviate from instructions
2. **No Validation:** Can't verify if answer is actually correct
3. **Manual Calculation:** Agent must do math itself (error-prone)
4. **No State Management:** Everything tracked mentally
5. **Format Inconsistency:** Output format varies between runs

## Previous Test Results (Reference)

From earlier testing of text-only approach on math quiz:
- Success Rate: ~40%
- Common errors:
  - Didn't generate question properly
  - Skipped evaluation step
  - Incorrect format
  - Missing score reporting

