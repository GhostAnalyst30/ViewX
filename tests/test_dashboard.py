import viewx as vx
from viewx import Dashboard


def test_manual_dashboard_save(tmp_path, sales_df):
    dash = Dashboard(title="Test", theme="dark_enterprise", cols=12, rows=8)
    dash.add_valuebox("Total", "123", icon_key="dollar", row=1, col=1, height=2, width=3)
    dash.add_infobox(df=sales_df, variable="revenue", row=1, col=4, height=4, width=3)
    dash.add_chart(data=sales_df, chart_type="bar", x="region", y="revenue",
                   title="Revenue", row=3, col=1, height=4, width=6)
    dash.add_table(sales_df.head(5), title="Sample", row=3, col=7, height=4, width=6)
    out = dash.save(str(tmp_path / "dash.html"))
    content = open(out, encoding="utf-8").read()
    assert "plotly" in content.lower()
    assert "Revenue" in content


def test_dashboard_accepts_vx_chart(tmp_path, sales_df):
    chart = vx.plot(sales_df, kind="line", x="date", y="revenue", title="Trend")
    dash = Dashboard(title="Chart embed")
    dash.add_chart(chart, row=1, col=1, height=6, width=12)
    out = dash.save(str(tmp_path / "embed.html"))
    assert "Trend" in open(out, encoding="utf-8").read()


def test_auto_returns_dashboard(tmp_path, sales_df):
    dash = Dashboard.auto(sales_df, theme="void_indigo", title="Auto")
    assert isinstance(dash, Dashboard)
    out = dash.save(str(tmp_path / "auto.html"))
    content = open(out, encoding="utf-8").read()
    assert "<html" in content.lower()


def test_html_alias_still_works():
    from viewx import HTML
    assert HTML is Dashboard
