#!/usr/bin/env python3
"""
Simplified PoC Test Script

This script provides a simpler way to test PoCs by:
1. Starting agents manually (or checking if they're running)
2. Sending test queries via A2A protocol
3. Collecting and analyzing results

Usage:
    # First, start agents manually in separate terminals:
    # Terminal 1: python poc2_mcp_tools/mcp_server.py
    # Terminal 2: agentbeats run poc1_python_tools/green_agent_card.toml ...
    
    # Then run this script:
    python test_poc_results.py --runs 5
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import requests

try:
    from a2a.client import A2AClient, A2ACardResolver
    from a2a.types import Message, Part, TextPart, Role, MessageSendParams, SendStreamingMessageRequest
    import httpx
except ImportError:
    print("⚠️  a2a library not found. Install with: pip install a2a")
    sys.exit(1)

@dataclass
class TestResult:
    """Results from a single test run"""
    poc_name: str
    run_number: int
    success: bool
    error_type: Optional[str]
    error_message: Optional[str]
    tool_calls_detected: List[str]
    expected_tools: List[str]
    response_time: float
    response_text: str
    timestamp: str

@dataclass
class POCMetrics:
    """Aggregated metrics for a PoC"""
    poc_name: str
    total_runs: int
    successful_runs: int
    failed_runs: int
    success_rate: float
    error_rate: float
    avg_response_time: float
    tool_calling_accuracy: float
    common_errors: Dict[str, int]

# PoC configurations
POC_CONFIGS = {
    "PoC 1: Python Tools": {
        "url": "http://localhost:9031",
        "expected_tools": ["generate_math_question", "evaluate_answer", "report_results"],
        "test_query": "Run the math quiz benchmark. Generate a question, evaluate an answer, and report the results."
    },
    "PoC 2: MCP Tools": {
        "url": "http://localhost:9032",
        "expected_tools": ["generate_math_question", "evaluate_answer", "report_results"],
        "test_query": "Run the math quiz benchmark using MCP tools. Generate a question, evaluate an answer, and report the results."
    },
    "PoC 4: Hybrid": {
        "url": "http://localhost:9033",
        "expected_tools": ["generate_math_question", "evaluate_answer_mcp", "report_results_mcp"],
        "test_query": "Run the math quiz benchmark using the hybrid approach. Follow the workflow: generate a question, evaluate an answer, and report the results."
    }
}

def check_agent_available(url: str) -> bool:
    """Check if agent is available"""
    try:
        response = requests.get(f"{url}/.well-known/agent.json", timeout=3)
        return response.status_code == 200
    except:
        return False

def send_query_to_agent(url: str, query: str) -> Tuple[bool, str, float]:
    """Send a query to agent using A2A protocol"""
    try:
        start_time = time.time()
        
        async def _send():
            async with httpx.AsyncClient() as client:
                resolver = A2ACardResolver(httpx_client=client, base_url=url)
                card = await resolver.get_agent_card("/.well-known/agent.json")
                
                if not card:
                    return False, "Failed to resolve agent card", 0.0
                
                a2a_client = A2AClient(httpx_client=client, agent_card=card)
                
                params = MessageSendParams(
                    message=Message(
                        role=Role.user,
                        parts=[Part(TextPart(text=query))],
                        messageId="test-" + str(int(time.time())),
                        taskId=None,
                    )
                )
                
                req = SendStreamingMessageRequest(id="test-request", params=params)
                chunks = []
                
                async for chunk in a2a_client.send_message_streaming(req):
                    if hasattr(chunk, 'root') and hasattr(chunk.root, 'result'):
                        result = chunk.root.result
                        if hasattr(result, 'artifact') and result.artifact:
                            for p in result.artifact.parts:
                                if hasattr(p, 'root') and isinstance(p.root, TextPart):
                                    chunks.append(p.root.text)
                        elif hasattr(result, 'status') and result.status:
                            if result.status.message:
                                for p in result.status.message.parts:
                                    if hasattr(p, 'root') and isinstance(p.root, TextPart):
                                        chunks.append(p.root.text)
                
                response_time = time.time() - start_time
                response_text = "".join(chunks).strip() or "No response"
                
                return True, response_text, response_time
        
        import asyncio
        return asyncio.run(_send())
        
    except Exception as e:
        response_time = time.time() - start_time
        return False, f"Error: {str(e)}", response_time

def analyze_response(response_text: str, expected_tools: List[str]) -> Tuple[List[str], bool]:
    """Analyze response to detect tool calls"""
    tool_calls = []
    response_lower = response_text.lower()
    
    # Look for tool names in response
    for tool in expected_tools:
        tool_variants = [
            tool.lower(),
            tool.lower().replace("_", " "),
            tool.lower().replace("_", ""),
        ]
        for variant in tool_variants:
            if variant in response_lower:
                if tool not in tool_calls:
                    tool_calls.append(tool)
                break
    
    # Check if we found most expected tools (80% threshold)
    found_ratio = len(tool_calls) / len(expected_tools) if expected_tools else 0
    success = found_ratio >= 0.8
    
    return tool_calls, success

def run_test(poc_name: str, config: dict, run_number: int) -> TestResult:
    """Run a single test"""
    print(f"\n{'='*60}")
    print(f"Test {run_number}: {poc_name}")
    print(f"{'='*60}")
    
    url = config["url"]
    query = config["test_query"]
    expected_tools = config["expected_tools"]
    
    # Check if agent is available
    if not check_agent_available(url):
        print(f"❌ Agent not available at {url}")
        print(f"   Please start the agent first!")
        return TestResult(
            poc_name=poc_name,
            run_number=run_number,
            success=False,
            error_type="agent_unavailable",
            error_message=f"Agent not running at {url}",
            tool_calls_detected=[],
            expected_tools=expected_tools,
            response_time=0.0,
            response_text="",
            timestamp=datetime.now().isoformat()
        )
    
    print(f"✅ Agent available at {url}")
    print(f"📤 Sending query: {query[:60]}...")
    
    # Send query
    success, response_text, response_time = send_query_to_agent(url, query)
    
    if not success:
        print(f"❌ Failed to get response")
        return TestResult(
            poc_name=poc_name,
            run_number=run_number,
            success=False,
            error_type="request_failed",
            error_message=response_text[:200],
            tool_calls_detected=[],
            expected_tools=expected_tools,
            response_time=response_time,
            response_text=response_text[:500],
            timestamp=datetime.now().isoformat()
        )
    
    # Analyze response
    tool_calls, tools_success = analyze_response(response_text, expected_tools)
    
    overall_success = success and tools_success
    
    error_type = None
    error_message = None
    
    if not tools_success:
        error_type = "tool_calling_incomplete"
        error_message = f"Expected {len(expected_tools)} tools, detected {len(tool_calls)}"
    
    result = TestResult(
        poc_name=poc_name,
        run_number=run_number,
        success=overall_success,
        error_type=error_type,
        error_message=error_message,
        tool_calls_detected=tool_calls,
        expected_tools=expected_tools,
        response_time=response_time,
        response_text=response_text[:1000],  # Truncate
        timestamp=datetime.now().isoformat()
    )
    
    status = "✅ SUCCESS" if overall_success else "❌ FAILED"
    print(f"Result: {status}")
    print(f"Tools detected: {len(tool_calls)}/{len(expected_tools)}")
    print(f"  Found: {', '.join(tool_calls) if tool_calls else 'none'}")
    print(f"Response time: {response_time:.2f}s")
    
    return result

def calculate_metrics(results: List[TestResult]) -> POCMetrics:
    """Calculate aggregated metrics"""
    if not results:
        return POCMetrics(
            poc_name="Unknown",
            total_runs=0,
            successful_runs=0,
            failed_runs=0,
            success_rate=0.0,
            error_rate=0.0,
            avg_response_time=0.0,
            tool_calling_accuracy=0.0,
            common_errors={}
        )
    
    poc_name = results[0].poc_name
    total_runs = len(results)
    successful_runs = sum(1 for r in results if r.success)
    failed_runs = total_runs - successful_runs
    
    success_rate = (successful_runs / total_runs * 100) if total_runs > 0 else 0.0
    error_rate = (failed_runs / total_runs * 100) if total_runs > 0 else 0.0
    
    avg_response_time = sum(r.response_time for r in results) / total_runs if total_runs > 0 else 0.0
    
    # Calculate tool calling accuracy
    total_expected = sum(len(r.expected_tools) for r in results)
    total_detected = sum(len(r.tool_calls_detected) for r in results)
    tool_calling_accuracy = (total_detected / total_expected * 100) if total_expected > 0 else 0.0
    
    # Count common errors
    common_errors = {}
    for r in results:
        if r.error_type:
            common_errors[r.error_type] = common_errors.get(r.error_type, 0) + 1
    
    return POCMetrics(
        poc_name=poc_name,
        total_runs=total_runs,
        successful_runs=successful_runs,
        failed_runs=failed_runs,
        success_rate=success_rate,
        error_rate=error_rate,
        avg_response_time=avg_response_time,
        tool_calling_accuracy=tool_calling_accuracy,
        common_errors=common_errors
    )

def generate_report(all_results: Dict[str, List[TestResult]], output_file: str):
    """Generate comprehensive test report"""
    print(f"\n{'='*80}")
    print("GENERATING TEST REPORT")
    print(f"{'='*80}\n")
    
    report = {
        "test_date": datetime.now().isoformat(),
        "summary": {},
        "detailed_results": {}
    }
    
    # Calculate metrics for each PoC
    for poc_name, results in all_results.items():
        metrics = calculate_metrics(results)
        report["summary"][poc_name] = asdict(metrics)
        report["detailed_results"][poc_name] = [asdict(r) for r in results]
    
    # Write JSON report
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    print("=" * 80)
    print("TEST RESULTS SUMMARY")
    print("=" * 80)
    print()
    
    for poc_name, results in all_results.items():
        metrics = calculate_metrics(results)
        print(f"\n{poc_name}")
        print("-" * 60)
        print(f"  Total Runs:        {metrics.total_runs}")
        print(f"  Successful:        {metrics.successful_runs} ({metrics.success_rate:.1f}%)")
        print(f"  Failed:             {metrics.failed_runs} ({metrics.error_rate:.1f}%)")
        print(f"  Avg Response Time: {metrics.avg_response_time:.2f}s")
        print(f"  Tool Accuracy:     {metrics.tool_calling_accuracy:.1f}%")
        
        if metrics.common_errors:
            print(f"  Common Errors:")
            for error, count in metrics.common_errors.items():
                print(f"    - {error}: {count}")
    
    print("\n" + "=" * 80)
    print(f"Full report saved to: {output_file}")
    print("=" * 80)

def main():
    parser = argparse.ArgumentParser(
        description="Test PoC implementations and collect metrics",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example usage:

1. Start agents manually in separate terminals:

   # For PoC 1 (Python Tools):
   cd poc_tool_approaches/poc1_python_tools
   agentbeats run green_agent_card.toml \\
       --launcher_host 0.0.0.0 --launcher_port 9030 \\
       --agent_host 0.0.0.0 --agent_port 9031 \\
       --model_type openai --model_name gpt-4o-mini \\
       --tool tools.py

   # For PoC 2 (MCP Tools):
   # Terminal 1: Start MCP server
   cd poc_tool_approaches/poc2_mcp_tools
   python mcp_server.py
   
   # Terminal 2: Start agent
   agentbeats run green_agent_card.toml \\
       --launcher_host 0.0.0.0 --launcher_port 9031 \\
       --agent_host 0.0.0.0 --agent_port 9032 \\
       --model_type openai --model_name gpt-4o-mini \\
       --mcp http://localhost:9005/sse

   # For PoC 4 (Hybrid):
   # Terminal 1: Start MCP server
   cd poc_tool_approaches/poc4_hybrid
   python mcp_server.py
   
   # Terminal 2: Start agent
   agentbeats run green_agent_card.toml \\
       --launcher_host 0.0.0.0 --launcher_port 9032 \\
       --agent_host 0.0.0.0 --agent_port 9033 \\
       --model_type openai --model_name gpt-4o-mini \\
       --tool tools.py \\
       --mcp http://localhost:9005/sse

2. Then run this script:
   python test_poc_results.py --runs 5 --poc all
        """
    )
    
    parser.add_argument("--runs", type=int, default=5, help="Number of test runs per PoC")
    parser.add_argument("--poc", type=str, choices=["1", "2", "4", "all"], default="all",
                       help="Which PoC to test (1, 2, 4, or all)")
    parser.add_argument("--output", type=str, default="poc_test_results.json",
                       help="Output file for results")
    
    args = parser.parse_args()
    
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ ERROR: OPENAI_API_KEY environment variable not set")
        print("   Please set it with: export OPENAI_API_KEY='your-key-here'")
        sys.exit(1)
    
    print("=" * 80)
    print("PoC TEST RUNNER")
    print("=" * 80)
    print(f"Runs per PoC: {args.runs}")
    print(f"Testing: {args.poc}")
    print("\n⚠️  Make sure agents are running before starting tests!")
    print("   See --help for instructions on starting agents.")
    print("=" * 80)
    
    # Select PoCs to test
    pocs_to_test = {}
    if args.poc in ["1", "all"]:
        pocs_to_test["PoC 1: Python Tools"] = POC_CONFIGS["PoC 1: Python Tools"]
    if args.poc in ["2", "all"]:
        pocs_to_test["PoC 2: MCP Tools"] = POC_CONFIGS["PoC 2: MCP Tools"]
    if args.poc in ["4", "all"]:
        pocs_to_test["PoC 4: Hybrid"] = POC_CONFIGS["PoC 4: Hybrid"]
    
    all_results = {}
    
    try:
        for poc_name, config in pocs_to_test.items():
            print(f"\n{'='*80}")
            print(f"Testing {poc_name}")
            print(f"{'='*80}")
            
            results = []
            for run_num in range(1, args.runs + 1):
                result = run_test(poc_name, config, run_num)
                results.append(result)
                if run_num < args.runs:
                    time.sleep(2)  # Brief pause between tests
            
            all_results[poc_name] = results
        
        # Generate report
        output_path = Path(__file__).parent / args.output
        generate_report(all_results, str(output_path))
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

