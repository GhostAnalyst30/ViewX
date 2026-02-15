import os
import pandas as pd
import plotly.express as px
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading
import webbrowser
from typing import Optional, Tuple, Union
import time

# ============================================================
#                         ViewX PRO
# ============================================================

class HTML:
    def __init__(
        self,
        data=None,
        title="ViewX Report",
        template_color: Optional[Union[int, Tuple[str, str, str, str]]] = 0,
        num_divs: int = 1,
        num_cols: int = 1,
        num_rows: int = 1
    ):
        self.data = data
        self.title = title
        self.colors = self._resolve_colors(template_color)
        self.num_divs = num_divs
        self.num_cols = num_cols
        self.num_rows = num_rows

        # CSS dinámico del grid
        self.grid_css = []

        # Contenido por slot
        self.slots = {f"div{i}": [] for i in range(1, num_divs + 1)}

        print("¡Bienvenido a ViewX!")
        print("Encendiendo Motores...")

    def _resolve_colors(self, template_color):
        templates = {
            0: ("#0F172A","#1E293B","#3B82F6","#E5E7EB"),
            1: ("#F8FAFC","#FFFFFF","#10B981","#1F2937"),
            2: ("#FFF7ED","#FFFFFF","#F97316","#1C1917"),
        }

        if isinstance(template_color, int):
            return templates.get(template_color, templates[0])

        if isinstance(template_color, tuple):
            if len(template_color) != 4:    
                raise ValueError("La tupla debe tener 4 colores")
            return template_color

        return templates[0]

    # ========================================================
    #               REGISTRO DE BLOQUES
    # ========================================================
    def _add_to_slot(self, html, slot):
        if slot not in self.slots:
            raise ValueError(f"El slot '{slot}' no existe.")
        self.slots[slot].append(html)

    def _register_block(self, slot, row, col, height, width):
        # Validación
        if row < 1 or col < 1:
            raise ValueError("Fila y columna deben empezar en 1")

        if row + height - 1 > self.num_rows:
            raise ValueError("Bloque excede filas del grid")

        if col + width - 1 > self.num_cols:
            raise ValueError("Bloque excede columnas del grid")

        row_start = row
        row_end   = row + height
        col_start = col
        col_end   = col + width

        self.grid_css.append(
            f".{slot} {{ grid-area: {row_start} / {col_start} / {row_end} / {col_end}; }}"
        )

    # ========================================================
    #                     VALUEBOX
    # ========================================================
    def add_valuebox(
        self,
        title,
        value,
        icon="📊",
        color=None,
        slot_grid=("div1", 1, 1, 1, 1),
        position_icon="left",
        insert_css=None
    ):  

        slot, row, col, height, width = slot_grid
        if height < 1 or width < 1:
            raise ValueError("height y width deben ser >= 1")
        self._register_block(slot, row, col, height, width)

        direction = "row-reverse" if position_icon == "right" else "row"
        bg = color if color is not None else self.colors[2]
        extra = (insert_css.strip() + ";") if insert_css else ""

        box = f"""
        <div style="
            background:{bg};
            padding:20px;
            border-radius:15px;
            color:white;
            font-family:Arial;
            box-shadow:0 3px 10px rgba(0,0,0,0.15);
            width:100%; height:100%;
            box-sizing:border-box;
            display:flex;
            flex-direction:{direction};
            align-items:center;
            gap:15px;
            overflow:hidden;
            {extra}
        ">
            <div style="font-size:48px; min-width:80px;">{icon}</div>
            <div>
                <div style="font-size:28px;font-weight:bold;">{value}</div>
                <div style="opacity:0.85;font-size:18px;">{title}</div>
            </div>
        </div>
        """

        self._add_to_slot(box, slot)
        print("Cargando ValueBox...")
        return self


    # ========================================================
    #                       GRÁFICOS
    # ========================================================
    def add_plot(
        self,
        kind="scatter",
        x=None,
        y=None,
        z=None,
        title="",
        slot_grid=("div1", 1, 1, 1, 1)
    ):
        if self.data is None:
            raise ValueError("No hay datos cargados")
        

        slot, row, col, height, width = slot_grid
        if height < 1 or width < 1:
            raise ValueError("height y width deben ser >= 1")
        self._register_block(slot, row, col, height, width)

        # =========================
        # CREAR FIGURA
        # =========================
        match kind:
            case "scatter":
                fig = px.scatter(self.data, x=x, y=y, title=title)

            case "line":
                fig = px.line(self.data, x=x, y=y, title=title)

            case "bar":
                fig = px.bar(self.data, x=x, y=y, title=title)

            case "hist":
                fig = px.histogram(self.data, x=x, title=title)

            case "box":
                fig = px.box(self.data, x=x, y=y, title=title)

            case "pie":
                fig = px.pie(self.data, names=x, values=y, title=title)

            case "scatter_3d":
                fig = px.scatter_3d(self.data, x=x, y=y, z=z, title=title)

            case _:
                raise ValueError(f"Tipo '{kind}' no soportado")

        # =========================
        # APLICAR THEME
        # =========================
        bg, primary, secondary, text = self.colors
        color_seq = [primary, secondary, text]
        
        fig.update_layout(
            paper_bgcolor=bg,
            plot_bgcolor=bg,
            font=dict(color=text),
            title_font=dict(color=text),
            legend=dict(font=dict(color=text)),
            margin=dict(l=40, r=40, t=60, b=40),
            autosize=True
        )

        # ejes
        fig.update_xaxes(
            showgrid=True,
            gridcolor="rgba(128,128,128,0.25)",
            zeroline=False,
            color=text
        )

        fig.update_yaxes(
            showgrid=True,
            gridcolor="rgba(128,128,128,0.25)",
            zeroline=False,
            color=text
        )

        # =========================
        # COLORES SEGÚN TIPO
        # =========================
        if kind == "scatter":
            fig.update_traces(marker_color=text)

        elif kind == "line":
            fig.update_traces(line_color=text)

        elif kind == "bar":
            fig.update_traces(
                marker=dict(
                    color=primary,
                    line=dict(color=text, width=1.5)
                )
            )

        elif kind == "hist":
            fig.update_traces(marker_color=text)

        elif kind == "box":
            fig.update_traces(
                marker_color=primary,
                line_color=secondary,
                fillcolor=text
            )

        elif kind == "pie":
            fig.update_traces(marker=dict(colors=color_seq))

        elif kind == "scatter_3d":
            fig.update_traces(marker=dict(color=text))


        # =========================
        # EXPORTAR HTML
        # =========================
        config = {"responsive": True}
        
        html_plot = fig.to_html(full_html=False, include_plotlyjs="cdn", config=config)
        
        box = f"""
        <div style="
            width:100%;
            height:100%;
        ">
            {html_plot}
        </div>
        """

        self._add_to_slot(box, slot)
        print("Cargando Plot...")
        return self


    # ========================================================
    #                        TABLAS
    # ========================================================
    def add_table(
        self,
        columns=None,
        slot_grid=("div1", 1, 1, 1, 1)
    ):
        if self.data is None:
            raise ValueError("No hay datos cargados")
        
        
        slot, row, col, height, width = slot_grid
        if height < 1 or width < 1:
            raise ValueError("height y width deben ser >= 1")
        self._register_block(slot, row, col, height, width)

        df = self.data if columns in (None, "all") else self.data[columns]

        bg, primary, secondary, text = self.colors

        # clase única para no contaminar otras tablas
        import uuid
        cls = f"vx_table_{uuid.uuid4().hex[:8]}"

        table_html = df.to_html(classes=cls, border=0, index=False)

        style = f"""
        <style>
        .{cls} {{
            width:100%;
            border-collapse:collapse;
            font-family:Arial;
            background:{bg};
            color:{text};
        }}

        /* encabezado */
        .{cls} thead th {{
            background:{primary};
            color:white;
            padding:9px;
            text-align:left;
            position:sticky;
            top:0;
            z-index:2;
        }}

        /* celdas */
        .{cls} tbody td {{
            padding:7px;
            border-bottom:1px solid {text}22;
        }}

        /* zebra rows */
        .{cls} tbody tr:nth-child(even) {{
            background:{secondary}22;
        }}

        /* hover */
        .{cls} tbody tr:hover {{
            background:{primary}33;
            transition:background 0.15s;
        }}
        </style>
        """

        box = f"""
        <div style="
            overflow:auto;
            background:{bg};
            border-radius:12px;
            width:100%; height:100%;
            box-sizing:border-box;
            padding:10px;
        ">
            {style}
            {table_html}
        </div>
        """

        self._add_to_slot(box, slot)
        print("Cargando Tabla...")
        return self

    def add_sparkline(
        self,
        x,
        y,
        title="",
        slot_grid=("div1", 1, 1, 1, 1)
    ):
        if self.data is None:
            raise ValueError("No hay datos cargados")
        slot, row, col, height, width = slot_grid
        if height < 1 or width < 1:
            raise ValueError("height y width deben ser >= 1")
        self._register_block(slot, row, col, height, width)

        bg, primary, secondary, text = self.colors

        fig = px.line(self.data, x=x, y=y)

        fig.update_layout(
            paper_bgcolor="transparent",
            plot_bgcolor="transparent",
            margin=dict(l=0, r=0, t=20, b=0),
            height=120,
            showlegend=False,
            font=dict(color=text)
        )

        fig.update_xaxes(visible=False)
        fig.update_yaxes(visible=False)

        fig.update_traces(line=dict(color=primary, width=2))

        html_plot = fig.to_html(full_html=False, include_plotlyjs=False)

        box = f"""
        <div style="
            background:{bg};
            padding:15px;
            border-radius:12px;
            color:{text};
            font-family:Arial;
            width:100%; height:100%;
            box-sizing:border-box;
        ">
            <div style="margin-bottom:6px; font-weight:bold;">
                {title}
            </div>
            {html_plot}
        </div>
        """

        self._add_to_slot(box, slot)
        print("Cargando Sparkline...")
        return self



    # ========================================================
    #                        TEXTO
    # ========================================================
    def add_text(
        self,
        content,
        slot_grid=("div1", 1, 1, 1, 1)
    ):
        slot, row, col, height, width = slot_grid
        if height < 1 or width < 1:
            raise ValueError("height y width deben ser >= 1")
        self._register_block(slot, row, col, height, width)

        bg, primary, secondary, text = self.colors

        box = f"""
        <div style="
            background:{bg};
            color:{text};
            border:1px solid {text}22;
            padding:14px;
            border-radius:12px;
            width:100%; height:100%;
            box-sizing:border-box;
            line-height:1.5;
            overflow:auto;
            font-family:Arial;
        ">
            {content}
        </div>
        """

        self._add_to_slot(box, slot)
        print("Cargando Texto...")
        return self


    # ========================================================
    #                        EXPORT
    # ========================================================
    def export(self, filename="report.html"):
        css_parent = f"""
        .parent {{
            display:grid;
            grid-template-columns: repeat({self.num_cols}, 1fr);
            grid-template-rows: repeat({self.num_rows}, 1fr);
            width:100vw;
            height:100vh;
            box-sizing:border-box;

            min-height: 100vh;

            align-items: stretch;
            justify-items: stretch;
        }}
        """

        css_divs = "\n".join(self.grid_css)

        html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>{self.title}</title>
