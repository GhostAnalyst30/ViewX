import os
import pandas as pd
import plotly.express as px
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading
import webbrowser
from typing import Optional, Tuple, Union
import time
import uuid

# ============================================================
#                      ViewX PRO  v2.0
# ============================================================

def load_dataset(path: str) -> pd.DataFrame:
    """Carga un CSV y retorna un DataFrame."""
    return pd.read_csv(path)


class HTML:
    def __init__(
        self,
        data=None,
        title: str = "ViewX Report",
        template_color: Optional[Union[int, Tuple[str, str, str, str]]] = 0,
        num_divs: int = 1,
        num_cols: int = 1,
        num_rows: int = 1,
        navbar: dict = None,
        gap: int = 10,            # espacio entre celdas del grid (px)
        padding: int = 10,        # padding exterior del grid (px)
    ):
        self.data = data
        self.title = title
        self.navbar = navbar
        self.gap = gap
        self.padding = padding

        # ── Paletas ──────────────────────────────────────────
        # Cada tupla: (bg_page, bg_card, accent, text)
        self.templates = {
            0:  ("#07080F", "#0F1117", "#5865F2", "#E2E5FF"),   # Void Indigo
            1:  ("#F7F5F0", "#FFFFFF", "#E63946", "#1A1A2E"),   # Paper Red
            2:  ("#0A0E17", "#111827", "#00C2CB", "#CFF8FC"),   # Deep Cyan
            3:  ("#FAFAF8", "#FFFFFF", "#0B7285", "#0D2B33"),   # Arctic Ink
            4:  ("#100D0A", "#1C1915", "#F5A623", "#FFF3DC"),   # Ember Dark
            5:  ("#F0F4FF", "#FFFFFF", "#4361EE", "#10184A"),   # Blueprint
            6:  ("#060A14", "#0D1526", "#38EF7D", "#D4FCDF"),   # Matrix Green
            7:  ("#FDF6EE", "#FFFFFF", "#C1440E", "#2C1200"),   # Terracotta
            8:  ("#0B0D14", "#141621", "#FF2D78", "#FFD6E7"),   # Neon Pink
            9:  ("#F5F7FA", "#FFFFFF", "#7209B7", "#1A003D"),   # Amethyst Light
            10: ("#080C10", "#101820", "#00B4FF", "#C8F0FF"),   # Cobalt Night
            11: ("#FFFEF8", "#FFFFFF", "#3D8B37", "#0D2209"),   # Sage Paper
        }

        self.colors = self._resolve_colors(template_color)
        self.num_divs = num_divs
        self.num_cols = num_cols
        self.num_rows = num_rows
        self.grid_css: list[str] = []
        self.slots: dict[str, list[str]] = {f"div{i}": [] for i in range(1, num_divs + 1)}

        self.navbar_height = (self.navbar or {}).get("height", 64)
        self.title_font_size = (self.navbar or {}).get("title_font_size", 22)
        self.items_font_size = (self.navbar or {}).get("items_font_size", 15)

        print("╔══════════════════════════════╗")
        print("║          ViewX v2.0          ║")
        print("╚══════════════════════════════╝")

        if title:
            print(f"Title: {title}")

        if template_color:
            print(f"Template color: {template_color}")

        if num_divs and num_cols and num_rows:
            print(f"Number of divs: {num_divs}, Number of cols: {num_cols}, Number of rows: {num_rows}")

        if isinstance(self.navbar, dict):
            print("Navbar:")
            for key, value in self.navbar.items():
                if key == "items":
                    print(f"- {key}:")
                    for item in value:
                        print(f"  - {item.get('label')}: {item.get('link')}")
                else:
                    print(f"- {key}: {value}")

        if gap:
            print(f"Gap: {gap}")

        if padding:
            print(f"Padding: {padding}")

    # ────────────────────────────────────────────────────────
    #  Helpers internos
    # ────────────────────────────────────────────────────────
    def _resolve_colors(self, template_color):
        if isinstance(template_color, int):
            return self.templates.get(template_color, self.templates[0])
        if isinstance(template_color, tuple):
            if len(template_color) != 4:
                raise ValueError("La tupla de color debe tener exactamente 4 valores.")
            return template_color
        return self.templates[0]

    def _add_to_slot(self, html: str, slot: str):
        if slot not in self.slots:
            raise ValueError(f"Slot '{slot}' no existe. Slots válidos: {list(self.slots)}")
        self.slots[slot].append(html)

    def _register_block(self, slot: str, row: int, col: int, height: int, width: int):
        if row < 1 or col < 1:
            raise ValueError("row y col deben ser >= 1.")
        if row + height - 1 > self.num_rows:
            raise ValueError(f"Bloque excede filas: row={row}, height={height}, num_rows={self.num_rows}")
        if col + width - 1 > self.num_cols:
            raise ValueError(f"Bloque excede columnas: col={col}, width={width}, num_cols={self.num_cols}")
        self.grid_css.append(
            f".{slot} {{ grid-area: {row} / {col} / {row + height} / {col + width}; }}"
        )

    @staticmethod
    def _uid() -> str:
        return uuid.uuid4().hex[:8]

    # ────────────────────────────────────────────────────────
    #  NAVBAR
    # ────────────────────────────────────────────────────────
    def _build_navbar(self) -> str:
        if not self.navbar:
            return ""

        bg, primary, secondary, text = self.colors
        items_html = "".join(
            f'<a href="{item.get("link","#")}" class="nav-item">{item.get("label","")}</a>'
            for item in self.navbar.get("items", [])
        )

        logo = self.navbar.get("logo", "")
        logo_html = f'<img src="{logo}" class="nav-logo" alt="logo">' if logo else ""

        return f"""
<style>
:root {{
    --nav-h: {self.navbar_height}px;
    --nav-accent: {primary};
    --nav-text: {text};
    --nav-bg: {secondary};
    --nav-title-size: {self.title_font_size}px;
    --nav-item-size: {self.items_font_size}px;
}}

.navbar {{
    width:100%;
    height:var(--nav-h);
    background: linear-gradient(90deg, {secondary}ee, {bg}dd);
    backdrop-filter: blur(16px) saturate(180%);
    -webkit-backdrop-filter: blur(16px) saturate(180%);
    border-bottom: 1px solid {primary}33;
    display:flex;
    align-items:center;
    justify-content:space-between;
    padding:0 36px;
    box-sizing:border-box;
    position:fixed;
    top:0; left:0;
    z-index:1000;
    box-shadow: 0 1px 40px {primary}22;
    animation: navSlide 0.6s cubic-bezier(.16,1,.3,1) both;
}}

@keyframes navSlide {{
    from {{ transform: translateY(-100%); opacity:0; }}
    to   {{ transform: translateY(0);     opacity:1; }}
}}

.nav-brand {{
    font-weight:800;
    font-size:var(--nav-title-size);
    color: {primary};
    letter-spacing: -0.5px;
    display:flex;
    align-items:center;
    gap:10px;
    cursor:pointer;
    transition: opacity .2s;
}}
.nav-brand:hover {{ opacity:.8; }}

.nav-logo {{ height:32px; border-radius:6px; }}

.nav-items {{ display:flex; align-items:center; gap:4px; }}

.nav-item {{
    color: var(--nav-text);
    text-decoration:none;
    font-size:var(--nav-item-size);
    font-weight:500;
    padding:6px 14px;
    border-radius:8px;
    position:relative;
    transition: color .2s, background .2s;
}}
.nav-item::after {{
    content:'';
    position:absolute;
    bottom:2px; left:14px; right:14px;
    height:2px;
    background: {primary};
    border-radius:2px;
    transform: scaleX(0);
    transform-origin: right;
    transition: transform .3s cubic-bezier(.16,1,.3,1);
}}
.nav-item:hover {{ color:{primary}; background:{primary}18; }}
.nav-item:hover::after {{ transform:scaleX(1); transform-origin:left; }}
</style>

<nav class="navbar">
    <div class="nav-brand">
        {logo_html}
        {self.navbar.get("title","ViewX")}
    </div>
    <div class="nav-items">{items_html}</div>
</nav>
"""

    # ────────────────────────────────────────────────────────
    #  VALUEBOX
    # ────────────────────────────────────────────────────────
    def add_valuebox(
        self,
        title: str,
        value,
        icon: str = "📊",
        color: Optional[str] = None,
        slot_grid: tuple = ("div1", 1, 1, 1, 1),
        position_icon: str = "left",   # "left" | "right"
        subtitle: str = "",            # texto secundario opcional
        insert_css: str = "",
    ):
        slot, row, col, height, width = slot_grid
        self._register_block(slot, row, col, height, width)

        bg_page, accent, secondary, text_col = self.colors
        card_bg = color or accent
        uid = self._uid()
        flex_dir = "row-reverse" if position_icon == "right" else "row"
        extra = (insert_css.strip() + ";") if insert_css else ""

        html = f"""
<style>
.vxvb-{uid} {{
    background: linear-gradient(135deg, {card_bg}ee, {card_bg}bb);
    border: 1px solid {card_bg}55;
    padding: 18px 22px;
    border-radius: 18px;
    color: {text_col};
    font-family: 'Segoe UI', system-ui, sans-serif;
    box-shadow: 0 4px 24px {card_bg}44, inset 0 1px 0 rgba(255,255,255,.12);
    width:100%; height:100%;
    box-sizing:border-box;
    display:flex;
    flex-direction:{flex_dir};
    align-items:center;
    gap:18px;
    overflow:hidden;
    position:relative;
    cursor:default;
    transition: transform .35s cubic-bezier(.16,1,.3,1),
                box-shadow .35s ease;
    animation: vxvbIn .5s cubic-bezier(.16,1,.3,1) both;
    {extra}
}}
@keyframes vxvbIn {{
    from {{ opacity:0; transform:translateY(14px) scale(.97); }}
    to   {{ opacity:1; transform:translateY(0) scale(1);      }}
}}
.vxvb-{uid}:hover {{
    transform: translateY(-4px) scale(1.02);
    box-shadow: 0 12px 36px {card_bg}66, inset 0 1px 0 rgba(255,255,255,.18);
}}
/* shimmer */
.vxvb-{uid}::before {{
    content:'';
    position:absolute;
    inset:0;
    background: linear-gradient(110deg, transparent 30%, rgba(255,255,255,.08) 50%, transparent 70%);
    transform: translateX(-100%);
    transition: transform .6s ease;
}}
.vxvb-{uid}:hover::before {{ transform:translateX(100%); }}

/* glow orb */
.vxvb-{uid}::after {{
    content:'';
    position:absolute;
    width:120px; height:120px;
    border-radius:50%;
    background: radial-gradient(circle, rgba(255,255,255,.15), transparent 70%);
    top:-30px;
    {"right:-30px" if position_icon=="right" else "left:-30px"};
    pointer-events:none;
}}

.vxvb-icon-{uid} {{
    font-size:48px;
    min-width:64px;
    text-align:center;
    filter: drop-shadow(0 2px 6px rgba(0,0,0,.25));
    transition: transform .4s cubic-bezier(.34,1.56,.64,1);
    will-change: transform;
    z-index:1;
}}
.vxvb-{uid}:hover .vxvb-icon-{uid} {{
    transform: scale(1.5) rotate(12deg);
}}
.vxvb-body-{uid} {{ z-index:1; }}
.vxvb-value-{uid} {{
    font-size:28px;
    font-weight:800;
    letter-spacing:-1px;
    line-height:1.1;
    text-shadow: 0 2px 8px rgba(0,0,0,.2);
    color: {text_col};
}}
.vxvb-title-{uid} {{
    font-size:13px;
    font-weight:500;
    opacity:.85;
    text-transform:uppercase;
    letter-spacing:.8px;
    margin-top:4px;
    color: {text_col};
}}
.vxvb-sub-{uid} {{
    font-size:11px;
    opacity:.6;
    margin-top:3px;
    color: {text_col};
}}
</style>
<div class="vxvb-{uid}">
    <div class="vxvb-icon-{uid}">{icon}</div>
    <div class="vxvb-body-{uid}">
        <div class="vxvb-value-{uid}">{value}</div>
        <div class="vxvb-title-{uid}">{title}</div>
        {"" if not subtitle else f'<div class="vxvb-sub-{uid}">{subtitle}</div>'}
    </div>
</div>
"""
        self._add_to_slot(html, slot)
        print(f"  ✔ ValueBox añadido → {slot}")
        print("╔══════════════════════════════╗")
        print("║            ValueBox          ║")
        print("╚══════════════════════════════╝")

        if title:
            print(f"Title: {title}")

        if value:
            print(f"Value: {value}")

        if subtitle:
            print(f"Subtitle: {subtitle}")

        if icon:
            print(f"Icon: {icon}")

        if color:
            print(f"Color: {color}")

        if slot_grid:
            print(f"Slot: {slot}, Row: {row}, Col: {col}, Height: {height}, Width: {width}")

        return self

    # ────────────────────────────────────────────────────────
    #  PLOTS
    # ────────────────────────────────────────────────────────

    @staticmethod
    def _hex_alpha(hex_color: str, alpha: float) -> str:
        """Convierte '#RRGGBB' + alpha (0.0-1.0) → 'rgba(r,g,b,alpha)'
        Compatible con Plotly (que no acepta hex de 8 dígitos #RRGGBBAA).
        """
        h = hex_color.lstrip("#")
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        return f"rgba({r},{g},{b},{alpha})"
    
    def add_plot(self, kind="scatter", x=None, y=None, z=None,
                color=None, alpha: float = 0.8, size=None, title="",
                slot_grid=("div1",1,1,1,1), padding=6, show_grid=True, **kwargs):

        if self.data is None:
            raise ValueError("No hay datos.")

        slot, row, col, height, width = slot_grid
        self._register_block(slot, row, col, height, width)

        bg_page, accent, secondary, text_col = self.colors

        kw = kwargs.copy()
        if color and "color" not in kw: kw["color"] = color
        if size  and "size"  not in kw: kw["size"]  = size

        fig_map = {
            "scatter":    lambda: px.scatter(self.data, x=x, y=y, title=title, **kw),
            "line":       lambda: px.line(self.data, x=x, y=y, title=title, **kw),
            "bar":        lambda: px.bar(self.data, x=x, y=y, title=title, **kw),
            "hist":       lambda: px.histogram(self.data, x=x, title=title, **kw),
            "box":        lambda: px.box(self.data, x=x, y=y, title=title, **kw),
            "violin":     lambda: px.violin(self.data, x=x, y=y, title=title, **kw),
            "pie":        lambda: px.pie(self.data, names=x, values=y, title=title, **kw),
            "scatter_3d": lambda: px.scatter_3d(self.data, x=x, y=y, z=z, title=title, **kw),
            "heatmap":    lambda: px.density_heatmap(self.data, x=x, y=y, title=title, **kw),
            "area":       lambda: px.area(self.data, x=x, y=y, title=title, **kw),
            "funnel":     lambda: px.funnel(self.data, x=x, y=y, title=title, **kw),
            "treemap":    lambda: px.treemap(self.data, path=x, values=y, title=title, **kw),
            "sunburst":   lambda: px.sunburst(self.data, path=x, values=y, title=title, **kw),
            "strip":      lambda: px.strip(self.data, x=x, y=y, title=title, **kw),
        }
        if kind not in fig_map:
            raise ValueError(f"Tipo '{kind}' no soportado. Opciones: {list(fig_map)}")

        fig = fig_map[kind]()

        # ── Paleta sin repetidos ─────────────────────────────────────────
        palette = [accent, secondary, "#F72585", "#4CC9F0", "#F4A261",
                "#06D6A0", "#FFB703", "#9B5DE5", "#FF6B6B"]

        # ── Layout ──────────────────────────────────────────────────────
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color=text_col, family="'Segoe UI', system-ui, sans-serif"),
            title=dict(
                text=title,
                font=dict(color=text_col, size=15),
                x=0.03, xanchor="left",
            ),
            legend=dict(
                font=dict(color=text_col, size=12),
                bgcolor="rgba(0,0,0,0.15)",
                bordercolor=self._hex_alpha(text_col, alpha=alpha),  # FIX: rgba válido
                borderwidth=1,
            ),
            colorway=palette,
            autosize=True,
            margin=dict(l=8, r=8, t=40, b=8),
        )

        # FIX: rgba válido para gridcolor
        grid_color = self._hex_alpha(text_col, alpha=alpha)
        if show_grid:
            fig.update_xaxes(showgrid=True, gridcolor=grid_color, gridwidth=1,
                            zeroline=False, color=text_col, tickfont=dict(size=11))
            fig.update_yaxes(showgrid=True, gridcolor=grid_color, gridwidth=1,
                            zeroline=False, color=text_col, tickfont=dict(size=11))
        else:
            fig.update_xaxes(showgrid=False, zeroline=False, color=text_col)
            fig.update_yaxes(showgrid=False, zeroline=False, color=text_col)

        # ── Colores por tipo ─────────────────────────────────────────────
        match kind:
            case "scatter":
                fig.update_traces(marker=dict(
                    color=accent, size=7, opacity=.85,
                    line=dict(color="#fff", width=.5)
                ))
            case "line":
                fig.update_traces(line=dict(color=accent, width=2.5))
            case "area":
                fig.update_traces(
                    line=dict(color=accent, width=2),
                    fillcolor=self._hex_alpha(accent, alpha=alpha),
                )
            case "bar":
                fig.update_traces(marker=dict(
                    color=accent,
                    line=dict(width=0),
                    cornerradius=6,
                ))
            case "hist":
                fig.update_traces(marker=dict(
                    color=accent,
                    line=dict(color=self._hex_alpha(accent, alpha=alpha), width=1)
                ))
            case "box":
                fig.update_traces(
                    marker_color=accent,
                    line_color=accent,
                    fillcolor=self._hex_alpha(accent, alpha=alpha),
                )
            case "violin":
                fig.update_traces(
                    fillcolor=self._hex_alpha(accent, alpha=alpha),
                    line_color=accent,
                )
            case "pie" | "sunburst":
                fig.update_traces(
                    marker=dict(colors=palette),
                    textfont=dict(color="#fff"),
                )
            case "scatter_3d":
                fig.update_traces(marker=dict(color=accent, size=4, opacity=.8))
            case "heatmap":
                fig.update_traces(colorscale=[[0, bg_page], [1, accent]])

        uid = self._uid()
        config = {"responsive": True, "displaylogo": False,
                "modeBarButtonsToRemove": ["select2d", "lasso2d"]}
        plot_html = fig.to_html(full_html=False, include_plotlyjs="cdn",
                                config=config, div_id=f"plt-{uid}")

        html = f"""
    <style>
    .vxplot-{uid} {{
        padding:{padding}px; box-sizing:border-box;
        width:100%; height:100%;
        display:flex; flex-direction:column;
        animation: vxplotIn .55s cubic-bezier(.16,1,.3,1) both;
    }}
    @keyframes vxplotIn {{
        from {{ opacity:0; transform:scale(.97); }}
        to   {{ opacity:1; transform:scale(1); }}
    }}
    .vxplot-{uid} > div,
    .vxplot-{uid} > div > div,
    #plt-{uid} {{
        flex:1 !important; width:100% !important;
        height:100% !important; min-height:0 !important;
    }}
    </style>
    <div class="vxplot-{uid}">{plot_html}</div>
    """
        self._add_to_slot(html, slot)
        print(f"  ✔ Plot ({kind}) añadido → {slot}")
        print("╔══════════════════════════════╗")
        print("║          Plot (Plotly)       ║")
        print("╚══════════════════════════════╝")
        """kind="scatter", x=None, y=None, z=None,
                color=None, alpha: float = 0.8, size=None, title="",
                slot_grid=("div1",1,1,1,1), padding=6, show_grid=True, **kwargs"""
        if kind:
            print(f"Type: {kind}")
        if x and y:
            print("Data okay!")
        if color:
            print(f"Color: {color}")
        if size:
            print(f"Size: {size}")
        if title:
            print(f"Title: {title}")
        if slot_grid:
            print(f"Slot: {slot_grid}, Row: {row}, Col: {col}, Height: {height}, Width: {width}")
        if padding:
            print(f"Padding: {padding}")
        if show_grid:
            print(f"Show grid: {show_grid}")
        if kwargs:
            print(f"Kwargs: {kwargs}")

        return self

    # ────────────────────────────────────────────────────────
    #  TABLA
    # ────────────────────────────────────────────────────────
    def add_table(
        self,
        columns=None,
        slot_grid: tuple = ("div1", 1, 1, 1, 1),
        max_rows: Optional[int] = None,
        searchable: bool = False,   # añade barra de búsqueda JS
        striped: bool = True,
    ):
        if self.data is None:
            raise ValueError("No hay datos.")

        slot, row, col, height, width = slot_grid
        self._register_block(slot, row, col, height, width)

        df = self.data.copy() if columns in (None, "all") else self.data[columns].copy()
        if max_rows:
            df = df.head(max_rows)

        bg_page, accent, secondary, text_col = self.colors
        uid = self._uid()
        cls = f"vxt_{uid}"
        table_html = df.to_html(classes=cls, border=0, index=False, escape=True)

        search_html = f"""
<input id="search-{uid}" type="text" placeholder="🔍  Buscar…" oninput="vxSearch('{uid}',this.value)"
  style="width:100%;padding:8px 12px;border-radius:10px;border:1px solid {accent}55;
         background:{bg_page};color:{text_col};font-size:13px;box-sizing:border-box;
         margin-bottom:8px;outline:none;transition:border .2s;"
  onfocus="this.style.borderColor='{accent}'" onblur="this.style.borderColor='{accent}55'">
<script>
function vxSearch(uid, q){{
    const rows = document.querySelectorAll('.vxt_'+uid+' tbody tr');
    const lq = q.toLowerCase();
    rows.forEach(r => {{
        r.style.display = r.innerText.toLowerCase().includes(lq) ? '' : 'none';
    }});
}}
</script>
""" if searchable else ""

        zebra_css = f".{cls} tbody tr:nth-child(even){{background:{accent}0d;}}" if striped else ""

        html = f"""
<style>
.vxtable-wrap-{uid} {{
    overflow:auto;
    width:100%; height:100%;
    box-sizing:border-box;
    padding:12px;
    animation: vxtIn .5s cubic-bezier(.16,1,.3,1) both;
}}
@keyframes vxtIn {{
    from {{ opacity:0; transform:translateY(10px); }}
    to   {{ opacity:1; transform:translateY(0);    }}
}}
.{cls} {{
    width:100%;
    border-collapse:collapse;
    font-family:'Segoe UI',system-ui,sans-serif;
    color:{text_col};
    font-size:13px;
}}
.{cls} thead th {{
    background: linear-gradient(160deg,{secondary},{accent}cc);
    color:#fff;
    padding:11px 10px;
    text-align:left;
    position:sticky; top:0; z-index:2;
    font-weight:700; font-size:12px;
    text-transform:uppercase; letter-spacing:.6px;
    border-bottom: 2px solid {accent};
    white-space: nowrap;
}}
.{cls} tbody td {{
    padding:9px 10px;
    border-bottom:1px solid {text_col}15;
    transition: background .15s;
}}
{zebra_css}
.{cls} tbody tr:hover {{
    background:{accent}22 !important;
}}
/* scrollbar */
.vxtable-wrap-{uid}::-webkit-scrollbar{{width:6px;height:6px;}}
.vxtable-wrap-{uid}::-webkit-scrollbar-track{{background:{bg_page};border-radius:6px;}}
.vxtable-wrap-{uid}::-webkit-scrollbar-thumb{{background:{accent};border-radius:6px;}}
</style>
<div class="vxtable-wrap-{uid}">
    {search_html}
    {table_html}
</div>
"""
        self._add_to_slot(html, slot)
        print(f"  ✔ Tabla añadida → {slot}")
        print("╔══════════════════════════════╗")
        print("║             Table            ║")
        print("╚══════════════════════════════╝")
        """        columns=None,
        slot_grid: tuple = ("div1", 1, 1, 1, 1),
        max_rows: Optional[int] = None,
        searchable: bool = False,   # añade barra de búsqueda JS
        striped: bool = True,"""

        if columns in (None, "all"):
            print(f"Columns: {list(self.data.columns)}")
        else:
            print(f"Columns: {columns}")
        
        if max_rows:
            print(f"Max rows: {max_rows}")
        if searchable:
            print(f"Searchable: {searchable}")
        if striped:
            print(f"Striped: {striped}")

        if slot_grid:
            print(f"Slot: {slot}, Row: {row}, Col: {col}, Height: {height}, Width: {width}")
        
        
        return self

    # ────────────────────────────────────────────────────────
    #  TEXTO / CARD
    # ────────────────────────────────────────────────────────
    def add_text(
        self,
        content: str,
        slot_grid: tuple = ("div1", 1, 1, 1, 1),
        align: str = "left",          # "left"|"center"|"right"
        glass: bool = False,          # efecto glassmorphism
        border_accent: bool = True,   # borde izquierdo con accent
    ):
        slot, row, col, height, width = slot_grid
        self._register_block(slot, row, col, height, width)

        bg_page, accent, secondary, text_col = self.colors
        uid = self._uid()

        flex_align = {"left": "flex-start", "center": "center", "right": "flex-end"}.get(align, "flex-start")
        glass_css = (
            f"background:rgba(255,255,255,.05)!important;"
            f"backdrop-filter:blur(12px) saturate(160%);"
            f"-webkit-backdrop-filter:blur(12px) saturate(160%);"
            f"border:1px solid rgba(255,255,255,.12);"
        ) if glass else ""
        border_css = f"border-left:4px solid {accent};" if border_accent else ""

        html = f"""
<style>
.vxtxt-{uid} {{
    background:linear-gradient(135deg,{bg_page},{secondary}18);
    color:{text_col};
    {border_css}
    {glass_css}
    border-radius:16px;
    padding:22px 24px;
    width:100%; height:100%;
    box-sizing:border-box;
    overflow:auto;
    font-family:'Segoe UI',system-ui,sans-serif;
    display:flex; flex-direction:column;
    justify-content:{flex_align};
    align-items:{flex_align};
    text-align:{align};
    transition: box-shadow .3s, transform .3s;
    animation: vxtxtIn .55s cubic-bezier(.16,1,.3,1) both;
}}
@keyframes vxtxtIn {{
    from{{ opacity:0; transform:translateX(-10px); }}
    to  {{ opacity:1; transform:translateX(0);     }}
}}
.vxtxt-{uid}:hover {{
    box-shadow:0 8px 32px {accent}25;
    transform:translateY(-2px);
}}
.vxtxt-{uid} h1,.vxtxt-{uid} h2,.vxtxt-{uid} h3 {{
    color:{text_col}; margin-top:0; margin-bottom:12px;
}}
.vxtxt-{uid} p {{ line-height:1.7; margin-bottom:10px; }}
.vxtxt-{uid} a {{ color:{accent}; text-decoration:none; }}
.vxtxt-{uid} a:hover {{ text-decoration:underline; }}
.vxtxt-{uid} button {{
    background:linear-gradient(135deg,{accent},{secondary});
    color:#fff; border:none; padding:9px 20px;
    border-radius:9px; cursor:pointer; font-weight:600;
    font-size:14px; margin-top:10px;
    transition:transform .2s,box-shadow .2s;
    box-shadow:0 4px 14px {accent}55;
}}
.vxtxt-{uid} button:hover {{
    transform:translateY(-2px);
    box-shadow:0 8px 20px {accent}77;
}}
.vxtxt-{uid}::-webkit-scrollbar{{width:5px;}}
.vxtxt-{uid}::-webkit-scrollbar-thumb{{background:{accent};border-radius:5px;}}
</style>
<div class="vxtxt-{uid}">{content}</div>
"""
        self._add_to_slot(html, slot)
        print(f"  ✔ Texto añadido → {slot}")

        print("╔══════════════════════════════╗")
        print("║             Text             ║")
        print("╚══════════════════════════════╝")

        if content:
            print(f"Content: ", content[:100])

        if align:
            print(f"Align: {align}")

        if glass:
            print(f"Glass: {glass}")

        if border_accent:
            print(f"Border Accent: {border_accent}")

        if slot_grid:
            print(f"Slot: {slot}, Row: {row}, Col: {col}, Height: {height}, Width: {width}")

        return self

    # ────────────────────────────────────────────────────────
    #  PROGRESO / KPI BAR
    # ────────────────────────────────────────────────────────
    def add_progress(
        self,
        items: list[dict],
        title: str = "",
        slot_grid: tuple = ("div1", 1, 1, 1, 1),
    ):
        """
        items: lista de dicts con claves 'label', 'value' (0-100), y opcionalmente 'color'.
        """
        slot, row, col, height, width = slot_grid
        self._register_block(slot, row, col, height, width)

        bg_page, accent, secondary, text_col = self.colors
        uid = self._uid()

        bars_html = ""
        for i, item in enumerate(items):
            val = max(0, min(100, item.get("value", 0)))
            lbl = item.get("label", f"Item {i+1}")
            clr = item.get("color", accent)
            delay = i * 0.08
            bars_html += f"""
<div style="margin-bottom:14px;">
    <div style="display:flex;justify-content:space-between;
                color:{text_col};font-size:13px;margin-bottom:5px;font-weight:500;">
        <span>{lbl}</span>
        <span style="color:{clr};font-weight:700;">{val}%</span>
    </div>
    <div style="background:{text_col}18;border-radius:99px;height:8px;overflow:hidden;">
        <div style="
            height:100%;width:0;background:linear-gradient(90deg,{clr},{clr}bb);
            border-radius:99px;box-shadow:0 0 8px {clr}66;
            animation:vxbar{uid}{i} .9s {delay:.2f}s cubic-bezier(.16,1,.3,1) forwards;
        "></div>
    </div>
</div>
<style>
@keyframes vxbar{uid}{i} {{
    from{{width:0}} to{{width:{val}%}}
}}
</style>
"""

        title_html = f'<div style="color:{text_col};font-weight:700;font-size:15px;margin-bottom:16px;">{title}</div>' if title else ""

        html = f"""
<div style="background:linear-gradient(135deg,{bg_page},{secondary}18);
            border-radius:16px;padding:20px;width:100%;height:100%;
            box-sizing:border-box;overflow:auto;
            animation:vxpIn .5s cubic-bezier(.16,1,.3,1) both;">
<style>@keyframes vxpIn{{from{{opacity:0;transform:translateY(8px)}}to{{opacity:1;transform:none}}}}</style>
{title_html}
{bars_html}
</div>
"""
        self._add_to_slot(html, slot)
        print(f"  ✔ Progress añadido → {slot}")
        print("╔══════════════════════════════╗")
        print("║           Progress           ║")
        print("╚══════════════════════════════╝")
        if title:
            print(f"Title: {title}")

        if isinstance(items, dict):
            print(f"Items: ", items)

        if isinstance(items, list):
            for item in items:
                print(f"  - {item['label']}: {item['value']}%")


        if slot_grid:
            print(f"Slot: {slot}, Row: {row}, Col: {col}, Height: {height}, Width: {width}")

        return self

    # ────────────────────────────────────────────────────────
    #  TEXT
    # ────────────────────────────────────────────────────────
        return self

    # ────────────────────────────────────────────────────────
    #  BADGE / CHIP LIST
    # ────────────────────────────────────────────────────────
    def add_badges(
        self,
        items: list[str],
        title: str = "",
        slot_grid: tuple = ("div1", 1, 1, 1, 1),
    ):
        slot, row, col, height, width = slot_grid
        self._register_block(slot, row, col, height, width)

        bg_page, accent, secondary, text_col = self.colors
        uid = self._uid()

        colors_cycle = [accent, secondary, "#FF6B6B", "#FFD93D", "#6BCB77", "#4D96FF",
                        "#A8DADC", "#E76F51", "#00B4D8", "#C77DFF"]
        badges = "".join(
            f'<span style="background:{colors_cycle[i%len(colors_cycle)]}22;'
            f'color:{colors_cycle[i%len(colors_cycle)]};border:1px solid '
            f'{colors_cycle[i%len(colors_cycle)]}55;padding:5px 13px;border-radius:99px;'
            f'font-size:13px;font-weight:600;white-space:nowrap;'
            f'animation:vxbdg .4s {i*0.04:.2f}s cubic-bezier(.16,1,.3,1) both;">{b}</span>'
            for i, b in enumerate(items)
        )
        title_html = f'<div style="color:{accent};font-weight:700;font-size:15px;margin-bottom:14px;">{title}</div>' if title else ""

        html = f"""
<style>
@keyframes vxbdg{{from{{opacity:0;transform:scale(.8)}}to{{opacity:1;transform:scale(1)}}}}
</style>
<div style="background:linear-gradient(135deg,{bg_page},{secondary}18);
            border-radius:16px;padding:20px;width:100%;height:100%;
            box-sizing:border-box;overflow:auto;
            font-family:'Segoe UI',system-ui,sans-serif;">
{title_html}
<div style="display:flex;flex-wrap:wrap;gap:8px;">
{badges}
</div>
</div>
"""
        self._add_to_slot(html, slot)
        print(f"  ✔ Badges añadidos → {slot}")
        print("╔══════════════════════════════╗")
        print("║            Badges            ║")
        print("╚══════════════════════════════╝")
        if title:
            print(f"Title: {title}")

        if items:
            print(f"Items: ", items)

        if slot_grid:
            print(f"Slot: {slot}, Row: {row}, Col: {col}, Height: {height}, Width: {width}")

        return self

    # ────────────────────────────────────────────────────────
    #  EXPORT
    # ────────────────────────────────────────────────────────
    def export(self, filename: str = "report.html") -> str:
        bg_page, accent, secondary, text_col = self.colors

        css_grid = f"""
.vx-parent {{
    display:grid;
    grid-template-columns: repeat({self.num_cols}, 1fr);
    grid-template-rows: repeat({self.num_rows}, 1fr);
    gap:{self.gap}px;
    padding:{self.padding}px;
    box-sizing:border-box;
    width:100vw;
    height:calc(100vh - {self.navbar_height}px);
    margin-top:{self.navbar_height}px;
}}
"""
        css_slots = "\n".join(self.grid_css).replace("div", ".div")
        # fix: _register_block guarda ".divN" ya, pero por seguridad normalizamos
        css_slots_fixed = "\n".join(
            f".{line.split('.', 1)[1]}" if not line.startswith(".") else line
            for line in "\n".join(self.grid_css).splitlines()
        )

        slots_html = "".join(
            f'<div class="div{i} vx-slot">{"".join(self.slots[f"div{i}"])}</div>'
            for i in range(1, self.num_divs + 1)
        )

        html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{self.title}</title>
