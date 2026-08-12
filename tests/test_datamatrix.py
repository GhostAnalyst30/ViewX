import viewx as vx
from viewx import DataMatrix
from viewx.DataMatrix.explorer import build_explorer_payload


def test_analyze_and_summary(iris):
    dm = DataMatrix(iris).analyze()
    info = dm.summary()
    assert info["rows"] == len(iris)
    assert info["numeric"] >= 4


def test_save_report(tmp_path, iris):
    out = DataMatrix(iris).analyze().save(str(tmp_path / "eda.html"), theme="dark_enterprise")
    content = open(out, encoding="utf-8").read()
    assert "DataMatrix" in content


def test_sample_tab_is_capped(tmp_path, big_df):
    dm = DataMatrix(big_df).analyze()
    html = dm.render_html(sample_rows=100)
    # only 100 sample rows embedded, with a notice
    assert "Showing the first 100" in html
    assert html.count("<tr>") < 5000  # far fewer than the 30k source rows


def test_explorer_payload_truncated_stratified(big_df):
    dm = DataMatrix(big_df).analyze()
    payload = build_explorer_payload(big_df, dm.report, max_rows=1000)
    assert payload["truncated"] is True
    assert payload["loadedRows"] <= 1000
    # stratified sample keeps every category present
    cats = {r["cat"] for r in payload["records"]}
    assert cats == {"a", "b", "c"}


def test_correlations_are_signed(iris):
    dm = DataMatrix(iris.select_dtypes("number")).analyze()
    pairs = dm.report.correlation_pairs
    assert pairs, "iris should have correlated columns"
    # signed values in [-1, 1], sorted by absolute value
    assert all(-1.0 <= r <= 1.0 for _, _, r in pairs)
    abs_vals = [abs(r) for _, _, r in pairs]
    assert abs_vals == sorted(abs_vals, reverse=True)
