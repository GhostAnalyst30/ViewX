import pandas as pd
import re

class BibliometricsAnalyzer:
    def __init__(self):
        # Mapeo de nombres comunes de columnas para bases bibliográficas
        self.column_map = {
            'AU': ['Authors', 'AU', 'Author', 'Autores'],
            'PY': ['Year', 'PY', 'Publication Year', 'Año'],
            'SO': ['Source title', 'SO', 'Journal', 'Source', 'Revista'],
            'DE': ['Author Keywords', 'DE', 'Keywords', 'Palabras Clave'],
            'TC': ['Cited by', 'TC', 'Times Cited', 'Citas']
        }

    def _find_column(self, df, key):
        for col in df.columns:
            if col in self.column_map[key] or col.upper() in [c.upper() for c in self.column_map[key]]:
                return col
        return None

    def analyze(self, df: pd.DataFrame):
        results = {}
        
        # 1. Producción Anual
        py_col = self._find_column(df, 'PY')
        if py_col:
            prod = df[py_col].dropna().value_counts().sort_index().reset_index()
            prod.columns = ['Year', 'Count']
            results['annual_production'] = prod

        # 2. Autores Top
        au_col = self._find_column(df, 'AU')
        if au_col:
            # Manejar autores separados por ; o ,
            all_authors = []
            for entry in df[au_col].dropna():
                # Split común en Scopus/WoS es ';'
                authors = [a.strip() for a in re.split(';|,', str(entry))]
                all_authors.extend(authors)
            
            au_df = pd.Series(all_authors).value_counts().head(15).reset_index()
            au_df.columns = ['Author', 'Count']
            results['top_authors'] = au_df

        # 3. Fuentes Top
        so_col = self._find_column(df, 'SO')
        if so_col:
            so_df = df[so_col].dropna().value_counts().head(10).reset_index()
            so_df.columns = ['Source', 'Count']
            results['top_sources'] = so_df

        return results if results else None
