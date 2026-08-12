from __future__ import annotations

import warnings
from datetime import datetime
from typing import Dict, List, Optional, Union

import pandas as pd

from .analyzers import AnalyzerEngine, DatasetReport
from .bibliometrics import BibliometricsAnalyzer
from .explorer import build_explorer_payload, explorer_json_script
from .visualizer import Visualizer

from viewx.shared import datamatrix_runtime_js, plotly_script_tag
from viewx.shared.insights import compute_highlights
from viewx.shared.themes import datamatrix_mode, get_theme, theme_spec


class DataMatrix:
    def __init__(self, df: pd.DataFrame):
        self.original_df = df.copy()
        self.df = df.copy()
        self.analyzer = AnalyzerEngine()
        self.visualizer = Visualizer()
        self.bib_analyzer = BibliometricsAnalyzer()
        self.report: Optional[DatasetReport] = None
        self.bib_results: Optional[dict] = None

    def clean_data(
        self,
        drop_duplicates: bool = True,
        fill_na: Union[bool, str] = False,
        na_strategy: Optional[Dict[str, str]] = None,
    ) -> "DataMatrix":
        if drop_duplicates:
            before = len(self.df)
            self.df.drop_duplicates(inplace=True)
            after = len(self.df)
            if before > after:
                print(f"  removed {before - after} duplicate rows")

        if fill_na:
            if isinstance(fill_na, str):
                method = fill_na.lower()
                if method == "ffill":
                    self.df = self.df.ffill()
                elif method == "bfill":
                    self.df = self.df.bfill()
                else:
                    raise ValueError(f"Unsupported fill method: {method}. Use 'ffill' or 'bfill'.")
                print(f"  filled missing values using '{method}' method")
            else:
                for col in self.df.columns:
                    if self.df[col].isna().any():
                        if na_strategy and col in na_strategy:
                            strategy = na_strategy[col]
                        else:
                            strategy = "auto"

                        if strategy == "auto":
                            if pd.api.types.is_numeric_dtype(self.df[col]):
                                self.df[col] = self.df[col].fillna(self.df[col].median())
                            else:
                                mode_val = self.df[col].mode()
                                fill_val = mode_val[0] if not mode_val.empty else "Unknown"
                                self.df[col] = self.df[col].fillna(fill_val)
                        elif strategy == "mean":
                            self.df[col] = self.df[col].fillna(self.df[col].mean())
                        elif strategy == "median":
                            self.df[col] = self.df[col].fillna(self.df[col].median())
                        elif strategy == "mode":
                            mode_val = self.df[col].mode()
                            fill_val = mode_val[0] if not mode_val.empty else "Unknown"
                            self.df[col] = self.df[col].fillna(fill_val)
                        elif strategy == "drop":
                            self.df = self.df.dropna(subset=[col])
                print("  filled missing values")
        return self

    def filter_rows(self, query: str) -> "DataMatrix":
        """Filter rows with a pandas query expression. Returns self for chaining."""
        self.df = self.df.query(query).copy()
        self.report = None
        self.bib_results = None
        return self

    def select_columns(self, columns: List[str]) -> "DataMatrix":
        """Keep only the given columns. Returns self for chaining."""
        missing = [c for c in columns if c not in self.df.columns]
        if missing:
            raise KeyError(f"Columns not found: {missing}")
        self.df = self.df[columns].copy()
        self.report = None
        self.bib_results = None
        return self

    def reset_data(self) -> "DataMatrix":
        """Restore the original dataset before clean/filter operations."""
        self.df = self.original_df.copy()
        self.report = None
        self.bib_results = None
        return self

    def analyze(self) -> "DataMatrix":
        self.report = self.analyzer.analyze_dataset(self.df)
        self.bib_results = self.bib_analyzer.analyze(self.df)
        return self

    def summary(self, detailed: bool = False) -> Dict:
        if self.report is None:
            self.analyze()

        r = self.report
        info = {
            "rows": r.n_rows,
            "columns": r.n_cols,
            "duplicates": r.n_duplicates,
            "missing_cells": r.n_missing_total,
            "missing_pct": round(r.p_missing_total, 2),
            "memory": r.memory_usage,
            "numeric": len(r.numeric_columns),
            "categorical": len(r.categorical_columns),
            "datetime": len(r.datetime_columns),
            "boolean": len(r.boolean_columns),
        }

        if detailed:
            info["alerts"] = r.alerts
            info["highlights"] = self.highlights()
            info["numeric_columns"] = r.numeric_columns
            info["categorical_columns"] = r.categorical_columns
            info["datetime_columns"] = r.datetime_columns
            info["correlations"] = [
                {"x": a, "y": b, "r": round(v, 4)}
                for a, b, v in r.correlation_pairs
            ]

        return info

    def alerts(self) -> List[str]:
        if self.report is None:
            self.analyze()
        return self.report.alerts

    def highlights(self) -> List[str]:
        if self.report is None:
            self.analyze()
        return compute_highlights(self.report)

    def save(
        self,
        path: str = "datamatrix_report.html",
        title: str = "ViewX DataMatrix Report",
        theme: Optional[str] = None,
        sample_rows: int = 200,
        explorer_max_rows: int = 5000,
        open_browser: bool = False,
    ) -> str:
        """Write the EDA report to an HTML file. Returns the file path."""
        html = self.render_html(
            title=title, theme=theme,
            sample_rows=sample_rows, explorer_max_rows=explorer_max_rows,
        )

        import os
        directory = os.path.dirname(path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)

        if open_browser:
            import webbrowser
            webbrowser.open("file://" + os.path.abspath(path))

        return path

    def show(self, path: str = "datamatrix_report.html", **kwargs) -> str:
        """Write the EDA report and open it in the default browser."""
        return self.save(path, open_browser=True, **kwargs)

    def generate_report(
        self,
        output_path: str = "datamatrix_report.html",
        title: str = "ViewX DataMatrix Report",
        theme: str = "dark",
        show: bool = True,
        template: Optional[str] = None,
        explorer_max_rows: int = 5000,
    ) -> str:
        """Deprecated: use ``save(path)`` or ``show()`` instead."""
        warnings.warn(
            "DataMatrix.generate_report() is deprecated; use save(path) or show().",
            DeprecationWarning, stacklevel=2,
        )
        return self.save(
            output_path, title=title, theme=template or theme,
            explorer_max_rows=explorer_max_rows, open_browser=show,
        )

    def render_html(
        self,
        title: str = "ViewX DataMatrix Report",
        theme: Optional[str] = None,
        sample_rows: int = 200,
        explorer_max_rows: int = 5000,
    ) -> str:
        if self.report is None:
            self.analyze()

        theme_name = theme if theme is not None else get_theme()
        mode = datamatrix_mode(theme_name)
        accent = theme_spec(theme_name).get("accent", "#6366F1")

        self.visualizer.set_mode(mode)
        tmpl = ReportTheme(mode=mode, accent_color=accent)
        return tmpl.render(
            title=title,
            report=self.report,
            bib_results=self.bib_results,
            df=self.df,
            visualizer=self.visualizer,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            sample_rows=sample_rows,
            explorer_max_rows=explorer_max_rows,
        )


