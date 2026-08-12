"""One-step chart API for analysts: ``vx.plot(df, kind=..., x=..., y=...)``."""

from __future__ import annotations

import os
import webbrowser
from typing import Optional

import pandas as pd

from viewx.shared.themes import chart_colors, theme_spec
from .factory import (
    CHART_KINDS,
    build_plotly_figure,
    build_static_figure,
    infer_kind,
)

__all__ = ["plot", "Chart", "CHART_KINDS"]

_STATIC_EXTS = {".png", ".svg", ".pdf", ".jpg", ".jpeg", ".webp"}


class Chart:
    """Wrapper around a Plotly or matplotlib figure with a uniform API.

    - ``chart.save("out.html" | "out.png" | "out.svg")``
    - ``chart.show()`` opens the chart (or renders inline in a notebook)
    - ``chart.fig`` exposes the underlying figure object
    """

    def __init__(self, fig, interactive: bool = True, title: str = ""):
        self.fig = fig
        self.interactive = interactive
        self.title = title

    # ── export ────────────────────────────────────────────────────────────
    def save(self, path: str, open_browser: bool = False) -> str:
        ext = os.path.splitext(path)[1].lower()
        directory = os.path.dirname(path)
        if directory:
            os.makedirs(directory, exist_ok=True)

        if self.interactive:
            if ext in ("", ".html"):
                if ext == "":
                    path += ".html"
                self.fig.write_html(path, include_plotlyjs="cdn")
            elif ext in _STATIC_EXTS:
                try:
                    self.fig.write_image(path)
                except Exception as exc:
                    raise RuntimeError(
                        f"Could not export interactive chart to '{ext}'. "
                        "Static export of Plotly figures requires kaleido "
                        "(pip install kaleido), or build the chart with "
                        "vx.plot(..., static=True)."
                    ) from exc
            else:
                raise ValueError(f"Unsupported extension '{ext}' for interactive charts.")
        else:
            if ext in ("", ".html"):
                raise ValueError(
                    "Static (matplotlib) charts export to image formats "
                    "(.png, .svg, .pdf). Use static=False for HTML output."
                )
            self.fig.savefig(path, dpi=150, bbox_inches="tight")

        if open_browser:
            webbrowser.open("file://" + os.path.abspath(path))
        return os.path.abspath(path)

    def show(self) -> "Chart":
        if self.interactive:
            self.fig.show()
        else:
            import tempfile
            tmp = os.path.join(tempfile.gettempdir(), "viewx_chart.png")
            self.fig.savefig(tmp, dpi=150, bbox_inches="tight")
            webbrowser.open("file://" + tmp)
        return self

    # ── notebook integration ──────────────────────────────────────────────
    def _repr_html_(self) -> Optional[str]:
        if self.interactive:
            return self.fig.to_html(full_html=False, include_plotlyjs="cdn")
        return None

    def _repr_png_(self):
        if self.interactive:
            return None
        import io
        buf = io.BytesIO()
        self.fig.savefig(buf, format="png", dpi=110, bbox_inches="tight")
        return buf.getvalue()


def plot(
    data: pd.DataFrame,
    kind: Optional[str] = None,
    x=None,
    y=None,
    z=None,
    title: str = "",
    theme=None,
    static: bool = False,
    downsample: bool = True,
) -> Chart:
    """Create a chart from a DataFrame in a single call.

    Parameters
    ----------
    data : DataFrame
    kind : one of ``vx.plot.CHART_KINDS`` (inferred from dtypes when omitted)
    x, y, z : column names (z = color / size / value depending on kind)
    title : chart title
    theme : ViewX theme name (defaults to the global theme, see ``vx.set_theme``)
    static : build a matplotlib figure instead of an interactive Plotly one
    downsample : reduce series larger than 10k points automatically

    Examples
    --------
    >>> vx.plot(df, x="date", y="revenue")                       # interactive line
    >>> vx.plot(df, kind="histogram", x="age", static=True).save("hist.png")
    """
    if kind is None:
        kind = infer_kind(data, x if not isinstance(x, list) else None, y)

    colors = chart_colors(theme)

    if static:
        fig = build_static_figure(
            data, kind=kind, x=x, y=y, z=z, title=title,
            colors=colors, downsample=downsample,
        )
        return Chart(fig, interactive=False, title=title)

    fig = build_plotly_figure(
        data, kind=kind, x=x, y=y, z=z, title=title,
        colors=colors, downsample=downsample,
    )

    spec = theme_spec(theme)
    bg = spec.get("bg_card", "#FFFFFF")
    fig.update_layout(
        paper_bgcolor=bg if isinstance(bg, str) and bg.startswith("#") else "rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color=spec.get("text_primary", "#1A1A2E"),
        font_family="'Inter','Segoe UI',sans-serif",
        colorway=colors,
    )
    return Chart(fig, interactive=True, title=title)
