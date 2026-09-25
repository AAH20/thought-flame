"""
CLI interface and interactive demonstration runner for Thought-Flame.
"""

import sys
import argparse
from .profiler import TraceProfiler
from .renderer import FlameRenderer


def run_demo():
    print("=" * 74)
    print("  THOUGHT-FLAME: Cognitive Flamegraph Profiler for AI Reasoning")
    print("  Visualizing Uncertainty & Backtracking in Claude Opus 5.5 & GPT-6 Astra")
    print("=" * 74)

    sample_thinking_trace = """
    <thinking>
    Step 1: Inspect the reported database transaction deadlock on user checkout.
    First, we need to examine table row locking order in the PostgreSQL schema.
    Maybe the problem is caused by unindexed foreign key lookups during peak write traffic.
    Wait, let me rethink that: the query logs indicate an exclusive table lock rather than row lock.
    This would fail if concurrent webhooks attempt migrations during checkout sessions.
    The plan is to check the connection pool settings in database.py.
    Perhaps we might assume an aggressive lock timeout will clear blocked workers.
    Actually, holding on: an aggressive timeout would cause cascade checkout aborts for users!
    Instead, we should add optimistic concurrency control with retry backoff.
    I will call tool bash with command to inspect lock queries, passing timeout=15 seconds.
    </thinking>
    """

    print("\n[STEP 1] PROFILING RAW EXTENDED THINKING TRACE")
    profile = TraceProfiler.profile_trace(sample_thinking_trace)

    print(f"  Total Estimated Tokens : {profile.total_tokens}")
    print(f"  Backtracking Points    : {profile.backtrack_count} (Dead-End Paths Pruned)")
    print(f"  Average Uncertainty    : {profile.avg_uncertainty:.2f} (Hesitation Index)")
    print(f"  Profiling Duration     : {profile.profiling_latency_ms:.3f} ms")

    if profile.tool_parameter_lineage:
        print("\n[STEP 2] TOOL PARAMETER CAUSAL LINEAGE")
        for param, sentence in profile.tool_parameter_lineage.items():
            print(f"  * Parameter `{param}` derived from: \"{sentence}\"")

    print("\n[STEP 3] TERMINAL COGNITIVE FLAME TIMELINE:")
    print("-" * 74)
    ascii_flame = FlameRenderer.render_ascii_flame(profile)
    print(ascii_flame)
    print("-" * 74)

    html_out = FlameRenderer.render_html_dashboard(profile)
    print(f"\n[STEP 4] INTERACTIVE HTML FLAMEGRAPH GENERATED ({len(html_out)} bytes)")
    print("  Saved in-memory visual flamegraph. Ready for observability dashboard export.")

    print("\n" + "=" * 74)
    print("  THOUGHT-FLAME PROFILING COMPLETE: 100% REASONING TRANSPARENCY")
    print("=" * 74 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="thought-flame: Visual Flamegraph & Cognitive Uncertainty Profiler"
    )
    subparsers = parser.add_subparsers(dest="command")
    demo_parser = subparsers.add_parser("demo", help="Run interactive thought flamegraph demonstration")

    args = parser.parse_args()
    if args.command == "demo" or len(sys.argv) == 1:
        run_demo()


if __name__ == "__main__":
    main()