class ReportTheme:
    def __init__(
        self,
        mode: str = "dark",
        accent_color: str = "#6366F1",
        font_heading: str = "'Clash Display', system-ui, sans-serif",
        font_body: str = "'Geist', 'Segoe UI', system-ui, sans-serif",
    ):
        self.mode = mode
        self.accent = accent_color
        self.font_heading = font_heading
        self.font_body = font_body

    def render(
        self,
        title: str,
        report: DatasetReport,
        bib_results: Optional[dict],
        df: pd.DataFrame,
        visualizer: Visualizer,
        timestamp: str,
        sample_rows: int = 200,
        explorer_max_rows: int = 5000,
    ) -> str:
        overview_plots = visualizer.generate_overview_plots(report)
        col_plots = visualizer.generate_column_plots(df, report)
        bib_plots = (
            visualizer.generate_bibliometric_plots(bib_results) if bib_results else ""
        )
        corr_plots = visualizer.generate_correlation_plots(report)
        explorer_payload = build_explorer_payload(df, report, explorer_max_rows)
        explorer_data = explorer_json_script(explorer_payload)

        has_bib = bool(bib_results)
        has_corr = bool(report.correlation_pairs)

        highlights = compute_highlights(report)
        return self._html(
            title, report, overview_plots, col_plots, bib_plots, corr_plots,
            df, has_bib, has_corr, timestamp, explorer_data, highlights,
            sample_rows=sample_rows,
        )

    def _alerts_html(self, alerts: List[str]) -> str:
        if not alerts:
            return (
                '<div class="dm-alert dm-alert-info">'
                '<span>No critical issues detected</span></div>'
            )
        visible = alerts[:8]
        html = "".join(
            f'<div class="dm-alert dm-alert-warn"><span>{a}</span></div>'
            for a in visible
        )
        if len(alerts) > 8:
            extra = "".join(
                f'<div class="dm-alert dm-alert-warn"><span>{a}</span></div>'
                for a in alerts[8:]
            )
            html += (
                f'<div id="dm-alerts-extra" style="display:none" data-count="{len(alerts) - 8}">'
                f"{extra}</div>"
                f'<button id="dm-alerts-toggle" class="dm-btn-ghost" style="margin-top:10px">'
                f"Show all ({len(alerts) - 8} more)</button>"
            )
        return html

    def _highlights_html(self, highlights: List[str]) -> str:
        if not highlights:
            return ""
        visible = highlights[:8]
        html = "".join(
            f'<div class="dm-alert dm-alert-success"><span>{h}</span></div>'
            for h in visible
        )
        if len(highlights) > 8:
            extra = "".join(
                f'<div class="dm-alert dm-alert-success"><span>{h}</span></div>'
                for h in highlights[8:]
            )
            html += (
                f'<div id="dm-highlights-extra" style="display:none">'
                f"{extra}</div>"
                f'<button id="dm-highlights-toggle" class="dm-btn-ghost" style="margin-top:10px">'
                f"Show all ({len(highlights) - 8} more)</button>"
            )
        return html

    def _html(
        self, title, report, overview_plots, col_plots, bib_plots, corr_plots,
        df, has_bib, has_corr, timestamp, explorer_data, highlights=None,
        sample_rows: int = 200,
    ):
        is_dark = self.mode == "dark"
        bg_page = "#07080F" if is_dark else "#F3F4F6"
        bg_card = "#0F1117" if is_dark else "#FFFFFF"
        bg_sidebar = "#0A0B12" if is_dark else "#1A1A2E"
        text_primary = "#E2E5FF" if is_dark else "#1A1A2E"
        text_secondary = "#9CA3AF" if is_dark else "#6B7280"
        accent = self.accent
        border_color = "rgba(255,255,255,0.06)" if is_dark else "rgba(0,0,0,0.06)"
        alerts_html = self._alerts_html(report.alerts)
        highlights_html = self._highlights_html(highlights or [])

        return f"""<!DOCTYPE html>
<html lang="en" data-theme="{'dark' if is_dark else 'light'}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width,initial-scale=1.0">
    <title>{title}</title>
    {plotly_script_tag()}
    <style>
        @import url('https://api.fontshare.com/v2/css?f[]=clash-display@400,500,600,700&f[]=geist@400,500,600,700&display=swap');

        :root {{
            --bg-page: {bg_page};
            --bg-card: {bg_card};
            --bg-sidebar: {bg_sidebar};
            --accent: {accent};
            --accent-dim: {accent}22;
            --accent-glow: {accent}33;
            --text-primary: {text_primary};
            --text-secondary: {text_secondary};
            --border: {border_color};
            --font-heading: {self.font_heading};
            --font-body: {self.font_body};
            --radius-sm: 8px;
            --radius-md: 14px;
            --radius-lg: 20px;
            --radius-xl: 28px;
            --shadow-card: 0 8px 32px rgba(0,0,0,0.3);
            --transition: all 0.45s cubic-bezier(0.32, 0.72, 0, 1);
            --transition-fast: all 0.25s cubic-bezier(0.32, 0.72, 0, 1);
            --sidebar-width: 260px;
        }}

        *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

        html {{ scroll-behavior: smooth; }}

        body {{
            background: var(--bg-page);
            color: var(--text-primary);
            font-family: var(--font-body);
            min-height: 100vh;
            display: flex;
            line-height: 1.6;
            overflow-x: hidden;
        }}

        ::-webkit-scrollbar {{ width: 5px; height: 5px; }}
        ::-webkit-scrollbar-track {{ background: transparent; }}
        ::-webkit-scrollbar-thumb {{ background: {accent}55; border-radius: 3px; }}

        /* ── Sidebar ── */
        .dm-sidebar {{
            position: fixed;
            top: 0; left: 0;
            width: var(--sidebar-width);
            height: 100vh;
            background: var(--bg-sidebar);
            border-right: 1px solid var(--border);
            padding: 28px 0;
            display: flex;
            flex-direction: column;
            z-index: 100;
            overflow-y: auto;
            transition: transform 0.5s cubic-bezier(0.32, 0.72, 0, 1);
        }}

        .dm-sidebar-brand {{
            padding: 0 22px 24px;
            border-bottom: 1px solid var(--border);
            margin-bottom: 16px;
        }}

        .dm-sidebar-brand h1 {{
            font-family: var(--font-heading);
            font-weight: 700;
            font-size: 1.15rem;
            background: linear-gradient(135deg, var(--accent), {accent}aa);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            letter-spacing: -0.02em;
        }}

        .dm-sidebar-brand small {{
            font-size: 0.68rem;
            color: var(--text-secondary);
            display: block;
            margin-top: 4px;
            font-weight: 500;
        }}

        .dm-sidebar .nav {{
            display: flex;
            flex-direction: column;
            gap: 2px;
            padding: 0 12px;
            flex: 1;
        }}

        .dm-sidebar .nav-btn {{
            background: none;
            border: none;
            color: var(--text-secondary);
            font-family: var(--font-body);
            font-size: 0.82rem;
            font-weight: 500;
            padding: 10px 14px;
            border-radius: var(--radius-sm);
            cursor: pointer;
            text-align: left;
            transition: var(--transition-fast);
            position: relative;
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .dm-sidebar .nav-btn::before {{
            content: '';
            position: absolute;
            left: 0;
            top: 50%;
            transform: translateY(-50%) scaleY(0);
            width: 3px;
            height: 20px;
            background: var(--accent);
            border-radius: 0 3px 3px 0;
            transition: var(--transition-fast);
        }}

        .dm-sidebar .nav-btn:hover {{
            color: var(--text-primary);
            background: rgba(255,255,255,0.03);
        }}

        .dm-sidebar .nav-btn.active {{
            color: var(--accent);
            background: var(--accent-dim);
            font-weight: 600;
        }}

        .dm-sidebar .nav-btn.active::before {{
            transform: translateY(-50%) scaleY(1);
        }}

        .dm-sidebar .nav-icon {{
            width: 18px;
            height: 18px;
            flex-shrink: 0;
            opacity: 0.7;
        }}

        .dm-sidebar .nav-btn.active .nav-icon {{
            opacity: 1;
        }}

        .dm-sidebar-footer {{
            padding: 16px 22px 0;
            border-top: 1px solid var(--border);
            margin-top: auto;
            font-size: 0.68rem;
            color: var(--text-secondary);
        }}

        /* ── Main ── */
        .dm-main {{
            margin-left: var(--sidebar-width);
            flex: 1;
            padding: 32px 36px;
            max-width: 1400px;
            min-height: 100vh;
        }}

        .dm-tab {{
            display: none;
            animation: dmFadeUp 0.55s cubic-bezier(0.32, 0.72, 0, 1) both;
        }}

        .dm-tab.active {{ display: block; }}

        @keyframes dmFadeUp {{
            from {{ opacity: 0; transform: translateY(24px) scale(0.98); }}
            to {{ opacity: 1; transform: translateY(0) scale(1); }}
        }}

        .dm-tab-header {{
            font-family: var(--font-heading);
            font-weight: 700;
            font-size: 1.75rem;
            letter-spacing: -0.03em;
            margin-bottom: 8px;
        }}

        .dm-tab-sub {{
            color: var(--text-secondary);
            font-size: 0.88rem;
            margin-bottom: 28px;
        }}

        /* ── Cards ── */
        .dm-card {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: var(--radius-md);
            box-shadow: var(--shadow-card);
            padding: 22px 24px;
            transition: var(--transition);
            position: relative;
            overflow: hidden;
        }}

        .dm-card::before {{
            content: '';
            position: absolute;
            top: 0; left: 0;
            right: 0;
            height: 2px;
            background: linear-gradient(90deg, transparent, var(--accent), transparent);
            opacity: 0;
            transition: var(--transition);
        }}

        .dm-card:hover::before {{
            opacity: 1;
        }}

        .dm-card:hover {{
            transform: translateY(-2px);
            border-color: var(--accent-dim);
            box-shadow: 0 12px 40px rgba(0,0,0,0.35);
        }}

        .dm-card-title {{
            font-family: var(--font-heading);
            font-weight: 600;
            font-size: 0.95rem;
            margin-bottom: 14px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .dm-card-title .accent-dot {{
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: var(--accent);
            flex-shrink: 0;
        }}

        /* ── Grid ── */
        .dm-grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
        .dm-grid-3 {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; }}
        .dm-grid-4 {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; }}

        /* ── KPI Stats ── */
        .dm-kpi {{
            text-align: center;
            padding: 18px 12px;
        }}

        .dm-kpi-value {{
            font-family: var(--font-heading);
            font-weight: 700;
            font-size: 2rem;
            background: linear-gradient(135deg, var(--accent), {accent}aa);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            letter-spacing: -0.03em;
            line-height: 1.2;
        }}

        .dm-kpi-label {{
            color: var(--text-secondary);
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-top: 4px;
        }}

        .dm-kpi-icon {{
            margin-bottom: 8px;
            opacity: 0.5;
        }}

        /* ── Alerts ── */
        .dm-alert {{
            padding: 12px 16px;
            border-radius: var(--radius-sm);
            margin-bottom: 6px;
            font-size: 0.82rem;
            display: flex;
            align-items: flex-start;
            gap: 10px;
            animation: dmSlideIn 0.35s cubic-bezier(0.32, 0.72, 0, 1) both;
        }}

        .dm-alert-warn {{
            background: rgba(245, 158, 11, 0.1);
            border-left: 3px solid #F59E0B;
            color: #FCD34D;
        }}

        .dm-alert-info {{
            background: rgba(99, 102, 241, 0.1);
            border-left: 3px solid var(--accent);
            color: var(--text-primary);
        }}

        .dm-alert-success {{
            background: rgba(34, 197, 94, 0.1);
            border-left: 3px solid #22C55E;
            color: #86EFAC;
        }}

        @keyframes dmSlideIn {{
            from {{ opacity: 0; transform: translateX(-12px); }}
            to {{ opacity: 1; transform: translateX(0); }}
        }}

        /* ── Table ── */
        .dm-table-wrap {{
            overflow-x: auto;
            border-radius: var(--radius-sm);
        }}

        .dm-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.8rem;
        }}

        .dm-table th {{
            text-align: left;
            padding: 10px 12px;
            font-weight: 600;
            color: var(--accent);
            border-bottom: 2px solid var(--accent-dim);
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            position: sticky;
            top: 0;
            background: var(--bg-card);
        }}

        .dm-table td {{
            padding: 8px 12px;
            border-bottom: 1px solid var(--border);
            transition: var(--transition-fast);
        }}

        .dm-table tr:hover td {{
            background: var(--accent-dim);
        }}

        .dm-table .type-badge {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 99px;
            font-size: 0.68rem;
            font-weight: 600;
        }}

        .type-badge.numeric {{ background: rgba(16, 185, 129, 0.15); color: #10B981; }}
        .type-badge.categorical {{ background: rgba(99, 102, 241, 0.15); color: var(--accent); }}
        .type-badge.datetime {{ background: rgba(245, 158, 11, 0.15); color: #F59E0B; }}
        .type-badge.boolean {{ background: rgba(239, 68, 68, 0.15); color: #EF4444; }}

        /* ── Progress bar ── */
        .dm-progress {{
            height: 4px;
            background: rgba(255,255,255,0.06);
            border-radius: 2px;
            overflow: hidden;
            margin-top: 4px;
        }}

        .dm-progress-bar {{
            height: 100%;
            border-radius: 2px;
            background: linear-gradient(90deg, var(--accent), {accent}88);
            transition: width 0.8s cubic-bezier(0.32, 0.72, 0, 1);
        }}

        /* ── Column detail accordion ── */
        .dm-col-item {{
            border: 1px solid var(--border);
            border-radius: var(--radius-sm);
            margin-bottom: 8px;
            overflow: hidden;
            transition: var(--transition);
        }}

        .dm-col-header {{
            padding: 12px 16px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: rgba(255,255,255,0.02);
            transition: var(--transition-fast);
            user-select: none;
        }}

        .dm-col-header:hover {{
            background: var(--accent-dim);
        }}

        .dm-col-header .col-name {{
            font-weight: 600;
            font-size: 0.88rem;
        }}

        .dm-col-header .col-chevron {{
            transition: transform 0.4s cubic-bezier(0.32, 0.72, 0, 1);
            font-size: 0.75rem;
            color: var(--text-secondary);
        }}

        .dm-col-item.open .col-chevron {{
            transform: rotate(180deg);
        }}

        .dm-col-body {{
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.5s cubic-bezier(0.32, 0.72, 0, 1);
            padding: 0 16px;
        }}

        .dm-col-item.open .dm-col-body {{
            max-height: none;
            padding: 12px 16px 16px;
        }}

        .dm-alert-badge {{
            font-size: 0.65rem;
            font-weight: 600;
            padding: 2px 8px;
            border-radius: 99px;
            background: rgba(245, 158, 11, 0.15);
            color: #F59E0B;
        }}

        .dm-toolbar {{
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
            margin-bottom: 16px;
            align-items: center;
        }}

        .dm-search {{
            flex: 1;
            min-width: 200px;
            padding: 10px 14px;
            border-radius: var(--radius-sm);
            border: 1px solid var(--border);
            background: rgba(255,255,255,0.03);
            color: var(--text-primary);
            font-family: var(--font-body);
            font-size: 0.85rem;
        }}

        .dm-btn-ghost {{
            padding: 8px 14px;
            border-radius: var(--radius-sm);
            border: 1px solid var(--border);
            background: transparent;
            color: var(--text-secondary);
            cursor: pointer;
            font-size: 0.78rem;
            font-weight: 600;
        }}

        .dm-btn-ghost:hover {{ border-color: var(--accent); color: var(--accent); }}

        .dm-sample-controls {{
            display: flex;
            gap: 10px;
            align-items: center;
            margin-bottom: 12px;
            font-size: 0.82rem;
            color: var(--text-secondary);
        }}

        /* ── Interactive Explorer ── */
        .dm-exp-layout {{
            display: grid;
            grid-template-columns: 280px 1fr;
            gap: 20px;
            min-height: 520px;
        }}
        @media(max-width: 1024px) {{
            .dm-exp-layout {{ grid-template-columns: 1fr; }}
        }}
        .dm-exp-sidebar {{
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}
        .dm-exp-filters {{
            max-height: 360px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }}
        .dm-exp-filter-card {{
            background: rgba(255,255,255,0.02);
            border: 1px solid var(--border);
            border-radius: var(--radius-sm);
            padding: 10px 12px;
        }}
        .dm-exp-filter-card label {{
            font-size: 0.72rem;
            font-weight: 600;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.04em;
            display: block;
            margin-bottom: 6px;
        }}
        .dm-exp-filter-card input[type=range] {{
            width: 100%;
            accent-color: var(--accent);
        }}
        .dm-exp-range-row {{
            display: flex;
            justify-content: space-between;
            font-size: 0.72rem;
            color: var(--text-secondary);
            margin-top: 4px;
        }}
        .dm-exp-cat-list {{
            max-height: 120px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 4px;
        }}
        .dm-exp-cat-list label {{
            font-size: 0.78rem;
            font-weight: 400;
            text-transform: none;
            letter-spacing: 0;
            color: var(--text-primary);
            display: flex;
            align-items: center;
            gap: 6px;
            cursor: pointer;
        }}
        .dm-exp-toolbar {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            align-items: center;
            margin-bottom: 12px;
        }}
        .dm-exp-toolbar select {{
            padding: 8px 10px;
            border-radius: var(--radius-sm);
            border: 1px solid var(--border);
            background: rgba(255,255,255,0.03);
            color: var(--text-primary);
            font-family: var(--font-body);
            font-size: 0.82rem;
            min-width: 140px;
        }}
        .dm-exp-stats {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-bottom: 12px;
        }}
        .dm-exp-stat-pill {{
            padding: 6px 12px;
            border-radius: 99px;
            background: var(--accent-dim);
            color: var(--text-primary);
            font-size: 0.78rem;
            font-weight: 600;
        }}
        .dm-exp-chart {{
            min-height: 380px;
            margin-bottom: 16px;
        }}
        .dm-exp-profile {{
            margin-bottom: 16px;
            font-size: 0.82rem;
        }}
        .dm-exp-profile-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
            gap: 8px;
            margin-top: 8px;
        }}
        .dm-exp-profile-item {{
            padding: 8px;
            background: rgba(255,255,255,0.03);
            border-radius: var(--radius-sm);
        }}
        .dm-exp-profile-item span {{
            display: block;
            font-size: 0.65rem;
            color: var(--text-secondary);
            text-transform: uppercase;
        }}
        .dm-exp-profile-item strong {{
            font-size: 0.9rem;
        }}
        .dm-exp-col-checks {{
            max-height: 180px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 4px;
        }}
        .dm-exp-col-checks label {{
            font-size: 0.78rem;
            display: flex;
            gap: 6px;
            align-items: center;
            cursor: pointer;
        }}
        .dm-exp-banner {{
            padding: 10px 14px;
            border-radius: var(--radius-sm);
            background: rgba(245, 158, 11, 0.12);
            border: 1px solid rgba(245, 158, 11, 0.35);
            color: #FCD34D;
            font-size: 0.82rem;
            margin-bottom: 16px;
        }}

        /* ── Stat grid in column detail ── */
        .dm-stat-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
            gap: 8px;
        }}

        .dm-stat-item {{
            padding: 8px 10px;
            background: rgba(255,255,255,0.03);
            border-radius: var(--radius-sm);
        }}

        .dm-stat-item .stat-label {{
            font-size: 0.65rem;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-weight: 600;
        }}

        .dm-stat-item .stat-value {{
            font-size: 0.95rem;
            font-weight: 700;
            margin-top: 2px;
        }}

        /* ── Top values mini bar ── */
        .dm-top-val {{ display: flex; align-items: center; gap: 8px; margin: 3px 0; font-size: 0.75rem; }}
        .dm-top-val-bar {{ height: 4px; border-radius: 2px; background: var(--accent); min-width: 4px; transition: width 0.6s cubic-bezier(0.32, 0.72, 0, 1); }}

        /* ── Plot containers ── */
        .dm-plot {{
            width: 100%;
            min-height: 320px;
        }}

        .dm-plot .plotly-graph-div {{
            width: 100% !important;
        }}

        /* ── Loading shimmer ── */
        .dm-shimmer {{
            background: linear-gradient(90deg, var(--bg-card) 25%, rgba(255,255,255,0.04) 50%, var(--bg-card) 75%);
            background-size: 200% 100%;
            animation: shimmer 1.8s ease-in-out infinite;
            border-radius: var(--radius-sm);
        }}

        @keyframes shimmer {{
            0% {{ background-position: -200% 0; }}
            100% {{ background-position: 200% 0; }}
        }}

        /* ── Responsive ── */
        @media (max-width: 1024px) {{
            .dm-grid-4 {{ grid-template-columns: repeat(2, 1fr); }}
        }}

        @media (max-width: 768px) {{
            .dm-sidebar {{
                transform: translateX(-100%);
                width: 280px;
            }}
            .dm-sidebar.open {{ transform: translateX(0); }}
            .dm-main {{
                margin-left: 0;
                padding: 20px 16px;
            }}
            .dm-grid-2, .dm-grid-3, .dm-grid-4 {{ grid-template-columns: 1fr; }}
            .dm-kpi-value {{ font-size: 1.5rem; }}
            .dm-tab-header {{ font-size: 1.35rem; }}

            .dm-mobile-toggle {{
                display: flex !important;
                position: fixed;
                top: 12px;
                left: 12px;
                z-index: 200;
                width: 40px;
                height: 40px;
                border-radius: 12px;
                background: var(--bg-card);
                border: 1px solid var(--border);
                color: var(--text-primary);
                align-items: center;
                justify-content: center;
                cursor: pointer;
                font-size: 1.2rem;
                box-shadow: var(--shadow-card);
            }}
        }}

        .dm-mobile-toggle {{ display: none; }}

        /* ── Mobile sidebar overlay ── */
        .dm-sidebar-overlay {{
            display: none;
            position: fixed;
            inset: 0;
            background: rgba(0,0,0,0.5);
            z-index: 99;
            backdrop-filter: blur(4px);
        }}

        .dm-sidebar-overlay.open {{ display: block; }}

        @media (min-width: 769px) {{
            .dm-sidebar-overlay {{ display: none !important; }}
        }}

        /* ── Stagger animation for cards ── */
        .dm-card {{
            animation: dmCardIn 0.5s cubic-bezier(0.32, 0.72, 0, 1) both;
        }}

        @keyframes dmCardIn {{
            from {{ opacity: 0; transform: translateY(16px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        .dm-card:nth-child(1) {{ animation-delay: 0.05s; }}
        .dm-card:nth-child(2) {{ animation-delay: 0.1s; }}
        .dm-card:nth-child(3) {{ animation-delay: 0.15s; }}
        .dm-card:nth-child(4) {{ animation-delay: 0.2s; }}
        .dm-card:nth-child(5) {{ animation-delay: 0.25s; }}
        .dm-card:nth-child(6) {{ animation-delay: 0.3s; }}
        .dm-card:nth-child(7) {{ animation-delay: 0.35s; }}
        .dm-card:nth-child(8) {{ animation-delay: 0.4s; }}

        /* ── Smooth type badge pulse ── */
        .type-badge {{
            opacity: 1;
        }}
    </style>
</head>
<body>
    <button class="dm-mobile-toggle" id="dmToggle" onclick="toggleSidebar()" aria-label="Toggle sidebar">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/>
        </svg>
    </button>

    <div class="dm-sidebar-overlay" id="dmOverlay" onclick="toggleSidebar()"></div>

    <aside class="dm-sidebar" id="dmSidebar">
        <div class="dm-sidebar-brand">
            <h1>DataMatrix</h1>
            <small>{report.n_rows} rows · {report.n_cols} cols</small>
        </div>
        <div class="nav">
            <button class="nav-btn active" data-tab="overview" onclick="switchTab('overview', this)">
                <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="9"/><rect x="14" y="3" width="7" height="5"/><rect x="14" y="12" width="7" height="9"/><rect x="3" y="16" width="7" height="5"/></svg>
                Overview
            </button>
            <button class="nav-btn" data-tab="variables" onclick="switchTab('variables', this)">
                <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg>
                Variables
            </button>
            <button class="nav-btn" data-tab="explore" onclick="switchTab('explore', this)">
                <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/><line x1="11" y1="8" x2="11" y2="14"/><line x1="8" y1="11" x2="14" y2="11"/></svg>
                Explore
            </button>
            {f'''
            <button class="nav-btn" data-tab="correlations" onclick="switchTab('correlations', this)">
                <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
                Correlations
            </button>''' if has_corr else ""}
            {f'''
            <button class="nav-btn" data-tab="bibliometrics" onclick="switchTab('bibliometrics', this)">
                <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>
                Bibliometrics
            </button>''' if has_bib else ""}
            <button class="nav-btn" data-tab="sample" onclick="switchTab('sample', this)">
                <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>
                Data Sample
            </button>
        </div>
        <div class="dm-sidebar-footer">
            Generated {timestamp}
        </div>
    </aside>

    <main class="dm-main">
        <!-- Overview -->
        <div class="dm-tab active" id="tab-overview">
            <h2 class="dm-tab-header">Dataset Overview</h2>
            <p class="dm-tab-sub">High-level summary of data structure, quality, and composition</p>

            <div class="dm-grid-4">
                <div class="dm-card dm-kpi">
                    <div class="dm-kpi-icon">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{accent}" stroke-width="1.5"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>
                    </div>
                    <div class="dm-kpi-value">{report.estimated_rows}</div>
                    <div class="dm-kpi-label">Rows</div>
                </div>
                <div class="dm-card dm-kpi">
                    <div class="dm-kpi-icon">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{accent}" stroke-width="1.5"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>
                    </div>
                    <div class="dm-kpi-value">{report.n_cols}</div>
                    <div class="dm-kpi-label">Columns</div>
                </div>
                <div class="dm-card dm-kpi">
                    <div class="dm-kpi-icon">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{accent}" stroke-width="1.5"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
                    </div>
                    <div class="dm-kpi-value">{report.n_missing_total}</div>
                    <div class="dm-kpi-label">Missing Cells ({report.p_missing_total:.1f}%)</div>
                </div>
                <div class="dm-card dm-kpi">
                    <div class="dm-kpi-icon">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{accent}" stroke-width="1.5"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>
                    </div>
                    <div class="dm-kpi-value">{report.n_duplicates}</div>
                    <div class="dm-kpi-label">Duplicates</div>
                </div>
            </div>

            <div class="dm-grid-2" style="margin-top: 20px;">
                <div class="dm-card">
                    <div class="dm-card-title"><span class="accent-dot"></span>Column Types</div>
                    <div style="display:flex;flex-wrap:wrap;gap:12px;margin:8px 0 12px">
                        <span style="display:flex;align-items:center;gap:6px;font-size:0.82rem">
                            <span style="width:10px;height:10px;border-radius:3px;background:#10B981"></span>
                            Numeric: {len(report.numeric_columns)}
                        </span>
                        <span style="display:flex;align-items:center;gap:6px;font-size:0.82rem">
                            <span style="width:10px;height:10px;border-radius:3px;background:{accent}"></span>
                            Categorical: {len(report.categorical_columns)}
                        </span>
                        <span style="display:flex;align-items:center;gap:6px;font-size:0.82rem">
                            <span style="width:10px;height:10px;border-radius:3px;background:#F59E0B"></span>
                            Datetime: {len(report.datetime_columns)}
                        </span>
                        <span style="display:flex;align-items:center;gap:6px;font-size:0.82rem">
                            <span style="width:10px;height:10px;border-radius:3px;background:#EF4444"></span>
                            Boolean: {len(report.boolean_columns)}
                        </span>
                    </div>
                </div>
                <div class="dm-card">
                    <div class="dm-card-title"><span class="accent-dot"></span>Data Quality</div>
                    <div style="margin:6px 0">
                        <div style="display:flex;justify-content:space-between;font-size:0.82rem;margin-bottom:2px">
                            <span>Completeness</span>
                            <span style="font-weight:600">{100 - report.p_missing_total:.1f}%</span>
                        </div>
                        <div class="dm-progress" title="Share of non-missing cells across the dataset">
                            <div class="dm-progress-bar" style="width:{100 - report.p_missing_total}%"></div>
                        </div>
                    </div>
                    <div style="margin:6px 0">
                        <div style="display:flex;justify-content:space-between;font-size:0.82rem;margin-bottom:2px">
                            <span>Memory Usage</span>
                            <span style="font-weight:600">{report.memory_usage}</span>
                        </div>
                    </div>
                </div>
            </div>

            <div class="dm-card" style="margin-top:20px">
                <div class="dm-card-title"><span class="accent-dot"></span>Alerts & Insights</div>
                {f'<div style="margin-bottom:12px"><div style="font-size:0.75rem;font-weight:600;color:var(--text-secondary);margin-bottom:8px;text-transform:uppercase;letter-spacing:0.06em">Strengths</div>{highlights_html}</div>' if highlights_html else ''}
                {f'<div style="font-size:0.75rem;font-weight:600;color:var(--text-secondary);margin-bottom:8px;text-transform:uppercase;letter-spacing:0.06em">Warnings</div>' if highlights_html else ''}
                {alerts_html}
            </div>

            {overview_plots}
        </div>

        <!-- Variables -->
        <div class="dm-tab" id="tab-variables">
            <h2 class="dm-tab-header">Variable Analysis</h2>
            <p class="dm-tab-sub">Detailed profiling for each column in the dataset</p>

            <div class="dm-toolbar">
                <input id="dm-col-search" class="dm-search" type="search"
                       placeholder="Search columns..." aria-label="Search columns"/>
                <button id="dm-expand-all" class="dm-btn-ghost" data-state="closed">Expand all</button>
            </div>

            <div class="dm-card" style="margin-bottom:16px">
                <div class="dm-card-title"><span class="accent-dot"></span>Column Summary</div>
                <div class="dm-table-wrap">
                    <table class="dm-table" id="dm-summary-table">
                        <thead>
                            <tr>
                                <th>Column</th>
                                <th>Type</th>
                                <th>Unique</th>
                                <th>Missing</th>
                                <th>Missing %</th>
                                <th>Mean</th>
                                <th>Std</th>
                                <th>Min</th>
                                <th>Max</th>
                            </tr>
                        </thead>
                        <tbody>
                            {"".join(f'''
                            <tr data-col="{p.name}">
                                <td style="font-weight:600">{p.name}</td>
                                <td><span class="type-badge {p.inferred_type}">{p.inferred_type}</span></td>
                                <td>{p.n_unique}</td>
                                <td>{p.n_missing}</td>
                                <td>{p.p_missing:.1f}%</td>
                                <td>{f"{p.mean:.3f}" if p.inferred_type == "numeric" and p.mean is not None else "—"}</td>
                                <td>{f"{p.std:.3f}" if p.inferred_type == "numeric" and p.std is not None else "—"}</td>
                                <td>{f"{p.min:.3f}" if p.inferred_type == "numeric" and p.min is not None else "—"}</td>
                                <td>{f"{p.max:.3f}" if p.inferred_type == "numeric" and p.max is not None else "—"}</td>
                            </tr>''' for p in report.column_profiles.values())}
                        </tbody>
                    </table>
                </div>
            </div>

            {col_plots}
        </div>

        <!-- Correlations -->
        {f'''
        <div class="dm-tab" id="tab-correlations">
            <h2 class="dm-tab-header">Correlation Analysis</h2>
            <p class="dm-tab-sub">Pearson correlation pairs between numeric variables</p>
            {corr_plots}
        </div>''' if has_corr else ""}

        <!-- Bibliometrics -->
        {f'''
        <div class="dm-tab" id="tab-bibliometrics">
            <h2 class="dm-tab-header">Bibliometric Analysis</h2>
            <p class="dm-tab-sub">Publication trends, top authors, and source analysis</p>
            {bib_plots}
        </div>''' if has_bib else ""}

        <!-- Interactive Explorer -->
        <div class="dm-tab" id="tab-explore">
            <h2 class="dm-tab-header">Interactive Explorer</h2>
            <p class="dm-tab-sub">Filter your dataset, inspect columns, and build live visualizations — works with any tabular data</p>
            <div id="dm-exp-truncated" class="dm-exp-banner" style="display:none"></div>

            <div class="dm-exp-layout">
                <aside class="dm-exp-sidebar dm-card">
                    <input id="dm-exp-search" class="dm-search" type="search"
                           placeholder="Search across all columns..." aria-label="Global search"/>
                    <div id="dm-exp-filters" class="dm-exp-filters"></div>
                    <button id="dm-exp-reset" class="dm-btn-ghost">Reset all filters</button>
                    <div>
                        <div class="dm-card-title" style="margin-bottom:8px"><span class="accent-dot"></span>Table columns</div>
                        <div id="dm-exp-col-checks" class="dm-exp-col-checks"></div>
                    </div>
                </aside>

                <section class="dm-exp-main">
                    <div class="dm-exp-toolbar">
                        <select id="dm-exp-x" aria-label="X axis column"></select>
                        <select id="dm-exp-y" aria-label="Y axis column">
                            <option value="">— Y column (optional) —</option>
                        </select>
                        <select id="dm-exp-color" aria-label="Color column">
                            <option value="">— Color (optional) —</option>
                        </select>
                        <select id="dm-exp-chart-type" aria-label="Chart type">
                            <option value="auto">Auto chart</option>
                            <option value="histogram">Histogram</option>
                            <option value="bar">Bar chart</option>
                            <option value="scatter">Scatter</option>
                            <option value="box">Box plot</option>
                            <option value="pie">Pie / Donut</option>
                            <option value="line">Line chart</option>
                        </select>
                        <button id="dm-exp-download" class="dm-btn-ghost">Download filtered CSV</button>
                    </div>

                    <div id="dm-exp-stats" class="dm-exp-stats"></div>
                    <div id="dm-exp-profile" class="dm-card dm-exp-profile"></div>
                    <div id="dm-explorer-chart" class="dm-card dm-plot dm-exp-chart"></div>

                    <div class="dm-card">
                        <div class="dm-card-title"><span class="accent-dot"></span>Filtered data preview</div>
                        <div id="dm-exp-table-wrap" class="dm-table-wrap"></div>
                        <div class="dm-sample-controls">
                            <button id="dm-exp-prev" class="dm-btn-ghost">Previous</button>
                            <span id="dm-exp-page-info">Page 1</span>
                            <button id="dm-exp-next" class="dm-btn-ghost">Next</button>
                        </div>
                    </div>
                </section>
            </div>
        </div>

        <!-- Sample -->
        <div class="dm-tab" id="tab-sample">
            <h2 class="dm-tab-header">Data Sample</h2>
            <p class="dm-tab-sub">Paginated preview of dataset rows</p>
            <div class="dm-card">
                {f'<div class="dm-exp-banner">Showing the first {min(sample_rows, len(df)):,} of {len(df):,} rows. Use the Explore tab for the full interactive view.</div>' if len(df) > sample_rows else ''}
                <div class="dm-sample-controls">
                    <button id="dm-sample-prev" class="dm-btn-ghost">Previous</button>
                    <span id="dm-sample-page-info">Page 1</span>
                    <button id="dm-sample-next" class="dm-btn-ghost">Next</button>
                </div>
                <div class="dm-table-wrap">
                    {df.head(sample_rows).to_html(classes="dm-table", index=False, table_id="dm-sample-table")}
                </div>
            </div>
        </div>
    </main>

    {explorer_data}
    <script>{datamatrix_runtime_js()}</script>
</body>
</html>"""
