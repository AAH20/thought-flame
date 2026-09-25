"""
Flamegraph Visualizer & HTML Exporter for Thought-Flame.
"""

from typing import List
from .models import CognitivePhase, FlameProfile, FlameSpan


class FlameRenderer:
    """Renders profile spans into terminal charts and interactive HTML dashboards."""

    PHASE_COLORS = {
        CognitivePhase.HYPOTHESIS: "#3b82f6",         # Blue
        CognitivePhase.PLANNING: "#10b981",           # Emerald Green
        CognitivePhase.BACKTRACKING: "#ef4444",       # Bright Red
        CognitivePhase.TOOL_DETERMINATION: "#8b5cf6", # Purple
        CognitivePhase.EVALUATION: "#f59e0b"          # Amber
    }

    @classmethod
    def render_ascii_flame(cls, profile: FlameProfile) -> str:
        """Renders terminal-friendly cognitive timeline flamegraph."""
        lines = [
            f"=== THOUGHT-FLAME COGNITIVE PROFILE ===",
            f"Total Tokens: {profile.total_tokens} | Backtracks: {profile.backtrack_count} | Avg Uncertainty: {profile.avg_uncertainty:.2f}\n"
        ]

        for s in profile.spans:
            width = max(3, min(25, s.token_count // 3))
            bar_char = "█" if not s.is_backtracking else "▓"
            bar = bar_char * width

            phase_label = f"[{s.phase.value[:10]:<10}]"
            flag = " [BACKTRACK]" if s.is_backtracking else ""
            uncertainty = f"(Uncertainty: {s.uncertainty_score:.2f})"

            lines.append(f"{s.span_id} {phase_label} {bar:<25} {flag:<12} {uncertainty} : {s.summary}")

        return "\n".join(lines)

    @classmethod
    def render_html_dashboard(cls, profile: FlameProfile, title: str = "Thought-Flame Reasoning Profile") -> str:
        """Generates self-contained interactive HTML flamegraph."""
        spans_html = []
        for s in profile.spans:
            color = cls.PHASE_COLORS.get(s.phase, "#6b7280")
            pct_width = max(5, min(100, int((s.token_count / max(1, profile.total_tokens)) * 100 * 3)))
            border = "border: 2px solid #dc2626;" if s.is_backtracking else "border: 1px solid rgba(255,255,255,0.1);"

            spans_html.append(f"""
            <div style="background: {color}; width: {pct_width}%; min-width: 140px; margin: 4px; padding: 8px; border-radius: 6px; {border} color: #fff; font-family: monospace; font-size: 12px; display: inline-block; vertical-align: top;">
                <strong>{s.span_id} [{s.phase.value}]</strong><br/>
                <span>Tokens: {s.token_count}</span> | <span>Uncertainty: {s.uncertainty_score:.2f}</span>
                <p style="margin: 4px 0 0 0; opacity: 0.9; font-size: 11px;">{s.summary}</p>
            </div>
            """)

        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8"/>
    <title>{title}</title>
    <style>
        body {{ background: #0f172a; color: #f8fafc; font-family: -apple-system, sans-serif; padding: 24px; }}
        .header {{ margin-bottom: 20px; }}
        .stats {{ display: flex; gap: 16px; margin-bottom: 24px; }}
        .stat-card {{ background: #1e293b; padding: 12px 18px; border-radius: 8px; border: 1px solid #334155; }}
        .container {{ background: #1e293b; padding: 16px; border-radius: 8px; border: 1px solid #334155; overflow-x: auto; white-space: nowrap; }}
    </style>
</head>
<body>
    <div class="header">
        <h2>🔥 {title}</h2>
        <p>Interactive flamegraph visualizer for frontier model reasoning traces.</p>
    </div>
    <div class="stats">
        <div class="stat-card"><strong>Total Tokens:</strong> {profile.total_tokens}</div>
        <div class="stat-card"><strong>Backtracks Caught:</strong> {profile.backtrack_count}</div>
        <div class="stat-card"><strong>Average Uncertainty:</strong> {profile.avg_uncertainty:.2f}</div>
        <div class="stat-card"><strong>Latency:</strong> {profile.profiling_latency_ms:.3f} ms</div>
    </div>
    <div class="container">
        {''.join(spans_html)}
    </div>
</body>
</html>"""
        return html
