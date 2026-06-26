from __future__ import annotations

from typing import Any, Dict, Optional

PLOTLY_CDN = "https://cdn.plot.ly/plotly-2.35.2.min.js"

DEFAULT_PLOTLY_CONFIG: Dict[str, Any] = {
    "displaylogo": False,
    "responsive": True,
    "autosizable": True,
}


def plotly_script_tag() -> str:
    return f'<script src="{PLOTLY_CDN}"></script>'


def fig_to_html(
    fig,
    include_js: bool = False,
    config: Optional[Dict[str, Any]] = None,
) -> str:
    cfg = config or DEFAULT_PLOTLY_CONFIG
    return fig.to_html(
        full_html=False,
        include_plotlyjs="cdn" if include_js else False,
        config=cfg,
    )
