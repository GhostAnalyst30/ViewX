"""Canonical theme registry shared by every ViewX engine.

A single theme name (e.g. ``"dark_enterprise"``) works across Dashboard,
Presentation, Report and DataMatrix. Each entry defines the dashboard palette
plus per-engine variants (``slides`` sub-dict, ``mode`` for DataMatrix).
"""

from __future__ import annotations

from typing import Dict, List, Union

_FONT_SANS = "'Inter','Segoe UI',sans-serif"

THEMES: Dict[str, dict] = {
    "corporate_blue": {
        "id": 0, "name": "Corporate Blue", "mode": "light",
        "bg_page": "#F3F4F6", "bg_card": "#FFFFFF",
        "accent": "#0078D4", "text_primary": "#1A1A2E",
        "text_secondary": "#6B7280",
        "shadow": "0 2px 12px rgba(0,120,212,0.08)",
        "chart_colors": ["#0078D4", "#00B4D8", "#48CAE4", "#90E0EF", "#ADE8F4"],
        "slides": {
            "bg": "#ffffff", "surface": "#f1f5ff", "primary": "#0078D4", "accent": "#00B4D8",
            "text": "#0f172a", "muted": "#64748b", "border": "rgba(15,23,42,.10)",
            "shadow": "rgba(15,23,42,.10)", "font": _FONT_SANS,
        },
    },
    "dark_enterprise": {
        "id": 1, "name": "Dark Enterprise", "mode": "dark",
        "bg_page": "#0D0D0D", "bg_card": "#161616",
        "accent": "#3B82F6", "text_primary": "#F0F0F0",
        "text_secondary": "#9CA3AF",
        "shadow": "0 4px 24px rgba(0,0,0,0.5)",
        "chart_colors": ["#3B82F6", "#60A5FA", "#93C5FD", "#BFDBFE", "#2563EB"],
        "slides": {
            "bg": "#0f0f1a", "surface": "#1a1a2e", "primary": "#3B82F6", "accent": "#60A5FA",
            "text": "#f5f7fb", "muted": "#a7adbd", "border": "rgba(255,255,255,.12)",
            "shadow": "rgba(0,0,0,.42)", "font": _FONT_SANS,
        },
    },
    "modern_green": {
        "id": 2, "name": "Modern Green", "mode": "light",
        "bg_page": "#F0FAF4", "bg_card": "#FFFFFF",
        "accent": "#059669", "text_primary": "#1A2E1A",
        "text_secondary": "#6B7280",
        "shadow": "0 2px 12px rgba(5,150,105,0.1)",
        "chart_colors": ["#059669", "#10B981", "#34D399", "#6EE7B7", "#A7F3D0"],
        "slides": {
            "bg": "#f6fdf9", "surface": "#ffffff", "primary": "#059669", "accent": "#10B981",
            "text": "#12291a", "muted": "#5f7468", "border": "rgba(5,150,105,.14)",
            "shadow": "rgba(5,150,105,.12)", "font": _FONT_SANS,
        },
    },
    "void_indigo": {
        "id": 3, "name": "Void Indigo", "mode": "dark",
        "bg_page": "#07080F", "bg_card": "#0F1117",
        "accent": "#6366F1", "text_primary": "#E2E5FF",
        "text_secondary": "#9CA3AF",
        "shadow": "0 8px 32px rgba(99,102,241,0.15)",
        "chart_colors": ["#6366F1", "#818CF8", "#A5B4FC", "#C7D2FE", "#4F46E5"],
        "slides": {
            "bg": "#07080F", "surface": "#12142a", "primary": "#6366F1", "accent": "#818CF8",
            "text": "#E2E5FF", "muted": "#9CA3AF", "border": "rgba(99,102,241,.20)",
            "shadow": "rgba(0,0,0,.40)", "font": _FONT_SANS,
        },
    },
    "glass_ocean": {
        "id": 4, "name": "Glass Ocean", "mode": "dark",
        "bg_page": "linear-gradient(135deg,#0f2027,#203a43,#2c5364)",
        "bg_card": "rgba(255,255,255,0.06)",
        "accent": "#22D3EE", "text_primary": "#FFFFFF",
        "text_secondary": "#93C5FD",
        "shadow": "0 8px 32px rgba(0,0,0,0.25)",
        "glass": True,
        "chart_colors": ["#22D3EE", "#06B6D4", "#0891B2", "#0E7490", "#155E75"],
        "slides": {
            "bg": "#07172f", "surface": "#102544", "primary": "#22D3EE", "accent": "#48cae4",
            "text": "#dbeafe", "muted": "#93a4bd", "border": "rgba(100,255,218,.18)",
            "shadow": "rgba(0,0,0,.35)", "font": _FONT_SANS,
        },
    },
    "cyberpunk_neon": {
        "id": 5, "name": "Cyberpunk Neon", "mode": "dark",
        "bg_page": "#050505", "bg_card": "#0D0214",
        "accent": "#F000FF", "text_primary": "#00FFFF",
        "text_secondary": "#A78BFA",
        "shadow": "0 0 20px rgba(240,0,255,0.25)",
        "border_glow": True,
        "chart_colors": ["#F000FF", "#00FFFF", "#FF0080", "#FACC15", "#A78BFA"],
        "slides": {
            "bg": "#090014", "surface": "#13002b", "primary": "#F000FF", "accent": "#00FFFF",
            "text": "#ffffff", "muted": "#b9a9ff", "border": "rgba(240,0,255,.25)",
            "shadow": "rgba(240,0,255,.18)", "font": "'JetBrains Mono','Courier New',monospace",
        },
    },
}

# Legacy per-engine names accepted everywhere and resolved to canonical themes.
LEGACY_ALIASES: Dict[str, str] = {
    "dark": "dark_enterprise",
    "light": "corporate_blue",
    "corporate": "corporate_blue",
    "neon": "cyberpunk_neon",
    "ocean": "glass_ocean",
    "sunset": "void_indigo",
    "green": "modern_green",
}

_ID_MAP: Dict[int, str] = {spec["id"]: name for name, spec in THEMES.items()}

DEFAULT_THEME = "corporate_blue"

_active_theme: str = DEFAULT_THEME


def resolve_theme(theme: Union[int, str, None]) -> str:
    """Resolve any theme id/name/alias to a canonical theme name."""
    if theme is None:
        return _active_theme
    if isinstance(theme, int):
        return _ID_MAP.get(theme, DEFAULT_THEME)
    name = str(theme)
    if name in THEMES:
        return name
    return LEGACY_ALIASES.get(name, DEFAULT_THEME)


def theme_spec(theme: Union[int, str, dict, None] = None) -> dict:
    """Return the full spec dict for a theme (custom dicts pass through)."""
    if isinstance(theme, dict):
        return theme
    return THEMES[resolve_theme(theme)]


def chart_colors(theme: Union[int, str, dict, None] = None) -> List[str]:
    spec = theme_spec(theme)
    return list(spec.get("chart_colors", THEMES[DEFAULT_THEME]["chart_colors"]))


def slides_theme(theme: Union[int, str, None] = None) -> Dict[str, str]:
    return dict(THEMES[resolve_theme(theme)]["slides"])


def datamatrix_mode(theme: Union[int, str, None] = None) -> str:
    """Map any theme to the DataMatrix light/dark rendering mode."""
    return THEMES[resolve_theme(theme)]["mode"]


def set_theme(theme: Union[int, str]) -> str:
    """Set the global active theme used as default by every engine."""
    global _active_theme
    _active_theme = resolve_theme(theme)
    return _active_theme


def get_theme() -> str:
    """Return the name of the global active theme."""
    return _active_theme
