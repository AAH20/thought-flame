"""
thought-flame: Visual Flamegraph & Cognitive Uncertainty Profiler for Agent Extended Thinking Traces.
"""

from .models import (
    CognitivePhase,
    FlameSpan,
    FlameProfile,
)
from .profiler import TraceProfiler
from .renderer import FlameRenderer

__version__ = "0.1.0"
__all__ = [
    "CognitivePhase",
    "FlameSpan",
    "FlameProfile",
    "TraceProfiler",
    "FlameRenderer",
]
