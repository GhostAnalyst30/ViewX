from __future__ import annotations

import os
import uuid
import warnings
from typing import Dict, List, Optional, Tuple, Union, Literal

import pandas as pd
import plotly.express as px

from viewx.shared import (
    fig_to_html,
    html_modal_runtime_js,
    html_plotly_resize_js,
    html_table_sort_js,
    plotly_script_tag,
)
from viewx.shared.themes import THEMES as SHARED_THEMES, resolve_theme, get_theme
from viewx.shared.column_profile import (
    classify_columns,
    coerce_types,
    format_value,
    rank_categorical,
    rank_numeric,
    top_correlation_pairs,
)
from viewx.plot.factory import build_plotly_figure


# ──────────────────────────────────────────────────────────────────────────────
# SVG ICON LIBRARY  (Heroicons-inspired, 24×24 viewBox)
# ──────────────────────────────────────────────────────────────────────────────
def _svg(path_d: str, size: int = 20, color: str = "currentColor") -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 24 24" fill="none" stroke="{color}" '
        f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        f'{path_d}</svg>'
    )


ICON_PATHS = {
    "chart-bar":    '<rect x="3" y="12" width="4" height="9"/><rect x="10" y="7" width="4" height="14"/><rect x="17" y="3" width="4" height="18"/>',
    "trending-up":  '<polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/>',
    "dollar":       '<line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>',
    "hash":         '<line x1="4" y1="9" x2="20" y2="9"/><line x1="4" y1="15" x2="20" y2="15"/><line x1="10" y1="3" x2="8" y2="21"/><line x1="16" y1="3" x2="14" y2="21"/>',
    "target":       '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
    "zap":          '<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>',
    "box":          '<path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/>',
    "award":        '<circle cx="12" cy="8" r="6"/><path d="M15.477 12.89 17 22l-5-3-5 3 1.523-9.11"/>',
    "users":        '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    "activity":     '<polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>',
    "percent":      '<line x1="19" y1="5" x2="5" y2="19"/><circle cx="6.5" cy="6.5" r="2.5"/><circle cx="17.5" cy="17.5" r="2.5"/>',
    "clock":        '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
    "info":         '<circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>',
    "database":     '<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/>',
    "eye":          '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>',
    "grid":         '<rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/>',
    "maximize":     '<path d="M8 3H5a2 2 0 0 0-2 2v3"/><path d="M21 8V5a2 2 0 0 0-2-2h-3"/><path d="M3 16v3a2 2 0 0 0 2 2h3"/><path d="M16 21h3a2 2 0 0 0 2-2v-3"/>',
    "close":        '<line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>',
}

ICONS_SVG = {k: _svg(v) for k, v in ICON_PATHS.items()}

# Cycle of icons for auto KPIs
_KPI_ICON_CYCLE = [
    "trending-up", "dollar", "hash", "target", "zap", "box", "award", "users",
    "activity", "percent", "clock", "chart-bar",
]


def _kpi_icon(index: int, size: int = 22) -> str:
    key = _KPI_ICON_CYCLE[index % len(_KPI_ICON_CYCLE)]
    return _svg(ICON_PATHS[key], size=size)

ThemeName = Literal[
    "corporate_blue", "dark_enterprise", "modern_green",
    "void_indigo", "glass_ocean", "cyberpunk_neon"
]

# ──────────────────────────────────────────────────────────────────────────────
# THEME MANAGER
# ──────────────────────────────────────────────────────────────────────────────
class ThemeManager:
    """
    Manages dashboard themes. Supports built-in names/IDs *and* custom palettes.

    Custom palette example
    ----------------------
    ThemeManager({
        "bg_page":        "#0D0D0D",
        "bg_card":        "#1A1A2E",
        "accent":         "#E94560",
        "text_primary":   "#EAEAEA",
        "text_secondary": "#888888",
        "shadow":         "0 4px 20px rgba(0,0,0,0.5)",
    })
    """

    # Canonical registry lives in viewx.shared.themes (one definition for all engines)
    BUILT_IN: Dict[str, dict] = SHARED_THEMES

    def __init__(self, theme: Union[int, ThemeName, dict, None] = None):
        self.custom = False
        self.set_theme(theme)

    # ------------------------------------------------------------------
    def set_theme(self, theme: Union[int, ThemeName, dict, None]):
        if isinstance(theme, dict):
            self.current_theme_name = "custom"
            base = {
                "id": -1, "name": "Custom",
                "bg_page": "#F3F4F6", "bg_card": "#FFFFFF",
                "accent": "#0078D4", "text_primary": "#1A1A2E",
                "text_secondary": "#6B7280",
                "shadow": "0 2px 12px rgba(0,0,0,0.08)",
                "chart_colors": ["#0078D4","#3B82F6","#60A5FA","#93C5FD","#BFDBFE"],
            }
            base.update(theme)
            self.current_theme = base
            self.custom = True
            return

        name = resolve_theme(theme) if theme is not None else get_theme()
        self.current_theme_name = name
        self.current_theme = self.BUILT_IN[name]

    # ------------------------------------------------------------------
    def get_colors(self) -> Tuple[str, str, str, str]:
        t = self.current_theme
        return t["bg_page"], t["bg_card"], t["accent"], t["text_primary"]

    def chart_colors(self) -> List[str]:
        return self.current_theme.get(
            "chart_colors",
            ["#0078D4","#10B981","#F59E0B","#EF4444","#8B5CF6"],
        )

    # ------------------------------------------------------------------
    def get_global_css(self) -> str:
        t = self.current_theme
        bg_page, bg_card, accent, text_primary = self.get_colors()
        text_secondary = t["text_secondary"]
        shadow = t["shadow"]

        css = f"""
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        :root {{
            --vx-bg-page:       {bg_page};
            --vx-bg-card:       {bg_card};
            --vx-accent:        {accent};
            --vx-text-primary:  {text_primary};
            --vx-text-secondary:{text_secondary};
            --vx-card-radius:   14px;
            --vx-shadow:        {shadow};
            --vx-transition:    all 0.35s cubic-bezier(.16,1,.3,1);
            --vx-ease:          cubic-bezier(0.32,0.72,0,1);
        }}
        *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            background: var(--vx-bg-page);
            color: var(--vx-text-primary);
            font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
            overflow: hidden;
            height: 100dvh; width: 100vw;
        }}
        .vx-card {{
            background: var(--vx-bg-card);
            border-radius: var(--vx-card-radius);
            box-shadow: var(--vx-shadow);
            transition: var(--vx-transition);
            overflow: auto;
            border: 1px solid rgba(128,128,128,0.08);
            position: relative;
        }}
        .vx-card::before {{
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 2px;
            background: linear-gradient(90deg, transparent, var(--vx-accent), transparent);
            opacity: 0;
            transition: var(--vx-transition);
        }}
        .vx-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 28px rgba(0,0,0,0.14);
        }}
        .vx-card:hover::before {{ opacity: 1; }}
        .vx-card.vx-card-static:hover {{
            transform: none;
            box-shadow: var(--vx-shadow);
        }}
        .vx-card-header {{
            margin: 0; color: var(--vx-text-primary); font-weight: 600;
            font-size: 0.88rem;
            border-bottom: 2px solid rgba(128,128,128,0.12); padding-bottom: 6px;
        }}
        .vx-kpi-body {{
            padding: 18px 20px; display: flex; align-items: center;
            gap: 14px; height: 100%; position: relative; overflow: hidden;
        }}
        .vx-sortable-table th {{ cursor: pointer; user-select: none; }}
        .vx-sortable-table th:hover {{ background: {accent}18; }}
        .plotly-graph-div, .js-plotly-plot, .plot-container {{
            width: 100% !important; height: 100% !important;
        }}
        .vx-card::-webkit-scrollbar {{ width:5px; height:5px; }}
        .vx-card::-webkit-scrollbar-track {{ background: transparent; }}
        .vx-card::-webkit-scrollbar-thumb {{ background:{accent}55; border-radius:3px; }}

        /* ── Modal overlay ── */
        .vx-modal-overlay {{
            display: none; position: fixed; inset: 0;
            background: rgba(0,0,0,0.7); z-index: 9000;
            align-items: center; justify-content: center;
            backdrop-filter: blur(4px);
        }}
        .vx-modal-overlay.open {{ display: flex; }}
        .vx-modal-box {{
            background: {bg_card};
            border-radius: 16px;
            box-shadow: 0 24px 80px rgba(0,0,0,0.4);
            border: 1px solid {accent}33;
            width: min(92vw, 1100px);
            max-height: 88vh;
            display: flex; flex-direction: column;
            overflow: hidden;
            animation: vxModalIn .22s cubic-bezier(.16,1,.3,1);
        }}
        @keyframes vxModalIn {{
            from {{ opacity:0; transform: scale(.96) translateY(12px); }}
            to   {{ opacity:1; transform: scale(1) translateY(0); }}
        }}
        .vx-modal-header {{
            display: flex; align-items: center; justify-content: space-between;
            padding: 18px 24px 14px;
            border-bottom: 1px solid {accent}22;
            flex-shrink: 0;
        }}
        .vx-modal-header h3 {{
            font-size: 1.05rem; font-weight: 700; color: var(--vx-text-primary);
        }}
        .vx-modal-close {{
            background: none; border: none; cursor: pointer;
            color: var(--vx-text-secondary); border-radius: 8px;
            width:32px; height:32px; display:flex; align-items:center; justify-content:center;
            transition: var(--vx-transition);
        }}
        .vx-modal-close:hover {{ background:{accent}22; color:{accent}; }}
        .vx-modal-body {{
            flex: 1; overflow: auto; padding: 20px 24px 24px;
        }}

        /* ── Info FAB button on charts ── */
        .vx-chart-info-btn {{
            position: absolute; bottom: 10px; right: 10px;
            width: 32px; height: 32px; border-radius: 50%;
            background: {accent}EE; border: none; cursor: pointer;
            display: flex; align-items: center; justify-content: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.25);
            transition: var(--vx-transition); z-index: 10;
            opacity: 0.75;
        }}
        .vx-chart-info-btn:hover {{ opacity:1; transform: scale(1.12); }}
        .vx-chart-info-btn svg {{ pointer-events: none; }}

        /* ── Data button ── */
        .vx-data-fab {{
            position: fixed; bottom: 22px; right: 22px;
            background: {accent}; color: #fff;
            border: none; border-radius: 50px;
            padding: 10px 20px; font-weight: 700; font-size: 0.82rem;
            cursor: pointer; z-index: 8000;
            display: flex; align-items: center; gap: 8px;
            box-shadow: 0 4px 18px {accent}55;
            transition: var(--vx-transition); letter-spacing: 0.3px;
        }}
        .vx-data-fab:hover {{ transform: translateY(-2px); box-shadow: 0 8px 28px {accent}66; }}
        """

        if t.get("glass"):
            css += """
            .vx-card {
                backdrop-filter: blur(18px) saturate(180%);
                -webkit-backdrop-filter: blur(18px) saturate(180%);
                border: 1px solid rgba(255,255,255,0.1);
            }"""

        if t.get("border_glow"):
            css += f"""
            .vx-card {{
                border: 1px solid {accent}77;
                box-shadow: 0 0 22px {accent}33;
            }}"""

        return css


