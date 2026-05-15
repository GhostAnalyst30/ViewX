import pandas as pd
import numpy as np
import json
from datetime import datetime
from .visualizer import Visualizer
from .bibliometrics import BibliometricsAnalyzer

class DataMatrix:
    def __init__(self, df: pd.DataFrame):
        self.original_df = df.copy()
        self.df = df.copy()
        self.visualizer = Visualizer()
        self.bib_analyzer = BibliometricsAnalyzer()
        self.summary = {}
        self.column_stats = {}
        self.alerts = []

    def _get_column_type(self, series):
        if pd.api.types.is_numeric_dtype(series):
            return "numeric"
        elif pd.api.types.is_datetime64_any_dtype(series):
            return "datetime"
        elif pd.api.types.is_bool_dtype(series):
            return "boolean"
        else:
            return "categorical"

    def _analyze_columns(self):
        for col in self.df.columns:
            series = self.df[col]
            col_type = self._get_column_type(series)
            n_unique = series.nunique()
            n_missing = series.isna().sum()
            p_missing = (n_missing / len(series)) * 100
            
            stats = {
                "type": col_type,
                "n_unique": int(n_unique),
                "n_missing": int(n_missing),
                "p_missing": float(p_missing),
            }

            if col_type == "numeric":
                stats.update({
                    "mean": float(series.mean()),
                    "std": float(series.std()),
                    "min": float(series.min()),
                    "max": float(series.max()),
                    "median": float(series.median()),
                })
            
            if p_missing > 50:
                self.alerts.append(f"La columna '{col}' tiene más del 50% de valores faltantes.")
            if n_unique == 1:
                self.alerts.append(f"La columna '{col}' tiene un solo valor constante.")
            
            self.column_stats[col] = stats

    def clean_data(self, drop_duplicates=True, fill_na=False):
        if drop_duplicates:
            before = len(self.df)
            self.df.drop_duplicates(inplace=True)
            after = len(self.df)
            if before > after:
                self.alerts.append(f"Se eliminaron {before - after} filas duplicadas.")
        
        if fill_na:
            for col in self.df.columns:
                if self.df[col].isna().any():
                    if self._get_column_type(self.df[col]) == "numeric":
                        self.df[col] = self.df[col].fillna(self.df[col].median())
                    else:
                        mode_val = self.df[col].mode()
                        fill_val = mode_val[0] if not mode_val.empty else "Unknown"
                        self.df[col] = self.df[col].fillna(fill_val)
            self.alerts.append("Se imputaron valores faltantes.")

    def generate_report(self, output_path="datamatrix_report.html", title="Viewx DataMatrix Report"):
        self._analyze_columns()
        self.summary = {
            "n_rows": len(self.df),
            "n_cols": len(self.df.columns),
            "n_duplicates": int(self.df.duplicated().sum()),
            "n_missing_total": int(self.df.isna().sum().sum()),
            "p_missing_total": float((self.df.isna().sum().sum() / (len(self.df) * len(self.df.columns))) * 100),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # Bibliometría si es posible
        bib_results = self.bib_analyzer.analyze(self.df)
        
        # Construir HTML
        html = self._assemble_html(title, bib_results)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)

        import webbrowser
        webbrowser.open(output_path)
        return output_path

    def _assemble_html(self, title, bib_results):
        # Generar fragmentos de visualización
        overview_plots = self.visualizer.generate_overview_plots(self.summary, self.column_stats)
        col_plots = self.visualizer.generate_column_plots(self.df, self.column_stats)
        bib_plots = self.visualizer.generate_bibliometric_plots(bib_results) if bib_results else ""
        
        # Template HTML con Tabs y Estilo
        template = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {{ background-color: #f8f9fa; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }}
        .sidebar {{ background-color: #212529; color: white; min-height: 100vh; padding: 20px; }}
        .card {{ margin-bottom: 20px; border: none; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .stat-value {{ font-size: 2rem; font-weight: bold; color: #0d6efd; }}
        .alert-item {{ border-left: 4px solid #ffc107; background: #fff3cd; padding: 10px; margin-bottom: 5px; }}
        .nav-link {{ color: #adb5bd; }}
        .nav-link.active {{ color: white !important; font-weight: bold; border-left: 3px solid #0d6efd; }}
        .tab-content {{ padding: 20px; }}
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="row">
            <nav class="col-md-2 d-none d-md-block sidebar">
                <h4 class="mb-4">Viewx.DataMatrix</h4>
                <div class="nav flex-column nav-pills" id="v-pills-tab" role="tablist" aria-orientation="vertical">
                    <button class="nav-link active text-start" id="v-pills-overview-tab" data-bs-toggle="pill" data-bs-target="#v-pills-overview" type="button" role="tab">Resumen General</button>
                    <button class="nav-link text-start" id="v-pills-variables-tab" data-bs-toggle="pill" data-bs-target="#v-pills-variables" type="button" role="tab">Variables</button>
                    {"<button class='nav-link text-start' id='v-pills-bib-tab' data-bs-toggle='pill' data-bs-target='#v-pills-bib' type='button' role='tab'>Bibliometría</button>" if bib_results else ""}
                    <button class="nav-link text-start" id="v-pills-sample-tab" data-bs-toggle="pill" data-bs-target="#v-pills-sample" type="button" role="tab">Muestra de Datos</button>
                </div>
                <div class="mt-5 small text-muted">Generado el {self.summary['timestamp']}</div>
            </nav>

            <main class="col-md-10 tab-content">
                <!-- Overview Tab -->
                <div class="tab-pane fade show active" id="v-pills-overview" role="tabpanel">
                    <h2>Resumen del Dataset</h2>
                    <div class="row mt-4">
                        <div class="col-md-3"><div class="card p-3 text-center"><div class="stat-value">{self.summary['n_rows']}</div><div>Filas</div></div></div>
                        <div class="col-md-3"><div class="card p-3 text-center"><div class="stat-value">{self.summary['n_cols']}</div><div>Columnas</div></div></div>
                        <div class="col-md-3"><div class="card p-3 text-center"><div class="stat-value">{self.summary['n_missing_total']}</div><div>Nulos Totales</div></div></div>
                        <div class="col-md-3"><div class="card p-3 text-center"><div class="stat-value">{self.summary['n_duplicates']}</div><div>Duplicados</div></div></div>
                    </div>
                    
                    <div class="card p-4 mt-3">
                        <h4>Alertas</h4>
                        { "".join([f"<div class='alert-item'>{a}</div>" for a in self.alerts]) if self.alerts else "No se detectaron problemas críticos." }
                    </div>
                    {overview_plots}
                </div>

                <!-- Variables Tab -->
                <div class="tab-pane fade" id="v-pills-variables" role="tabpanel">
                    <h2>Análisis de Variables</h2>
                    {col_plots}
                </div>

                <!-- Bibliometrics Tab -->
                {f"<div class='tab-pane fade' id='v-pills-bib' role='tabpanel'><h2>Análisis Bibliométrico</h2>{bib_plots}</div>" if bib_results else ""}

                <!-- Sample Tab -->
                <div class="tab-pane fade" id="v-pills-sample" role="tabpanel">
                    <h2>Primeras 20 Filas</h2>
                    <div class="table-responsive card p-3">
                        {self.df.head(20).to_html(classes="table table-striped table-hover", index=False)}
                    </div>
                </div>
            </main>
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
        """
        return template
