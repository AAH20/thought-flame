"""
Unit tests for Thought-Flame trace profiling and flamegraph rendering.
"""

import unittest
from thought_flame.models import CognitivePhase
from thought_flame.profiler import TraceProfiler
from thought_flame.renderer import FlameRenderer


class TestThoughtFlame(unittest.TestCase):

    def test_trace_profiling_and_phases(self):
        trace = """
        <thinking>
        First, we should inspect the bug in service.py.
        Wait, let me rethink: the error is actually in the database schema.
        I will call tool read_file with path="schema.sql".
        </thinking>
        """
        profile = TraceProfiler.profile_trace(trace)
        self.assertEqual(len(profile.spans), 3)

        phases = [s.phase for s in profile.spans]
        self.assertEqual(phases[0], CognitivePhase.PLANNING)
        self.assertEqual(phases[1], CognitivePhase.BACKTRACKING)
        self.assertEqual(phases[2], CognitivePhase.TOOL_DETERMINATION)

        self.assertEqual(profile.backtrack_count, 1)

    def test_uncertainty_scoring(self):
        confident_trace = "The test fails at line 42 with KeyError."
        profile_conf = TraceProfiler.profile_trace(confident_trace)
        self.assertEqual(profile_conf.spans[0].uncertainty_score, 0.0)

        hesitant_trace = "Maybe this might perhaps be a race condition, but it is unclear."
        profile_hes = TraceProfiler.profile_trace(hesitant_trace)
        self.assertGreater(profile_hes.spans[0].uncertainty_score, 0.5)

    def test_renderers(self):
        trace = "First, check config. Wait, scratch that. Run command."
        profile = TraceProfiler.profile_trace(trace)

        ascii_out = FlameRenderer.render_ascii_flame(profile)
        self.assertIn("THOUGHT-FLAME", ascii_out)
        self.assertIn("BACKTRACK", ascii_out)

        html_out = FlameRenderer.render_html_dashboard(profile)
        self.assertIn("<!DOCTYPE html>", html_out)
        self.assertIn("flamegraph", html_out.lower())


if __name__ == "__main__":
    unittest.main()