# ──────────────────────────────────────────────────────────────────────────────
# MAIN DASHBOARD CLASS
# ──────────────────────────────────────────────────────────────────────────────
class Dashboard:
    """
    Manual dashboard builder.

    Usage
    -----
    dash = Dashboard(title="Sales Report", theme="dark_enterprise")
    dash.add_valuebox(title="Revenue", value="$1.2M", icon_key="dollar", row=1, col=1, height=2, width=3)
    dash.add_chart(fig=my_fig, title="Trend", row=1, col=4, height=4, width=9)
    dash.save("report.html")

    One-step version: ``Dashboard.auto(df).save("report.html")``
    """

    def __init__(
        self,
        title: str = "ViewX Dashboard",
        theme: Union[int, ThemeName, dict, None] = None,
        cols: int = 12,
        rows: int = 12,
        gap: int = 16,
        padding: int = 22,
        navbar: Optional[dict] = None,
        authors: Union[str, List, None] = None,
        data_button: bool = False,
        df: Optional[pd.DataFrame] = None,
        verbose: bool = False,
    ):
        self.title = title
        self.theme_manager = ThemeManager(theme)
        self.cols = cols
        self.rows = rows
        self.gap = gap
        self.padding = padding
        self.navbar = navbar
        self.data_button = data_button
        self._df = df
        self.verbose = verbose
        self._needs_plotly = False

        if isinstance(authors, list):
            self.authors = [a if isinstance(a, dict) else {"name": a, "email": None} for a in authors]
        elif isinstance(authors, str):
            self.authors = [{"name": authors, "email": None}]
        else:
            self.authors = []

        self.grid_css: List[str] = []
        self.components_html: List[str] = []
        self._component_counter = 0

        if not self.title:
            self.title = "Interactive Dashboard - ViewX"

        self._log("HTML DASHBOARD")
        self._log(f" - Title: {self.title}")
        self._log(f" - Theme: {self.theme_manager.current_theme_name}")
        self._log(f" - Layout: {self.cols} x {self.rows}")

        if self.navbar:
            self._log("\nNAVBAR CONFIGURATION:")
            for key, value in self.navbar.items():
                if key == "items":
                    self._log(f" - {key}:")
                    for item in value:
                        dest = item.get("anchor") or item.get("link", "")
                        self._log(f"    - {item['label']} -> {dest}")
                else:
                    self._log(f" - {key}: {value}")

        if self.authors:
            self._log("\nAUTHORS:")
            for author in self.authors:
                if author.get("email"):
                    self._log(f" - {author['name']} ({author['email']})")
                else:
                    self._log(f" - {author['name']}")

        if self._df is not None:
            self._log(f"\nShape of DataFrame: {self._df.shape[0]} rows x {self._df.shape[1]} columns")

    def _log(self, msg: str):
        if self.verbose:
            print(msg)


    # ── helpers ───────────────────────────────────────────────────────────────
    def _uid(self) -> str:
        self._component_counter += 1
        return f"c{self._component_counter}_{uuid.uuid4().hex[:6]}"

    def _register_block(self, uid: str, row: int, col: int, h: int, w: int):
        self.grid_css.append(
            f".{uid} {{ grid-area: {row} / {col} / {row+h} / {col+w}; }}"
        )

    def _hex_to_rgba(self, hex_color: str, alpha: float = 0.12) -> str:
        hx = hex_color.lstrip("#")
        r, g, b = int(hx[0:2], 16), int(hx[2:4], 16), int(hx[4:6], 16)
        return f"rgba({r},{g},{b},{alpha})"

    def _accent_hex(self) -> str:
        _, _, accent, _ = self.theme_manager.get_colors()
        return accent if accent.startswith("#") else "#0078D4"

    # ── add_valuebox ──────────────────────────────────────────────────────────
    def add_valuebox(
        self,
        title: str,
        value,
        icon_key: str = "chart-bar",
        color: str = None,
        row: int = 1, col: int = 1, height: int = 2, width: int = 3,
        # legacy emoji icon ignored silently
        icon: str = None,
    ) -> "Dashboard":
        uid = self._uid()
        self._register_block(uid, row, col, height, width)
        _, bg_card, accent, _ = self.theme_manager.get_colors()
        box_color = color or accent

        # Build SVG icon
        icon_path = ICON_PATHS.get(icon_key, ICON_PATHS["chart-bar"])
        icon_rendered = _svg(icon_path, size=24, color=box_color)

        self._log("Adding ValueBox:")
        self._log(f" - Title: {title}")
        self._log(f" - Value: {value}")
        self._log(f" - Icon: {icon_key}")
        self._log(f" - Color: {box_color}")
        self._log(f" - Position: (row {row}, col {col}), (height {height}, width {width})")
    

        html = f"""
        <style>
        .vb-{uid} {{
            padding: 18px 20px; display: flex; align-items: center;
            gap: 14px; border-left: 5px solid {box_color};
            height: 100%; position: relative; overflow: hidden;
        }}
        .vb-{uid}::after {{
            content:''; position:absolute; right:-18px; top:-18px;
            width:80px; height:80px; border-radius:50%;
            background:{box_color}0D;
        }}
        .vb-icon-{uid} {{
            width: 48px; height: 48px; border-radius: 12px;
            background: {box_color}15;
            display: flex; align-items: center; justify-content: center;
            flex-shrink: 0;
        }}
        .vb-label-{uid} {{
            font-size: 0.72rem; font-weight: 700; letter-spacing: 0.6px;
            text-transform: uppercase; color: var(--vx-text-secondary);
            margin-bottom: 5px;
        }}
        .vb-val-{uid} {{
            font-size: 1.75rem; font-weight: 800;
            color: var(--vx-text-primary); line-height: 1; letter-spacing: -0.5px;
        }}
        </style>
        <div class="vx-card vb-{uid} {uid} vx-valuebox" id="{uid}">
            <div class="vb-icon-{uid}">{icon_rendered}</div>
            <div>
                <div class="vb-label-{uid}">{title}</div>
                <div class="vb-val-{uid}">{value}</div>
            </div>
        </div>"""
        self.components_html.append(html)
        return self

    # ── add_infobox ───────────────────────────────────────────────────────────
    def add_infobox(
        self,
        df: pd.DataFrame,
        variable: str,
        info: List[str] = None,
        title: str = None,
        color: str = None,
        row: int = 1, col: int = 1, height: int = 3, width: int = 3,
    ) -> "Dashboard":
        """
        Multi-stat infobox for a single column.

        Parameters
        ----------
        df       : DataFrame containing the variable
        variable : Column name to analyse
        info     : list of stats to show. Supported:
                   mean, median, std, min, max, sum, count,
                   kurtosis, skewness, q1, q3, iqr, nulls, nunique
        title    : card title (defaults to variable name)
        """
        if info is None:
            info = ["mean", "median", "std", "min", "max", "count"]

        uid = self._uid()
        self._register_block(uid, row, col, height, width)
        _, _, accent, _ = self.theme_manager.get_colors()
        box_color = color or accent
        card_title = title or variable

        series = df[variable].dropna()
        is_numeric = pd.api.types.is_numeric_dtype(series)

        stat_map = {
            "mean":     ("Mean",     f"{series.mean():,.3g}"         if is_numeric else "—"),
            "median":   ("Median",   f"{series.median():,.3g}"       if is_numeric else "—"),
            "std":      ("Std Dev",  f"{series.std():,.3g}"          if is_numeric else "—"),
            "min":      ("Min",      f"{series.min():,.3g}"          if is_numeric else str(series.min())),
            "max":      ("Max",      f"{series.max():,.3g}"          if is_numeric else str(series.max())),
            "sum":      ("Sum",      f"{series.sum():,.3g}"          if is_numeric else "—"),
            "count":    ("Count",    f"{len(series):,}"),
            "kurtosis": ("Kurtosis", f"{series.kurtosis():.3f}"      if is_numeric else "—"),
            "skewness": ("Skewness", f"{series.skew():.3f}"          if is_numeric else "—"),
            "q1":       ("Q1 (25%)", f"{series.quantile(0.25):,.3g}" if is_numeric else "—"),
            "q3":       ("Q3 (75%)", f"{series.quantile(0.75):,.3g}" if is_numeric else "—"),
            "iqr":      ("IQR",      f"{(series.quantile(0.75)-series.quantile(0.25)):,.3g}" if is_numeric else "—"),
            "nulls":    ("Nulls",    f"{df[variable].isna().sum():,}"),
            "nunique":  ("Unique",   f"{series.nunique():,}"),
        }

        self._log("Adding InfoBox:")
        self._log(f" - Title: {card_title}")
        self._log(f" - Variable: {variable}")
        self._log(f" - Stats: {', '.join(info)}")
        self._log(f" - Color: {box_color}")
        self._log(f" - Position: (row {row}, col {col}), (height {height}, width {width})")

        rows_html = ""
        for key in info:
            if key not in stat_map:
                continue
            label, val = stat_map[key]
            rows_html += f"""
            <div class="ib-row-{uid}">
                <span class="ib-label-{uid}">{label}</span>
                <span class="ib-val-{uid}">{val}</span>
            </div>"""

        html = f"""
        <style>
        .ib-card-{uid} {{
            padding: 16px 18px; display: flex; flex-direction: column;
            height: 100%; border-top: 4px solid {box_color};
        }}
        .ib-title-{uid} {{
            font-size: 0.78rem; font-weight: 700; letter-spacing: 0.5px;
            text-transform: uppercase; color: {box_color}; margin-bottom: 12px;
        }}
        .ib-rows-{uid} {{ display: flex; flex-direction: column; gap: 7px; flex: 1; overflow: auto; }}
        .ib-row-{uid} {{
            display: flex; justify-content: space-between; align-items: center;
            padding: 5px 8px; border-radius: 7px; background: {box_color}09;
        }}
        .ib-label-{uid} {{
            font-size: 0.73rem; color: var(--vx-text-secondary); font-weight: 500;
        }}
        .ib-val-{uid} {{
            font-size: 0.82rem; font-weight: 700; color: var(--vx-text-primary);
        }}
        </style>
        <div class="vx-card ib-card-{uid} {uid}" id="{uid}">
            <div class="ib-title-{uid}">{card_title}</div>
            <div class="ib-rows-{uid}">{rows_html}</div>
        </div>"""
        self.components_html.append(html)
        return self

    # ── add_chart ─────────────────────────────────────────────────────────────
    ChartType = Literal[
        "line", "bar", "bar_h", "scatter", "area",
        "pie", "donut", "histogram", "box", "violin",
        "heatmap", "funnel", "treemap", "bubble"
    ]
    def add_chart(
        self,
        data=None, fig=None,
        chart_type: ChartType = "line",
        x=None, y=None, z=None,
        title: str = "",
        row: int = 1, col: int = 1, height: int = 6, width: int = 6,
        show_info_btn: bool = True,
        downsample: bool = True,
        # Extra info for the info modal
        _info_stats: Optional[dict] = None,
    ) -> "Dashboard":
        uid = self._uid()
        self._register_block(uid, row, col, height, width)
        _, _, accent, text = self.theme_manager.get_colors()
        colors = self.theme_manager.chart_colors()

        # Accept vx.plot() Chart objects transparently
        from viewx.plot import Chart
        if isinstance(data, Chart):
            fig, data = data, None
        if isinstance(fig, Chart):
            if not fig.interactive:
                raise ValueError(
                    "Static (matplotlib) charts cannot be embedded in a Dashboard. "
                    "Build the chart with static=False."
                )
            if not title:
                title = fig.title
            fig = fig.fig

        if fig is not None:
            chart_fig = fig
            chart_fig.update_layout(
                colorway=colors,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color=text,
                font_family="'Inter','Segoe UI',sans-serif",
            )
            first_trace = chart_fig.data[0] if chart_fig.data else None
            if first_trace and hasattr(first_trace, "line") and first_trace.line.color is None:
                chart_fig.update_traces(
                    selector=dict(type="scatter"),
                    line=dict(color=colors[0]),
                )
        elif data is not None and (x is not None or y is not None):
            chart_fig = build_plotly_figure(
                data, kind=chart_type, x=x, y=y, z=z,
                title=title, colors=colors, downsample=downsample,
            )
        else:
            raise ValueError("Provide fig, a vx.plot Chart, or (data + x/y)")

        grid_color = self._hex_to_rgba(self._accent_hex(), 0.10)
        chart_fig.update_layout(
            autosize=True,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color=text,
            title_text="",        # title shown in card header
            margin=dict(l=36, r=18, t=24, b=28),
            font_family="'Inter','Segoe UI',sans-serif",
            hovermode="closest",
            height=None, width=None,
            legend=dict(font=dict(size=11)),
            colorway=colors,
        )
        chart_fig.update_xaxes(gridcolor=grid_color, zerolinecolor=grid_color, showgrid=True)
        chart_fig.update_yaxes(gridcolor=grid_color, zerolinecolor=grid_color, showgrid=True)

        self._needs_plotly = True
        plot_html = fig_to_html(chart_fig, include_js=False)

        self._log("Adding Chart:")
        self._log(f" - Title: {title}")
        if chart_fig:
            self._log(f" - Type: {chart_fig.data[0].type if chart_fig.data else 'empty'}")
        if data is not None:
            self._log(f" - Data: {data.shape[0]} rows x {data.shape[1]} cols")
            self._log(f"   - x: {x}, y: {y}, z: {z}")
        self._log(f" - Position: (row {row}, col {col}), (height {height}, width {width})")
        if fig is not None and chart_fig:
            self._log(" - Figure provided directly")

        # Info button + modal
        info_btn_html = ""
        info_modal_html = ""
        if show_info_btn:
            modal_id = f"modal_{uid}"
            # Build stats content
            stats_content = ""
            if _info_stats:
                rows = ""
                for k, v in _info_stats.items():
                    rows += f"<tr><td style='padding:6px 10px;color:var(--vx-text-secondary);font-size:.8rem'>{k}</td><td style='padding:6px 10px;font-weight:600;font-size:.82rem'>{v}</td></tr>"
                stats_content = f"<table style='width:100%;border-collapse:collapse'>{rows}</table>"
            else:
                stats_content = "<p style='color:var(--vx-text-secondary);font-size:.85rem'>No additional statistics available.</p>"

            close_svg = _svg(ICON_PATHS["close"], size=16)
            info_svg = _svg(ICON_PATHS["info"], size=14, color="#fff")

            info_btn_html = f"""
            <button class="vx-chart-info-btn" onclick="vxOpenModal('{modal_id}')"
                    title="Chart details" aria-label="Open chart details">
                {info_svg}
            </button>"""

            info_modal_html = f"""
            <div id="{modal_id}" class="vx-modal-overlay" role="dialog" aria-modal="true"
                 aria-labelledby="{modal_id}-title">
                <div class="vx-modal-box" style="max-width:520px">
                    <div class="vx-modal-header">
                        <h3 id="{modal_id}-title">{title or "Chart Details"}</h3>
                        <button class="vx-modal-close" aria-label="Close dialog"
                                onclick="vxCloseModal('{modal_id}')">{close_svg}</button>
                    </div>
                    <div class="vx-modal-body">{stats_content}</div>
                </div>
            </div>"""

        html = f"""
        <style>
        .pc-{uid} {{
            padding: 12px 14px; display: grid;
            grid-template-rows: auto 1fr; height: 100%;
            width: 100%; overflow: hidden; gap: 6px; position: relative;
        }}
        .pc-{uid} h4 {{
            margin: 0; color: var(--vx-text-primary); font-weight: 600;
            font-size: 0.88rem;
            border-bottom: 2px solid {accent}28; padding-bottom: 6px;
        }}
        .pcc-{uid} {{ position:relative; width:100%; height:100%; min-height:0; overflow:hidden; }}
        .pcc-{uid} .plotly-graph-div {{ width:100%!important; height:100%!important; }}
        </style>
        <div class="vx-card pc-{uid} {uid} vx-card-static" id="{uid}">
            {f'<h4 class="vx-card-header">{title}</h4>' if title else '<div></div>'}
            <div class="pcc-{uid}">
                {plot_html}
                {info_btn_html}
            </div>
        </div>
        {info_modal_html}
        <script>{html_plotly_resize_js(f'pcc-{uid}')}</script>"""
        self.components_html.append(html)
        return self

    """
    # line / area
    dash.add_chart(data=df, chart_type="line",  x="fecha",     y="ventas",    ...)
    dash.add_chart(data=df, chart_type="area",  x="mes",       y="ingresos",  ...)

    # bar / bar_h
    dash.add_chart(data=df, chart_type="bar",   x="region",    y="unidades",  ...)
    dash.add_chart(data=df, chart_type="bar_h", x="producto",  y="ventas",    ...)

    # scatter con color por categoría
    dash.add_chart(data=df, chart_type="scatter", x="precio", y="margen", z="categoria", ...)

    # bubble — z es el tamaño de la burbuja
    dash.add_chart(data=df, chart_type="bubble", x="precio", y="margen", z="volumen", ...)

    # histogram — solo x
    dash.add_chart(data=df, chart_type="histogram", x="edad", ...)

    # box / violin — x puede ser None si no hay categoría
    dash.add_chart(data=df, chart_type="box",    x="region", y="salario", ...)
    dash.add_chart(data=df, chart_type="violin", x="region", y="salario", ...)

    # pie / donut
    dash.add_chart(data=df["pais"].value_counts().reset_index(),
                chart_type="donut", x="pais", y="count", ...)

    # funnel
    dash.add_chart(data=df, chart_type="funnel", x="etapa", y="usuarios", ...)

    # treemap — x puede ser lista para jerarquía
    dash.add_chart(data=df, chart_type="treemap", x=["continente","pais"], y="poblacion", ...)

    # heatmap — necesita los tres
    pivot_df = df  # debe tener cols para fila, columna y valor
    dash.add_chart(data=df, chart_type="heatmap", x="mes", y="region", z="ventas", ...)
    """

    # ── add_table ─────────────────────────────────────────────────────────────
    def add_table(
        self, df: pd.DataFrame, title: str = "",
        row: int = 1, col: int = 1, height: int = 4, width: int = 6,
    ) -> "Dashboard":
        uid = self._uid()
        self._register_block(uid, row, col, height, width)
        _, _, accent, _ = self.theme_manager.get_colors()
        table_html = df.to_html(
            classes=f"vxt-{uid} vx-sortable-table",
            border=0,
            index=False,
            max_rows=200,
        )

        self._log("Adding Table:")
        self._log(f" - Title: {title}")
        self._log(f" - DataFrame: {df.shape[0]} rows x {df.shape[1]} cols")
        self._log(f" - Position: (row {row}, col {col}), (height {height}, width {width})")

        html = f"""
        <style>
        .tc-{uid} {{ padding:14px 16px; display:flex; flex-direction:column; height:100%; }}
        .tc-{uid} h4 {{ color:var(--vx-text-primary); margin:0 0 10px; font-weight:600; font-size:.88rem; flex-shrink:0; }}
        .tcc-{uid} {{ overflow:auto; flex:1; scrollbar-width:thin; }}
        .vxt-{uid} {{ width:100%; border-collapse:collapse; font-size:.78rem; }}
        .vxt-{uid} th {{
            background:{accent}12; color:{accent}; padding:9px 8px;
            text-align:left; font-weight:700; position:sticky; top:0;
            border-bottom:2px solid {accent}33; font-size:.75rem; letter-spacing:.3px;
        }}
        .vxt-{uid} td {{ padding:7px 8px; border-bottom:1px solid rgba(128,128,128,.1); color:var(--vx-text-primary); }}
        .vxt-{uid} tr:hover {{ background:{accent}07; }}
        </style>
        <div class="vx-card tc-{uid} {uid} vx-card-static" id="{uid}">
            {f'<h4 class="vx-card-header">{title}</h4>' if title else ""}
            <div class="tcc-{uid}">{table_html}</div>
        </div>"""
        self.components_html.append(html)
        return self

    # ── add_text ──────────────────────────────────────────────────────────────
    def add_text(
        self, content: str,
        row: int = 1, col: int = 1, height: int = 2, width: int = 6,
    ) -> "Dashboard":
        uid = self._uid()
        self._register_block(uid, row, col, height, width)
        _, _, accent, _ = self.theme_manager.get_colors()

        self._log("Adding Text:")
        self._log(f" - Content: {content[:100]}{'...' if len(content)>100 else content}")
        self._log(f" - Position: (row {row}, col {col}), (height {height}, width {width})")

        html = f"""
        <style>
        .txc-{uid} {{ padding:20px; line-height:1.6; color:var(--vx-text-primary); height:100%; overflow:auto; font-size:.88rem; }}
        .txc-{uid} h2,.txc-{uid} h3 {{ color:{accent}; margin-top:0; font-weight:700; }}
        </style>
        <div class="vx-card txc-{uid} {uid}" id="{uid}">{content}</div>"""
        self.components_html.append(html)
        return self

    # Legacy alias used in early statslibx examples.
    add_plot = add_chart

    # ── navbar ────────────────────────────────────────────────────────────────
    def _build_navbar(self) -> str:
        if not self.navbar:
            return ""
        _, bg_card, accent, _ = self.theme_manager.get_colors()
        items_html = ""
        for i in self.navbar.get("items", []):
            anchor = i.get("anchor")
            if anchor:
                href = f"#{anchor}"
                onclick = f"onclick=\"event.preventDefault();document.getElementById('{anchor}')?.scrollIntoView({{behavior:'smooth',block:'start'}})\""
                items_html += f'<a href="{href}" class="nav-link" {onclick}>{i["label"]}</a>'
            else:
                items_html += f'<a href="{i.get("link", "#")}" class="nav-link">{i["label"]}</a>'
        author_block = ""
        if self.authors:
            parts = []
            for a in self.authors:

                if isinstance(a, str):
                    parts.append(f'<span class="nav-author">{a}</span>')
                    continue

                name = a.get("name", "Unknown")
                email = a.get("email")

                if email:
                    parts.append(
                        f'<a href="mailto:{email}" class="nav-author nav-alink">{name}</a>'
                    )
                else:
                    parts.append(
                        f'<span class="nav-author">{name}</span>'
                    )
            author_block = f'<div class="nav-author-wrap">by {", ".join(parts)}</div>'

        brand_icon = _svg(ICON_PATHS["grid"], size=18, color=accent)

        return f"""
        <style>
        .vx-navbar {{
            position:fixed; top:0; left:0; right:0; height:54px;
            background:{bg_card}F5; display:flex; align-items:center;
            justify-content:space-between; padding:0 24px; z-index:1000;
            box-shadow:0 1px 0 rgba(128,128,128,.12);
            border-bottom:2px solid {accent};
            backdrop-filter:blur(8px);
        }}
        .nav-brand-wrap {{ display:flex; flex-direction:column; gap:1px; }}
        .nav-brand {{
            font-weight:800; font-size:1.1rem; color:{accent};
            text-decoration:none; letter-spacing:-.4px;
            display:flex; align-items:center; gap:7px;
        }}
        .nav-author-wrap {{ font-size:.7rem; color:var(--vx-text-secondary); font-weight:500; }}
        .nav-author {{ font-size:.7rem; color:var(--vx-text-secondary); }}
        .nav-alink {{ color:{accent}; text-decoration:none; }}
        .nav-alink:hover {{ text-decoration:underline; }}
        .nav-links {{ display:flex; gap:18px; }}
        .nav-link {{
            color:var(--vx-text-primary); text-decoration:none;
            font-weight:600; font-size:.82rem; opacity:.75;
            transition:var(--vx-transition);
        }}
        .nav-link:hover {{ opacity:1; color:{accent}; }}
        </style>
        <nav class="vx-navbar">
            <div class="nav-brand-wrap">
                <a href="#" class="nav-brand">{brand_icon}{self.navbar.get("title", self.title)}</a>
                {author_block}
            </div>
            <div class="nav-links">{items_html}</div>
        </nav>"""

    # ── data modal ────────────────────────────────────────────────────────────
    def _build_data_modal(self) -> str:
        if not self.data_button or self._df is None:
            return ""
        _, _, accent, _ = self.theme_manager.get_colors()

        df = self._df
        # Describe stats
        desc = df.describe(include="all").round(3).fillna("—")
        desc_html = desc.to_html(border=0, classes="vx-desc-tbl")

        # Data preview (first 100 rows)
        preview_html = df.head(100).to_html(border=0, index=False, classes="vx-prev-tbl")

        close_svg = _svg(ICON_PATHS["close"], size=16)
        db_svg = _svg(ICON_PATHS["database"], size=16, color="#fff")

        n_rows, n_cols_total = df.shape
        numerics_count = len(df.select_dtypes(include="number").columns)
        cats_count = len(df.select_dtypes(include=["object", "category"]).columns)

        summary_badge = (
            f'<div class="vx-dm-badges">'
            f'<span class="vx-dm-badge">{n_rows:,} rows</span>'
            f'<span class="vx-dm-badge">{n_cols_total} columns</span>'
            f'<span class="vx-dm-badge">{numerics_count} numeric</span>'
            f'<span class="vx-dm-badge">{cats_count} categorical</span>'
            f'</div>'
        )

        return f"""
        <style>
        .vx-desc-tbl, .vx-prev-tbl {{
            width:100%; border-collapse:collapse; font-size:.75rem;
        }}
        .vx-desc-tbl th, .vx-prev-tbl th {{
            background:{accent}12; color:{accent}; padding:8px 10px;
            text-align:left; font-weight:700; position:sticky; top:0;
            border-bottom:2px solid {accent}33;
        }}
        .vx-desc-tbl td, .vx-prev-tbl td {{
            padding:6px 10px; border-bottom:1px solid rgba(128,128,128,.09);
            color:var(--vx-text-primary);
        }}
        .vx-desc-tbl tr:hover, .vx-prev-tbl tr:hover {{ background:{accent}06; }}
        .vx-dm-badges {{ display:flex; flex-wrap:wrap; gap:8px; margin-bottom:16px; }}
        .vx-dm-badge {{
            padding:4px 12px; border-radius:20px; font-size:.74rem;
            font-weight:600; background:{accent}15; color:{accent};
        }}
        .vx-dm-layout {{ display:grid; grid-template-columns:1fr 1fr; gap:20px; height:100%; }}
        .vx-dm-pane {{ overflow:auto; height:100%; }}
        .vx-dm-pane-title {{
            font-size:.78rem; font-weight:700; text-transform:uppercase;
            letter-spacing:.5px; color:var(--vx-text-secondary); margin-bottom:10px;
        }}
        @media(max-width:700px){{ .vx-dm-layout{{ grid-template-columns:1fr; }} }}
        </style>

        <div id="vx-data-modal" class="vx-modal-overlay" role="dialog" aria-modal="true"
             aria-labelledby="vx-data-modal-title">
            <div class="vx-modal-box" style="width: min(98vw, 1600px); max-height: 95vh;">
                <div class="vx-modal-header">
                    <h3 id="vx-data-modal-title">Dataset Overview</h3>
                    <button class="vx-modal-close" aria-label="Close dialog"
                            onclick="vxCloseModal('vx-data-modal')">
                        {close_svg}
                    </button>
                </div>
                <div class="vx-modal-body">
                    {summary_badge}
                    <div style="margin-bottom:12px">
                        <input id="vx-data-search" type="search" placeholder="Filter preview rows..."
                               aria-label="Filter preview rows"
                               style="width:100%;max-width:360px;padding:8px 12px;border-radius:8px;border:1px solid {accent}33;background:transparent;color:var(--vx-text-primary);font-size:.82rem"/>
                    </div>
                    <div class="vx-dm-layout">
                        <div class="vx-dm-pane">
                            <div class="vx-dm-pane-title">Data Preview</div>
                            {preview_html}
                        </div>
                        <div class="vx-dm-pane">
                            <div class="vx-dm-pane-title">Statistical Summary</div>
                            {desc_html}
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <button class="vx-data-fab" aria-label="View dataset"
                onclick="vxOpenModal('vx-data-modal')">
            {db_svg} View Data
        </button>"""

    # ── save / show ───────────────────────────────────────────────────────────
    def save(self, path: str = "dashboard.html", open_browser: bool = False) -> str:
        """Write the dashboard to an HTML file. Returns the file path."""
        return self._render_to_file(path, open_browser)

    def show(self, path: str = "dashboard.html") -> str:
        """Write the dashboard and open it in the default browser."""
        return self._render_to_file(path, True)

    def generate(self, filename: str = "dashboard.html", show: bool = True) -> str:
        """Deprecated: use ``save()`` or ``show()`` instead."""
        warnings.warn(
            "Dashboard.generate() is deprecated; use save(path) or show().",
            DeprecationWarning, stacklevel=2,
        )
        return self._render_to_file(filename, show)

    def _render_to_file(self, filename: str, open_browser: bool) -> str:
        _, _, accent, _ = self.theme_manager.get_colors()
        nav_offset = self.padding + 54 if self.navbar else self.padding
        plotly_head = plotly_script_tag() if self._needs_plotly else ""

        full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <title>{self.title}</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width,initial-scale=1">
    {plotly_head}
    <style>
        {self.theme_manager.get_global_css()}
        .dashboard-container {{
            padding: {nav_offset}px {self.padding}px {self.padding}px;
            height: 100vh; width: 100vw;
            display: flex; flex-direction: column; overflow: hidden;
        }}
        .vx-grid {{
            display: grid;
            grid-template-columns: repeat({self.cols}, 1fr);
            grid-template-rows: repeat({self.rows}, 1fr);
            gap: {self.gap}px;
            flex: 1; min-height: 0;
        }}
        {chr(10).join(self.grid_css)}
        .vx-card {{ animation: vxCardIn .4s cubic-bezier(0.32,0.72,0,1) both; }}
        @keyframes vxCardIn {{
            from {{ opacity:0; transform:translateY(18px) scale(0.98); filter:blur(2px); }}
            to   {{ opacity:1; transform:translateY(0) scale(1); filter:blur(0); }}
        }}
        .vx-valuebox {{ animation: vxValueIn .5s cubic-bezier(0.32,0.72,0,1) both; }}
        @keyframes vxValueIn {{
            from {{ opacity:0; transform:translateY(12px); }}
            to   {{ opacity:1; transform:translateY(0); }}
        }}
        {chr(10).join([f".vx-card:nth-child({i+1}){{animation-delay:{i*0.05}s}}" for i in range(len(self.components_html))])}
        @media(max-width:768px){{
            .vx-grid {{ display:flex; flex-direction:column; overflow-y:auto; }}
            .vx-card {{ min-height:220px; flex-shrink:0; }}
            body {{ overflow-y:auto; }}
        }}
    </style>
