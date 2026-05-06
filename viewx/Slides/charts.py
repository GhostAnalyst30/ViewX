from .slides_engine import Presentation, Component

try:
    import plotly.graph_objects as go
    import plotly.express as px
    import plotly.io as pio
    import pandas as pd
    import numpy as np
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    print("⚠️ Plotly no instalado. Ejecuta: pip install plotly pandas numpy")


class PlotlyBase(Component):
    """Base para gráficos Plotly adaptados al tema actual"""
    
    def __init__(self):
        super().__init__()
        self._config = {'displayModeBar': False, 'responsive': True}
        self.styles.update({
            "width": "85%",
            "height": "400px",
            "transition": "all 0.3s ease"
        })
    
    def _get_theme_colors(self):
        """Obtiene colores del tema actual para plotly"""
        t = Presentation._get_theme()
        return {
            'bg': t['bg'],
            'surface': t['surface'],
            'primary': t['primary'],
            'accent': t['accent'],
            'text': t['text'],
            'muted': t['muted'],
            'grid': t['border'],
            'paper_bg': t['surface'],
            'plot_bg': t['surface']
        }
    
    def _apply_theme_to_fig(self, fig):
        """Aplica el tema actual a una figura plotly"""
        colors = self._get_theme_colors()
        
        fig.update_layout(
            paper_bgcolor=colors['paper_bg'],
            plot_bgcolor=colors['plot_bg'],
            font=dict(color=colors['text'], family="var(--font)"),
            title_font=dict(color=colors['primary']),
            legend=dict(
                font=dict(color=colors['text']),
                bgcolor=colors['surface'],
                bordercolor=colors['grid'],
                borderwidth=1
            ),
            xaxis=dict(
                gridcolor=colors['grid'],
                linecolor=colors['grid'],
                tickfont=dict(color=colors['muted']),
                title_font=dict(color=colors['primary'])
            ),
            yaxis=dict(
                gridcolor=colors['grid'],
                linecolor=colors['grid'],
                tickfont=dict(color=colors['muted']),
                title_font=dict(color=colors['primary'])
            ),
            hoverlabel=dict(
                bgcolor=colors['surface'],
                font_size=12,
                font_family="var(--font)"
            ),
            margin=dict(l=40, r=40, t=50, b=40)
        )
        return fig
    
    def _render(self):
        if not PLOTLY_AVAILABLE:
            return '<div class="c-component" style="padding:20px;text-align:center;background:#ff000020">⚠️ Plotly no instalado. Instalar con: pip install plotly pandas numpy</div>'
        
        html = pio.to_html(self._create_figure(), 
                          config=self._config,
                          full_html=False,
                          include_plotlyjs='cdn')
        return self._wrap_tooltip(f'<div class="c-component" style="{self._render_style()}">{html}</div>')
    
    def _create_figure(self):
        raise NotImplementedError


class ScatterPlot(PlotlyBase):
    """
    Gráfico de dispersión con Plotly
    
    Data puede ser:
    - DataFrame con columnas x, y
    - Lista de tuplas [(x1,y1), ...]
    - Lista de dicts [{"x":1, "y":2}, ...]
    """
    
    def __init__(self, data, x_col="x", y_col="y", color_col=None, size_col=None, 
                 title="", x_label="", y_label="", trendline=False):
        super().__init__()
        self.data = data
        self.x_col = x_col
        self.y_col = y_col
        self.color_col = color_col
        self.size_col = size_col
        self.title = title
        self.x_label = x_label
        self.y_label = y_label
        self.trendline = trendline
        self.styles.update({"width": "85%", "height": "450px"})
    
    def _parse_data(self):
        if PLOTLY_AVAILABLE and isinstance(self.data, pd.DataFrame):
            return self.data
        elif isinstance(self.data, list):
            if all(isinstance(p, (tuple, list)) and len(p) >= 2 for p in self.data):
                return pd.DataFrame([{self.x_col: p[0], self.y_col: p[1]} for p in self.data])
            elif all(isinstance(p, dict) for p in self.data):
                return pd.DataFrame(self.data)
        return pd.DataFrame()
    
    def _create_figure(self):
        df = self._parse_data()
        colors = self._get_theme_colors()
        
        if df.empty:
            return go.Figure()
        
        fig = px.scatter(
            df, x=self.x_col, y=self.y_col,
            color=self.color_col, size=self.size_col,
            title=self.title,
            labels={self.x_col: self.x_label or self.x_col, 
                   self.y_col: self.y_label or self.y_col},
            color_continuous_scale=[[0, colors['primary']], [1, colors['accent']]]
        )
        
        if self.trendline:
            fig.add_traces(px.scatter(df, x=self.x_col, y=self.y_col, trendline="ols").data[1])
        
        if self.color_col is None:
            fig.update_traces(marker=dict(color=colors['primary'], size=10, opacity=0.7))
        
        return self._apply_theme_to_fig(fig)


