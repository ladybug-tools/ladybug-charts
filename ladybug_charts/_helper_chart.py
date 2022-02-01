"""Functions to help charts."""

import plotly.graph_objects as go


def get_dummy_trace(name: str, color: str) -> go:
    """Get a dummy trace to add to a figure."""
    return go.Scatter(
        x=[None],
        y=[None],
        mode='markers',
        marker=dict(size=10),
        showlegend=True,
        line_color=color,
        name=name)