</head>
<body>
    {self._build_navbar()}
    <div class="dashboard-container">
        <div class="vx-grid">
            {"".join(self.components_html)}
        </div>
    </div>
    {self._build_data_modal()}
    <script>{html_modal_runtime_js()}</script>
    <script>{html_table_sort_js()}</script>
</body>
</html>"""

        directory = os.path.dirname(filename)
        if directory:
            os.makedirs(directory, exist_ok=True)
        with open(filename, "w", encoding="utf-8") as f:
            f.write(full_html)

        if open_browser:
            import webbrowser
            webbrowser.open("file://" + os.path.abspath(filename))

        self._log("Dashboard generated successfully.")
        self._log(f" - Total components: {len(self.components_html)}")
        self._log(f" - Filename: {filename}")
        return filename

    # ── auto ──────────────────────────────────────────────────────────────────
    @classmethod
    def auto(
        cls,
        data: pd.DataFrame,
        columns: Optional[List[str]] = None,
        theme: Union[int, str, dict, None] = None,
        title: str = "Auto Dashboard",
        navbar: Optional[dict] = None,
        authors=None,
        method_valuebox: Literal["sum", "mean", "median", "max", "min"] = "sum",
        data_button: bool = False,
        color_palette: Optional[List[str]] = None,
        layout=None,
        verbose: bool = False,
    ) -> "Dashboard":
        """
        Build a professional dashboard from any DataFrame using intelligent layout.
        Returns the Dashboard instance; call ``.save(path)`` or ``.show()`` on it.

        layout options:
          - None / "default": standard KPI strip + charts
          - "kpi_focus": taller KPI row, fewer charts
          - "chart_focus": compact KPIs, charts dominate
          - "table_first": data table on main grid
          - list[dict]: custom placement with type kpi/chart/table + row/col/height/width
        """
        template = theme

        # ── 1. Column selection ───────────────────────────────────────────────
        cols_to_use = list(columns) if columns is not None else list(data.columns)
        missing = [c for c in cols_to_use if c not in data.columns]
        if missing:
            raise KeyError(f"Columns not found: {missing}. Available: {list(data.columns)}")

        # ── 2. Smart type coercion (shared heuristics) ────────────────────────
        df, coerced = coerce_types(data, cols_to_use)
        if coerced and verbose:
            print("Auto coercion:", ", ".join(f"{k}: {v}" for k, v in coerced.items()))

        # ── 3. Classify columns ───────────────────────────────────────────────
        col_types = classify_columns(df)
        all_num  = [c for c, t in col_types.items() if t == "numeric"]
        all_cat  = [c for c, t in col_types.items() if t == "categorical"]
        all_dt   = [c for c, t in col_types.items() if t == "datetime"]
        all_bool = [c for c, t in col_types.items() if t == "boolean"]

        if verbose:
            print(f"Detected -> numeric:{len(all_num)}  categorical:{len(all_cat)}  "
                  f"datetime:{len(all_dt)}  boolean:{len(all_bool)}")

        # ── 4. Statistical study: rank & select best variables ────────────────
        ranked_num = rank_numeric(df, all_num)
        ranked_cat = rank_categorical(df, all_cat)
        scatter_pairs = top_correlation_pairs(df, ranked_num)

        if verbose and scatter_pairs:
            print("Top correlations:")
            for a, b, r in scatter_pairs[:3]:
                print(f"    {a} x {b}  r={r:.3f}")

        # ── 5. Palette & theme setup ──────────────────────────────────────────
        tm_tmp = ThemeManager(template)
        if color_palette:
            tm_tmp.current_theme["chart_colors"] = color_palette
        pal = tm_tmp.chart_colors()

        def _fig_style(fig):
            """Apply palette and strip title (shown in card header)."""
            fig.update_layout(colorway=pal, title_text="")
            return fig

        # ── 6. Value formatter (shared) ───────────────────────────────────────
        _fmt = format_value

        # WebGL for large scatter clouds
        scatter_render = "webgl" if len(df) > 5000 else "auto"

        # ── 7. Build component catalogue ─────────────────────────────────────
        #
        #  LAYOUT TEMPLATE  (12-column grid, row heights all equal)
        #  ┌──────────────────────────────────────────────────────┐
        #  │  KPI  │  KPI  │  KPI  │  KPI   (row 1, height=2)    │
        #  ├────────────────────┬─────────────────────────────────┤
        #  │  CHART A  (col 6) │  CHART B  (col 6)  (row 3-7)    │
        #  ├────────────────────┴─────────────────────────────────┤
        #  │  CHART C  (col 6) │  CHART D  (col 6)  (row 8-12)   │
        #  └──────────────────────────────────────────────────────┘
        #  Data table lives inside the data modal (not in main grid)
        #
        #  KPI strip: up to 4; if fewer, they stretch proportionally
        #  Charts:    up to 4; fewer → remaining slots stay empty or widen

        MAX_KPIS   = 4
        MAX_CHARTS = 4
        COLS       = 12
        KPI_H      = 2
        CHART_H    = 5
        layout_preset = layout if isinstance(layout, str) else "default"
        add_main_table = False
        table_slot = None
        custom_layout = layout if isinstance(layout, list) else None

        if layout_preset == "kpi_focus":
            KPI_H = 3
            MAX_CHARTS = 2
            CHART_H = 4
        elif layout_preset == "chart_focus":
            KPI_H = 1
            MAX_KPIS = 2
            CHART_H = 5
        elif layout_preset == "table_first":
            add_main_table = True
            table_slot = (8, 1, 4, COLS)
            CHART_H = 4
            MAX_CHARTS = 2

        # --- KPIs (top 4 numeric, best scores) ---
        kpi_cols   = ranked_num[:MAX_KPIS]
        n_kpis     = len(kpi_cols)

        planned_kpis: List[Tuple[str, str, str]] = []
        for i, col in enumerate(kpi_cols):
            s = df[col]
            if   method_valuebox == "mean":   val = s.mean()
            elif method_valuebox == "median": val = s.median()
            elif method_valuebox == "max":    val = s.max()
            elif method_valuebox == "min":    val = s.min()
            else:                             val = s.sum()
            planned_kpis.append((col, _fmt(val), _KPI_ICON_CYCLE[i % len(_KPI_ICON_CYCLE)]))

        # --- Charts: plan intelligently, cap at MAX_CHARTS ---
        charts: List[Tuple] = []   # (fig, label, stats_dict)

        def _stats_num(col: str) -> dict:
            s = df[col].dropna()
            return {
                "Count":     f"{len(s):,}",
                "Mean":      _fmt(s.mean()),
                "Median":    _fmt(s.median()),
                "Std Dev":   _fmt(s.std()),
                "Min":       _fmt(s.min()),
                "Max":       _fmt(s.max()),
                "Nulls":     f"{df[col].isna().sum():,}",
            }

        # Chart slot 1: time-series of best numeric vs datetime
        if all_dt and ranked_num and len(charts) < MAX_CHARTS:
            date_col = all_dt[0]
            num_col  = ranked_num[0]
            agg = df.groupby(date_col)[num_col].sum().reset_index()
            fig = _fig_style(px.line(agg, x=date_col, y=num_col, markers=False,
                                     color_discrete_sequence=pal))
            fig.update_traces(line=dict(width=2.5))
            charts.append((fig, f"{num_col} over time", _stats_num(num_col)))

        # Chart slot 2: best categorical × best numeric (bar)
        if ranked_cat and ranked_num and len(charts) < MAX_CHARTS:
            cat_col = ranked_cat[0]
            num_col = ranked_num[0]
            agg = df.groupby(cat_col)[num_col].sum().nlargest(12).reset_index()
            fig = _fig_style(px.bar(
                agg.sort_values(num_col, ascending=True),
                x=num_col, y=cat_col, orientation="h",
                color=cat_col, color_discrete_sequence=pal,
            ))
            fig.update_layout(showlegend=False, yaxis=dict(tickfont=dict(size=11)))
            stats = {
                "Categories": str(df[cat_col].nunique()),
                "Top":        str(df[cat_col].value_counts().index[0]),
                f"Total {num_col}": _fmt(df[num_col].sum()),
            }
            charts.append((fig, f"{num_col} by {cat_col}", stats))

        # Chart slot 3: highest-correlation scatter pair
        if scatter_pairs and len(charts) < MAX_CHARTS:
            col_a, col_b, _ = scatter_pairs[0]
            color_col = ranked_cat[0] if ranked_cat else None
            fig = _fig_style(px.scatter(
                df, x=col_a, y=col_b, color=color_col,
                opacity=0.65, color_discrete_sequence=pal,
                render_mode=scatter_render,
            ))
            stats = {
                "Pearson r":    f"{df[[col_a, col_b]].corr().iloc[0,1]:.3f}",
                f"{col_a} mean": _fmt(df[col_a].mean()),
                f"{col_b} mean": _fmt(df[col_b].mean()),
            }
            charts.append((fig, f"{col_a} vs {col_b}", stats))

        # Chart slot 4a: second-best correlated pair scatter
        if len(scatter_pairs) >= 2 and len(charts) < MAX_CHARTS:
            col_a, col_b, _ = scatter_pairs[1]
            color_col = ranked_cat[0] if ranked_cat else None
            fig = _fig_style(px.scatter(
                df, x=col_a, y=col_b, color=color_col,
                opacity=0.65, color_discrete_sequence=pal,
                render_mode=scatter_render,
            ))
            stats = {
                "Pearson r":    f"{df[[col_a, col_b]].corr().iloc[0,1]:.3f}",
                f"{col_a} mean": _fmt(df[col_a].mean()),
                f"{col_b} mean": _fmt(df[col_b].mean()),
            }
            charts.append((fig, f"{col_a} vs {col_b}", stats))

        # Chart slot 4b (fallback): donut for second categorical
        if len(ranked_cat) >= 2 and len(charts) < MAX_CHARTS:
            cat_col = ranked_cat[1]
            counts = df[cat_col].value_counts().head(10).reset_index()
            counts.columns = [cat_col, "count"]
            fig = _fig_style(px.pie(counts, names=cat_col, values="count", hole=0.45,
                                    color_discrete_sequence=pal))
            charts.append((fig, f"Distribution: {cat_col}", {
                "Unique": str(df[cat_col].nunique()),
                "Top":    str(df[cat_col].mode().iloc[0]),
            }))

        # Chart slot 4c (fallback): boolean donut
        for bool_col in all_bool:
            if len(charts) >= MAX_CHARTS:
                break
            counts = df[bool_col].value_counts().reset_index()
            counts.columns = [bool_col, "count"]
            fig = _fig_style(px.pie(counts, names=bool_col, values="count", hole=0.42,
                                    color_discrete_sequence=pal))
            charts.append((fig, f"{bool_col} distribution", {
                "True":  str((df[bool_col] == True).sum()),
                "False": str((df[bool_col] == False).sum()),
            }))

        # Chart slot 4d (fallback): pure categorical only dataset
        if not ranked_num and ranked_cat and len(charts) < MAX_CHARTS:
            for cat_col in ranked_cat[:MAX_CHARTS - len(charts)]:
                counts = df[cat_col].value_counts().head(10).reset_index()
                counts.columns = [cat_col, "count"]
                fig = _fig_style(px.pie(counts, names=cat_col, values="count", hole=0.42,
                                        color_discrete_sequence=pal))
                charts.append((fig, f"Distribution: {cat_col}", {
                    "Unique": str(df[cat_col].nunique()),
                }))

        n_charts = min(len(charts), MAX_CHARTS)
        charts   = charts[:n_charts]

        if verbose:
            print(f"Layout -> {n_kpis} KPIs, {n_charts} charts, preset={layout_preset}")

        # ── 8. Single-template layout ─────────────────────────────────────────
        #
        #  Grid is always 12 columns.
        #  Row budget:
        #    • KPI strip:  always 2 rows  (if any KPIs)
        #    • Chart rows: 2 chart rows × CHART_H rows each
        #    Total rows = KPI_H + 2 × CHART_H   = 2 + 10 = 12
        #
        #  KPI widths:  split evenly across 12 cols (min 1, max 4 KPIs)
        #  Chart widths:
        #    0 charts → nothing
        #    1 chart  → full width (12)
        #    2 charts → each 6
        #    3 charts → first row: one full (12); second row: two×6
        #    4 charts → 2×6 / 2×6
        #
        #  All chart cells in the same logical row are the same height,
        #  so nothing is "taller" than its neighbour.

        has_kpis = n_kpis > 0
        kpi_row_start   = 1
        chart_row_start = (kpi_row_start + KPI_H) if has_kpis else 1

        # KPI widths
        if n_kpis == 0:
            kpi_slots = []
        else:
            kpi_w = COLS // n_kpis
            remainder = COLS - kpi_w * n_kpis
            kpi_widths = [kpi_w + (1 if i < remainder else 0) for i in range(n_kpis)]
            kpi_col_starts = []
            cur = 1
            for w in kpi_widths:
                kpi_col_starts.append(cur)
                cur += w
            kpi_slots = list(zip(kpi_col_starts, kpi_widths))  # (col_start, width)

        # Chart grid
        # row_a → charts[0], charts[1]  (or just charts[0] if only 1 total)
        # row_b → charts[2], charts[3]  (if they exist)
        if n_charts == 0:
            chart_slots = []
        elif n_charts == 1:
            chart_slots = [(chart_row_start, 1, CHART_H, COLS)]
        elif n_charts == 2:
            chart_slots = [
                (chart_row_start, 1,           CHART_H, 6),
                (chart_row_start, 7,           CHART_H, 6),
            ]
        elif n_charts == 3:
            # Row A: first chart full-width
            # Row B: next two split
            chart_slots = [
                (chart_row_start,            1, CHART_H, COLS),
                (chart_row_start + CHART_H,  1, CHART_H, 6),
                (chart_row_start + CHART_H,  7, CHART_H, 6),
            ]
        else:  # 4
            chart_slots = [
                (chart_row_start,           1, CHART_H, 6),
                (chart_row_start,           7, CHART_H, 6),
                (chart_row_start + CHART_H, 1, CHART_H, 6),
                (chart_row_start + CHART_H, 7, CHART_H, 6),
            ]

        # Total rows
        if chart_slots:
            last_r, _, last_h, _ = max(chart_slots, key=lambda x: x[0] + x[2])
            total_rows = last_r + last_h - 1
        elif add_main_table and table_slot:
            total_rows = table_slot[0] + table_slot[2] - 1
        elif has_kpis:
            total_rows = kpi_row_start + KPI_H - 1
        else:
            total_rows = 6
        total_rows = max(total_rows, 4)

        # ── 9. Assemble ───────────────────────────────────────────────────────
        eff_template = template
        if color_palette and not isinstance(template, dict):
            tm_base = ThemeManager(template)
            eff_template = dict(tm_base.current_theme)
            eff_template["chart_colors"] = color_palette

        dash = cls(
            title=title,
            theme=eff_template,
            cols=COLS,
            rows=total_rows,
            gap=14, padding=20,
            navbar=navbar or {"title": title, "items": []},
            authors=authors,
            data_button=data_button,
            df=df if data_button else None,
            verbose=verbose,
        )

        if custom_layout:
            for item in custom_layout:
                t = item.get("type")
                r, c, h, w = item["row"], item["col"], item["height"], item["width"]
                if t == "kpi":
                    idx = item.get("index", 0)
                    if idx < len(planned_kpis):
                        col_name, val, icon_key = planned_kpis[idx]
                        dash.add_valuebox(
                            title=col_name, value=val, icon_key=icon_key,
                            row=r, col=c, height=h, width=w,
                        )
                elif t == "chart":
                    idx = item.get("index", 0)
                    if idx < len(charts):
                        fig, chart_title, stats = charts[idx]
                        dash.add_chart(
                            fig=fig, title=chart_title,
                            row=r, col=c, height=h, width=w,
                            show_info_btn=True, _info_stats=stats,
                        )
                elif t == "table":
                    dash.add_table(df, title=item.get("title", "Data"), row=r, col=c, height=h, width=w)
            return dash

        # Place KPIs
        for i, (col_name, val, icon_key) in enumerate(planned_kpis):
            cs, cw = kpi_slots[i]
            dash.add_valuebox(
                title=col_name, value=val, icon_key=icon_key,
                row=kpi_row_start, col=cs, height=KPI_H, width=cw,
            )

        # Place charts
        for i, (fig, chart_title, stats) in enumerate(charts):
            r, c, h, w = chart_slots[i]
            dash.add_chart(
                fig=fig, title=chart_title,
                row=r, col=c, height=h, width=w,
                show_info_btn=True, _info_stats=stats,
            )

        if add_main_table and table_slot:
            tr, tc, th, tw = table_slot
            dash.add_table(df, title="Data Preview", row=tr, col=tc, height=th, width=tw)

        return dash

    @classmethod
    def auto_generate(
        cls,
        data: pd.DataFrame,
        columns: Optional[List[str]] = None,
        template: Union[int, str, dict, None] = None,
        title: str = "Auto Dashboard",
        filename: str = "auto_dashboard.html",
        navbar: Optional[dict] = None,
        authors=None,
        method_valuebox: Literal["sum", "mean", "median", "max", "min"] = "sum",
        data_button: bool = False,
        color_palette: Optional[List[str]] = None,
        layout=None,
        show: bool = True,
        verbose: bool = False,
    ) -> str:
        """Deprecated: use ``Dashboard.auto(df, ...).save(path)`` instead."""
        warnings.warn(
            "Dashboard.auto_generate() is deprecated; use Dashboard.auto(df, theme=...).save(path).",
            DeprecationWarning, stacklevel=2,
        )
        dash = cls.auto(
            data, columns=columns, theme=template, title=title,
            navbar=navbar, authors=authors, method_valuebox=method_valuebox,
            data_button=data_button, color_palette=color_palette,
            layout=layout, verbose=verbose,
        )
        return dash._render_to_file(filename, show)


# Backwards-friendly alias (the class was called HTML before v0.3.0)
HTML = Dashboard