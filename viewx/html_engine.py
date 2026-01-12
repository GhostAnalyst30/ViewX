import os
import pandas as pd
import plotly.express as px
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading
import webbrowser

# ============================================================
#                         ViewX PRO
# ============================================================

class HTML:
    def __init__(
        self,
        data=None,
        title="ViewX Report",
        template: int = 0,
        num_divs: int = 1,
        num_cols: int = 1,
        num_rows: int = 1
    ):
        self.data = data
        self.title = title
        self.template = max(template, 0)

        self.num_divs = num_divs
        self.num_cols = num_cols
        self.num_rows = num_rows

        # CSS dinámico del grid
        self.grid_css = []

        # Contenido por slot
        self.slots = {f"div{i}": [] for i in range(1, num_divs + 1)}

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
        color="#4C6EF5",
        slot_grid=("div1", 1, 1, 1, 1),
        position_icon="left"
    ):
        slot, row, col, height, width = slot_grid
        self._register_block(slot, row, col, height, width)

        direction = "row-reverse" if position_icon == "right" else "row"

        box = f"""
        <div style="
            background:{color};
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
        ">
            <div style="font-size:48px; min-width:80px;">{icon}</div>
            <div>
                <div style="font-size:28px;font-weight:bold;">{value}</div>
                <div style="opacity:0.85;font-size:18px;">{title}</div>
            </div>
        </div>
        """

        self._add_to_slot(box, slot)
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
        self._register_block(slot, row, col, height, width)

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

        html_plot = fig.to_html(full_html=False, include_plotlyjs="cdn")
        self._add_to_slot(html_plot, slot)
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
        self._register_block(slot, row, col, height, width)

        df = self.data if columns in (None, "all") else self.data[columns]

        table_html = df.to_html(border=0)

        box = f"""
        <div style="
            overflow:auto;
            border:1px solid #ddd;
            padding:10px;
            border-radius:12px;
            width:100%; height:100%;
            box-sizing:border-box;
        ">
            {table_html}
        </div>
        """

        self._add_to_slot(box, slot)
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
        self._register_block(slot, row, col, height, width)

        box = f"""
        <div style="
            border:1px solid #ddd;
            padding:10px;
            border-radius:12px;
            width:100%; height:100%;
            box-sizing:border-box;
        ">
            {content}
        </div>
        """

        self._add_to_slot(box, slot)
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
html, body {{
    margin:0;
    padding:0;
    height:100%;
}}

{css_parent}
{css_divs}

table {{
    width:100%;
    border-collapse:collapse;
    font-family:Arial;
    font-size:13px;
}}

th, td {{
    border:1px solid #ccc;
    padding:6px;
}}
</style>
</head>

<body>
<div class="parent">
{''.join(f'<div class="div{i}">{"".join(self.slots[f"div{i}"])}</div>' for i in range(1, self.num_divs + 1))}
</div>
</body>
</html>
"""

        with open(filename, "w", encoding="utf-8") as f:
            f.write(html)

        return filename

    # ========================================================
    #                        SERVIDOR
    # ========================================================
    def show(self, filename="report.html", port=8000):
        self.export(filename)
        directory = os.path.dirname(os.path.abspath(filename))

        class Handler(SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=directory, **kwargs)

        def run():
            HTTPServer(("localhost", port), Handler).serve_forever()

        thread = threading.Thread(target=run)
        thread.start()
        webbrowser.open(f"http://localhost:{port}/{filename}")

if __name__ == "__main__":
    from viewx.datasets import load_dataset


    df = load_dataset("iris.csv")

    HTML(data=df, title="Reporte Demo",
        num_divs=10, num_cols=8, num_rows=8
        ) \
        .add_valuebox(
            title="Div1",
            value=df.shape[0],
            icon="📁",
            color="#3C8DAD",
            slot_grid=("div1", 1, 1, 2, 2)
        ) \
        .add_valuebox(
            "Div2", df.shape[1], "📐", "#4C6EF5",
            slot_grid=("div2", 1, 3, 2, 2)
        ) \
        .add_valuebox(
            "Div3", df.shape[1], "📊", "#20C997",
            slot_grid=("div3", 1, 5, 2, 2)
        ) \
        .add_valuebox(
            "Div4", df.shape[1], "📈", "#FAB005",
            slot_grid=("div4", 1, 7, 2, 2)
        ) \
        .add_plot(
            kind="scatter",
            x="sepal_length",
            y="sepal_width",
            title="Relación Sepal",
            slot_grid=("div5", 3, 1, 4, 2)
        ) \
        .add_plot(
            kind="box",
            x="species",
            y="petal_length",
            title="Petal Length por especie",
            slot_grid=("div6", 3, 3, 4, 4)
        ) \
        .add_plot(
            kind="hist",
            x="petal_length",
            title="Distribución Petal Length",
            slot_grid=("div7", 3, 7, 4, 2)
        ) \
        .add_text(
            "<h3>Notas</h3><p>Texto libre de ejemplo</p>",
            slot_grid=("div8", 7, 1, 2, 3)
        ) \
        .add_valuebox(
            "Div9", "OK", "✅", "#51CF66",
            slot_grid=("div9", 7, 4, 2, 2)
        ) \
        .add_table(
            columns="all",
            slot_grid=("div10", 7, 6, 2, 3)
        ) \
        .show("demo_report2.html", port=8001)