<style>
html {{
    height:100%;
}}

body {{
    margin:0;
    padding:0;
    min-height:100%;
    background-color:{self.colors[0]};
}}

.js-plotly-plot, .plotly, .plot-container {{
    background: transparent !important;
}}

.viewx-slot {{
    background: {self.colors[1]};
    border-radius: 14px;
    padding: 14px;
    box-sizing: border-box;
    overflow: hidden;
    transition: 0.2s ease;

    width: 100%;
    height: 100%;
}}

.viewx-slot:hover {{
    box-shadow: 0 6px 20px rgba(0,0,0,0.08);
}}

.plotly-graph-div {{
    width:100% !important;
    height:100% !important;
}}

.js-plotly-plot {{
    width:100% !important;
    height:100% !important;
}}

.plot-container, .svg-container {{
    width:100% !important;
    height:100% !important;
}}


{css_parent}
{css_divs}

table { ... }
th, td { ... }

</style>
</head>

<body>
<div class="parent">
{''.join(f'<div class="div{i} viewx-slot">{"".join(self.slots[f"div{i}"])}</div>' for i in range(1, self.num_divs + 1))}
</div>
<script>
function viewx_attach_resize(){{
    const plots = document.querySelectorAll(".plotly-graph-div");

    if(plots.length === 0){{
        setTimeout(viewx_attach_resize, 200);
        return;
    }}

    plots.forEach(plot => {{
        const parent = plot.parentElement;

        const ro = new ResizeObserver(() => {{
            Plotly.Plots.resize(plot);
        }});

        ro.observe(parent);
    }});
}}

window.addEventListener("DOMContentLoaded", () => {{
    setTimeout(viewx_attach_resize, 300);
}});
</script>

</body>
</html>
"""

        with open(filename, "w", encoding="utf-8") as f:
            f.write(html)

        print("Exportando HTML...")

        return filename

    # ========================================================
    #                        SERVIDOR
    # ========================================================
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
        webbrowser.open(f"http://localhost:{port}/{filename}")