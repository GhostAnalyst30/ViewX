from __future__ import annotations

import json
from typing import Any, Dict, List

import numpy as np
import pandas as pd

from .analyzers import DatasetReport

DEFAULT_EXPLORER_MAX_ROWS = 5000


def _stratified_sample(
    df: pd.DataFrame, report: DatasetReport, max_rows: int
) -> pd.DataFrame:
    """Sample max_rows preserving category proportions when possible."""
    strat_col = None
    for col in report.categorical_columns:
        if 2 <= df[col].nunique(dropna=True) <= 50:
            strat_col = col
            break

    if strat_col is not None:
        frac = min(max_rows / len(df), 1.0)
        parts = [
            group.sample(frac=frac, random_state=0)
            for _, group in df.groupby(strat_col, observed=True)
        ]
        sampled = pd.concat(parts)
        if len(sampled) > max_rows:
            sampled = sampled.sample(n=max_rows, random_state=0)
        return sampled.sort_index()

    return df.sample(n=max_rows, random_state=0).sort_index()


def build_explorer_payload(
    df: pd.DataFrame,
    report: DatasetReport,
    max_rows: int = DEFAULT_EXPLORER_MAX_ROWS,
) -> Dict[str, Any]:
    """Serialize dataset + column metadata for client-side interactive exploration."""
    total_rows = len(df)
    truncated = total_rows > max_rows
    sample = _stratified_sample(df, report, max_rows) if truncated else df.copy()

    for col in sample.columns:
        if pd.api.types.is_datetime64_any_dtype(sample[col]):
            sample[col] = sample[col].dt.strftime("%Y-%m-%d %H:%M:%S").where(
                sample[col].notna(), None
            )
        elif pd.api.types.is_float_dtype(sample[col]):
            # Round floats to keep the embedded JSON payload compact
            sample[col] = sample[col].round(4)

    records: List[dict] = json.loads(
        sample.to_json(orient="records", date_format="iso")
    )

    columns: List[dict] = []
    for col in df.columns:
        profile = report.column_profiles.get(col)
        inferred = profile.inferred_type if profile else "text"
        meta: Dict[str, Any] = {
            "name": col,
            "type": inferred,
            "dtype": str(df[col].dtype),
            "missing": int(df[col].isna().sum()),
            "missingPct": round(float(df[col].isna().mean() * 100), 2),
            "unique": int(df[col].nunique(dropna=True)),
        }
        if profile:
            if inferred == "numeric":
                s = df[col].dropna()
                if len(s):
                    meta["min"] = float(s.min())
                    meta["max"] = float(s.max())
                    meta["mean"] = round(float(s.mean()), 4)
                    meta["median"] = round(float(s.median()), 4)
            elif inferred in ("categorical", "boolean"):
                vc = df[col].dropna().astype(str).value_counts().head(25)
                meta["values"] = [{"label": k, "count": int(v)} for k, v in vc.items()]
            elif inferred == "datetime":
                s = pd.to_datetime(df[col], errors="coerce").dropna()
                if len(s):
                    meta["min"] = s.min().strftime("%Y-%m-%d")
                    meta["max"] = s.max().strftime("%Y-%m-%d")

        columns.append(meta)

    return {
        "totalRows": total_rows,
        "loadedRows": len(sample),
        "truncated": truncated,
        "columns": columns,
        "records": records,
    }


def explorer_json_script(payload: Dict[str, Any]) -> str:
    """Embed explorer payload safely inside HTML."""
    raw = json.dumps(payload, ensure_ascii=False, default=_json_default)
    return f'<script type="application/json" id="dm-explorer-data">{raw}</script>'


def _json_default(obj: Any) -> Any:
    if isinstance(obj, (np.integer, np.floating)):
        return obj.item()
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if pd.isna(obj):
        return None
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
