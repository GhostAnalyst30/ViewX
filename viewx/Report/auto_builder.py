"""Auto-generate PDF quality reports from a pandas DataFrame."""

from __future__ import annotations

import os
from typing import List, Optional

import pandas as pd

from viewx.DataMatrix.analyzers import AnalyzerEngine
from viewx.shared.column_profile import best_categorical_col, best_numeric_col
from viewx.shared.insights import quality_summary


def _save_histogram(df: pd.DataFrame, col: str, images_dir: str) -> Optional[str]:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    s = df[col].dropna()
    if len(s) == 0:
        return None
    filename = f"auto_hist_{col.replace(' ', '_')}.png"
    path = os.path.join(images_dir, filename)
    plt.figure(figsize=(6, 4))
    plt.hist(s, bins=min(20, max(5, s.nunique())), color="#4f46e5", edgecolor="white")
    plt.title(f"Distribution: {col}")
    plt.xlabel(col)
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig(path, dpi=120)
    plt.close()
    return filename


def _save_bar_chart(df: pd.DataFrame, col: str, images_dir: str) -> Optional[str]:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    s = df[col].dropna()
    if len(s) == 0:
        return None
    top = s.value_counts().head(10)
    filename = f"auto_bar_{col.replace(' ', '_')}.png"
    path = os.path.join(images_dir, filename)
    plt.figure(figsize=(6, 4))
    plt.bar(top.index.astype(str), top.values, color="#06b6d4")
    plt.title(f"Top values: {col}")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(path, dpi=120)
    plt.close()
    return filename


def build_auto_report(
    df: pd.DataFrame,
    report_cls,
    title: str = "Dataset Quality Report",
    author: str = "ViewX",
    outdir: str = "output",
    columns: Optional[List[str]] = None,
    include_plots: bool = True,
    show_warnings: bool = True,
    show_highlights: bool = True,
):
    """Assemble a quality report (returns the Report; caller saves it)."""
    cols = list(columns) if columns else list(df.columns)
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise KeyError(f"Columns not found: {missing}")

    work = df[cols].copy()
    engine = AnalyzerEngine()
    dataset_report = engine.analyze_dataset(work)
    payload = quality_summary(work, report=dataset_report)
    summary = payload["summary"]
    alerts = payload["alerts"]
    highlights = payload["highlights"]
    correlations = payload["correlations"]

    rpt = report_cls(title=title, author=author, outdir=outdir)

    exec_text = (
        f"This report summarizes a dataset with {summary['rows']:,} rows and "
        f"{summary['columns']} columns ({summary['memory']} memory footprint). "
        f"The dataset contains {summary['numeric']} numeric, {summary['categorical']} "
        f"categorical, {summary['datetime']} datetime, and {summary['boolean']} boolean "
        f"columns. Overall completeness is {100 - summary['missing_pct']:.1f}% with "
        f"{summary['duplicates']} duplicate rows."
    )
    rpt.add_text(exec_text)
    rpt.add_text("")

    if show_warnings and alerts:
        with rpt.section("Quality Warnings"):
            rpt.add_itemize(alerts[:20])

    if show_highlights and highlights:
        with rpt.section("Dataset Strengths"):
            rpt.add_itemize(highlights)

    with rpt.section("Column Profiles"):
        headers = ["Column", "Type", "Missing %", "Unique", "Alerts"]
        rows = []
        for p in dataset_report.column_profiles.values():
            rows.append([
                p.name,
                p.inferred_type,
                f"{p.p_missing:.1f}",
                str(p.n_unique),
                str(len(p.alerts)),
            ])
        rpt.add_table(headers, rows, caption="Per-column quality profile")

    if correlations:
        with rpt.section("Notable Correlations"):
            corr_headers = ["Variable A", "Variable B", "Pearson r"]
            corr_rows = [[c["x"], c["y"], f"{c['r']:.4f}"] for c in correlations[:10]]
            rpt.add_table(corr_headers, corr_rows, caption="Top correlation pairs")

            top = correlations[0]
            x_vals = work[top["x"]].dropna().tolist()[:50]
            y_vals = work[top["y"]].dropna().tolist()[:50]
            if len(x_vals) == len(y_vals) and len(x_vals) >= 2:
                rpt.add_line_plot(
                    x_vals,
                    y_vals,
                    caption=f"Scatter: {top['x']} vs {top['y']} (r={top['r']:.3f})",
                )

    if include_plots:
        rpt.new_page()
        with rpt.section("Visual Summary"):
            num_col = best_numeric_col(work, dataset_report.numeric_columns)
            cat_col = best_categorical_col(work, dataset_report.categorical_columns)
            if num_col:
                hist_file = _save_histogram(work, num_col, rpt.images_dir)
                if hist_file:
                    rpt.add_image(hist_file, caption=f"Histogram of {num_col}")
            if cat_col:
                bar_file = _save_bar_chart(work, cat_col, rpt.images_dir)
                if bar_file:
                    rpt.add_image(bar_file, caption=f"Top categories in {cat_col}")

    rpt.new_page()
    with rpt.section("Sample Data"):
        sample = work.head(10)
        sample_headers = [str(c) for c in sample.columns[:8]]
        sample_rows = [
            [str(v)[:40] for v in row]
            for row in sample[sample_headers].itertuples(index=False, name=None)
        ]
        rpt.add_table(
            sample_headers,
            sample_rows,
            caption="First 10 rows (truncated values)",
        )

    return rpt
