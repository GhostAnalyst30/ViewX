from viewx.datasets import load_dataset
from viewx.HTML import HTML

# -----------------------------
# DATASET
# -----------------------------
df = load_dataset("iris.csv")

# -----------------------------
# DASHBOARD
# -----------------------------
(
HTML(
    data=df,
    title="Reporte Iris — ViewX",
    template_color=0,
    num_divs=8,
    num_cols=4,
    num_rows=5,
    navbar = {
    "title": "Mi Dashboard 🚀",
    "items": [
        {"label": "Inicio", "link": "#"},
        {"label": "Reportes", "link": "#"},
        {"label": "Datos", "link": "#"}
    ]
    }
)

# ===== VALUE BOXES =====
.add_valuebox(
    title="Filas",
    value=len(df),
    icon="📄",
    slot_grid=("div1", 1, 1, 1, 1)
)
# slot_grid = ("div#", fila_inicial, columna_inicial, alto, ancho)

.add_valuebox(
    title="Prom Sepal Length",
    value=round(df["sepal_length"].mean(), 2),
    icon="📏",
    slot_grid=("div2", 1, 2, 1, 1)
)

.add_valuebox(
    title="Prom Petal Width",
    value=round(df["petal_width"].mean(), 2),
    icon="🌸",
    slot_grid=("div3", 1, 3, 1, 1)
)

.add_text(
    """
    <h2>Iris Dataset Dashboard</h2>
    <p>Este DashBoard esta enlazado con el anterior</p>
    <a href="demo_viewx.html">
        <button>Ir al Main</button>
    </a>

    """,
    slot_grid=("div4", 1, 4, 1, 1)
)

# ===== PLOTS =====
.add_plot(
    kind="scatter",
    x="sepal_length",
    y="sepal_width",
    title="Sepal Length vs Width",
    slot_grid=("div5", 2, 1, 2, 2),
    height = 350
)


.add_plot(
    kind="box",
    x="species",
    y="petal_width",
    title="Petal Width por especie",
    slot_grid=("div6", 4, 1, 2, 2),
    height = 350
)

.add_plot(
    kind="bar",
    x="species",
    y="sepal_length",
    title="Promedio Sepal Length",
    slot_grid=("div7", 4, 3, 2, 2),
    height = 350
)

# ===== TABLE =====
.add_table(
    columns="all",
    slot_grid=("div8", 2, 3, 2, 2)
)

.show("demo_viewx.html", port=8001)
)


