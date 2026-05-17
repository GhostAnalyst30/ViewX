"""
ViewX Dashboard Engine  ·  v3.0
================================
A Python-to-HTML dashboard builder powered by Plotly.

Features
--------
- ThemeManager  : 6 built-in themes + custom palette support
- HTML class    : manual grid layout with add_valuebox / add_chart /
                  add_table / add_text / add_infobox
- auto_generate : smart one-liner that inspects any DataFrame and
                  builds a fully wired dashboard automatically
- data_button   : floating button → modal with data preview + describe()
- info button   : every chart has a ⓘ button that opens a detail modal
- SVG icons     : no emoji — professional Heroicon-style SVG icons
"""

from __future__ import annotations

import json
import os
import uuid
from typing import Dict, List, Optional, Tuple, Union

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


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


ICONS_SVG = {
    "chart-bar":    _svg('<rect x="3" y="12" width="4" height="9"/><rect x="10" y="7" width="4" height="14"/><rect x="17" y="3" width="4" height="18"/>'),
    "trending-up":  _svg('<polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/>'),
    "dollar":       _svg('<line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>'),
    "hash":         _svg('<line x1="4" y1="9" x2="20" y2="9"/><line x1="4" y1="15" x2="20" y2="15"/><line x1="10" y1="3" x2="8" y2="21"/><line x1="16" y1="3" x2="14" y2="21"/>'),
    "target":       _svg('<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>'),
    "zap":          _svg('<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>'),
    "box":          _svg('<path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/>'),
    "award":        _svg('<circle cx="12" cy="8" r="6"/><path d="M15.477 12.89 17 22l-5-3-5 3 1.523-9.11"/>'),
    "users":        _svg('<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>'),
    "activity":     _svg('<polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>'),
    "percent":      _svg('<line x1="19" y1="5" x2="5" y2="19"/><circle cx="6.5" cy="6.5" r="2.5"/><circle cx="17.5" cy="17.5" r="2.5"/>'),
    "clock":        _svg('<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>'),
    "info":         _svg('<circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>'),
    "database":     _svg('<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/>'),
    "eye":          _svg('<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>'),
    "grid":         _svg('<rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/>'),
    "maximize":     _svg('<path d="M8 3H5a2 2 0 0 0-2 2v3"/><path d="M21 8V5a2 2 0 0 0-2-2h-3"/><path d="M3 16v3a2 2 0 0 0 2 2h3"/><path d="M16 21h3a2 2 0 0 0 2-2v-3"/>'),
    "close":        _svg('<line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>'),
}

# Cycle of icons for auto KPIs
_KPI_ICON_CYCLE = [
    "trending-up", "dollar", "hash", "target", "zap", "box", "award", "users",
    "activity", "percent", "clock", "chart-bar",
]


