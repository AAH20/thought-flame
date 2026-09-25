"""
Data models and flamegraph span definitions for Thought-Flame.
Visual Flamegraph & Cognitive Uncertainty Profiler for Agent Extended Thinking Traces.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any
import time


class CognitivePhase(str, Enum):
    HYPOTHESIS = "HYPOTHESIS"
    PLANNING = "PLANNING"
    BACKTRACKING = "BACKTRACKING"
    TOOL_DETERMINATION = "TOOL_DETERMINATION"
    EVALUATION = "EVALUATION"


@dataclass
class FlameSpan:
    span_id: str
    phase: CognitivePhase
    summary: str
    text_snippet: str
    start_char: int
    end_char: int
    token_count: int
    uncertainty_score: float = 0.0  # 0.0 (certain) to 1.0 (high hesitation)
    is_backtracking: bool = False
    children: List['FlameSpan'] = field(default_factory=list)


@dataclass
class FlameProfile:
    total_tokens: int
    backtrack_count: int
    avg_uncertainty: float
    spans: List[FlameSpan] = field(default_factory=list)
    tool_parameter_lineage: Dict[str, str] = field(default_factory=dict)
    profiling_latency_ms: float = 0.0
