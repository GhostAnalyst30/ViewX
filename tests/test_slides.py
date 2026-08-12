import viewx as vx
from viewx import Presentation, Slide
from viewx.Slides import BarPlot, Title, PlotlyChart


def test_manual_presentation_save(tmp_path):
    pres = Presentation("Demo", theme="dark_enterprise")
    with Slide(title="Portada"):
        Title("Hola")
        BarPlot(["A", "B"], [1, 2], title="Barras")
    out = pres.save(str(tmp_path / "deck.html"))
    content = open(out, encoding="utf-8").read()
    assert "Plotly.newPlot" in content


def test_auto_returns_presentation(tmp_path, sales_df):
    pres = Presentation.auto(sales_df, title="Auto deck", theme="glass_ocean")
    assert isinstance(pres, Presentation)
    assert len(pres.slides) >= 3
    out = pres.save(str(tmp_path / "auto_deck.html"))
    assert "Auto deck" in open(out, encoding="utf-8").read()


def test_plotlychart_from_vx_chart(tmp_path, sales_df):
    chart = vx.plot(sales_df, kind="bar", x="region", y="revenue")
    pres = Presentation("Embed")
    with Slide(title="Chart"):
        PlotlyChart.from_figure(chart)
    out = pres.save(str(tmp_path / "embed_deck.html"))
    assert "Plotly.newPlot" in open(out, encoding="utf-8").read()


def test_legacy_theme_names_resolve():
    pres = Presentation("x", theme="ocean")
    assert pres.theme["primary"]  # resolves via shared registry
