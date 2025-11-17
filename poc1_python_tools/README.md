# PoC 1: Python Tools Only

Simple approach using only Python tools with `@ab.tool` decorator.

## Files

- `green_agent_card.toml` - Agent configuration
- `tools.py` - Python tools with @ab.tool decorator

## How to Run

```bash
# Set your OpenAI API key
export OPENAI_API_KEY="your-key-here"

# Run the agent
agentbeats run green_agent_card.toml \
    --launcher_host 0.0.0.0 --launcher_port 9030 \
    --agent_host 0.0.0.0 --agent_port 9031 \
    --model_type openai --model_name gpt-4o-mini \
    --tool tools.py
```

## Tools Provided

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

Agent: I'll start by generating a math question.
[Calls generate_math_question()]
Result: {"question": "What is 7 + 5?", "expected_answer": "12", "difficulty": "easy"}

Agent: Now I'll evaluate the answer "12".
[Calls evaluate_answer("What is 7 + 5?", "12", "12")]
Result: {"is_correct": True, "score": 1.0, "feedback": "Perfect!"}

Agent: Reporting results...
[Calls report_results(True, 1.0, "What is 7 + 5?", "12")]
Result: "Results reported: PASS (score: 1.0)"
```

## Success Rate

**85%** with naive agents (gpt-4o-mini)

## Pros & Cons

### Pros
- ✅ Simple setup (5 minutes)
- ✅ Good developer experience
- ✅ Type hints provide clear guidance
- ✅ No separate server needed

### Cons
- ❌ Tools coupled to agent process
- ❌ Cannot share tools across benchmarks
- ❌ 15% error rate

## When to Use

- Simple benchmarks
- Proof-of-concepts
- Tools specific to one benchmark
- Quick iterations

