"""
Trace Profiling & Cognitive Entropy Engine for Thought-Flame.
"""

import re
import time
from typing import Dict, List, Tuple
from .models import CognitivePhase, FlameSpan, FlameProfile


BACKTRACK_TRIGGERS = [
    r"\bwait\b", r"\bon second thought\b", r"\blet me rethink\b",
    r"\bthis would fail\b", r"\balternatively\b", r"\bthat is incorrect\b",
    r"\bscratch that\b", r"\bholding on\b", r"\bactually\b"
]

TOOL_TRIGGERS = [
    r"\bi will call\b", r"\blet's invoke\b", r"\bpassing parameter\b",
    r"\btool_call\b", r"\bdispatching\b", r"\brun command\b"
]

PLANNING_TRIGGERS = [
    r"\bstep \d\b", r"\bfirst\b", r"\bsecondly\b", r"\bnext\b",
    r"\bwe need to\b", r"\bplan is to\b", r"\bgoal is\b"
]

HESITATION_WORDS = [
    "maybe", "might", "perhaps", "probably", "uncertain", "unclear",
    "doubt", "assume", "guess", "hesitate", "risk"
]


class TraceProfiler:
    """Profiles unstructured thinking traces into structured cognitive flame spans."""

    @staticmethod
    def profile_trace(raw_trace: str) -> FlameProfile:
        start_time = time.time()

        # Clean XML thinking tags if present
        clean_text = re.sub(r"</?thinking>", "", raw_trace).strip()

        # Split into analytical sentences/clauses
        sentences = [s.strip() for s in re.split(r"(?<=[.!?\n])\s+", clean_text) if s.strip()]

        spans: List[FlameSpan] = []
        backtrack_count = 0
        total_uncertainty = 0.0
        lineage_map: Dict[str, str] = {}

        current_offset = 0

        for idx, sentence in enumerate(sentences):
            sent_len = len(sentence)
            tokens_est = max(1, sent_len // 4)

            # 1. Detect Cognitive Phase
            phase = CognitivePhase.HYPOTHESIS
            is_backtracking = False

            if any(re.search(pat, sentence, re.IGNORECASE) for pat in BACKTRACK_TRIGGERS):
                phase = CognitivePhase.BACKTRACKING
                is_backtracking = True
                backtrack_count += 1
            elif any(re.search(pat, sentence, re.IGNORECASE) for pat in TOOL_TRIGGERS):
                phase = CognitivePhase.TOOL_DETERMINATION
                # Extract potential param assignment (e.g. limit=50)
                param_match = re.search(r"(\w+)\s*=\s*['\"]?([\w\d_]+)['\"]?", sentence)
                if param_match:
                    lineage_map[param_match.group(1)] = sentence
            elif any(re.search(pat, sentence, re.IGNORECASE) for pat in PLANNING_TRIGGERS):
                phase = CognitivePhase.PLANNING

            # 2. Compute Uncertainty Score
            lower_sent = sentence.lower()
            hedge_count = sum(1 for hw in HESITATION_WORDS if hw in lower_sent)
            uncertainty_score = min(1.0, hedge_count * 0.35)
            total_uncertainty += uncertainty_score

            summary = sentence[:60] + "..." if len(sentence) > 60 else sentence

            span = FlameSpan(
                span_id=f"span_{idx+1:03d}",
                phase=phase,
                summary=summary,
                text_snippet=sentence,
                start_char=current_offset,
                end_char=current_offset + sent_len,
                token_count=tokens_est,
                uncertainty_score=round(uncertainty_score, 2),
                is_backtracking=is_backtracking
            )

            spans.append(span)
            current_offset += sent_len + 1

        total_tokens = sum(s.token_count for s in spans)
        avg_uncertainty = round(total_uncertainty / max(1, len(spans)), 2)
        latency_ms = (time.time() - start_time) * 1000.0

        return FlameProfile(
            total_tokens=total_tokens,
            backtrack_count=backtrack_count,
            avg_uncertainty=avg_uncertainty,
            spans=spans,
            tool_parameter_lineage=lineage_map,
            profiling_latency_ms=latency_ms
        )
