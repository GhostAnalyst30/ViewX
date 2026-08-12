from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd


@dataclass
class ColumnProfile:
    name: str
    dtype: str
    inferred_type: str
    n_unique: int
    n_missing: int
    p_missing: float
    is_constant: bool
    cardinality_ratio: float
    skewness: Optional[float] = None
    kurtosis: Optional[float] = None
    mean: Optional[float] = None
    std: Optional[float] = None
    min: Optional[float] = None
    max: Optional[float] = None
    median: Optional[float] = None
    q1: Optional[float] = None
    q3: Optional[float] = None
    iqr: Optional[float] = None
    top_values: Dict = field(default_factory=dict)
    outliers: int = 0
    alerts: List[str] = field(default_factory=list)


@dataclass
class DatasetReport:
    n_rows: int
    n_cols: int
    n_duplicates: int
    n_missing_total: int
    p_missing_total: float
    memory_usage: str
    estimated_rows: str
    column_profiles: Dict[str, ColumnProfile]
    correlation_pairs: List[Tuple[str, str, float]]
    alerts: List[str]
    categorical_columns: List[str]
    numeric_columns: List[str]
    datetime_columns: List[str]
    boolean_columns: List[str]


class ColumnTypeStrategy(ABC):
    @abstractmethod
    def infer(self, series: pd.Series) -> str:
        ...

    @abstractmethod
    def analyze(self, series: pd.Series, col: str, n_total: int) -> ColumnProfile:
        ...


class NumericStrategy(ColumnTypeStrategy):
    def infer(self, series: pd.Series) -> str:
        return "numeric"

    def analyze(self, series: pd.Series, col: str, n_total: int) -> ColumnProfile:
        s = series.dropna()
        n_missing = series.isna().sum()
        p_missing = (n_missing / n_total) * 100
        n_unique = series.nunique()

        profile = ColumnProfile(
            name=col,
            dtype=str(series.dtype),
            inferred_type="numeric",
            n_unique=n_unique,
            n_missing=n_missing,
            p_missing=p_missing,
            is_constant=n_unique == 1,
            cardinality_ratio=n_unique / n_total if n_total > 0 else 0,
        )

        if len(s) > 0:
            profile.mean = float(s.mean())
            profile.std = float(s.std())
            profile.min = float(s.min())
            profile.max = float(s.max())
            profile.median = float(s.median())
            profile.q1 = float(s.quantile(0.25))
            profile.q3 = float(s.quantile(0.75))
            profile.iqr = profile.q3 - profile.q1
            profile.skewness = float(s.skew()) if len(s) > 2 else 0.0
            profile.kurtosis = float(s.kurtosis()) if len(s) > 2 else 0.0

            q1, q3 = profile.q1, profile.q3
            iqr = profile.iqr
            if iqr and iqr > 0:
                lower = q1 - 1.5 * iqr
                upper = q3 + 1.5 * iqr
                profile.outliers = int(((s < lower) | (s > upper)).sum())

        if p_missing > 50:
            profile.alerts.append(f"Column '{col}': {p_missing:.1f}% missing values")
        if profile.is_constant:
            profile.alerts.append(f"Column '{col}': constant value ({s.iloc[0] if len(s) > 0 else 'N/A'})")
        if profile.skewness is not None and abs(profile.skewness) > 2:
            profile.alerts.append(f"Column '{col}': high skewness ({profile.skewness:.2f})")
        if profile.outliers > 0:
            profile.alerts.append(f"Column '{col}': {profile.outliers} outliers detected")

        return profile


class CategoricalStrategy(ColumnTypeStrategy):
    def infer(self, series: pd.Series) -> str:
        return "categorical"

    def analyze(self, series: pd.Series, col: str, n_total: int) -> ColumnProfile:
        s = series.dropna()
        n_missing = series.isna().sum()
        p_missing = (n_missing / n_total) * 100
        n_unique = series.nunique()

        top_values = {}
        if len(s) > 0:
            top_n = s.value_counts().head(5)
            top_values = {str(k): int(v) for k, v in top_n.items()}

        profile = ColumnProfile(
            name=col,
            dtype=str(series.dtype),
            inferred_type="categorical",
            n_unique=n_unique,
            n_missing=n_missing,
            p_missing=p_missing,
            is_constant=n_unique <= 1,
            cardinality_ratio=n_unique / n_total if n_total > 0 else 0,
            top_values=top_values,
        )

        if p_missing > 50:
            profile.alerts.append(f"Column '{col}': {p_missing:.1f}% missing values")
        if profile.is_constant:
            profile.alerts.append(f"Column '{col}': constant value")
        if n_unique == n_total:
            profile.alerts.append(f"Column '{col}': all values unique (possible ID)")

        return profile


class DateTimeStrategy(ColumnTypeStrategy):
    def infer(self, series: pd.Series) -> str:
        return "datetime"

    def analyze(self, series: pd.Series, col: str, n_total: int) -> ColumnProfile:
        s = series.dropna()
        n_missing = series.isna().sum()
        p_missing = (n_missing / n_total) * 100
        n_unique = series.nunique()

        profile = ColumnProfile(
            name=col,
            dtype=str(series.dtype),
            inferred_type="datetime",
            n_unique=n_unique,
            n_missing=n_missing,
            p_missing=p_missing,
            is_constant=n_unique <= 1,
            cardinality_ratio=n_unique / n_total if n_total > 0 else 0,
        )

        if len(s) > 0:
            try:
                years = s.dt.year
                profile.min = float(years.min())
                profile.max = float(years.max())
                profile.mean = float(years.mean())
            except Exception:
                pass

        if p_missing > 50:
            profile.alerts.append(f"Column '{col}': {p_missing:.1f}% missing values")

        return profile


