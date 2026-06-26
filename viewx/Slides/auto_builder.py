"""Auto-generate HTML slide decks from a pandas DataFrame."""

from __future__ import annotations

from typing import List, Optional

import pandas as pd

from viewx.DataMatrix.analyzers import AnalyzerEngine
from viewx.shared.insights import quality_summary

from .charts import BarPlot, PiePlot, ScatterPlot
from .components import BulletList, IconStat, Subtitle, Text, Title
from .slides_engine import Grid, Presentation, Slide


def _best_numeric_col(df: pd.DataFrame, numeric_cols: List[str]) -> Optional[str]:
    if not numeric_cols:
        return None

    def score(col: str) -> float:
        s = df[col].dropna()
        if len(s) == 0:
            return 0.0
        completeness = len(s) / len(df)
        cv = (s.std() / abs(s.mean())) if s.mean() != 0 else 0.0
        return 0.5 * completeness + 0.5 * min(cv, 5.0) / 5.0

    return max(numeric_cols, key=score)


def _best_categorical_col(df: pd.DataFrame, cat_cols: List[str]) -> Optional[str]:
    if not cat_cols:
        return None

    def score(col: str) -> float:
        s = df[col].dropna()
        completeness = len(s) / max(len(df), 1)
        n_unique = s.nunique()
        card_score = 1.0 if 2 <= n_unique <= 20 else max(0.0, 1.0 - (n_unique - 20) / 80)
        return completeness * card_score

    return max(cat_cols, key=score)


def build_auto_presentation(
    df: pd.DataFrame,
    title: str = "Dataset Overview",
    theme: str = "dark",
    filename: str = "auto_slides.html",
    columns: Optional[List[str]] = None,
    max_slides: int = 8,
    show: bool = True,
) -> str:
    """Build and export an auto-generated presentation from a DataFrame."""
    cols = list(columns) if columns else list(df.columns)
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise KeyError(f"Columns not found: {missing}")

    work = df[cols].copy()
    engine = AnalyzerEngine()
    report = engine.analyze_dataset(work)
    payload = quality_summary(work, report=report)
    summary = payload["summary"]
    alerts = payload["alerts"]
    highlights = payload["highlights"]

    pres = Presentation(title, theme=theme)
    pres.meta(author="ViewX", generator="auto_generate")

    with Slide(title="Cover", notes="Auto-generated dataset overview."):
        Title(title).center("x").pos(top=18).zoom_in(duration=1.0)
        Subtitle(
            f"{summary['rows']:,} rows × {summary['columns']} columns · {summary['memory']}"
        ).center("x").pos(top=34).fade_in(delay=0.2)
        Text(
            "Generated automatically by ViewX Slides",
            color="#9ca3af",
        ).center("x").pos(top=48).size(width="60%").align("center").fade_in(delay=0.35)

    with Slide(title="Key Metrics", notes="Dataset dimensions and quality KPIs."):
        Title("Key Metrics").pos(left=6, top=8).slide_in("left")
        with Grid(columns=4, gap=16).pos(left=6, top=28).size(width="88%"):
            IconStat("database", str(summary["rows"]), "Rows")
            IconStat("grid", str(summary["columns"]), "Columns")
            IconStat("percent", f"{100 - summary['missing_pct']:.0f}%", "Complete")
            IconStat("users", str(summary["duplicates"]), "Duplicates")

    quality_items: List[str] = []
    if alerts:
        quality_items.extend([f"Warning: {a}" for a in alerts[:6]])
    if highlights:
        quality_items.extend([f"Strength: {h}" for h in highlights[:6]])
    if not quality_items:
        quality_items = ["No quality issues or highlights to report."]

    with Slide(title="Data Quality", notes="Warnings and strengths."):
        Title("Data Quality").pos(left=6, top=8).slide_in("left")
        BulletList(quality_items).pos(left=8, top=26).size(width="84%").fade_in(delay=0.2)

    num_col = _best_numeric_col(work, report.numeric_columns)
    if num_col:
        s = work[num_col].dropna()
        bins = min(12, max(3, int(s.nunique())))
        counts, edges = pd.cut(s, bins=bins, retbins=True)
        value_counts = counts.value_counts().sort_index()
        labels = [
            f"{interval.left:.1f}-{interval.right:.1f}"
            for interval in value_counts.index
        ]
        with Slide(title=f"Numeric: {num_col}", notes=f"Distribution of {num_col}."):
            Title(num_col).pos(left=6, top=8).zoom_in()
            Text(
                f"Numeric distribution · mean={s.mean():.2f}, std={s.std():.2f}"
            ).pos(left=7, top=20).size(width="40%")
            BarPlot(labels, value_counts.values.tolist(), title=num_col).pos(
                left=8, top=32
            ).size(width="84%", height="52%")

    cat_col = _best_categorical_col(work, report.categorical_columns)
    if cat_col:
        top = work[cat_col].value_counts().head(8)
        with Slide(title=f"Categorical: {cat_col}", notes=f"Top categories in {cat_col}."):
            Title(cat_col).pos(left=6, top=8).slide_in("right")
            PiePlot(
                top.index.astype(str).tolist(),
                top.values.tolist(),
                title=cat_col,
                hole=0.35,
            ).pos(left=10, top=24).size(width="80%", height="58%")

    if report.correlation_pairs:
        col_a, col_b, r_val = report.correlation_pairs[0]
        with Slide(title="Correlations", notes="Strongest numeric correlation pair."):
            Title("Top Correlation").pos(left=6, top=8).zoom_in()
            Text(f"{col_a} vs {col_b} · r = {r_val:.3f}").pos(left=7, top=22).size(
                width="40%"
            )
            ScatterPlot(
                work[col_a].tolist(),
                work[col_b].tolist(),
                title=f"{col_a} vs {col_b}",
            ).pos(left=8, top=32).size(width="84%", height="52%")

    profile_lines = []
    for p in list(report.column_profiles.values())[:12]:
        alert_note = f" · {len(p.alerts)} alert(s)" if p.alerts else ""
        profile_lines.append(
            f"{p.name} ({p.inferred_type}): {p.p_missing:.1f}% missing, "
            f"{p.n_unique} unique{alert_note}"
        )
    with Slide(title="Column Profiles", notes="Summary of column profiles."):
        Title("Column Profiles").pos(left=6, top=8).slide_in("left")
        BulletList(profile_lines).pos(left=8, top=24).size(width="84%").fade_in(
            delay=0.15
        )

    sample = work.head(8)
    display_cols = list(sample.columns[:6])
    sample_lines = [
        " | ".join(str(v)[:18] for v in row)
        for row in sample[display_cols].itertuples(index=False, name=None)
    ]
    header = " | ".join(display_cols)
    with Slide(title="Sample Data", notes="First rows of the dataset."):
        Title("Sample Data").pos(left=6, top=8).fade_in()
        Text(f"Columns: {header}").pos(left=7, top=20).size(width="88%")
        BulletList(sample_lines[:6]).pos(left=8, top=30).size(width="88%")

    return pres.export(filename, open_browser=show)
