"""Shared chart factory used by ``vx.plot`` and ``Dashboard.add_chart``.

Builds interactive Plotly figures (with automatic downsampling and WebGL for
large series) and static matplotlib figures from the same ``kind`` vocabulary.
"""

from __future__ import annotations

from typing import List, Optional, Tuple

import pandas as pd

CHART_KINDS = (
    "line", "bar", "bar_h", "scatter", "area",
    "pie", "donut", "histogram", "box", "violin",
    "heatmap", "funnel", "treemap", "bubble",
)

DOWNSAMPLE_THRESHOLD = 10_000
WEBGL_THRESHOLD = 5_000

_DOWNSAMPLE_KINDS = {"line", "scatter", "area", "bubble"}


def infer_kind(data: pd.DataFrame, x: Optional[str], y: Optional[str]) -> str:
    """Infer a sensible chart kind from the dtypes of x/y."""
    def _type(col: Optional[str]) -> Optional[str]:
        if col is None or col not in data.columns:
            return None
        s = data[col]
        if pd.api.types.is_datetime64_any_dtype(s):
            return "datetime"
        if pd.api.types.is_numeric_dtype(s):
            return "numeric"
        return "categorical"

    tx, ty = _type(x), _type(y)
    if tx == "datetime":
        return "line"
    if tx == "numeric" and ty == "numeric":
        return "scatter"
    if tx == "categorical" and ty == "numeric":
        return "bar"
    if tx == "numeric" and ty is None:
        return "histogram"
    if tx == "categorical" and ty is None:
        return "bar"
    return "line"


