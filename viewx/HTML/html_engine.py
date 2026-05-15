import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import uuid
from typing import Optional, Tuple, Union, List, Dict

class ThemeManager:
    def __init__(self, theme_name: Union[int, str] = "corporate_blue"):
        self.themes = {
            "corporate_blue": {
                "id": 0, "name": "Corporate Blue",
                "bg_page": "#F3F4F6", "bg_card": "#FFFFFF", "accent": "#0078D4", 
                "text_primary": "#252423", "text_secondary": "#605E5C", "shadow": "0 4px 12px rgba(0,0,0,0.08)"
            },
            "dark_enterprise": {
                "id": 1, "name": "Dark Enterprise",
                "bg_page": "#111111", "bg_card": "#1E1E1E", "accent": "#0078D4", 
                "text_primary": "#F3F2F1", "text_secondary": "#C8C6C4", "shadow": "0 4px 20px rgba(0,0,0,0.4)"
            },
            "modern_green": {
                "id": 2, "name": "Modern Green",
                "bg_page": "#F0F5F0", "bg_card": "#FFFFFF", "accent": "#107C10", 
                "text_primary": "#252423", "text_secondary": "#605E5C", "shadow": "0 4px 12px rgba(0,0,0,0.08)"
            },
            "void_indigo": {
                "id": 3, "name": "Void Indigo",
                "bg_page": "#07080F", "bg_card": "#0F1117", "accent": "#5865F2", 
                "text_primary": "#E2E5FF", "text_secondary": "#A0A8E0", "shadow": "0 8px 32px rgba(0,0,0,0.2)"
            },
            "glass_ocean": {
                "id": 4, "name": "Glass Ocean",
                "bg_page": "linear-gradient(135deg, #0f2027, #203a43, #2c5364)", 
                "bg_card": "rgba(255, 255, 255, 0.05)", "accent": "#00C2CB", 
                "text_primary": "#FFFFFF", "text_secondary": "#B0D8DA", "shadow": "0 8px 32px rgba(0,0,0,0.2)",
                "glass": True
            },
            "cyberpunk_neon": {
                "id": 5, "name": "Cyberpunk Neon",
                "bg_page": "#050505", "bg_card": "#0D0214", "accent": "#FF00FF", 
                "text_primary": "#00FFFF", "text_secondary": "#00CCCC", "shadow": "0 0 15px rgba(255,0,255,0.3)",
                "border_glow": True
            }
        }
        
        self.id_map = {t['id']: k for k, t in self.themes.items()}
        self.set_theme(theme_name)

    def set_theme(self, theme_name: Union[int, str]):
        if isinstance(theme_name, int):
            theme_name = self.id_map.get(theme_name, "corporate_blue")
        
        if theme_name not in self.themes:
            self.current_theme_name = "corporate_blue"
        else:
            self.current_theme_name = theme_name
            
        self.current_theme = self.themes[self.current_theme_name]

    def get_colors(self):
        t = self.current_theme
        return (t["bg_page"], t["bg_card"], t["accent"], t["text_primary"])

    def get_global_css(self):
        t = self.current_theme
        bg_page, bg_card, accent, text_primary = self.get_colors()
        text_secondary = t["text_secondary"]
        shadow = t["shadow"]
        
        css = f"""
        :root {{
            --vx-bg-page: {bg_page};
            --vx-bg-card: {bg_card};
            --vx-accent: {accent};
            --vx-text-primary: {text_primary};
            --vx-text-secondary: {text_secondary};
            --vx-card-radius: 12px;
            --vx-shadow: {shadow};
            --vx-transition: all 0.3s cubic-bezier(.16,1,.3,1);
        }}
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        body {{
            background: var(--vx-bg-page);
            color: var(--vx-text-primary);
            font-family: 'Segoe UI', 'Inter', system-ui, sans-serif;
            overflow: hidden;
            height: 100vh;
            width: 100vw;
        }}
        .vx-card {{
            background: var(--vx-bg-card);
            border-radius: var(--vx-card-radius);
            box-shadow: var(--vx-shadow);
            transition: var(--vx-transition);
            overflow: auto;
            border: 1px solid rgba(0,0,0,0.05);
        }}
        .vx-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.12);
        }}
        
        /* Asegurar que los gráficos Plotly sean 100% responsivos */
        .plotly-graph-div {{
            width: 100% !important;
            height: 100% !important;
        }}
        
        .js-plotly-plot, .plot-container {{
            width: 100% !important;
            height: 100% !important;
        }}
        
        /* Scroll interno elegante */
        .vx-card::-webkit-scrollbar {{
            width: 6px;
            height: 6px;
        }}
        .vx-card::-webkit-scrollbar-track {{
            background: transparent;
        }}
        .vx-card::-webkit-scrollbar-thumb {{
            background: {accent}55;
            border-radius: 3px;
        }}
        """
        
        if t.get("glass"):
            css += """
            .vx-card {
                backdrop-filter: blur(16px) saturate(180%);
                -webkit-backdrop-filter: blur(16px) saturate(180%);
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
            """
        
        if t.get("border_glow"):
            css += f"""
            .vx-card {{
                border: 1px solid {accent}88;
                box-shadow: 0 0 20px {accent}33;
            }}
            """
            
        return css