class BooleanStrategy(ColumnTypeStrategy):
    def infer(self, series: pd.Series) -> str:
        return "boolean"

    def analyze(self, series: pd.Series, col: str, n_total: int) -> ColumnProfile:
        s = series.dropna()
        n_missing = series.isna().sum()
        p_missing = (n_missing / n_total) * 100
        n_unique = series.nunique()
        true_count = int(s.astype(bool).sum()) if len(s) > 0 else 0

        profile = ColumnProfile(
            name=col,
            dtype=str(series.dtype),
            inferred_type="boolean",
            n_unique=n_unique,
            n_missing=n_missing,
            p_missing=p_missing,
            is_constant=n_unique <= 1,
            cardinality_ratio=n_unique / n_total if n_total > 0 else 0,
            mean=float(true_count / len(s)) if len(s) > 0 else 0,
            top_values={"True": true_count, "False": len(s) - true_count} if len(s) > 0 else {},
        )

        if p_missing > 50:
            profile.alerts.append(f"Column '{col}': {p_missing:.1f}% missing values")

        return profile


class AnalyzerEngine:
    def __init__(self):
        self.strategies: Dict[str, ColumnTypeStrategy] = {
            "numeric": NumericStrategy(),
            "categorical": CategoricalStrategy(),
            "datetime": DateTimeStrategy(),
            "boolean": BooleanStrategy(),
        }

    def infer_column_type(self, series: pd.Series) -> str:
        if pd.api.types.is_datetime64_any_dtype(series):
            return "datetime"
        if pd.api.types.is_bool_dtype(series):
            return "boolean"
        if pd.api.types.is_numeric_dtype(series):
            return "numeric"
        return "categorical"

    def analyze_column(self, series: pd.Series, col: str, n_total: int) -> ColumnProfile:
        ctype = self.infer_column_type(series)
        strategy = self.strategies[ctype]
        return strategy.analyze(series, col, n_total)

    def analyze_dataset(self, df: pd.DataFrame) -> DatasetReport:
        profiles: Dict[str, ColumnProfile] = {}
        all_alerts: List[str] = []
        categorical_columns: List[str] = []
        numeric_columns: List[str] = []
        datetime_columns: List[str] = []
        boolean_columns: List[str] = []

        for col in df.columns:
            profile = self.analyze_column(df[col], col, len(df))
            profiles[col] = profile
            all_alerts.extend(profile.alerts)

            if profile.inferred_type == "numeric":
                numeric_columns.append(col)
            elif profile.inferred_type == "categorical":
                categorical_columns.append(col)
            elif profile.inferred_type == "datetime":
                datetime_columns.append(col)
            elif profile.inferred_type == "boolean":
                boolean_columns.append(col)

        n_duplicates = int(df.duplicated().sum())
        if n_duplicates > 0:
            all_alerts.append(f"Found {n_duplicates} duplicate rows")

        correlation_pairs = self._find_correlations(df, numeric_columns)

        mem_bytes = df.memory_usage(deep=True).sum()
        if mem_bytes > 1e9:
            memory_usage = f"{mem_bytes / 1e9:.2f} GB"
        elif mem_bytes > 1e6:
            memory_usage = f"{mem_bytes / 1e6:.2f} MB"
        else:
            memory_usage = f"{mem_bytes / 1e3:.1f} KB"

        n_rows = len(df)
        if n_rows > 1_000_000:
            estimated_rows = f"{n_rows / 1_000_000:.1f}M"
        elif n_rows > 1_000:
            estimated_rows = f"{n_rows / 1_000:.1f}K"
        else:
            estimated_rows = str(n_rows)

        n_missing_total = sum(p.n_missing for p in profiles.values())
        total_cells = n_rows * len(df.columns)
        p_missing_total = (n_missing_total / total_cells) * 100 if total_cells > 0 else 0

        return DatasetReport(
            n_rows=n_rows,
            n_cols=len(df.columns),
            n_duplicates=n_duplicates,
            n_missing_total=n_missing_total,
            p_missing_total=p_missing_total,
            memory_usage=memory_usage,
            estimated_rows=estimated_rows,
            column_profiles=profiles,
            correlation_pairs=correlation_pairs,
            alerts=all_alerts,
            categorical_columns=categorical_columns,
            numeric_columns=numeric_columns,
            datetime_columns=datetime_columns,
            boolean_columns=boolean_columns,
        )

    def _find_correlations(
        self, df: pd.DataFrame, numeric_cols: List[str], threshold: float = 0.3
    ) -> List[Tuple[str, str, float]]:
        # Single vectorized corr() pass; signed values read from the same matrix.
        from viewx.shared.column_profile import top_correlation_pairs

        return top_correlation_pairs(df, numeric_cols, threshold=threshold, top=10)
