import pytest

import viewx as vx
from viewx.plot import Chart
from viewx.plot.factory import infer_kind, maybe_downsample


INTERACTIVE_KINDS = [
    ("line", dict(x="date", y="revenue")),
    ("bar", dict(x="region", y="revenue")),
    ("bar_h", dict(x="region", y="revenue")),
    ("scatter", dict(x="revenue", y="units")),
    ("area", dict(x="date", y="revenue")),
    ("pie", dict(x="region", y="revenue")),
    ("donut", dict(x="region", y="revenue")),
    ("histogram", dict(x="revenue")),
    ("box", dict(x="region", y="revenue")),
    ("violin", dict(x="region", y="revenue")),
    ("heatmap", dict(x="region", y="active", z="revenue")),
    ("funnel", dict(x="region", y="units")),
    ("treemap", dict(x="region", y="units")),
    ("bubble", dict(x="revenue", y="units", z="units")),
]


@pytest.mark.parametrize("kind,cols", INTERACTIVE_KINDS)
def test_plot_every_kind_interactive(sales_df, kind, cols):
    chart = vx.plot(sales_df, kind=kind, title=kind, **cols)
    assert isinstance(chart, Chart)
    assert chart.interactive
    assert len(chart.fig.data) >= 1


def test_plot_save_html(tmp_path, sales_df):
    chart = vx.plot(sales_df, kind="bar", x="region", y="revenue")
    out = chart.save(str(tmp_path / "chart.html"))
    content = open(out, encoding="utf-8").read()
    assert "plotly" in content.lower()


def test_kind_inference(sales_df):
    assert infer_kind(sales_df, "date", "revenue") == "line"
    assert infer_kind(sales_df, "revenue", "units") == "scatter"
    assert infer_kind(sales_df, "region", "revenue") == "bar"
    assert infer_kind(sales_df, "revenue", None) == "histogram"
    assert infer_kind(sales_df, "region", None) == "bar"


def test_downsampling(big_df):
    sampled, was_sampled = maybe_downsample(big_df, "line")
    assert was_sampled
    assert len(sampled) <= 10_002
    # keeps last row
    assert big_df.index[-1] in sampled.index

    kept, untouched = maybe_downsample(big_df, "bar")
    assert not untouched
    assert len(kept) == len(big_df)


def test_webgl_for_large_scatter(big_df):
    chart = vx.plot(big_df, kind="scatter", x="x", y="y", downsample=False)
    assert chart.fig.data[0].type == "scattergl"


def test_static_chart(tmp_path, sales_df):
    pytest.importorskip("matplotlib")
    chart = vx.plot(sales_df, kind="histogram", x="revenue", static=True)
    assert not chart.interactive
    out = chart.save(str(tmp_path / "hist.png"))
    import os
    assert os.path.getsize(out) > 0


def test_static_rejects_html(sales_df):
    pytest.importorskip("matplotlib")
    chart = vx.plot(sales_df, kind="bar", x="region", y="revenue", static=True)
    with pytest.raises(ValueError):
        chart.save("out.html")