class PieChart(PlotlyBase):
    """
    Gráfico de pastel con Plotly
    
    Data puede ser:
    - Diccionario: {"label1": value1, "label2": value2}
    - DataFrame con columnas 'label' y 'value'
    - Lista de dicts [{"label": "A", "value": 10}, ...]
    """
    
    def __init__(self, data, label_col="label", value_col="value", title="", hole=0, pull=None):
        super().__init__()
        self.data = data
        self.label_col = label_col
        self.value_col = value_col
        self.title = title
        self.hole = hole
        self.pull = pull or []
        self.styles.update({"width": "500px", "height": "450px"})
    
    def _parse_data(self):
        if PLOTLY_AVAILABLE and isinstance(self.data, pd.DataFrame):
            return self.data
        elif isinstance(self.data, dict):
            return pd.DataFrame(list(self.data.items()), columns=[self.label_col, self.value_col])
        elif isinstance(self.data, list) and all(isinstance(d, dict) for d in self.data):
            return pd.DataFrame(self.data)
        return pd.DataFrame()
    
    def _create_figure(self):
        df = self._parse_data()
        colors = self._get_theme_colors()
        
        if df.empty:
            return go.Figure()
        
        fig = go.Figure(data=[go.Pie(
            labels=df[self.label_col], values=df[self.value_col],
            hole=self.hole, pull=self.pull,
            marker=dict(colors=px.colors.qualitative.Set3),
            textinfo='label+percent', textposition='auto',
            hoverinfo='label+value+percent',
            domain=dict(x=[0, 1], y=[0, 1])
        )])
        
        fig.update_layout(
            title=self.title or "",
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5)
        )
        
        return self._apply_theme_to_fig(fig)


class BarChart(PlotlyBase):
    """
    Gráfico de barras con Plotly
    
    Data puede ser:
    - DataFrame
    - Diccionario de series: {"Serie1": [10,20,30], ...}
    - Lista de valores
    """
    
    def __init__(self, data, x_labels=None, title="", x_label="", y_label="", barmode='group', horizontal=False):
        super().__init__()
        self.data = data
        self.x_labels = x_labels
        self.title = title
        self.x_label = x_label
        self.y_label = y_label
        self.barmode = barmode
        self.horizontal = horizontal
        self.styles.update({"width": "85%", "height": "450px"})
    
    def _parse_data(self):
        if PLOTLY_AVAILABLE and isinstance(self.data, pd.DataFrame):
            return self.data
        elif isinstance(self.data, dict):
            max_len = max(len(v) for v in self.data.values()) if self.data else 0
            df_dict = {}
            for series_name, values in self.data.items():
                df_dict[series_name] = values + [None] * (max_len - len(values))
            return pd.DataFrame(df_dict)
        elif isinstance(self.data, list):
            return pd.DataFrame({"value": self.data})
        return pd.DataFrame()
    
    def _create_figure(self):
        df = self._parse_data()
        colors = self._get_theme_colors()
        
        if df.empty:
            return go.Figure()
        
        if len(df.columns) == 1 and 'value' in df.columns and self.x_labels:
            # Datos simples
            fig = go.Figure(data=[go.Bar(
                x=self.x_labels, y=df['value'],
                marker_color=colors['primary'],
                orientation='h' if self.horizontal else 'v'
            )])
        else:
            # Múltiples series
            fig = go.Figure()
            color_list = px.colors.qualitative.Set3
            for i, col in enumerate(df.columns):
                fig.add_trace(go.Bar(
                    name=col, x=self.x_labels or df.index, y=df[col],
                    marker_color=color_list[i % len(color_list)],
                    orientation='h' if self.horizontal else 'v'
                ))
        
        fig.update_layout(
            title=self.title,
            xaxis_title=self.x_label,
            yaxis_title=self.y_label,
            barmode=self.barmode,
            bargap=0.15
        )
        
        return self._apply_theme_to_fig(fig)