def _kpi_icon(index: int, size: int = 22) -> str:
    key = _KPI_ICON_CYCLE[index % len(_KPI_ICON_CYCLE)]
    path_d = ICONS_SVG[key]
    # re-render at requested size
    return _svg(
        path_d.split('">')[1].rstrip("</svg>"),
        size=size,
    )


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

    BUILT_IN: Dict[str, dict] = {
        "corporate_blue": {
            "id": 0, "name": "Corporate Blue",
            "bg_page": "#F3F4F6", "bg_card": "#FFFFFF",
            "accent": "#0078D4", "text_primary": "#1A1A2E",
            "text_secondary": "#6B7280",
            "shadow": "0 2px 12px rgba(0,120,212,0.08)",
            "chart_colors": ["#0078D4","#00B4D8","#48CAE4","#90E0EF","#ADE8F4"],
        },
        "dark_enterprise": {
            "id": 1, "name": "Dark Enterprise",
            "bg_page": "#0D0D0D", "bg_card": "#161616",
            "accent": "#3B82F6", "text_primary": "#F0F0F0",
            "text_secondary": "#9CA3AF",
            "shadow": "0 4px 24px rgba(0,0,0,0.5)",
            "chart_colors": ["#3B82F6","#60A5FA","#93C5FD","#BFDBFE","#2563EB"],
        },
        "modern_green": {
            "id": 2, "name": "Modern Green",
            "bg_page": "#F0FAF4", "bg_card": "#FFFFFF",
            "accent": "#059669", "text_primary": "#1A2E1A",
            "text_secondary": "#6B7280",
            "shadow": "0 2px 12px rgba(5,150,105,0.1)",
            "chart_colors": ["#059669","#10B981","#34D399","#6EE7B7","#A7F3D0"],
        },
        "void_indigo": {
            "id": 3, "name": "Void Indigo",
            "bg_page": "#07080F", "bg_card": "#0F1117",
            "accent": "#6366F1", "text_primary": "#E2E5FF",
            "text_secondary": "#9CA3AF",
            "shadow": "0 8px 32px rgba(99,102,241,0.15)",
            "chart_colors": ["#6366F1","#818CF8","#A5B4FC","#C7D2FE","#4F46E5"],
        },
        "glass_ocean": {
            "id": 4, "name": "Glass Ocean",
            "bg_page": "linear-gradient(135deg,#0f2027,#203a43,#2c5364)",
            "bg_card": "rgba(255,255,255,0.06)",
            "accent": "#22D3EE", "text_primary": "#FFFFFF",
            "text_secondary": "#93C5FD",
            "shadow": "0 8px 32px rgba(0,0,0,0.25)",
            "glass": True,
            "chart_colors": ["#22D3EE","#06B6D4","#0891B2","#0E7490","#155E75"],
        },
        "cyberpunk_neon": {
            "id": 5, "name": "Cyberpunk Neon",
            "bg_page": "#050505", "bg_card": "#0D0214",
            "accent": "#F000FF", "text_primary": "#00FFFF",
            "text_secondary": "#A78BFA",
            "shadow": "0 0 20px rgba(240,0,255,0.25)",
            "border_glow": True,
            "chart_colors": ["#F000FF","#00FFFF","#FF0080","#FACC15","#A78BFA"],
        },
    }

    def __init__(self, theme: Union[int, str, dict] = "corporate_blue"):
        self._id_map = {t["id"]: k for k, t in self.BUILT_IN.items()}
        self.custom = False
        self.set_theme(theme)

    # ------------------------------------------------------------------
    def set_theme(self, theme: Union[int, str, dict]):
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

        if isinstance(theme, int):
            theme = self._id_map.get(theme, "corporate_blue")
        if theme not in self.BUILT_IN:
            theme = "corporate_blue"
        self.current_theme_name = theme
        self.current_theme = self.BUILT_IN[theme]

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
            --vx-transition:    all 0.28s cubic-bezier(.16,1,.3,1);
        }}
        *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            background: var(--vx-bg-page);
            color: var(--vx-text-primary);
            font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
            overflow: hidden;
            height: 100vh; width: 100vw;
        }}
        .vx-card {{
            background: var(--vx-bg-card);
            border-radius: var(--vx-card-radius);
            box-shadow: var(--vx-shadow);
            transition: var(--vx-transition);
            overflow: auto;
            border: 1px solid rgba(128,128,128,0.08);
        }}
        .vx-card:hover {{ transform: translateY(-2px); box-shadow: 0 8px 28px rgba(0,0,0,0.14); }}
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
# MAIN HTML CLASS
# ──────────────────────────────────────────────────────────────────────────────
class HTML:
    """
    Manual dashboard builder.

    Usage
    -----
    dash = HTML(title="Sales Report", theme="dark_enterprise")
    dash.add_valuebox(title="Revenue", value="$1.2M", icon_key="dollar", row=1, col=1, height=2, width=3)
    dash.add_chart(fig=my_fig, title="Trend", row=1, col=4, height=4, width=9)
    dash.generate("report.html")
    """

    def __init__(
        self,
        title: str = "ViewX Dashboard",
        theme: Union[int, str, dict] = "corporate_blue",
        cols: int = 12,
        rows: int = 12,
        gap: int = 16,
        padding: int = 22,
        navbar: dict = None,
        authors: Union[str, List] = None,
        data_button: bool = False,
        df: pd.DataFrame = None,
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

        if isinstance(authors, list):
            self.authors = [a if isinstance(a, dict) else {"name": a, "email": None} for a in authors]
        elif isinstance(authors, str):
            self.authors = [{"name": authors, "email": None}]
        else:
            self.authors = []

        self.grid_css: List[str] = []
        self.components_html: List[str] = []
        self._component_counter = 0

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
    ) -> "HTML":
        uid = self._uid()
        self._register_block(uid, row, col, height, width)
        _, bg_card, accent, _ = self.theme_manager.get_colors()
        box_color = color or accent

        # Build SVG icon
        icon_svg = ICONS_SVG.get(icon_key, ICONS_SVG["chart-bar"])
        # Rebuild at 24px with box_color stroke
        svg_content = icon_svg.split('">')[1].rstrip("</svg>")
        icon_rendered = _svg(svg_content, size=24, color=box_color)

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
        <div class="vx-card vb-{uid} {uid}">
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
    ) -> "HTML":
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
        <div class="vx-card ib-card-{uid} {uid}">
            <div class="ib-title-{uid}">{card_title}</div>
            <div class="ib-rows-{uid}">{rows_html}</div>
        </div>"""
        self.components_html.append(html)
        return self

    # ── add_chart ─────────────────────────────────────────────────────────────
    def add_chart(
        self,
        data=None, fig=None,
        chart_type: str = "line",
        x=None, y=None, z=None,
        title: str = "",
        row: int = 1, col: int = 1, height: int = 6, width: int = 6,
        show_info_btn: bool = True,
        # Extra info for the info modal
        _info_stats: dict = None,
    ) -> "HTML":
        uid = self._uid()
        self._register_block(uid, row, col, height, width)
        _, _, accent, text = self.theme_manager.get_colors()
        colors = self.theme_manager.chart_colors()

        if fig is not None:
            chart_fig = fig
        elif data is not None and x is not None and y is not None:
            kw = dict(color_discrete_sequence=colors)
            if chart_type == "bar":
                chart_fig = px.bar(data, x=x, y=y, title=title, **kw)
            elif chart_type == "scatter":
                chart_fig = px.scatter(data, x=x, y=y, color=z, title=title, **kw)
            elif chart_type == "area":
                chart_fig = px.area(data, x=x, y=y, title=title, **kw)
            else:
                chart_fig = px.line(data, x=x, y=y, title=title, **kw)
        else:
            raise ValueError("Provide fig or (data + x + y)")

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

        plot_html = chart_fig.to_html(
            full_html=False, include_plotlyjs="cdn",
            config={"displaylogo": False, "responsive": True, "autosizable": True},
        )

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

            close_icon = ICONS_SVG["close"].split('">')[1].rstrip("</svg>")
            close_svg = _svg(close_icon, size=16)
            info_icon_svg = ICONS_SVG["info"].split('">')[1].rstrip("</svg>")
            info_svg = _svg(info_icon_svg, size=14, color="#fff")

            info_btn_html = f"""
            <button class="vx-chart-info-btn" onclick="document.getElementById('{modal_id}').classList.add('open')"
                    title="Variable info">
                {info_svg}
            </button>"""

            info_modal_html = f"""
            <div id="{modal_id}" class="vx-modal-overlay" onclick="if(event.target===this)this.classList.remove('open')">
                <div class="vx-modal-box" style="max-width:520px">
                    <div class="vx-modal-header">
                        <h3>{title or "Chart Details"}</h3>
                        <button class="vx-modal-close" onclick="document.getElementById('{modal_id}').classList.remove('open')">{close_svg}</button>
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
        <div class="vx-card pc-{uid} {uid}">
            {f'<h4>{title}</h4>' if title else '<div></div>'}
            <div class="pcc-{uid}">
                {plot_html}
                {info_btn_html}
            </div>
        </div>
        {info_modal_html}
        <script>
        (function(){{
            var cont = document.querySelector('.pcc-{uid}');
            var t;
            function resize(){{
                var d = cont ? cont.querySelector('.plotly-graph-div') : null;
                if(d && window.Plotly){{
                    var w = cont.clientWidth, h = cont.clientHeight;
                    if(w>0&&h>0) Plotly.relayout(d,{{width:w,height:h}});
                }}
            }}
            if(window.ResizeObserver && cont)
                new ResizeObserver(()=>{{clearTimeout(t);t=setTimeout(resize,50);}}).observe(cont);
            window.addEventListener('resize',()=>{{clearTimeout(t);t=setTimeout(resize,100);}});
            (function wait(n){{
                var d=cont?cont.querySelector('.plotly-graph-div'):null;
                if(d&&window.Plotly) resize();
                else if(n>0) setTimeout(()=>wait(n-1),120);
            }})(18);
        }})();
        </script>"""
        self.components_html.append(html)
        return self

    # ── add_table ─────────────────────────────────────────────────────────────
    def add_table(
        self, df: pd.DataFrame, title: str = "",
        row: int = 1, col: int = 1, height: int = 4, width: int = 6,
    ) -> "HTML":
        uid = self._uid()
        self._register_block(uid, row, col, height, width)
        _, _, accent, _ = self.theme_manager.get_colors()
        table_html = df.to_html(classes=f"vxt-{uid}", border=0, index=False, max_rows=200)

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
        <div class="vx-card tc-{uid} {uid}">
            {f'<h4>{title}</h4>' if title else ""}
            <div class="tcc-{uid}">{table_html}</div>
        </div>"""
        self.components_html.append(html)
        return self

    # ── add_text ──────────────────────────────────────────────────────────────
    def add_text(
        self, content: str,
        row: int = 1, col: int = 1, height: int = 2, width: int = 6,
    ) -> "HTML":
        uid = self._uid()
        self._register_block(uid, row, col, height, width)
        _, _, accent, _ = self.theme_manager.get_colors()

        html = f"""
        <style>
        .txc-{uid} {{ padding:20px; line-height:1.6; color:var(--vx-text-primary); height:100%; overflow:auto; font-size:.88rem; }}
        .txc-{uid} h2,.txc-{uid} h3 {{ color:{accent}; margin-top:0; font-weight:700; }}
        </style>
        <div class="vx-card txc-{uid} {uid}">{content}</div>"""
        self.components_html.append(html)
        return self

    # ── navbar ────────────────────────────────────────────────────────────────
    def _build_navbar(self) -> str:
        if not self.navbar:
            return ""
        _, bg_card, accent, _ = self.theme_manager.get_colors()
        items_html = "".join(
            f'<a href="{i["link"]}" class="nav-link">{i["label"]}</a>'
            for i in self.navbar.get("items", [])
        )
        author_block = ""
        if self.authors:
            parts = []
            for a in self.authors:
                if a["email"]:
                    parts.append(f'<a href="mailto:{a["email"]}" class="nav-author nav-alink">{a["name"]}</a>')
                else:
                    parts.append(f'<span class="nav-author">{a["name"]}</span>')
            author_block = f'<div class="nav-author-wrap">by {", ".join(parts)}</div>'

        grid_icon = ICONS_SVG["grid"].split('">')[1].rstrip("</svg>")
        brand_icon = _svg(grid_icon, size=18, color=accent)

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

        close_icon = ICONS_SVG["close"].split('">')[1].rstrip("</svg>")
        close_svg = _svg(close_icon, size=16)
        db_icon = ICONS_SVG["database"].split('">')[1].rstrip("</svg>")
        db_svg = _svg(db_icon, size=16, color="#fff")

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

        <div id="vx-data-modal" class="vx-modal-overlay"
             onclick="if(event.target===this)this.classList.remove('open')">
            <div class="vx-modal-box">
                <div class="vx-modal-header">
                    <h3>Dataset Overview</h3>
                    <button class="vx-modal-close"
                            onclick="document.getElementById('vx-data-modal').classList.remove('open')">
                        {close_svg}
                    </button>
                </div>
                <div class="vx-modal-body">
                    {summary_badge}
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

        <button class="vx-data-fab"
                onclick="document.getElementById('vx-data-modal').classList.add('open')">
            {db_svg} View Data
        </button>"""

    # ── generate ──────────────────────────────────────────────────────────────
    def generate(self, filename: str = "dashboard.html") -> str:
        _, _, accent, _ = self.theme_manager.get_colors()
        nav_offset = self.padding + 54 if self.navbar else self.padding

        full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <title>{self.title}</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width,initial-scale=1">
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
        .vx-card {{ animation: vxFadeUp .35s ease-out both; }}
        @keyframes vxFadeUp {{
            from {{ opacity:0; transform:translateY(10px); }}
            to   {{ opacity:1; transform:translateY(0); }}
        }}
        {chr(10).join([f".vx-card:nth-child({i+1}){{animation-delay:{i*.04}s}}" for i in range(len(self.components_html))])}
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
</body>
</html>"""

        with open(filename, "w", encoding="utf-8") as f:
            f.write(full_html)
        print(f"✅  Dashboard → {os.path.abspath(filename)}")
        import webbrowser
        webbrowser.open(filename)
        return filename

    # ── auto_generate ─────────────────────────────────────────────────────────
    @classmethod
    def auto_generate(
        cls,
        data: pd.DataFrame,
        columns: List[str] = None,
        template: Union[int, str, dict] = "corporate_blue",
        title: str = "Auto Dashboard",
        filename: str = "auto_dashboard.html",
        navbar: dict = None,
        authors=None,
        method_valuebox: str = "sum",
        data_button: bool = False,
        color_palette: List[str] = None,
        layout=None,   # legacy compat, ignored
    ) -> str:
        """
        Builds a professional dashboard from any DataFrame using a single
        intelligent layout template.

        The engine first runs a statistical study of the data:
          - Selects the most complete numeric variables (fewest nulls, highest variance)
          - Finds the 2 pairs with highest absolute Pearson correlation → scatter
          - Picks the most informative categorical column (best cardinality)
          - Then assembles everything in a proportional, non-elongated grid

        Parameters
        ----------
        data            : source DataFrame
        columns         : column subset (None = all)
        template        : theme name / id / custom dict
        title           : dashboard title
        filename        : output HTML path
        navbar          : dict {"title":..., "items":[{"label":..,"link":..}]}
        authors         : str | list[str | dict{"name","email"}]
        method_valuebox : "sum"|"mean"|"median"|"max"|"min"
        data_button     : floating "View Data" button with modal preview
        color_palette   : list of hex colors to override theme palette
        """

        # ── 1. Column selection ───────────────────────────────────────────────
        cols_to_use = list(columns) if columns is not None else list(data.columns)
        missing = [c for c in cols_to_use if c not in data.columns]
        if missing:
            raise KeyError(f"\n❌  Columns not found: {missing}\n✅  Available: {list(data.columns)}")

        df = data[cols_to_use].copy()

        # ── 2. Smart type coercion ────────────────────────────────────────────
        def _try_parse(s: pd.Series) -> pd.Series:
            if not pd.api.types.is_object_dtype(s):
                return s
            cleaned = s.astype(str).str.strip().str.replace(r"[$€£¥%\s,]", "", regex=True)
            num = pd.to_numeric(cleaned, errors="coerce")
            if num.notna().sum() / max(len(s.dropna()), 1) >= 0.80:
                return num
            try:
                dt = pd.to_datetime(s, errors="coerce")
                if dt.notna().sum() / max(len(s.dropna()), 1) >= 0.80:
                    return dt
            except Exception:
                pass
            return s

        coerced: Dict[str, str] = {}
        for col in cols_to_use:
            old = str(df[col].dtype)
            df[col] = _try_parse(df[col])
            new = str(df[col].dtype)
            if old != new:
                coerced[col] = f"{old} → {new}"
        if coerced:
            print("🔄  Auto coercion:", ", ".join(f"{k}: {v}" for k, v in coerced.items()))

        # ── 3. Classify columns ───────────────────────────────────────────────
        def _classify(s: pd.Series) -> str:
            if pd.api.types.is_datetime64_any_dtype(s): return "datetime"
            if pd.api.types.is_bool_dtype(s):           return "boolean"
            if pd.api.types.is_numeric_dtype(s):        return "numeric"
            return "categorical" if s.nunique() / max(len(s), 1) < 0.5 else "text"

        col_types    = {c: _classify(df[c]) for c in cols_to_use}
        all_num      = [c for c, t in col_types.items() if t == "numeric"]
        all_cat      = [c for c, t in col_types.items() if t == "categorical"]
        all_dt       = [c for c, t in col_types.items() if t == "datetime"]
        all_bool     = [c for c, t in col_types.items() if t == "boolean"]

        for c in all_dt:
            df[c] = pd.to_datetime(df[c])

        print(f"📊  Detected → numeric:{len(all_num)}  categorical:{len(all_cat)}  "
              f"datetime:{len(all_dt)}  boolean:{len(all_bool)}")

        # ── 4. Statistical study: rank & select best variables ────────────────
        #
        # Numeric ranking:  completeness (0.5) + normalized variance (0.5)
        # KPI limit: up to 4 (keeps the strip compact)
        # Chart limit: up to 4 charts on the canvas (2 per row × 2 rows)

        def _score_numeric(col: str) -> float:
            s = df[col].dropna()
            if len(s) == 0:
                return 0.0
            completeness = len(s) / len(df)
            cv = (s.std() / abs(s.mean())) if s.mean() != 0 else 0.0
            return 0.5 * completeness + 0.5 * min(cv, 5.0) / 5.0

        ranked_num = sorted(all_num, key=_score_numeric, reverse=True)

        # Best categorical: highest completeness × moderate cardinality (5–20)
        def _score_cat(col: str) -> float:
            s = df[col].dropna()
            completeness = len(s) / max(len(df), 1)
            n_unique = s.nunique()
            card_score = 1.0 if 2 <= n_unique <= 20 else max(0.0, 1.0 - (n_unique - 20) / 80)
            return completeness * card_score

        ranked_cat = sorted(all_cat, key=_score_cat, reverse=True)

        # Correlation study for scatter selection
        scatter_pairs: List[Tuple[float, str, str]] = []
        if len(ranked_num) >= 2:
            corr_mat = df[ranked_num].corr().abs()
            for i in range(len(ranked_num)):
                for j in range(i + 1, len(ranked_num)):
                    r = corr_mat.iloc[i, j]
                    scatter_pairs.append((r, ranked_num[i], ranked_num[j]))
            scatter_pairs.sort(reverse=True)

        print("📈  Variable scores:")
        for col in ranked_num[:6]:
            sc = _score_numeric(col)
            null_pct = df[col].isna().mean() * 100
            print(f"    {col:25s}  score={sc:.3f}  nulls={null_pct:.1f}%")
        if scatter_pairs:
            print("🔗  Top correlations:")
            for r, a, b in scatter_pairs[:3]:
                print(f"    {a} × {b}  r={r:.3f}")

        # ── 5. Palette & theme setup ──────────────────────────────────────────
        tm_tmp = ThemeManager(template)
        if color_palette:
            tm_tmp.current_theme["chart_colors"] = color_palette
        pal = tm_tmp.chart_colors()

        def _fig_style(fig):
            """Apply palette and strip title (shown in card header)."""
            fig.update_layout(colorway=pal, title_text="")
            return fig

        # ── 6. Value formatter ────────────────────────────────────────────────
        def _fmt(v: float) -> str:
            a = abs(v)
            if a >= 1_000_000_000: return f"{v/1_000_000_000:,.2f}B"
            if a >= 1_000_000:     return f"{v/1_000_000:,.2f}M"
            if a >= 1_000:         return f"{v/1_000:,.1f}K"
            return f"{v:,.2f}"

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
        KPI_H      = 2    # grid rows for KPI strip
        CHART_H    = 5    # grid rows per chart row

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
            _, col_a, col_b = scatter_pairs[0]
            color_col = ranked_cat[0] if ranked_cat else None
            fig = _fig_style(px.scatter(
                df, x=col_a, y=col_b, color=color_col,
                opacity=0.65, color_discrete_sequence=pal,
            ))
            stats = {
                "Pearson r":    f"{df[[col_a, col_b]].corr().iloc[0,1]:.3f}",
                f"{col_a} mean": _fmt(df[col_a].mean()),
                f"{col_b} mean": _fmt(df[col_b].mean()),
            }
            charts.append((fig, f"{col_a} vs {col_b}", stats))

        # Chart slot 4a: second-best correlated pair scatter
        if len(scatter_pairs) >= 2 and len(charts) < MAX_CHARTS:
            _, col_a, col_b = scatter_pairs[1]
            color_col = ranked_cat[0] if ranked_cat else None
            fig = _fig_style(px.scatter(
                df, x=col_a, y=col_b, color=color_col,
                opacity=0.65, color_discrete_sequence=pal,
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

        print(f"🗂   Layout → {n_kpis} KPIs, {n_charts} charts")

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
        )

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

        return dash.generate(filename=filename)


"""
ViewX Dashboard Engine — Full Feature Demo  (v3.1)
===================================================
Run:  python demo_viewx.py
Each example generates an HTML file in the current directory.
"""

import numpy as np
import pandas as pd
import plotly.express as px
rng = np.random.default_rng(42)
n   = 300

dates    = pd.date_range("2023-01-01", periods=n, freq="D")
regions  = rng.choice(["North", "South", "East", "West"], n)
products = rng.choice(["Alpha", "Beta", "Gamma", "Delta"], n)
revenue  = (rng.normal(8_000, 2_000, n) + np.linspace(0, 5_000, n)).clip(100)
costs    = revenue * rng.uniform(0.45, 0.65, n)
units    = (revenue / rng.uniform(40, 120, n)).astype(int)
rating   = rng.uniform(3.0, 5.0, n).round(1)
returned = rng.choice([True, False], n, p=[0.12, 0.88])

# Revenue stored as "$1,234" strings — engine auto-coerces to float
revenue_str = [f"${v:,.0f}" for v in revenue]

df = pd.DataFrame({
    "date": dates, "region": regions, "product": products,
    "revenue": revenue_str, "costs": costs.round(2),
    "units": units, "rating": rating, "returned": returned,
})

print("=" * 64)
print("  ViewX Dashboard Engine — Demo Suite  (v3.1)")
print("=" * 64)

# ── DEMO 1 ── corporate_blue, all columns, data_button ───────────────────────
print("\n[1/7]  corporate_blue . all columns . data_button=True")
HTML.auto_generate(
    data=df, title="Sales Dashboard", template="corporate_blue",
    filename="demo1_auto_default.html",
    navbar={"title": "Sales Dashboard", "items": [
        {"label": "Overview", "link": "#"},
        {"label": "Reports",  "link": "#"},
    ]},
    authors=["Alice Rivera"],
    data_button=True,
    method_valuebox="sum",
)

# ── DEMO 2 ── dark_enterprise, selected columns ───────────────────────────────
print("\n[2/7]  dark_enterprise . selected columns")
HTML.auto_generate(
    data=df,
    columns=["date", "revenue", "costs", "units"],
    title="Financial Trends", template="dark_enterprise",
    filename="demo2_dark_selected.html",
    navbar={"title": "Financial Trends", "items": []},
    authors=[{"name": "Bob Kim", "email": "bob@acme.com"}],
    data_button=True, method_valuebox="mean",
)

# ── DEMO 3 ── void_indigo + custom color palette ──────────────────────────────
print("\n[3/7]  void_indigo . custom palette")
HTML.auto_generate(
    data=df, title="Custom Palette Dashboard", template="void_indigo",
    filename="demo3_custom_palette.html",
    color_palette=["#F43F5E", "#FB923C", "#FBBF24", "#34D399", "#818CF8"],
    navbar={"title": "Custom Palette", "items": []},
    data_button=True,
)

# ── DEMO 4 ── glass_ocean ─────────────────────────────────────────────────────
print("\n[4/7]  glass_ocean")
HTML.auto_generate(
    data=df, title="Ocean Glass Dashboard", template="glass_ocean",
    filename="demo4_glass_ocean.html",
    navbar={"title": "Ocean Glass", "items": []},
)

# ── DEMO 5 ── cyberpunk_neon ──────────────────────────────────────────────────
print("\n[5/7]  cyberpunk_neon")
HTML.auto_generate(
    data=df, title="Neon Dashboard", template="cyberpunk_neon",
    filename="demo5_cyberpunk.html",
    navbar={"title": "Neon Board", "items": []},
    authors=["CyberTeam"],
)

# ── DEMO 6 ── Manual build: valuebox + infobox + charts ──────────────────────
print("\n[6/7]  Manual build — modern_green")

df2 = df.copy()
df2["revenue"] = pd.to_numeric(
    df2["revenue"].str.replace(r"[$,]", "", regex=True), errors="coerce"
)

fig_bar = px.bar(
    df2.groupby("region")["revenue"].sum().reset_index().sort_values("revenue"),
    x="revenue", y="region", orientation="h", color="region",
    color_discrete_sequence=["#059669", "#10B981", "#34D399", "#6EE7B7"],
)
fig_bar.update_layout(showlegend=False)

fig_line = px.line(
    df2.groupby("date")["revenue"].sum().reset_index(),
    x="date", y="revenue", color_discrete_sequence=["#059669"],
)

dash = HTML(
    title="Manual Dashboard", theme="modern_green",
    cols=12, rows=9, gap=14, padding=20,
    navbar={"title": "Manual Dashboard",
            "items": [{"label": "Home", "link": "#"}, {"label": "Analytics", "link": "#"}]},
    authors=[{"name": "Data Team", "email": "data@acme.com"}],
    data_button=True, df=df2,
)

dash.add_valuebox("Total Revenue", "$2.4M",  icon_key="dollar",  row=1, col=1,  height=2, width=3)
dash.add_valuebox("Total Units",   "18.4K",  icon_key="box",     row=1, col=4,  height=2, width=3)
dash.add_valuebox("Avg Rating",    "4.12",   icon_key="award",   row=1, col=7,  height=2, width=3)
dash.add_valuebox("Return Rate",   "12%",    icon_key="percent", row=1, col=10, height=2, width=3)

dash.add_infobox(df=df2, variable="revenue",
    info=["mean", "median", "std", "min", "max", "kurtosis", "skewness", "nulls"],
    title="Revenue Stats", row=3, col=1, height=4, width=3)
dash.add_chart(fig=fig_bar, title="Revenue by Region",
    row=3, col=4, height=4, width=9, show_info_btn=True,
    _info_stats={"Regions": "4", "Total": "$2.4M"})
dash.add_chart(fig=fig_line, title="Daily Revenue Trend",
    row=7, col=1, height=3, width=12, show_info_btn=True)

dash.generate("demo6_manual.html")

# ── DEMO 7 ── Fully custom theme dict ────────────────────────────────────────
print("\n[7/7]  Custom theme dict")
HTML.auto_generate(
    data=df,
    columns=["region", "product", "units", "rating", "returned"],
    title="Brand Dashboard",
    template={
        "bg_page":        "#0A0A1A",
        "bg_card":        "#12122A",
        "accent":         "#FF6B35",
        "text_primary":   "#F0EAD6",
        "text_secondary": "#A09080",
        "shadow":         "0 4px 20px rgba(255,107,53,0.15)",
        "chart_colors":   ["#FF6B35", "#F7C59F", "#EFEFD0", "#004E89", "#1A936F"],
    },
    filename="demo7_custom_theme.html",
    navbar={"title": "Brand Dashboard", "items": []},
    authors=["Brand Studio"],
    data_button=True,
)

print("\n" + "=" * 64)
print("  All 7 demos generated. Open any demo*.html in your browser.")
print("=" * 64)