import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import json

class Visualizer:
    def __init__(self):
        pass

    def _to_html(self, fig):
        return fig.to_html(full_html=False, include_plotlyjs=False)

    def generate_overview_plots(self, summary, column_stats):
        # Gráfico de tipos de variables
        types = [s['type'] for s in column_stats.values()]
        type_counts = pd.Series(types).value_counts()
        fig_types = px.pie(names=type_counts.index, values=type_counts.values, title="Distribución de Tipos de Datos", hole=0.4)
        
        # Gráfico de valores faltantes por columna
        missing = {col: s['p_missing'] for col, s in column_stats.items()}
        fig_missing = px.bar(x=list(missing.keys()), y=list(missing.values()), title="Porcentaje de Valores Faltantes por Columna", labels={'x': 'Columna', 'y': '% Faltante'})
        
        return f"""
        <div class="row mt-4">
            <div class="col-md-6"><div class="card p-3">{self._to_html(fig_types)}</div></div>
            <div class="col-md-6"><div class="card p-3">{self._to_html(fig_missing)}</div></div>
        </div>
        """

    def generate_column_plots(self, df, column_stats):
        html = ""
        for col, stats in column_stats.items():
            html += f"<div class='card p-4'><h4>{col} <small class='text-muted'>({stats['type']})</small></h4>"
            html += "<div class='row'><div class='col-md-4'>"
            html += f"<table class='table table-sm'><tr><td>Unicos</td><td>{stats['n_unique']}</td></tr>"
            html += f"<tr><td>Faltantes</td><td>{stats['n_missing']} ({stats['p_missing']:.1f}%)</td></tr>"
            if stats['type'] == 'numeric':
                html += f"<tr><td>Media</td><td>{stats['mean']:.2f}</td></tr>"
                html += f"<tr><td>Mediana</td><td>{stats['median']:.2f}</td></tr>"
                html += f"<tr><td>Desv. Est.</td><td>{stats['std']:.2f}</td></tr>"
            html += "</table></div>"
            
            # Gráfico por columna
            fig = None
            if stats['type'] == 'numeric':
                fig = px.histogram(df, x=col, title=f"Distribución de {col}")
            else:
                top_n = df[col].value_counts().head(10)
                fig = px.bar(x=top_n.index, y=top_n.values, title=f"Top 10 Valores de {col}")
            
            if fig:
                html += f"<div class='col-md-8'>{self._to_html(fig)}</div>"
            html += "</div></div>"
        return html

    def generate_bibliometric_plots(self, bib_results):
        html = "<div class='row'>"
        
        if 'annual_production' in bib_results:
            df_ap = bib_results['annual_production']
            fig_ap = px.line(df_ap, x='Year', y='Count', title="Producción Científica Anual", markers=True)
            html += f"<div class='col-md-12'><div class='card p-3'>{self._to_html(fig_ap)}</div></div>"
            
        if 'top_authors' in bib_results:
            df_au = bib_results['top_authors']
            fig_au = px.bar(df_au, x='Author', y='Count', title="Autores más Productivos", color='Count')
            html += f"<div class='col-md-6'><div class='card p-3'>{self._to_html(fig_au)}</div></div>"
            
        if 'top_sources' in bib_results:
            df_so = bib_results['top_sources']
            fig_so = px.pie(df_so, names='Source', values='Count', title="Fuentes Principales", hole=0.3)
            html += f"<div class='col-md-6'><div class='card p-3'>{self._to_html(fig_so)}</div></div>"

        html += "</div>"
        return html
