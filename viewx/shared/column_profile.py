"""Shared column classification, ranking and coercion for ViewX auto-builders.

Single source of truth for the heuristics previously duplicated in
``Report/auto_builder.py``, ``Slides/auto_builder.py`` and ``HTML.auto_generate``.
"""

from __future__ import annotations

import re
from typing import Dict, List, Optional, Tuple

import pandas as pd

# Cheap pre-check before attempting an expensive pd.to_datetime on object columns.
_DATETIME_HINT = re.compile(
    r"^\s*(\d{4}[-/.]\d{1,2}[-/.]\d{1,2}|\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4})"
)


def classify_series(s: pd.Series) -> str:
    """Classify a series as datetime / boolean / numeric / categorical / text."""
    if pd.api.types.is_datetime64_any_dtype(s):
        return "datetime"
    if pd.api.types.is_bool_dtype(s):
        return "boolean"
    if pd.api.types.is_numeric_dtype(s):
        return "numeric"
    return "categorical" if s.nunique() / max(len(s), 1) < 0.5 else "text"


def classify_columns(df: pd.DataFrame) -> Dict[str, str]:
    return {c: classify_series(df[c]) for c in df.columns}


def score_numeric(df: pd.DataFrame, col: str) -> float:
    """Rank score: completeness (0.5) + normalized coefficient of variation (0.5)."""
    s = df[col].dropna()
    if len(s) == 0:
        return 0.0
    completeness = len(s) / len(df)
    cv = (s.std() / abs(s.mean())) if s.mean() != 0 else 0.0
    return 0.5 * completeness + 0.5 * min(cv, 5.0) / 5.0


def score_categorical(df: pd.DataFrame, col: str) -> float:
    """Rank score: completeness weighted by having moderate cardinality (2-20)."""
    s = df[col].dropna()
    completeness = len(s) / max(len(df), 1)
    n_unique = s.nunique()
    card_score = 1.0 if 2 <= n_unique <= 20 else max(0.0, 1.0 - (n_unique - 20) / 80)
    return completeness * card_score


def rank_numeric(df: pd.DataFrame, cols: List[str]) -> List[str]:
    return sorted(cols, key=lambda c: score_numeric(df, c), reverse=True)


def rank_categorical(df: pd.DataFrame, cols: List[str]) -> List[str]:
    return sorted(cols, key=lambda c: score_categorical(df, c), reverse=True)


def best_numeric_col(df: pd.DataFrame, numeric_cols: List[str]) -> Optional[str]:
    if not numeric_cols:
        return None
    return max(numeric_cols, key=lambda c: score_numeric(df, c))


def best_categorical_col(df: pd.DataFrame, cat_cols: List[str]) -> Optional[str]:
    if not cat_cols:
        return None
    return max(cat_cols, key=lambda c: score_categorical(df, c))


def top_correlation_pairs(
    df: pd.DataFrame,
    numeric_cols: List[str],
    threshold: float = 0.0,
    top: Optional[int] = None,
) -> List[Tuple[str, str, float]]:
    """Signed Pearson pairs sorted by |r| desc, computed from a single corr matrix."""
    if len(numeric_cols) < 2:
        return []
    corr = df[numeric_cols].corr()
    pairs: List[Tuple[str, str, float]] = []
    for i in range(len(numeric_cols)):
        for j in range(i + 1, len(numeric_cols)):
            r = float(corr.iloc[i, j])
            if pd.notna(r) and abs(r) >= threshold:
                pairs.append((numeric_cols[i], numeric_cols[j], r))
    pairs.sort(key=lambda p: abs(p[2]), reverse=True)
    return pairs[:top] if top else pairs


def looks_like_datetime(s: pd.Series, sample_size: int = 50) -> bool:
    """Cheap heuristic to avoid running pd.to_datetime on every object column."""
    sample = s.dropna().astype(str).head(sample_size)
    if sample.empty:
        return False
    hits = sum(bool(_DATETIME_HINT.match(v)) for v in sample)
    return hits / len(sample) >= 0.8


def coerce_types(
    df: pd.DataFrame, columns: Optional[List[str]] = None
) -> Tuple[pd.DataFrame, Dict[str, str]]:
    """Try to convert object columns to numeric or datetime (returns copy + log)."""
    cols = list(columns) if columns is not None else list(df.columns)
    out = df[cols].copy()
    coerced: Dict[str, str] = {}
    for col in cols:
        s = out[col]
        if not pd.api.types.is_object_dtype(s):
            continue
        old = str(s.dtype)
        cleaned = s.astype(str).str.strip().str.replace(r"[$€£¥%\s,]", "", regex=True)
        num = pd.to_numeric(cleaned, errors="coerce")
        if num.notna().sum() / max(len(s.dropna()), 1) >= 0.80:
            out[col] = num
        elif looks_like_datetime(s):
            dt = pd.to_datetime(s, errors="coerce")
            if dt.notna().sum() / max(len(s.dropna()), 1) >= 0.80:
                out[col] = dt
        new = str(out[col].dtype)
        if old != new:
            coerced[col] = f"{old} -> {new}"
    return out, coerced


def format_value(v: float) -> str:
    """Compact human formatting for KPI-style numbers (1.2K, 3.4M, ...)."""
    a = abs(v)
    if a >= 1_000_000_000:
        return f"{v / 1_000_000_000:,.2f}B"
    if a >= 1_000_000:
        return f"{v / 1_000_000:,.2f}M"
    if a >= 1_000:
        return f"{v / 1_000:,.1f}K"
    return f"{v:,.2f}"
