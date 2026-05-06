import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import uuid
from typing import Optional, Tuple, Union, List, Dict

# ============================================================
#                      ViewX Dashboard PRO v4.0
# ============================================================

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
        * {{ box-sizing: border-box; }}
        body {{
            background: var(--vx-bg-page);
            color: var(--vx-text-primary);
            font-family: 'Segoe UI', 'Inter', system-ui, sans-serif;
            margin: 0; padding: 0;
            overflow-x: hidden;
        }}
        .vx-card {{
            background: var(--vx-bg-card);
            border-radius: var(--vx-card-radius);
            box-shadow: var(--vx-shadow);
            transition: var(--vx-transition);
            overflow: hidden;
            border: 1px solid rgba(0,0,0,0.05);
        }}
        .vx-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.12);
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
        data=None,
        title: str = "ViewX Dashboard",
        theme: Union[int, str] = "corporate_blue",
        num_cols: int = 12,
        num_rows: int = 12,
        gap: int = 16,
        padding: int = 24,
        navbar: dict = None
    ):
        self.data = data
        self.title = title
        self.theme_manager = ThemeManager(theme)
        self.num_cols = num_cols
        self.num_rows = num_rows
        self.gap = gap
        self.padding = padding
        self.navbar = navbar
        
        self.grid_css = []
        self.components_html = []
        
    def _register_block(self, slot_id: str, row: int, col: int, height: int, width: int):
        css = f".{slot_id} {{ grid-area: {row} / {col} / {row + height} / {col + width}; }}"
        self.grid_css.append(css)

    def _uid(self) -> str:
        return f"comp_{uuid.uuid4().hex[:8]}"

    def add_valuebox(self, title: str, value, icon: str = "📊", color: str = None, slot_grid: tuple = (1, 1, 2, 3)):
        row, col, height, width = slot_grid
        uid = self._uid()
        self._register_block(uid, row, col, height, width)
        
        bg_page, bg_card, accent, text = self.theme_manager.get_colors()
        box_color = color or accent
        
        html = f"""
        <style>
            .vb-{uid} {{
                padding: 24px;
                display: flex;
                align-items: center;
                gap: 20px;
                border-left: 6px solid {box_color};
            }}
            .vb-icon-{uid} {{ 
                font-size: 2.8rem; 
                color: {box_color}; 
                opacity: 0.9;
                background: {box_color}15;
                width: 64px; height: 64px;
                display: flex; align-items: center; justify-content: center;
                border-radius: 12px;
            }}
            .vb-content-{uid} {{ flex: 1; }}
            .vb-title-{uid} {{ 
                font-size: 0.85rem; 
                color: var(--vx-text-secondary); 
                text-transform: uppercase; 
                font-weight: 700;
                letter-spacing: 0.5px;
                margin-bottom: 4px;
            }}
            .vb-val-{uid} {{ 
                font-size: 2rem; 
                font-weight: 800; 
                color: var(--vx-text-primary); 
                line-height: 1;
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

    def add_plot(self, fig, slot_grid: tuple = (1, 1, 6, 6), title: str = ""):
        row, col, height, width = slot_grid
        uid = self._uid()
        self._register_block(uid, row, col, height, width)
        
        bg_page, bg_card, accent, text = self.theme_manager.get_colors()
        
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color=text,
            title_font_color=accent,
            margin=dict(l=10, r=10, t=40, b=10),
            font_family="'Segoe UI', sans-serif"
        )
        
        plot_html = fig.to_html(full_html=False, include_plotlyjs='cdn', config={'displaylogo': False})
        
        html = f"""
        <style>
            .plot-card-{uid} {{
                padding: 16px;
                display: flex;
                flex-direction: column;
                height: 100%;
            }}
            .plot-card-{uid} h4 {{ 
                margin: 0 0 12px 4px; 
                color: var(--vx-text-primary); 
                font-weight: 600;
                font-size: 1.1rem;
                border-bottom: 2px solid {accent}22;
                padding-bottom: 8px;
            }}
            .plot-container-{uid} {{ flex: 1; min-height: 0; }}
        </style>
        <div class="vx-card plot-card-{uid} {uid}">
            {f"<h4>{title}</h4>" if title else ""}
            <div class="plot-container-{uid}">{plot_html}</div>
        </div>
        """
        self.components_html.append(html)
        return self

    def add_table(self, df: pd.DataFrame, slot_grid: tuple = (1, 1, 4, 6), title: str = "", searchable: bool = True):
        row, col, height, width = slot_grid
        uid = self._uid()
        self._register_block(uid, row, col, height, width)
        
        bg_page, bg_card, accent, text = self.theme_manager.get_colors()
        table_html = df.to_html(classes=f"vxt-{uid}", border=0, index=False)
        
        html = f"""
        <style>
            .table-card-{uid} {{
                padding: 20px;
                display: flex;
                flex-direction: column;
                height: 100%;
            }}
            .table-card-{uid} h4 {{ 
                color: var(--vx-text-primary); 
                margin: 0 0 16px 0; 
                font-weight: 600;
                font-size: 1.1rem;
            }}
            .table-container-{uid} {{ 
                overflow: auto; 
                flex: 1; 
                scrollbar-width: thin;
                scrollbar-color: {accent}44 transparent;
            }}
            .vxt-{uid} {{
                width: 100%;
                border-collapse: collapse;
                font-size: 0.9rem;
            }}
            .vxt-{uid} th {{
                background: {accent}11;
                color: {accent};
                padding: 14px 12px;
                text-align: left;
                font-weight: 700;
                position: sticky; top: 0;
                border-bottom: 2px solid {accent}44;
            }}
            .vxt-{uid} td {{
                padding: 12px;
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

    def add_text(self, content: str, slot_grid: tuple = (1, 1, 2, 6)):
        row, col, height, width = slot_grid
        uid = self._uid()
        self._register_block(uid, row, col, height, width)
        
        html = f"""
        <style>
            .text-card-{uid} {{
                padding: 24px;
                line-height: 1.6;
                color: var(--vx-text-primary);
                height: 100%;
                overflow: auto;
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

    def _build_navbar(self) -> str:
        if not self.navbar: return ""
        bg_page, bg_card, accent, text = self.theme_manager.get_colors()
        
        items_html = "".join([f'<a href="{i["link"]}" class="nav-link">{i["label"]}</a>' for i in self.navbar.get("items", [])])
        
        return f"""
        <style>
            .vx-navbar {{
                position: fixed; top: 0; left: 0; right: 0; height: 64px;
                background: {bg_card};
                display: flex; align-items: center; justify-content: space-between;
                padding: 0 32px; z-index: 1000; 
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                border-bottom: 3px solid {accent};
            }}
            .nav-brand {{ 
                font-weight: 800; font-size: 1.5rem; 
                color: {accent}; text-decoration: none; 
                letter-spacing: -0.5px;
            }}
            .nav-links {{ display:flex; gap: 24px; }}
            .nav-link {{ 
                color: var(--vx-text-primary); 
                text-decoration: none; 
                font-weight: 600; 
                font-size: 0.95rem;
                opacity: 0.8; transition: var(--vx-transition); 
            }}
            .nav-link:hover {{ opacity: 1; color: {accent}; transform: translateY(-1px); }}
        </style>
        <nav class="vx-navbar">
            <a href="#" class="nav-brand">{self.navbar.get("title", self.title)}</a>
            <div class="nav-links">{items_html}</div>
        </nav>
        """

    def generate(self, filename: str = "dashboard.html"):
        bg_page, bg_card, accent, text = self.theme_manager.get_colors()
        
        full_html = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <title>{self.title}</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap" rel="stylesheet">
            <style>
                {self.theme_manager.get_global_css()}
                
                .dashboard-container {{
                    padding: {self.padding}px;
                    padding-top: {84 if self.navbar else self.padding}px;
                    min-height: 100vh;
                    display: flex;
                    flex-direction: column;
                    max-width: 1600px;
                    margin: 0 auto;
                }}
                
                .vx-grid {{
                    display: grid;
                    grid-template-columns: repeat({self.num_cols}, 1fr);
                    grid-template-rows: repeat({self.num_rows}, 1fr);
                    gap: {self.gap}px;
                    flex: 1;
                    min-height: 800px;
                }}
                
                {chr(10).join(self.grid_css)}
                
                .vx-card {{
                    animation: fadeInUp 0.6s cubic-bezier(.16,1,.3,1) both;
                }}
                
                @keyframes fadeInUp {{
                    from {{ opacity: 0; transform: translateY(20px); }}
                    to {{ opacity: 1; transform: translateY(0); }}
                }}
                
                /* Secuencial para cada componente */
                {chr(10).join([f".vx-card:nth-child({i+1}) {{ animation-delay: {i*0.1}s; }}" for i in range(len(self.components_html))])}

                @media (max-width: 1024px) {{
                    .vx-grid {{
                        display: flex;
                        flex-direction: column;
                    }}
                    .vx-card {{
                        height: auto !important;
                        width: 100% !important;
                        min-height: 300px;
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
        return filename
