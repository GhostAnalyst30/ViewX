import viewx as vx
from viewx.shared.themes import (
    THEMES, chart_colors, datamatrix_mode, resolve_theme, slides_theme,
)


def test_canonical_names():
    assert set(THEMES) == {
        "corporate_blue", "dark_enterprise", "modern_green",
        "void_indigo", "glass_ocean", "cyberpunk_neon",
    }


def test_legacy_aliases_resolve():
    assert resolve_theme("dark") == "dark_enterprise"
    assert resolve_theme("light") == "corporate_blue"
    assert resolve_theme("ocean") == "glass_ocean"
    assert resolve_theme(1) == "dark_enterprise"
    assert resolve_theme("no_existe") == "corporate_blue"


def test_same_theme_works_everywhere(tmp_path, sales_df):
    name = "void_indigo"
    # Dashboard
    dash = vx.Dashboard(title="t", theme=name)
    assert dash.theme_manager.current_theme_name == name
    # Slides
    pres = vx.Presentation("t", theme=name)
    assert pres.theme == slides_theme(name)
    # DataMatrix
    assert datamatrix_mode(name) == "dark"


def test_global_theme(sales_df):
    vx.set_theme("cyberpunk_neon")
    try:
        assert vx.get_theme() == "cyberpunk_neon"
        dash = vx.Dashboard(title="t")  # no theme arg -> global
        assert dash.theme_manager.current_theme_name == "cyberpunk_neon"
        chart = vx.plot(sales_df, kind="bar", x="region", y="revenue")
        assert list(chart.fig.layout.colorway) == chart_colors("cyberpunk_neon")
    finally:
        vx.set_theme("corporate_blue")