class BoxPlot(PlotlyBase):
    """
    Diagrama de caja con Plotly
    
    Data puede ser:
    - DataFrame con varias columnas numéricas
    - Lista de listas [[valores1], [valores2], ...]
    - Diccionario {"Grupo1": [valores], ...}
    """
    
    def __init__(self, data, labels=None, title="", x_label="", y_label="", points='outliers'):
        super().__init__()
        self.data = data
        self.labels = labels
        self.title = title
        self.x_label = x_label
        self.y_label = y_label
        self.points = points
        self.styles.update({"width": "85%", "height": "450px"})
    
    def _parse_data(self):
        if PLOTLY_AVAILABLE and isinstance(self.data, pd.DataFrame):
            return self.data
        elif isinstance(self.data, dict):
            return pd.DataFrame([{k: v for v in vals} for k, vals in self.data.items()])
        elif isinstance(self.data, list):
            if self.labels:
                return pd.DataFrame({self.labels[i]: vals for i, vals in enumerate(self.data)})
            return pd.DataFrame({f"Grupo {i+1}": vals for i, vals in enumerate(self.data)})
        return pd.DataFrame()
    
    def _create_figure(self):
        df = self._parse_data()
        colors = self._get_theme_colors()
        
        if df.empty:
            return go.Figure()
        
        fig = go.Figure()
        color_list = px.colors.qualitative.Set3
        
        for i, col in enumerate(df.columns):
            if df[col].dropna().tolist():
                fig.add_trace(go.Box(
                    y=df[col].dropna(), name=col,
                    marker_color=color_list[i % len(color_list)],
                    boxmean='sd', boxpoints=self.points,
                    line=dict(color=colors['primary'], width=2)
                ))
        
        fig.update_layout(
            title=self.title,
            xaxis_title=self.x_label,
            yaxis_title=self.y_label,
            showlegend=True
        )
        
        return self._apply_theme_to_fig(fig)


class Histogram(PlotlyBase):
    """Histograma interactivo con Plotly"""
    
    def __init__(self, data, column=None, bins=30, title="", x_label="", y_label="", color=None):
        super().__init__()
        self.data = data
        self.column = column
        self.bins = bins
        self.title = title
        self.x_label = x_label
        self.y_label = y_label
        self.color = color
        self.styles.update({"width": "85%", "height": "450px"})
    
    def _parse_data(self):
        if PLOTLY_AVAILABLE and isinstance(self.data, pd.DataFrame):
            return self.data[self.column] if self.column else self.data
        elif isinstance(self.data, (list, np.ndarray)):
            return pd.Series(self.data)
        return pd.Series()
    
    def _create_figure(self):
        series = self._parse_data()
        colors = self._get_theme_colors()
        
        if series.empty:
            return go.Figure()
        
        fig = go.Figure(data=[go.Histogram(
            x=series, nbinsx=self.bins,
            marker_color=self.color or colors['primary'],
            opacity=0.8
        )])
        
        fig.update_layout(
            title=self.title,
            xaxis_title=self.x_label or (self.column if self.column else "Valor"),
            yaxis_title=self.y_label or "Frecuencia",
            bargap=0.05
        )
        
        return self._apply_theme_to_fig(fig)


class LineChart(PlotlyBase):
    """Gráfico de líneas interactivo"""
    
    def __init__(self, data, x_col=None, y_cols=None, title="", x_label="", y_label=""):
        super().__init__()
        self.data = data
        self.x_col = x_col
        self.y_cols = y_cols
        self.title = title
        self.x_label = x_label
        self.y_label = y_label
        self.styles.update({"width": "85%", "height": "450px"})
    
    def _parse_data(self):
        if PLOTLY_AVAILABLE and isinstance(self.data, pd.DataFrame):
            return self.data
        return pd.DataFrame()
    
    def _create_figure(self):
        df = self._parse_data()
        colors = self._get_theme_colors()
        
        if df.empty:
            return go.Figure()
        
        fig = go.Figure()
        color_list = px.colors.qualitative.Set3
        
        if self.x_col:
            x_vals = df[self.x_col]
            y_cols = self.y_cols or [c for c in df.columns if c != self.x_col]
            
            for i, col in enumerate(y_cols):
                fig.add_trace(go.Scatter(
                    x=x_vals, y=df[col], mode='lines+markers',
                    name=col, line=dict(width=3, color=color_list[i % len(color_list)]),
                    marker=dict(size=6)
                ))
        else:
            # Si no hay x_col, usar índice
            for i, col in enumerate(df.columns):
                fig.add_trace(go.Scatter(
                    y=df[col], mode='lines+markers',
                    name=col, line=dict(width=3, color=color_list[i % len(color_list)]),
                    marker=dict(size=6)
                ))
        
        fig.update_layout(
            title=self.title,
            xaxis_title=self.x_label,
            yaxis_title=self.y_label,
            hovermode='x unified'
        )
        
        return self._apply_theme_to_fig(fig)