<style>
*, *::before, *::after {{ box-sizing:border-box; margin:0; padding:0; }}
html,body {{
    height:100%; width:100%;
    background:{bg_page};
    overflow:hidden;
    font-family:'Segoe UI',system-ui,sans-serif;
    color:{text_col};
}}

{css_grid}
{css_slots_fixed}

.vx-slot {{
    background:{secondary};
    border-radius:16px;
    overflow:hidden;
    display:flex;
    flex-direction:column;
    min-height:0;
    min-width:0;
    box-shadow:0 2px 16px rgba(0,0,0,.12);
    transition:box-shadow .3s;
}}
.vx-slot:hover {{
    box-shadow:0 6px 28px {accent}30;
}}

/* Plotly transparent bg */
.js-plotly-plot, .plotly, .plot-container {{ background:transparent !important; }}
.plotly-graph-div {{ width:100% !important; height:100% !important; }}
</style>
</head>
<body>
{self._build_navbar()}
<div class="vx-parent">
{slots_html}
</div>

<script>
/* ── Autoajuste Plotly ───────────────────────────────── */
(function(){{
    function resize(plot){{
        const p = plot.parentElement;
        if(!p) return;
        const r = p.getBoundingClientRect();
        if(r.width < 1 || r.height < 1) return;
        try{{
            Plotly.relayout(plot, {{width: r.width, height: r.height}});
        }}catch(e){{}}
    }}

    function resizeAll(){{
        document.querySelectorAll('.plotly-graph-div').forEach(resize);
    }}

    function init(){{
        const plots = document.querySelectorAll('.plotly-graph-div');
        if(!plots.length){{ requestAnimationFrame(init); return; }}

        /* Observer por slot */
        const ro = new ResizeObserver(entries => {{
            entries.forEach(e => {{
                e.target.querySelectorAll('.plotly-graph-div').forEach(resize);
            }});
        }});
        document.querySelectorAll('.vx-slot').forEach(el => ro.observe(el));

        /* Primera vez con pequeño delay para dejar renderizar */
        setTimeout(resizeAll, 100);
        setTimeout(resizeAll, 500);
    }}

    if(document.readyState === 'loading'){{
        document.addEventListener('DOMContentLoaded', init);
    }} else {{
        init();
    }}
    window.addEventListener('resize', resizeAll);
}})();
</script>
</body>
</html>
"""
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html)

        print(f"\n  ✔ HTML exportado → {filename}")
        return filename

    # ────────────────────────────────────────────────────────
    #  SHOW (servidor local)
    # ────────────────────────────────────────────────────────
    def show(self, filename="report.html", port=8000):
        print("Mostrando HTML...")
        self.export(filename)
        directory = os.path.dirname(os.path.abspath(filename))

        class Handler(SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=directory, **kwargs)
        time.sleep(3)
        def run():
            HTTPServer(("localhost", port), Handler).serve_forever()

        thread = threading.Thread(target=run)
        thread.start()
        time.sleep(0.5)
        url = f"http://localhost:{port}/{filename}"
        print(f"  🌐 Servidor en {url}")
        webbrowser.open(url)
        return self