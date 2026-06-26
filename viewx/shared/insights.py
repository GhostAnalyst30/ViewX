"""Shared dataset quality insights for ViewX engines."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import pandas as pd

from viewx.DataMatrix.analyzers import AnalyzerEngine, DatasetReport


def compute_highlights(report: DatasetReport) -> List[str]:
    """Return positive quality traits for a analyzed dataset."""
    highlights: List[str] = []

    if report.p_missing_total < 5:
        highlights.append(
            f"Low global missing rate ({report.p_missing_total:.1f}%)"
        )

    if report.n_duplicates == 0:
        highlights.append("No duplicate rows detected")

    type_mix = sum(
        bool(getattr(report, key))
        for key in (
            "numeric_columns",
            "categorical_columns",
            "datetime_columns",
            "boolean_columns",
        )
    )
    if type_mix >= 2:
        highlights.append(
            f"Diverse column mix: {len(report.numeric_columns)} numeric, "
            f"{len(report.categorical_columns)} categorical, "
            f"{len(report.datetime_columns)} datetime, "
            f"{len(report.boolean_columns)} boolean"
        )

    for col_a, col_b, r_val in report.correlation_pairs[:3]:
        if abs(r_val) >= 0.7:
            highlights.append(
                f"Strong correlation: {col_a} vs {col_b} (r={r_val:.2f})"
            )

    high_completeness = [
        p.name for p in report.column_profiles.values() if p.p_missing < 5
    ]
    if high_completeness:
        if len(high_completeness) == len(report.column_profiles):
            highlights.append("All columns have >95% completeness")
        elif len(high_completeness) >= 3:
            highlights.append(
                f"{len(high_completeness)} columns with >95% completeness"
            )

    usable_cat = [
        p
        for p in report.column_profiles.values()
        if p.inferred_type == "categorical" and 2 <= p.n_unique <= 20
    ]
    if usable_cat:
        highlights.append(
            f"{len(usable_cat)} categorical columns with ideal cardinality (2-20 values)"
        )

    if report.n_rows >= 100:
        highlights.append(f"Substantial sample size ({report.n_rows:,} rows)")

    clean_numeric = [
        p.name
        for p in report.column_profiles.values()
        if p.inferred_type == "numeric" and p.p_missing < 10 and not p.is_constant
    ]
    if len(clean_numeric) >= 2:
        highlights.append(
            f"{len(clean_numeric)} numeric columns ready for analysis"
        )

    if not highlights:
        highlights.append("Dataset ready for exploratory analysis")

    return highlights


def quality_summary(
    df: pd.DataFrame,
    report: Optional[DatasetReport] = None,
    analyzer: Optional[AnalyzerEngine] = None,
) -> Dict[str, Any]:
    """Build a reusable quality payload for Slides, Report, and DataMatrix."""
    if report is None:
        engine = analyzer or AnalyzerEngine()
        report = engine.analyze_dataset(df)

    highlights = compute_highlights(report)
    summary = {
        "rows": report.n_rows,
        "columns": report.n_cols,
        "duplicates": report.n_duplicates,
        "missing_cells": report.n_missing_total,
        "missing_pct": round(report.p_missing_total, 2),
        "memory": report.memory_usage,
        "numeric": len(report.numeric_columns),
        "categorical": len(report.categorical_columns),
        "datetime": len(report.datetime_columns),
        "boolean": len(report.boolean_columns),
    }
    correlations = [
        {"x": a, "y": b, "r": round(v, 4)}
        for a, b, v in report.correlation_pairs
    ]

    return {
        "alerts": report.alerts,
        "highlights": highlights,
        "summary": summary,
        "correlations": correlations,
        "report": report,
    }
