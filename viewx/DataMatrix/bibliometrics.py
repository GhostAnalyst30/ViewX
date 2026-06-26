from __future__ import annotations

from collections import Counter
from typing import Dict, List, Optional, Tuple

import pandas as pd


class BibliometricsAnalyzer:
    def __init__(self):
        self.column_map = {
            "AU": ["Authors", "AU", "Author", "Autores", "AUTHOR", "authors"],
            "PY": ["Year", "PY", "Publication Year", "Año", "YEAR", "year"],
            "SO": [
                "Source title", "SO", "Journal", "Source", "Revista",
                "SOURCE", "source", "Publication Name",
            ],
            "DE": [
                "Author Keywords", "DE", "Keywords", "Palabras Clave",
                "KEYWORDS", "keywords", "Index Keywords",
            ],
            "TC": [
                "Cited by", "TC", "Times Cited", "Citas",
                "CITING", "citations", "Citations",
            ],
            "TI": ["Title", "TI", "TITLE", "Article Title", "title"],
            "DI": ["DOI", "DI", "DOI Number", "doi"],
            "AF": [
                "Affiliation", "AF", "AFFILIATION", "affiliation",
                "Author Affiliation", "Author Affiliations",
            ],
            "AB": ["Abstract", "AB", "ABSTRACT", "abstract"],
            "DT": [
                "Document Type", "DT", "Document Type", "document_type",
            ],
        }

    def _find_column(self, df: pd.DataFrame, key: str) -> Optional[str]:
        candidates = self.column_map[key]
        for col in df.columns:
            col_upper = col.strip().upper()
            for c in candidates:
                if col_upper == c.upper() or col.strip() == c:
                    return col
                if col_upper.replace(" ", "_") == c.upper().replace(" ", "_"):
                    return col
        return None

    def _split_multi(self, raw: str, separators: str = ";,", strip_parens: bool = True) -> List[str]:
        if not isinstance(raw, str) or not raw.strip():
            return []
        result = []
        for part in raw.split():
            if not part.strip():
                continue
            items = [item.strip() for item in part.replace(";", ",").split(",")]
            for item in items:
                item = item.strip().strip(".").strip()
                if strip_parens:
                    item = item.split("(")[0].strip()
                if item and len(item) > 1:
                    result.append(item)
        return result

    def _split_list_field(self, raw: str) -> List[str]:
        if not isinstance(raw, str) or not raw.strip():
            return []
        items = [x.strip() for x in raw.replace(";", ",").split(",")]
        return [x for x in items if x]

    def analyze(self, df: pd.DataFrame) -> Optional[dict]:
        results: Dict[str, pd.DataFrame] = {}

        py_col = self._find_column(df, "PY")
        if py_col:
            year_series = df[py_col].dropna()
            year_numeric = pd.to_numeric(year_series, errors="coerce").dropna()
            if len(year_numeric) > 0:
                prod = year_numeric.value_counts().sort_index().reset_index()
                prod.columns = ["Year", "Count"]
                prod["Year"] = prod["Year"].astype(int)
                results["annual_production"] = prod

        au_col = self._find_column(df, "AU")
        if au_col:
            all_authors: List[str] = []
            for entry in df[au_col].dropna():
                all_authors.extend(self._split_list_field(str(entry)))

            if all_authors:
                au_counts = Counter(all_authors)
                au_df = (
                    pd.DataFrame(au_counts.most_common(20), columns=["Author", "Count"])
                    .sort_values("Count", ascending=False)
                    .reset_index(drop=True)
                )
                results["top_authors"] = au_df

                n_unique = len(au_counts)
                total = sum(au_counts.values())
                results["author_summary"] = {
                    "total_authors": total,
                    "unique_authors": n_unique,
                    "avg_per_publication": round(total / max(len(df), 1), 2),
                }

        so_col = self._find_column(df, "SO")
        if so_col:
            so_counts = df[so_col].dropna().value_counts().head(15)
            if len(so_counts) > 0:
                so_df = so_counts.reset_index()
                so_df.columns = ["Source", "Count"]
                results["top_sources"] = so_df

        de_col = self._find_column(df, "DE")
        if de_col:
            all_keywords: List[str] = []
            for entry in df[de_col].dropna():
                all_keywords.extend(self._split_list_field(str(entry)))

            if all_keywords:
                kw_counts = Counter(all_keywords)
                kw_df = (
                    pd.DataFrame(kw_counts.most_common(20), columns=["Keyword", "Count"])
                    .sort_values("Count", ascending=False)
                    .reset_index(drop=True)
                )
                results["top_keywords"] = kw_df

        tc_col = self._find_column(df, "TC")
        if tc_col:
            tc_series = pd.to_numeric(df[tc_col], errors="coerce").dropna()
            if len(tc_series) > 0:
                results["citation_summary"] = {
                    "total_citations": int(tc_series.sum()),
                    "mean_citations": round(tc_series.mean(), 2),
                    "median_citations": round(tc_series.median(), 2),
                    "max_citations": int(tc_series.max()),
                    "min_citations": int(tc_series.min()),
                }


        return results if results else None
