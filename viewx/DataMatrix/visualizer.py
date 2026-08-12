from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from viewx.shared.plotly_bundle import fig_to_html

from .analyzers import ColumnProfile, DatasetReport


class Visualizer:
    CHART_COLORS = [
        "#6366F1", "#10B981", "#F59E0B", "#EF4444", "#EC4899",
        "#8B5CF6", "#06B6D4", "#84CC16", "#F97316", "#14B8A6",
    ]

    DARK_LAYOUT = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="'Geist','Segoe UI',sans-serif", color="#E2E5FF"),
        margin=dict(l=40, r=20, t=30, b=40),
        hovermode="closest",
        legend=dict(font=dict(size=10), orientation="h", y=-0.15),
        colorway=CHART_COLORS,
        xaxis=dict(gridcolor="rgba(255,255,255,0.06)", zerolinecolor="rgba(255,255,255,0.06)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.06)", zerolinecolor="rgba(255,255,255,0.06)"),
        dragmode=False,
    )

    LIGHT_LAYOUT = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="'Geist','Segoe UI',sans-serif", color="#1A1A2E"),
        margin=dict(l=40, r=20, t=30, b=40),
        hovermode="closest",
        legend=dict(font=dict(size=10), orientation="h", y=-0.15),
        colorway=CHART_COLORS,
        xaxis=dict(gridcolor="rgba(0,0,0,0.06)", zerolinecolor="rgba(0,0,0,0.06)"),
        yaxis=dict(gridcolor="rgba(0,0,0,0.06)", zerolinecolor="rgba(0,0,0,0.06)"),
        dragmode=False,
    )

    def __init__(self):
        self.mode = "dark"

    def set_mode(self, mode: str):
        self.mode = mode if mode in ("dark", "light") else "dark"

    _PLOT_CONFIG = dict(
        displaylogo=False,
        responsive=True,
        modeBarButtonsToRemove=[
            "zoom2d", "pan2d", "select2d", "lasso2d",
            "zoomIn2d", "zoomOut2d", "autoScale2d",
            "hoverClosestCartesian", "hoverCompareCartesian",
        ],
    )

    def _to_html(self, fig: go.Figure) -> str:
        # Delegates to the shared Plotly-to-HTML helper (single code path)
        return fig_to_html(fig, include_js=False, config=self._PLOT_CONFIG)

    def _apply_theme(self, fig: go.Figure) -> go.Figure:
        layout = self.DARK_LAYOUT if self.mode == "dark" else self.LIGHT_LAYOUT
        fig.update_layout(**layout)
        grid = "rgba(255,255,255,0.06)" if self.mode == "dark" else "rgba(0,0,0,0.06)"
        fig.update_xaxes(gridcolor=grid, zerolinecolor=grid)
        fig.update_yaxes(gridcolor=grid, zerolinecolor=grid)
        return fig

    def generate_overview_plots(self, report: DatasetReport) -> str:
        type_counts = {}
        for p in report.column_profiles.values():
            t = p.inferred_type
            type_counts[t] = type_counts.get(t, 0) + 1

        fig_types = px.pie(
            names=list(type_counts.keys()),
            values=list(type_counts.values()),
            hole=0.55,
            color_discrete_sequence=self.CHART_COLORS,
        )
        fig_types.update_traces(
            textinfo="label+percent",
            textfont_size=12,
            marker=dict(line=dict(color="rgba(0,0,0,0)", width=0)),
            pull=[0.02 if v == max(type_counts.values()) else 0 for v in type_counts.values()],
        )
        fig_types.add_annotation(
            text=f"{len(report.column_profiles)}<br>total",
            showarrow=False,
            font=dict(size=14, color="#E2E5FF"),
            align="center",
        )
        self._apply_theme(fig_types)

        missing_data = [
            (p.name, p.p_missing)
            for p in sorted(
                report.column_profiles.values(),
                key=lambda x: x.p_missing,
                reverse=True,
            )
            if p.p_missing > 0
        ]

        if missing_data:
            names, vals = zip(*missing_data)
            fig_missing = go.Figure(go.Bar(
                x=list(vals),
                y=list(names),
                orientation="h",
                marker=dict(
                    color=[self.CHART_COLORS[i % len(self.CHART_COLORS)] for i in range(len(names))],
                    line=dict(width=0),
                ),
                text=[f"{v:.1f}%" for v in vals],
                textposition="outside",
            ))
            fig_missing.update_layout(
                xaxis=dict(title="Missing %", range=[0, max(vals) * 1.25 if vals else 100]),
                yaxis=dict(autorange="reversed"),
                uniformtext_minsize=8,
            )
            self._apply_theme(fig_missing)
        else:
            fig_missing = go.Figure()
            fig_missing.add_annotation(
                text="No missing values",
                showarrow=False,
                font=dict(size=14, color="#10B981"),
            )
            self._apply_theme(fig_missing)

        return f"""
        <div class="dm-grid-2" style="margin-top:20px">
            <div class="dm-card">
                <div class="dm-card-title"><span class="accent-dot"></span>Data Type Distribution</div>
                <div class="dm-plot">{self._to_html(fig_types)}</div>
            </div>
            <div class="dm-card">
                <div class="dm-card-title"><span class="accent-dot"></span>Missing Values by Column</div>
                <div class="dm-plot">{self._to_html(fig_missing)}</div>
            </div>
        </div>"""

    def generate_column_plots(self, df: pd.DataFrame, report: DatasetReport) -> str:
        html_parts = []

        for col, profile in report.column_profiles.items():
            series = df[col].dropna()
            top_values_html = ""

            if profile.top_values:
                max_val = max(profile.top_values.values()) if profile.top_values else 1
                items = ""
                for k, v in list(profile.top_values.items())[:5]:
                    pct = (v / max_val) * 100
                    items += f"""
                    <div class="dm-top-val">
                        <span style="flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:0.78rem">{k}</span>
                        <span style="font-weight:600;font-size:0.75rem;min-width:30px;text-align:right">{v}</span>
                        <div style="flex:0.5;height:4px;background:rgba(255,255,255,0.06);border-radius:2px;overflow:hidden">
                            <div class="dm-top-val-bar" style="width:{pct}%"></div>
                        </div>
                    </div>"""
                top_values_html = f"""
                <div style="margin-top:10px;padding-top:10px;border-top:1px solid var(--border)">
                    <div style="font-size:0.72rem;color:var(--text-secondary);font-weight:600;margin-bottom:6px">Top Values</div>
                    {items}
                </div>"""

            fig = None
            if profile.inferred_type == "numeric":
                fig = px.histogram(
                    df, x=col,
                    nbins=min(40, profile.n_unique),
                    color_discrete_sequence=[self.CHART_COLORS[0]],
                )
                fig.update_traces(
                    marker=dict(
                        line=dict(width=0.5, color="rgba(255,255,255,0.1)"),
                    ),
                    hovertemplate="Range: %{x}<br>Count: %{y}<extra></extra>",
                )
                self._apply_theme(fig)

                if profile.mean is not None:
                    fig.add_vline(
                        x=profile.mean,
                        line_dash="dash",
                        line_color="#EF4444",
                        opacity=0.6,
                        annotation_text=f"μ={profile.mean:.2f}",
                        annotation_position="top right",
                        annotation_font_size=10,
                    )
                if profile.median is not None:
                    fig.add_vline(
                        x=profile.median,
                        line_dash="dot",
                        line_color="#10B981",
                        opacity=0.6,
                        annotation_text=f"M={profile.median:.2f}",
                        annotation_position="top left",
                        annotation_font_size=10,
                    )

            elif profile.inferred_type in ("categorical", "boolean"):
                value_counts = df[col].value_counts().head(15)
                fig = go.Figure(go.Bar(
                    x=list(value_counts.values),
                    y=list(value_counts.index.astype(str)),
                    orientation="h",
                    marker=dict(
                        color=self.CHART_COLORS[:min(len(value_counts), 10)] * 2,
                        line=dict(width=0),
                    ),
                    text=list(value_counts.values),
                    textposition="outside",
                    hovertemplate="%{y}: %{x}<extra></extra>",
                ))
                fig.update_layout(
                    yaxis=dict(autorange="reversed"),
                    uniformtext_minsize=8,
                )
                self._apply_theme(fig)

            elif profile.inferred_type == "datetime":
                if len(series) > 0 and hasattr(series, "dt"):
                    counts = series.dt.year.value_counts().sort_index()
                    fig = go.Figure(go.Scatter(
                        x=list(counts.index),
                        y=list(counts.values),
                        mode="lines+markers",
                        line=dict(
                            color=self.CHART_COLORS[0],
                            width=2.5,
                            shape="spline",
                        ),
                        marker=dict(
                            color=self.CHART_COLORS[0],
                            size=6,
                            line=dict(width=1, color="rgba(255,255,255,0.3)"),
                        ),
                        fill="tozeroy",
                        fillcolor=f"rgba(99,102,241,0.08)",
                    ))
                    self._apply_theme(fig)

            stat_items = ""
            stat_fields = [
                ("Type", profile.inferred_type),
                ("Unique", str(profile.n_unique)),
                ("Missing", f"{profile.n_missing} ({profile.p_missing:.1f}%)"),
                ("Cardinality", f"{profile.cardinality_ratio:.2%}"),
            ]
            if profile.inferred_type == "numeric":
                if profile.mean is not None:
                    stat_fields.extend([
                        ("Mean", f"{profile.mean:.3f}"),
                        ("Median", f"{profile.median:.3f}"),
                        ("Std Dev", f"{profile.std:.3f}"),
                        ("Min", f"{profile.min:.3f}"),
                        ("Max", f"{profile.max:.3f}"),
                        ("Q1", f"{profile.q1:.3f}"),
                        ("Q3", f"{profile.q3:.3f}"),
                        ("IQR", f"{profile.iqr:.3f}"),
                        ("Skewness", f"{profile.skewness:.3f}" if profile.skewness is not None else "—"),
                        ("Kurtosis", f"{profile.kurtosis:.3f}" if profile.kurtosis is not None else "—"),
                        ("Outliers", str(profile.outliers)),
                    ])
                else:
                    stat_fields.append(("Mean", "—"))

            for label, val in stat_fields:
                stat_items += f"""
                <div class="dm-stat-item">
                    <div class="stat-label">{label}</div>
                    <div class="stat-value">{val}</div>
                </div>"""

            chart_html = self._to_html(fig) if fig else ""
            tpl_id = f"dm-tpl-{col.replace(' ', '_')}"
            alert_badge = ""
            if profile.alerts:
                alert_badge = f'<span class="dm-alert-badge" title="{profile.alerts[0]}">{len(profile.alerts)} alert(s)</span>'

            html_parts.append(f"""
            <div class="dm-col-item" data-col="{col}">
                <div class="dm-col-header">
                    <div style="display:flex;align-items:center;gap:10px">
                        <span class="type-badge {profile.inferred_type}" style="font-size:0.68rem;padding:2px 8px;border-radius:99px">{profile.inferred_type}</span>
                        <span class="col-name">{col}</span>
                        {alert_badge}
                    </div>
                    <div style="display:flex;align-items:center;gap:12px">
                        <span style="font-size:0.72rem;color:var(--text-secondary)">{profile.dtype}</span>
                        <span class="col-chevron">▼</span>
                    </div>
                </div>
                <div class="dm-col-body">
                    <div class="dm-grid-2">
                        <div>
                            <div class="dm-stat-grid">{stat_items}</div>
                            {top_values_html}
                        </div>
                        <div class="dm-plot dm-lazy-plot" data-tpl="{tpl_id}" data-loaded="0">
                            {'<div style="padding:40px;text-align:center;color:var(--text-secondary)">Expand to load chart</div>' if chart_html else '<div style="padding:40px;text-align:center;color:var(--text-secondary)">No chart available</div>'}
                        </div>
                    </div>
                </div>
            </div>
            {f'<script type="text/template" id="{tpl_id}"><div class="dm-plot">{chart_html}</div></script>' if chart_html else ""}""")

        return "".join(html_parts)

    def generate_correlation_plots(self, report: DatasetReport) -> str:
        pairs = report.correlation_pairs
        if not pairs:
            return ""

        names = list({a for pair in pairs for a in (pair[0], pair[1])})
        n = len(names)
        corr_matrix = np.zeros((n, n))
        name_to_idx = {name: i for i, name in enumerate(names)}

        for a, b, r in pairs:
            i, j = name_to_idx[a], name_to_idx[b]
            corr_matrix[i][j] = r
            corr_matrix[j][i] = r
        np.fill_diagonal(corr_matrix, 1.0)

        fig = go.Figure(go.Heatmap(
            z=corr_matrix,
            x=names,
            y=names,
            colorscale=[
                [0.0, "#EF4444"],
                [0.25, "#F59E0B"],
                [0.5, "#1A1A2E"],
                [0.75, "#10B981"],
                [1.0, "#6366F1"],
            ],
            zmin=-1,
            zmax=1,
            text=[[f"{v:.2f}" for v in row] for row in corr_matrix],
            texttemplate="%{text}",
            textfont=dict(size=9, color="#E2E5FF"),
            hoverongaps=False,
        ))
        fig.update_layout(
            height=400,
            xaxis=dict(side="bottom", tickangle=-45),
            yaxis=dict(autorange="reversed"),
        )
        self._apply_theme(fig)

        top_pairs_html = ""
        for i, (a, b, r) in enumerate(pairs[:6]):
            strength = (
                "very strong" if abs(r) > 0.8
                else "strong" if abs(r) > 0.6
                else "moderate" if abs(r) > 0.4
                else "weak"
            )
            direction = "positive" if r > 0 else "negative"
            top_pairs_html += f"""
            <div style="display:flex;justify-content:space-between;align-items:center;padding:8px 10px;background:rgba(255,255,255,0.02);border-radius:6px;margin-bottom:4px">
                <div>
                    <span style="font-weight:600;font-size:0.82rem">{a}</span>
                    <span style="color:var(--text-secondary);margin:0 6px">×</span>
                    <span style="font-weight:600;font-size:0.82rem">{b}</span>
                </div>
                <div style="display:flex;align-items:center;gap:8px">
                    <span style="font-size:0.85rem;font-weight:700;color:{'#10B981' if r > 0 else '#EF4444'}">{r:.4f}</span>
                    <span style="font-size:0.65rem;color:var(--text-secondary);background:rgba(255,255,255,0.04);padding:2px 6px;border-radius:4px">{strength} · {direction}</span>
                </div>
            </div>"""

        return f"""
        <div class="dm-grid-2">
            <div class="dm-card">
                <div class="dm-card-title"><span class="accent-dot"></span>Correlation Heatmap</div>
                <div class="dm-plot">{self._to_html(fig)}</div>
            </div>
            <div class="dm-card">
                <div class="dm-card-title"><span class="accent-dot"></span>Top Correlations</div>
                <div style="margin-top:4px">{top_pairs_html}</div>
            </div>
        </div>"""

    def generate_bibliometric_plots(self, bib_results: dict) -> str:
        html_parts = []
        kpi_parts = []

        if bib_results.get("citation_summary"):
            cs = bib_results["citation_summary"]
            kpi_parts.extend([
                ("Total Citations", f"{cs['total_citations']:,}"),
                ("Mean Citations", f"{cs['mean_citations']}"),
                ("Max Citations", f"{cs['max_citations']:,}"),
            ])

        if bib_results.get("author_summary"):
            aus = bib_results["author_summary"]
            kpi_parts.extend([
                ("Unique Authors", f"{aus['unique_authors']:,}"),
                ("Avg Authors/Paper", f"{aus['avg_per_publication']}"),
            ])

        if kpi_parts:
            cards = "".join(
                f"""<div class="dm-card dm-kpi"><div class="dm-kpi-value">{val}</div>
                <div class="dm-kpi-label">{label}</div></div>"""
                for label, val in kpi_parts[:4]
            )
            html_parts.append(f'<div class="dm-grid-4" style="margin-bottom:20px">{cards}</div>')

        if "annual_production" in bib_results:
            df_ap = bib_results["annual_production"]
            fig_ap = px.line(
                df_ap, x="Year", y="Count",
                markers=True,
                color_discrete_sequence=[self.CHART_COLORS[0]],
            )
            fig_ap.update_traces(
                line=dict(width=2.5, shape="spline"),
                marker=dict(size=6, line=dict(width=1, color="rgba(255,255,255,0.3)")),
                fill="tozeroy",
                fillcolor="rgba(99,102,241,0.06)",
            )
            self._apply_theme(fig_ap)
            fig_ap.update_layout(
                yaxis=dict(title="Publications"),
                xaxis=dict(title="Year"),
            )
            html_parts.append(f"""
            <div class="dm-card" style="margin-bottom:20px">
                <div class="dm-card-title"><span class="accent-dot"></span>Annual Scientific Production</div>
                <div class="dm-plot">{self._to_html(fig_ap)}</div>
            </div>""")

        if "top_authors" in bib_results:
            df_au = bib_results["top_authors"]
            fig_au = go.Figure(go.Bar(
                x=list(df_au["Count"]),
                y=list(df_au["Author"]),
                orientation="h",
                marker=dict(
                    color=self.CHART_COLORS[:len(df_au)] * 2,
                    line=dict(width=0),
                ),
                text=list(df_au["Count"]),
                textposition="outside",
            ))
            fig_au.update_layout(
                yaxis=dict(autorange="reversed", title="Author"),
                xaxis=dict(title="Publications"),
                uniformtext_minsize=8,
            )
            self._apply_theme(fig_au)
            html_parts.append(f"""
            <div class="dm-card" style="margin-bottom:20px">
                <div class="dm-card-title"><span class="accent-dot"></span>Most Productive Authors</div>
                <div class="dm-plot">{self._to_html(fig_au)}</div>
            </div>""")

        if "top_sources" in bib_results:
            df_so = bib_results["top_sources"]
            fig_so = px.pie(
                df_so, names="Source", values="Count",
                hole=0.45,
                color_discrete_sequence=self.CHART_COLORS,
            )
            fig_so.update_traces(
                textinfo="label+percent",
                textfont_size=11,
                marker=dict(line=dict(color="rgba(0,0,0,0)", width=0)),
            )
            self._apply_theme(fig_so)
            html_parts.append(f"""
            <div class="dm-card" style="margin-bottom:20px">
                <div class="dm-card-title"><span class="accent-dot"></span>Top Sources</div>
                <div class="dm-plot">{self._to_html(fig_so)}</div>
            </div>""")

        if "top_keywords" in bib_results:
            df_kw = bib_results["top_keywords"].head(15)
            fig_kw = go.Figure(go.Bar(
                x=list(df_kw["Count"]),
                y=list(df_kw["Keyword"]),
                orientation="h",
                marker=dict(color=self.CHART_COLORS[2], line=dict(width=0)),
            ))
            fig_kw.update_layout(yaxis=dict(autorange="reversed", title="Keyword"), xaxis=dict(title="Count"))
            self._apply_theme(fig_kw)
            html_parts.append(f"""
            <div class="dm-card" style="margin-bottom:20px">
                <div class="dm-card-title"><span class="accent-dot"></span>Top Keywords</div>
                <div class="dm-plot">{self._to_html(fig_kw)}</div>
            </div>""")

        if not html_parts:
            return ""

        return "".join(html_parts)