def maybe_downsample(
    data: pd.DataFrame,
    kind: str,
    downsample: bool = True,
    threshold: int = DOWNSAMPLE_THRESHOLD,
) -> Tuple[pd.DataFrame, bool]:
    """Uniform-stride downsample for large point series (keeps first/last rows)."""
    if not downsample or kind not in _DOWNSAMPLE_KINDS or len(data) <= threshold:
        return data, False
    stride = max(1, len(data) // threshold)
    sampled = data.iloc[::stride]
    if data.index[-1] not in sampled.index:
        sampled = pd.concat([sampled, data.iloc[[-1]]])
    return sampled, True


def build_plotly_figure(
    data: pd.DataFrame,
    kind: str = "line",
    x=None,
    y=None,
    z=None,
    title: str = "",
    colors: Optional[List[str]] = None,
    downsample: bool = True,
):
    """Build a Plotly figure for any supported chart kind."""
    import plotly.express as px
    import plotly.graph_objects as go

    if colors is None:
        from viewx.shared.themes import chart_colors
        colors = chart_colors()

    if kind not in CHART_KINDS:
        raise ValueError(f"chart kind '{kind}' not supported. Use one of {CHART_KINDS}")

    data, downsampled = maybe_downsample(data, kind, downsample)
    kw = dict(color_discrete_sequence=colors)
    use_webgl = len(data) > WEBGL_THRESHOLD

    if kind == "bar":
        fig = px.bar(data, x=x, y=y, title=title, **kw)
    elif kind == "bar_h":
        fig = px.bar(data, x=y, y=x, orientation="h", title=title, **kw)
    elif kind == "scatter":
        fig = px.scatter(
            data, x=x, y=y, color=z, title=title,
            render_mode="webgl" if use_webgl else "auto", **kw,
        )
    elif kind == "area":
        fig = px.area(data, x=x, y=y, title=title, **kw)
    elif kind == "line":
        fig = px.line(
            data, x=x, y=y, title=title,
            render_mode="webgl" if use_webgl else "auto", **kw,
        )
    elif kind == "pie":
        fig = px.pie(data, names=x, values=y, title=title,
                     color_discrete_sequence=colors)
    elif kind == "donut":
        fig = px.pie(data, names=x, values=y, hole=0.45, title=title,
                     color_discrete_sequence=colors)
    elif kind == "histogram":
        fig = px.histogram(data, x=x, title=title, **kw)
    elif kind == "box":
        fig = px.box(data, x=x, y=y, title=title, **kw)
    elif kind == "violin":
        fig = px.violin(data, x=x, y=y, title=title, box=True, **kw)
    elif kind == "heatmap":
        # x = row category, y = column category, z = numeric value
        pivot = data.pivot_table(index=x, columns=y, values=z, aggfunc="sum")
        fig = go.Figure(go.Heatmap(
            z=pivot.values, x=list(pivot.columns),
            y=list(pivot.index), colorscale=colors[::-1],
        ))
        if title:
            fig.update_layout(title_text=title)
    elif kind == "funnel":
        fig = px.funnel(data, x=y, y=x, title=title, **kw)
    elif kind == "treemap":
        path_cols = x if isinstance(x, list) else [x]
        fig = px.treemap(data, path=path_cols, values=y,
                         title=title, color_discrete_sequence=colors)
    elif kind == "bubble":
        fig = px.scatter(
            data, x=x, y=y, size=z, title=title,
            render_mode="webgl" if use_webgl else "auto", **kw,
        )
    else:  # pragma: no cover - guarded above
        raise ValueError(f"chart kind '{kind}' not recognized")

    if downsampled:
        fig.add_annotation(
            text=f"downsampled to {len(data):,} points",
            xref="paper", yref="paper", x=1, y=1.06,
            showarrow=False, font=dict(size=10, color="#9CA3AF"),
        )
    return fig


def build_static_figure(
    data: pd.DataFrame,
    kind: str = "line",
    x=None,
    y=None,
    z=None,
    title: str = "",
    colors: Optional[List[str]] = None,
    downsample: bool = True,
    figsize: Tuple[float, float] = (8, 5),
):
    """Build a static matplotlib figure for papers / PDFs.

    Requires matplotlib (``pip install viewx[static]``).
    """
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError as exc:  # pragma: no cover
        raise ImportError(
            "matplotlib is required for static charts. "
            "Install it with: pip install viewx[static]"
        ) from exc

    if colors is None:
        from viewx.shared.themes import chart_colors
        colors = chart_colors()

    if kind in ("funnel", "treemap"):
        raise ValueError(
            f"chart kind '{kind}' is not available in static mode. "
            "Use static=False for an interactive version."
        )

    data, downsampled = maybe_downsample(data, kind, downsample)
    fig, ax = plt.subplots(figsize=figsize)
    c0 = colors[0]

    if kind == "line":
        ax.plot(data[x], data[y], color=c0, linewidth=2)
    elif kind == "area":
        ax.plot(data[x], data[y], color=c0, linewidth=2)
        ax.fill_between(data[x], data[y], alpha=0.25, color=c0)
    elif kind == "bar":
        ax.bar(data[x].astype(str), data[y], color=colors[: max(1, len(data))] * (len(data) // len(colors) + 1))
        ax.tick_params(axis="x", rotation=45)
    elif kind == "bar_h":
        ax.barh(data[x].astype(str), data[y], color=c0)
    elif kind in ("scatter", "bubble"):
        sizes = None
        if kind == "bubble" and z is not None:
            s = data[z].astype(float)
            rng = (s.max() - s.min()) or 1.0
            sizes = 20 + 180 * (s - s.min()) / rng
        ax.scatter(data[x], data[y], s=sizes, color=c0, alpha=0.65, edgecolors="white", linewidths=0.4)
    elif kind in ("pie", "donut"):
        wedgeprops = {"width": 0.55} if kind == "donut" else None
        ax.pie(
            data[y], labels=data[x].astype(str), colors=colors,
            autopct="%1.1f%%", wedgeprops=wedgeprops,
        )
    elif kind == "histogram":
        s = data[x].dropna()
        ax.hist(s, bins=min(40, max(5, s.nunique())), color=c0, edgecolor="white")
        ax.set_ylabel("Count")
    elif kind == "box":
        if x is not None and y is not None:
            groups = [g[y].dropna().values for _, g in data.groupby(x)]
            labels = [str(k) for k, _ in data.groupby(x)]
            ax.boxplot(groups, tick_labels=labels)
        else:
            ax.boxplot(data[x if y is None else y].dropna().values)
    elif kind == "violin":
        if x is not None and y is not None:
            groups = [g[y].dropna().values for _, g in data.groupby(x)]
            labels = [str(k) for k, _ in data.groupby(x)]
            ax.violinplot(groups, showmedians=True)
            ax.set_xticks(range(1, len(labels) + 1), labels)
        else:
            ax.violinplot(data[x if y is None else y].dropna().values, showmedians=True)
    elif kind == "heatmap":
        pivot = data.pivot_table(index=x, columns=y, values=z, aggfunc="sum")
        im = ax.imshow(pivot.values, aspect="auto", cmap="viridis")
        ax.set_xticks(range(len(pivot.columns)), [str(c) for c in pivot.columns], rotation=45)
        ax.set_yticks(range(len(pivot.index)), [str(i) for i in pivot.index])
        fig.colorbar(im, ax=ax)
    else:  # pragma: no cover
        raise ValueError(f"chart kind '{kind}' not recognized")

    if title:
        full_title = title + (" (downsampled)" if downsampled else "")
        ax.set_title(full_title)
    if x is not None and kind not in ("pie", "donut", "heatmap") and not isinstance(x, list):
        ax.set_xlabel(str(x))
    if y is not None and kind not in ("pie", "donut", "heatmap", "bar_h"):
        ax.set_ylabel(str(y))
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    return fig
