from viewx.datasets import load_iris
from viewx import HTML

df = load_iris()


# ── Dashboard ───────────────────────────────────────────
page = HTML(
    data=df,
    title="ViewX PRO — Demo Completo",
    template_color=0,          # Deep Space (oscuro)
    num_divs=14,
    num_cols=4,
    num_rows=6,
    gap=8,
    padding=8,
    navbar={
        "title": "ViewX PRO 🚀",
        "items": [
            {"label": "Inicio",    "link": "#"},
            {"label": "Ventas",    "link": "#"},
            {"label": "Análisis",  "link": "#"},
            {"label": "Acerca",    "link": "#"},
        ],
        "height": 64,
        "title_font_size": 20,
        "items_font_size": 14,
    }
)

# ── Fila 1: Value Boxes ─────────────────────────────────
page.add_valuebox(
    title="Total Ventas",
    value=f"${df['ventas'].sum():,}",
    icon="💰",
    slot_grid=("div1", 1, 1, 1, 1),
    subtitle=f"+{df['ventas'].pct_change().mean()*100:.1f}% promedio",
)
page.add_valuebox(
    title="Ganancia Total",
    value=f"${df['ganancia'].sum():,}",
    icon="📈",
    color="#00B894",
    slot_grid=("div2", 1, 2, 1, 1),
    subtitle=f"Margen: {df['margen'].mean():.1f}%",
)
page.add_valuebox(
    title="Satisfacción",
    value=f"{df['satisfaccion'].mean():.2f} ★",
    icon="⭐",
    color="#D4AF37",
    slot_grid=("div3", 1, 3, 1, 1),
    position_icon="right",
)
page.add_valuebox(
    title="Registros",
    value=f"{len(df):,}",
    icon="📋",
    color="#E94560",
    slot_grid=("div4", 1, 4, 1, 1),
    subtitle="últimos 120 días",
)

# ── Fila 2-3: Plots grandes ─────────────────────────────
page.add_plot(
    kind="line",
    x="mes", y="ventas",
    title="Evolución de Ventas",
    slot_grid=("div5", 2, 1, 2, 2),
    color="categoria",
)
page.add_plot(
    kind="bar",
    x="categoria", y="ventas",
    title="Ventas por Categoría",
    slot_grid=("div6", 2, 3, 1, 2),
    color="categoria",
)
page.add_table(
    columns=["mes", "ventas", "ganancia", "categoria", "margen"],
    slot_grid=("div7", 3, 3, 1, 2),
    max_rows=20,
    searchable=True,
    striped=True,
)

# ── Fila 4: Distribuciones ──────────────────────────────
page.add_plot(
    kind="box",
    x="categoria", y="ganancia",
    title="Distribución Ganancia",
    slot_grid=("div8", 4, 1, 1, 2),
)
page.add_plot(
    kind="violin",
    x="region", y="satisfaccion",
    title="Satisfacción por Región",
    slot_grid=("div9", 4, 3, 1, 2),
    color="region",
)

# ── Fila 5: Más plots ───────────────────────────────────
page.add_plot(
    kind="scatter",
    x="ventas", y="ganancia",
    title="Ventas vs Ganancia",
    slot_grid=("div10", 5, 1, 1, 1),
    color="categoria",
    size="satisfaccion",
)
page.add_plot(
    kind="hist",
    x="margen",
    title="Distribución del Margen %",
    slot_grid=("div11", 5, 2, 1, 1),
)
page.add_plot(
    kind="pie",
    x="categoria", y="ventas",
    title="Participación de Ventas",
    slot_grid=("div12", 5, 3, 1, 1),
)

# ── Progress bars ───────────────────────────────────────
page.add_progress(
    title="Metas por Región",
    items=[
        {"label": "Norte",  "value": 82, "color": "#7C3AED"},
        {"label": "Sur",    "value": 67, "color": "#00B894"},
        {"label": "Este",   "value": 91, "color": "#D4AF37"},
        {"label": "Oeste",  "value": 54, "color": "#E94560"},
    ],
    slot_grid=("div13", 5, 4, 1, 1),
)

# ── Texto / Card ────────────────────────────────────────
page.add_text(
    """
    <h2>ViewX PRO v2.0</h2>
    <p>Dashboard interactivo con autoajuste de gráficas, animaciones fluidas y componentes avanzados.</p>
    <p>✅ 12 tipos de gráficas &nbsp;|&nbsp; ✅ Tabla buscable &nbsp;|&nbsp; ✅ Progress bars</p>
    <button onclick="window.scrollTo(0,0)">↑ Volver arriba</button>
    """,
    slot_grid=("div14", 6, 1, 1, 4),
    align="center",
    glass=False,
    border_accent=True,
)

page.show("demo_viewx_pro.html", port=8001)