class HTML:
    def __init__(
        self,
        title: str = "ViewX Dashboard",
        theme: Union[int, str] = "corporate_blue",
        cols: int = 12,
        rows: int = 12,
        gap: int = 16,
        padding: int = 24,
        navbar: dict = None,
        authors: str | List[str] = None
    ):
        self.title = title
        self.theme_manager = ThemeManager(theme)
        self.cols = cols
        self.rows = rows
        self.gap = gap
        self.padding = padding
        self.navbar = navbar
        
        if isinstance(authors, list):
            # Soporta tanto strings como dicts {"name": ..., "email": ...}
            self.authors = [
                a if isinstance(a, dict) else {"name": a, "email": None}
                for a in authors
            ]
        elif isinstance(authors, str):
            self.authors = [{"name": authors, "email": None}]
        else:
            self.authors = []

        self.grid_css = []
        self.components_html = []
        self._component_counter = 0
        
    def _register_block(self, component_id: str, row: int, col: int, height: int, width: int):
        css = f".{component_id} {{ grid-area: {row} / {col} / {row + height} / {col + width}; }}"
        self.grid_css.append(css)

    def _uid(self) -> str:
        self._component_counter += 1
        return f"comp_{self._component_counter}_{uuid.uuid4().hex[:6]}"

    def add_valuebox(self, title: str, value, icon: str = "📊", color: str = None, 
                     row: int = 1, col: int = 1, height: int = 2, width: int = 3):
        """Añade una tarjeta con valor destacado (KPI)"""
        uid = self._uid()
        self._register_block(uid, row, col, height, width)
        
        bg_page, bg_card, accent, text = self.theme_manager.get_colors()
        box_color = color or accent
        
        html = f"""
        <style>
            .vb-{uid} {{
                padding: 20px;
                display: flex;
                align-items: center;
                gap: 16px;
                border-left: 6px solid {box_color};
                height: 100%;
            }}
            .vb-icon-{uid} {{ 
                font-size: 2.5rem; 
                color: {box_color}; 
                opacity: 0.9;
                background: {box_color}15;
                width: 56px; height: 56px;
                display: flex; align-items: center; justify-content: center;
                border-radius: 12px;
            }}
            .vb-content-{uid} {{ flex: 1; }}
            .vb-title-{uid} {{ 
                font-size: 0.8rem; 
                color: var(--vx-text-secondary); 
                text-transform: uppercase; 
                font-weight: 700;
                letter-spacing: 0.5px;
                margin-bottom: 4px;
            }}
            .vb-val-{uid} {{ 
                font-size: 1.8rem; 
                font-weight: 800; 
                color: var(--vx-text-primary); 
                line-height: 1;
            }}
            @media (max-height: 700px) {{
                .vb-{uid} {{ padding: 12px; }}
                .vb-icon-{uid} {{ font-size: 1.8rem; width: 44px; height: 44px; }}
                .vb-val-{uid} {{ font-size: 1.4rem; }}
            }}
        </style>
        <div class="vx-card vb-{uid} {uid}">
            <div class="vb-icon-{uid}">{icon}</div>
            <div class="vb-content-{uid}">
                <div class="vb-title-{uid}">{title}</div>
                <div class="vb-val-{uid}">{value}</div>
            </div>
        </div>
        """
        self.components_html.append(html)
        return self
    
    def _hex_to_rgba(self, hex_color: str, alpha: float = 0.13) -> str:
        """Convierte hex a rgba para Plotly"""
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        return f"rgba({r}, {g}, {b}, {alpha})"

    def add_chart(self, data=None, fig=None, chart_type="line", x=None, y=None, z=None,
                    title: str = "", row: int = 1, col: int = 1, height: int = 6, width: int = 6):
            """
            Añade un gráfico interactivo que se autoajusta al zoom/redimensionamiento.
            
            Modos de uso:
            1. Pasar fig (figura Plotly ya creada)
            2. Pasar data + x + y (+ opcional chart_type)
            """
            uid = self._uid()
            self._register_block(uid, row, col, height, width)
            
            bg_page, bg_card, accent, text = self.theme_manager.get_colors()
            
            # Si se pasa una figura, usarla directamente
            if fig is not None:
                chart_fig = fig
            elif data is not None and x is not None and y is not None:
                # Crear figura automática
                if chart_type == "line":
                    chart_fig = px.line(data, x=x, y=y, title=title)
                elif chart_type == "bar":
                    chart_fig = px.bar(data, x=x, y=y, title=title)
                elif chart_type == "scatter":
                    chart_fig = px.scatter(data, x=x, y=y, title=title, color=z if z else None)
                elif chart_type == "area":
                    chart_fig = px.area(data, x=x, y=y, title=title)
                else:
                    chart_fig = px.line(data, x=x, y=y, title=title)
            else:
                raise ValueError("Debes proporcionar fig o (data + x + y)")
            
            # Configurar el estilo - CLAVE PARA AUTO-REDIMENSIÓN
            chart_fig.update_layout(
                autosize=True,  # Permite redimensionamiento automático
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color=text,
                title_font_color=accent,
                title_font_size=14,
                margin=dict(l=40, r=20, t=40, b=30),
                font_family="'Segoe UI', sans-serif",
                hovermode='closest',
                height=None,  # Sin altura fija
                width=None    # Sin ancho fijo
            )
            
            # Configurar ejes
            grid_color = self._hex_to_rgba(text, 0.13)
            chart_fig.update_xaxes(
                gridcolor=grid_color,
                zerolinecolor=grid_color,
                showgrid=True
            )
            chart_fig.update_yaxes(
                gridcolor=grid_color,
                zerolinecolor=grid_color,
                showgrid=True
            )
            
            # Configuración responsive mejorada
            plot_html = chart_fig.to_html(
                full_html=False, 
                include_plotlyjs='cdn', 
                config={
                    'displaylogo': False, 
                    'responsive': True,
                    'autosizable': True,
                    'frameMargins': 0
                }
            )
            
            html = f"""
                    <style>
                        .plot-card-{uid} {{
                            padding: 12px;
                            display: grid;
                            grid-template-rows: auto 1fr;
                            height: 100%;
                            width: 100%;
                            overflow: hidden;
                            gap: 8px;
                        }}
                        .plot-card-{uid} h4 {{ 
                            margin: 0; 
                            color: var(--vx-text-primary); 
                            font-weight: 600;
                            font-size: 0.95rem;
                            border-bottom: 2px solid {accent}33;
                            padding-bottom: 6px;
                        }}
                        .plot-container-{uid} {{ 
                            position: relative;
                            width: 100%;
                            height: 100%;
                            min-height: 0;
                            overflow: hidden;
                        }}
                        /* Quitar position: absolute del graph-div */
                        .plot-container-{uid} .plotly-graph-div {{
                            width: 100% !important;
                            height: 100% !important;
                            /* sin position: absolute */
                        }}
                        .plot-container-{uid} .js-plotly-plot {{
                            width: 100% !important;
                            height: 100% !important;
                        }}
                    </style>

                    <div class="vx-card plot-card-{uid} {uid}">
                        {f'<h4>{title}</h4>' if title else ""}
                        <div class="plot-container-{uid}">{plot_html}</div>
                    </div>

                    <!-- Script DESPUÉS del div para que container no sea null -->
                    <script>
                    (function() {{
                        var container = document.querySelector('.plot-container-{uid}');
                        var resizeTimeout;

                        function forceResize_{uid}() {{
                            if (!container) return;
                            var plotDiv = container.querySelector('.plotly-graph-div');
                            if (plotDiv && window.Plotly) {{
                                // Subir al padre para leer dimensiones reales
                                var card = container.closest('.plot-card-{uid}');
                                var ref = card || container;
                                var w = ref.clientWidth;
                                var h = container.clientHeight;   // altura sigue viniendo del container
                                if (w > 0 && h > 0) {{
                                    Plotly.relayout(plotDiv, {{ width: w, height: h }});
                                }}
                            }}
                        }}

                        // Reintentar hasta que Plotly esté listo
                        function waitAndResize_{uid}(attempts) {{
                            var plotDiv = container ? container.querySelector('.plotly-graph-div') : null;
                            if (plotDiv && window.Plotly) {{
                                forceResize_{uid}();
                            }} else if (attempts > 0) {{
                                setTimeout(function() {{ waitAndResize_{uid}(attempts - 1); }}, 100);
                            }}
                        }}

                        if (window.ResizeObserver && container) {{
                            new ResizeObserver(function() {{
                                clearTimeout(resizeTimeout);
                                resizeTimeout = setTimeout(forceResize_{uid}, 50);
                            }}).observe(container);
                        }}

                        window.addEventListener('resize', function() {{
                            clearTimeout(resizeTimeout);
                            resizeTimeout = setTimeout(forceResize_{uid}, 100);
                        }});

                        document.addEventListener('keydown', function(e) {{
                            if ((e.ctrlKey || e.metaKey) && ['+','-','0','='].includes(e.key)) {{
                                clearTimeout(resizeTimeout);
                                resizeTimeout = setTimeout(forceResize_{uid}, 150);
                            }}
                        }});

                        // Esperar hasta 20 intentos × 100ms = 2 segundos
                        waitAndResize_{uid}(20);
                    }})();
                    </script>
                    """
            self.components_html.append(html)
            return self


    def add_table(self, df: pd.DataFrame, row: int = 1, col: int = 1, 
                  height: int = 4, width: int = 6, title: str = ""):
        """Añade una tabla interactiva con scroll interno"""
        uid = self._uid()
        self._register_block(uid, row, col, height, width)
        
        bg_page, bg_card, accent, text = self.theme_manager.get_colors()
        table_html = df.to_html(classes=f"vxt-{uid}", border=0, index=False, max_rows=100)
        
        html = f"""
        <style>
            .table-card-{uid} {{
                padding: 16px;
                display: flex;
                flex-direction: column;
                height: 100%;
            }}
            .table-card-{uid} h4 {{ 
                color: var(--vx-text-primary); 
                margin: 0 0 12px 0; 
                font-weight: 600;
                font-size: 0.95rem;
                flex-shrink: 0;
            }}
            .table-container-{uid} {{ 
                overflow: auto; 
                flex: 1; 
                scrollbar-width: thin;
            }}
            .vxt-{uid} {{
                width: 100%;
                border-collapse: collapse;
                font-size: 0.8rem;
            }}
            .vxt-{uid} th {{
                background: {accent}11;
                color: {accent};
                padding: 10px 8px;
                text-align: left;
                font-weight: 700;
                position: sticky; top: 0;
                border-bottom: 2px solid {accent}44;
            }}
            .vxt-{uid} td {{
                padding: 8px;
                border-bottom: 1px solid var(--vx-text-secondary)22;
                color: var(--vx-text-primary);
            }}
            .vxt-{uid} tr:hover {{ background: {accent}08; }}
        </style>
        <div class="vx-card table-card-{uid} {uid}">
            {f"<h4>{title}</h4>" if title else ""}
            <div class="table-container-{uid}">{table_html}</div>
        </div>
        """
        self.components_html.append(html)
        return self

    def add_text(self, content: str, row: int = 1, col: int = 1, height: int = 2, width: int = 6):
        """Añade una tarjeta de texto"""
        uid = self._uid()
        self._register_block(uid, row, col, height, width)
        
        html = f"""
        <style>
            .text-card-{uid} {{
                padding: 20px;
                line-height: 1.5;
                color: var(--vx-text-primary);
                height: 100%;
                overflow: auto;
                font-size: 0.9rem;
            }}
            .text-card-{uid} h2, .text-card-{uid} h3 {{ 
                color: var(--vx-accent); 
                margin-top: 0; 
                font-weight: 700;
            }}
        </style>
        <div class="vx-card text-card-{uid} {uid}">
            {content}
        </div>
        """
        self.components_html.append(html)
        return self

    def _build_navbar(self, title_link = "#") -> str:
        if not self.navbar: return ""
        bg_page, bg_card, accent, text = self.theme_manager.get_colors()
        
        items_html = "".join([f'<a href="{i["link"]}" class="nav-link">{i["label"]}</a>' for i in self.navbar.get("items", [])])

        if self.authors:
            authors_html = ", ".join([
                f'<a href="mailto:{a["email"]}" class="nav-author nav-author-link">{a["name"]}</a>'
                if a["email"]
                else f'<span class="nav-author">{a["name"]}</span>'
                for a in self.authors
            ])
            author_block = f'<div class="nav-author-wrap">by {authors_html}</div>'
        else:
            author_block = ""
        
        return f"""
        <style>
            .vx-navbar {{
                position: fixed; top: 0; left: 0; right: 0; height: 56px;
                background: {bg_card};
                display: flex; align-items: center; justify-content: space-between;
                padding: 0 24px; z-index: 1000; 
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                border-bottom: 2px solid {accent};
            }}
            .nav-brand {{ 
                font-weight: 800; font-size: 1.3rem; 
                color: {accent}; text-decoration: none; 
                letter-spacing: -0.5px;
            }}
            .nav-author {{
                font-size: 0.72rem;
                color: var(--vx-text-secondary);
                font-weight: 500;
                letter-spacing: 0.2px;
            }}
            .nav-links {{ display:flex; gap: 20px; }}
            .nav-link {{ 
                color: var(--vx-text-primary); 
                text-decoration: none; 
                font-weight: 600; 
                font-size: 0.85rem;
                opacity: 0.8; transition: var(--vx-transition); 
            }}
            .nav-link:hover {{ opacity: 1; color: {accent}; }}
            .nav-author-wrap {{
                font-size: 0.72rem;
                color: var(--vx-text-secondary);
                font-weight: 500;
            }}
            .nav-author-link {{
                color: {accent};
                text-decoration: none;
                transition: var(--vx-transition);
            }}
            .nav-author-link:hover {{
                text-decoration: underline;
                opacity: 0.8;
            }}
        </style>
        <nav class="vx-navbar">
            <div style="display:flex; flex-direction:column; gap:1px;">
                <a href="{title_link}" class="nav-brand">{self.navbar.get("title", self.title)}</a>
                {author_block}
            </div>
            <div class="nav-links">{items_html}</div>
        </nav>
        """

    def generate(self, filename: str = "dashboard.html"):
        """Genera el dashboard estático sin scrollbar global"""
        bg_page, bg_card, accent, text = self.theme_manager.get_colors()
        
        full_html = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <title>{self.title}</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1, user-scalable=no">
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
            <style>
                {self.theme_manager.get_global_css()}
                
                .dashboard-container {{
                    padding: {self.padding}px;
                    padding-top: {self.padding + 56 if self.navbar else self.padding}px;
                    height: 100vh;
                    width: 100vw;
                    display: flex;
                    flex-direction: column;
                }}
                
                .vx-grid {{
                    display: grid;
                    grid-template-columns: repeat({self.cols}, 1fr);
                    grid-template-rows: repeat({self.rows}, 1fr);
                    gap: {self.gap}px;
                    flex: 1;
                    min-height: 0;  /* Importante para evitar overflow */
                }}
                
                {chr(10).join(self.grid_css)}
                
                .vx-card {{
                    animation: fadeInUp 0.4s ease-out both;
                }}
                
                @keyframes fadeInUp {{
                    from {{ opacity: 0; transform: translateY(10px); }}
                    to {{ opacity: 1; transform: translateY(0); }}
                }}
                
                /* Animación secuencial */
                {chr(10).join([f".vx-card:nth-child({i+1}) {{ animation-delay: {i*0.05}s; }}" for i in range(len(self.components_html))])}
                
                /* Responsive: en pantallas pequeñas se apilan */
                @media (max-width: 768px) {{
                    .vx-grid {{
                        display: flex;
                        flex-direction: column;
                        gap: {self.gap}px;
                        overflow-y: auto;
                    }}
                    .vx-card {{
                        min-height: 250px;
                        flex-shrink: 0;
                    }}
                    body {{
                        overflow-y: auto;
                    }}
                }}
            </style>
        </head>
        <body>
            {self._build_navbar()}
            <div class="dashboard-container">
                <div class="vx-grid">
                    {"".join(self.components_html)}
                </div>
            </div>
        </body>
        </html>
        """
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(full_html)
        print(f"✅ Dashboard generado: {os.path.abspath(filename)}")

        import webbrowser
        webbrowser.open(filename)
        return filename
    
    @classmethod
    def auto_generate(
        cls,
        data: pd.DataFrame,
        columns: List[str] = None,
        template: Union[int, str] = "corporate_blue",
        title: str = "Auto Dashboard",
        filename: str = "auto_dashboard.html",
        navbar: dict = None,
        authors=None,
        layout: Union[str, List[dict]] = "auto"
    ) -> str:

        # ── 1. Seleccionar columnas ──────────────────────────────────────────
        cols_to_use = list(columns) if columns is not None else list(data.columns)
        missing = [c for c in cols_to_use if c not in data.columns]
        if missing:
            raise KeyError(
                f"\n❌ Columnas no encontradas: {missing}"
                f"\n✅ Columnas disponibles: {list(data.columns)}"
                f"\n💡 Tip: revisa mayúsculas, espacios o caracteres especiales."
            )

        df = data[cols_to_use].copy()

        # ── 2. Parseo automático ─────────────────────────────────────────────
        def try_parse_col(series: pd.Series) -> pd.Series:
            if not pd.api.types.is_object_dtype(series):
                return series

            numeric_attempt = (
                series.astype(str)
                    .str.strip()
                    .str.replace(r"[$€£¥%\s]", "", regex=True)
                    .str.replace(r"(?<=\d),(?=\d{3})", "", regex=True)
            )
            converted = pd.to_numeric(numeric_attempt, errors="coerce")
            ratio_numeric = converted.notna().sum() / max(len(series.dropna()), 1)
            if ratio_numeric >= 0.8:
                return converted

            try:
                converted_dt = pd.to_datetime(series, errors="coerce")
                ratio_dt = converted_dt.notna().sum() / max(len(series.dropna()), 1)
                if ratio_dt >= 0.8:
                    return converted_dt
            except Exception:
                pass

            return series

        for col in cols_to_use:
            df[col] = try_parse_col(df[col])

        # ── 3. Clasificar columnas ───────────────────────────────────────────
        def classify_col(series: pd.Series):
            if pd.api.types.is_datetime64_any_dtype(series):
                return "datetime"
            if pd.api.types.is_bool_dtype(series):
                return "boolean"
            if pd.api.types.is_numeric_dtype(series):
                return "numeric"
            cardinality = series.nunique()
            return "categorical" if cardinality / max(len(series), 1) < 0.5 else "text"

        col_types    = {c: classify_col(df[c]) for c in cols_to_use}
        numerics     = [c for c, t in col_types.items() if t == "numeric"]
        categoricals = [c for c, t in col_types.items() if t == "categorical"]
        datetimes    = [c for c, t in col_types.items() if t == "datetime"]
        booleans     = [c for c, t in col_types.items() if t == "boolean"]

        for c in datetimes:
            df[c] = pd.to_datetime(df[c])

        # ── 4. Planificar KPIs ───────────────────────────────────────────────
        ICONS = [
            "\U0001F4CA",
            "\U0001F4B0",
            "\U0001F4C8",
            "\U0001F522",
            "\U0001F3AF",
            "\U000026A1",
            "\U0001F4E6",
            "\U0001F3C6",
        ]
        planned = []
        for i, num_col in enumerate(numerics):
            total = df[num_col].sum()
            fmt   = lambda v: f"{v:,.0f}" if abs(v) >= 1000 else f"{v:,.2f}"
            planned.append(("kpi", num_col, fmt(total), ICONS[i % len(ICONS)]))

        # ── 5. Planificar gráficos ───────────────────────────────────────────
        charts = []

        if datetimes and numerics:
            date_col = datetimes[0]
            for num_col in numerics:
                agg = df.groupby(date_col)[num_col].sum().reset_index()
                fig = px.line(agg, x=date_col, y=num_col, markers=True)
                charts.append(("chart", fig, f"{num_col} en el tiempo"))

        if categoricals and numerics:
            cat_col = categoricals[0]
            num_col = numerics[0]
            agg = df.groupby(cat_col)[num_col].sum().nlargest(15).reset_index()
            fig = px.bar(agg, x=cat_col, y=num_col, color=cat_col)
            charts.append(("chart", fig, f"{num_col} por {cat_col}"))

        if len(numerics) >= 2:
            color_col = categoricals[0] if categoricals else None
            fig = px.scatter(df, x=numerics[0], y=numerics[1],
                            color=color_col, opacity=0.7)
            charts.append(("chart", fig, f"{numerics[0]} vs {numerics[1]}"))

        if categoricals and not numerics:
            cat_col = categoricals[0]
            counts  = df[cat_col].value_counts().head(10).reset_index()
            counts.columns = [cat_col, "count"]
            fig = px.pie(counts, names=cat_col, values="count", hole=0.4)
            charts.append(("chart", fig, f"Distribución de {cat_col}"))

        for bool_col in booleans:
            counts = df[bool_col].value_counts().reset_index()
            counts.columns = [bool_col, "count"]
            fig = px.pie(counts, names=bool_col, values="count", hole=0.35)
            charts.append(("chart", fig, f"Distribución de {bool_col}"))

        if len(numerics) >= 3:
            corr = df[numerics].corr()
            fig  = px.imshow(corr, text_auto=".2f", color_continuous_scale="RdBu_r",
                            zmin=-1, zmax=1)
            charts.append(("chart", fig, "Correlación entre variables"))

        show_table = len(df) > 0

        # ── 6. Calcular dimensiones base ─────────────────────────────────────
        COLS             = 12
        kpi_height       = 2
        chart_height     = 5
        table_rows       = 4
        MAX_KPIS_PER_ROW = 6

        n_kpis   = len(planned)
        n_charts = len(charts)

        kpi_per_row      = min(n_kpis, MAX_KPIS_PER_ROW) if n_kpis else 1
        actual_kpi_width = COLS // kpi_per_row
        kpi_rows_needed  = -(-n_kpis // MAX_KPIS_PER_ROW) if n_kpis else 0
        kpi_rows_used    = kpi_rows_needed * kpi_height

        chart_cols       = 6 if n_charts > 1 else 12
        chart_rows_total = -(-n_charts // 2) * chart_height

        table_rows_used  = table_rows if show_table else 0

        # ── 6b. Resolver layout ──────────────────────────────────────────────
        PRESETS = {
            "kpi_focus": [
                *[{"type": "kpi", "index": i,
                "row": 1 + (i // 4) * 3, "col": (i % 4) * 3 + 1,
                "height": 3, "width": 3}
                for i in range(n_kpis)],
                *[{"type": "chart", "index": i,
                "row": 1 + (-(-n_kpis // 4)) * 3 + (i // 2) * 5,
                "col": (i % 2) * 6 + 1, "height": 5, "width": 6}
                for i in range(n_charts)],
                *([ {"type": "table",
                    "row": 1 + (-(-n_kpis // 4)) * 3 + (-(-n_charts // 2)) * 5,
                    "col": 1, "height": table_rows, "width": COLS} ]
                if show_table else [])
            ],
            "chart_focus": [
                *[{"type": "kpi", "index": i,
                "row": 1, "col": i * 2 + 1, "height": 2, "width": 2}
                for i in range(min(n_kpis, 6))],
                *[{"type": "chart", "index": i,
                "row": 3 + (i // 2) * 6, "col": (i % 2) * 6 + 1,
                "height": 6, "width": 6}
                for i in range(n_charts)],
                *([ {"type": "table",
                    "row": 3 + (-(-n_charts // 2)) * 6,
                    "col": 1, "height": table_rows, "width": COLS} ]
                if show_table else [])
            ],
            "table_first": [
                {"type": "table", "row": 1, "col": 1, "height": 5, "width": COLS},
                *[{"type": "kpi", "index": i,
                "row": 6, "col": i * 2 + 1, "height": 2, "width": 2}
                for i in range(min(n_kpis, 6))],
                *[{"type": "chart", "index": i,
                "row": 8 + (i // 2) * 5, "col": (i % 2) * 6 + 1,
                "height": 5, "width": 6}
                for i in range(n_charts)],
            ],
        }

        use_custom_layout = isinstance(layout, list)
        if use_custom_layout:
            all_blocks = layout
        elif layout in PRESETS:
            all_blocks = PRESETS[layout]
        else:
            all_blocks = None  # "auto"

        # ── 7. Calcular total_rows ───────────────────────────────────────────
        if all_blocks:
            total_rows = max(b["row"] + b["height"] - 1 for b in all_blocks)
        else:
            total_rows = kpi_rows_used + chart_rows_total + table_rows_used
            total_rows = max(total_rows, 6)

        # ── 8. Construir dashboard ───────────────────────────────────────────
        dash = cls(
            title=title,
            theme=template,
            cols=COLS,
            rows=total_rows,
            gap=14,
            padding=20,
            navbar=navbar or {"title": title, "items": []},
            authors=authors
        )

        if all_blocks:
            # ── Layout personalizado o preset ────────────────────────────────
            kpi_idx   = 0
            chart_idx = 0
            for block in all_blocks:
                btype = block["type"]
                r, c, h, w = block["row"], block["col"], block["height"], block["width"]
                idx = block.get("index")

                if btype == "kpi":
                    i = idx if idx is not None else kpi_idx
                    if i < len(planned):
                        _, col_name, val, icon = planned[i]
                        dash.add_valuebox(title=col_name, value=val, icon=icon,
                                        row=r, col=c, height=h, width=w)
                        kpi_idx += 1

                elif btype == "chart":
                    i = idx if idx is not None else chart_idx
                    if i < len(charts):
                        _, fig, chart_title = charts[i]
                        dash.add_chart(fig=fig, title=chart_title,
                                    row=r, col=c, height=h, width=w)
                        chart_idx += 1

                elif btype == "table" and show_table:
                    dash.add_table(df=df.head(200), title="Vista de datos",
                                row=r, col=c, height=h, width=w)

        else:
            # ── Layout automático ────────────────────────────────────────────
            current_row = 1

            if n_kpis:
                for i, (_, col_name, val, icon) in enumerate(planned):
                    fila_kpi = i // MAX_KPIS_PER_ROW
                    col_kpi  = i %  MAX_KPIS_PER_ROW
                    dash.add_valuebox(
                        title=col_name, value=val, icon=icon,
                        row=current_row + fila_kpi * kpi_height,
                        col=col_kpi * actual_kpi_width + 1,
                        height=kpi_height, width=actual_kpi_width
                    )
                current_row += kpi_rows_used

            for i, (_, fig, chart_title) in enumerate(charts):
                col_pos = (i % 2) * chart_cols + 1
                dash.add_chart(
                    fig=fig, title=chart_title,
                    row=current_row, col=col_pos,
                    height=chart_height, width=chart_cols
                )
                if i % 2 == 1:
                    current_row += chart_height

            if n_charts % 2 != 0:
                current_row += chart_height

            if show_table:
                dash.add_table(
                    df=df.head(200), title="Vista de datos",
                    row=current_row, col=1,
                    height=table_rows, width=COLS
                )

        return dash.generate(filename=filename)