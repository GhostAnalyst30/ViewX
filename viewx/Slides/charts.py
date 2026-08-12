"""Gráficos Plotly para `viewx.Slides`."""

from __future__ import annotations

import json
import uuid
from typing import Any, Dict, Iterable, List, Optional

from .components import Component


DEFAULT_PALETTE = ["#4f46e5", "#06b6d4", "#22c55e", "#f97316", "#e11d48", "#a855f7", "#14b8a6", "#facc15"]


class PlotlyChart(Component):
    """Componente base para incrustar una figura Plotly dentro de una slide."""

    def __init__(self, data: List[Dict[str, Any]], layout: Optional[Dict[str, Any]] = None, config: Optional[Dict[str, Any]] = None, **styles: Any) -> None:
        super().__init__(**styles)
        self.chart_id = f"vx_plot_{uuid.uuid4().hex}"
        self.data = data
        self.layout = layout or {}
        self.config = {"displayModeBar": False, "responsive": True, **(config or {})}
        self.classes.append("vx-plot")
        self.styles.setdefault("width", "520px")
        self.styles.setdefault("height", "340px")
        self.styles.setdefault("left", "52%")
        self.styles.setdefault("top", "28%")

    @classmethod
    def from_figure(cls, fig: Any, **styles: Any) -> "PlotlyChart":
        """Embed a Plotly figure or a ``vx.plot`` Chart inside a slide."""
        try:
            from viewx.plot import Chart as _VxChart
            if isinstance(fig, _VxChart):
                if not fig.interactive:
                    raise ValueError(
                        "Static (matplotlib) charts cannot be embedded in slides. "
                        "Build the chart with static=False."
                    )
                fig = fig.fig
        except ImportError:
            pass
        import plotly.io as pio
        fig_dict = json.loads(pio.to_json(fig))
        return cls(
            data=fig_dict.get("data", []),
            layout=fig_dict.get("layout", {}),
            **styles,
        )

    def _merged_layout(self) -> Dict[str, Any]:
        base = {
            "paper_bgcolor": "rgba(0,0,0,0)",
            "plot_bgcolor": "rgba(0,0,0,0)",
            "font": {"color": "#dbeafe", "family": "Inter, Segoe UI, sans-serif"},
            "margin": {"l": 48, "r": 26, "t": 48, "b": 48},
            "autosize": True,
        }
        base.update(self.layout)
        return base

    def _content(self) -> str:
        data = json.dumps(self.data, ensure_ascii=False)
        layout = json.dumps(self._merged_layout(), ensure_ascii=False)
        config = json.dumps(self.config, ensure_ascii=False)
        return f"<div id=\"{self.chart_id}\" style=\"width:100%;height:100%;\"></div><script>window.addEventListener('DOMContentLoaded',function(){{if(window.Plotly){{Plotly.newPlot('{self.chart_id}', {data}, {layout}, {config});}}}});</script>"


class BarPlot(PlotlyChart):
    def __init__(self, x: Iterable[Any], y: Iterable[Any], orientation: str = "v", name: str = "", color: str = "#4f46e5", title: str = "", **styles: Any) -> None:
        trace: Dict[str, Any]
        if orientation == "h":
            trace = {"type": "bar", "x": list(y), "y": list(x), "orientation": "h", "name": name, "marker": {"color": color}}
        else:
            trace = {"type": "bar", "x": list(x), "y": list(y), "name": name, "marker": {"color": color}}
        layout = {"title": {"text": title, "x": 0.03, "xanchor": "left"}} if title else {}
        super().__init__([trace], layout=layout, **styles)


class PiePlot(PlotlyChart):
    def __init__(self, labels: Iterable[Any], values: Iterable[Any], title: str = "", hole: float = 0.0, colors: Optional[List[str]] = None, **styles: Any) -> None:
        trace = {
            "type": "pie",
            "labels": list(labels),
            "values": list(values),
            "hole": hole,
            "marker": {"colors": colors or DEFAULT_PALETTE},
            "textinfo": "label+percent",
        }
        layout = {"title": {"text": title, "x": 0.03, "xanchor": "left"}, "showlegend": True} if title else {"showlegend": True}
        super().__init__([trace], layout=layout, **styles)


class DonutPlot(PiePlot):
    def __init__(self, labels: Iterable[Any], values: Iterable[Any], title: str = "", colors: Optional[List[str]] = None, **styles: Any) -> None:
        super().__init__(labels, values, title=title, hole=0.52, colors=colors, **styles)


class LinePlot(PlotlyChart):
    def __init__(self, x: Iterable[Any], y: Iterable[Any], name: str = "", color: str = "#06b6d4", title: str = "", fill: bool = False, **styles: Any) -> None:
        trace = {"type": "scatter", "mode": "lines+markers", "x": list(x), "y": list(y), "name": name, "line": {"color": color, "width": 3}, "marker": {"size": 7}}
        if fill:
            trace["fill"] = "tozeroy"
        layout = {"title": {"text": title, "x": 0.03, "xanchor": "left"}} if title else {}
        super().__init__([trace], layout=layout, **styles)


class ScatterPlot(PlotlyChart):
    def __init__(self, x: Iterable[Any], y: Iterable[Any], labels: Optional[Iterable[Any]] = None, name: str = "", color: str = "#22c55e", title: str = "", **styles: Any) -> None:
        trace: Dict[str, Any] = {"type": "scatter", "mode": "markers", "x": list(x), "y": list(y), "name": name, "marker": {"color": color, "size": 12, "opacity": 0.84}}
        if labels is not None:
            trace["text"] = list(labels)
            trace["hovertemplate"] = "%{text}<br>x=%{x}<br>y=%{y}<extra></extra>"
        layout = {"title": {"text": title, "x": 0.03, "xanchor": "left"}} if title else {}
        super().__init__([trace], layout=layout, **styles)


class AreaPlot(LinePlot):
    def __init__(self, x: Iterable[Any], y: Iterable[Any], name: str = "", color: str = "#a855f7", title: str = "", **styles: Any) -> None:
        super().__init__(x, y, name=name, color=color, title=title, fill=True, **styles)


__all__ = ["PlotlyChart", "BarPlot", "PiePlot", "DonutPlot", "LinePlot", "ScatterPlot", "AreaPlot", "DEFAULT_PALETTE"]
