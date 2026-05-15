import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from viewx.HTML.html_engine import HTML

# ── Generar datos de demo ────────────────────────────────────────────────────
np.random.seed(42)
n = 200

fechas    = [datetime(2024, 1, 1) + timedelta(days=i) for i in range(n)]
regiones  = np.random.choice(["Norte", "Sur", "Este", "Oeste", "Centro"], n)
productos = np.random.choice(["Laptop", "Tablet", "Phone", "Monitor", "Teclado"], n)
ventas    = np.random.randint(500, 10000, n)
utilidad  = ventas * np.random.uniform(0.1, 0.4, n)
unidades  = np.random.randint(1, 50, n)
activo    = np.random.choice([True, False], n)

df = pd.DataFrame({
    "fecha"    : fechas,
    "region"   : regiones,
    "producto" : productos,
    "ventas"   : ventas,
    "utilidad" : utilidad.astype(int),
    "unidades" : unidades,
    "activo"   : activo,
})

print("Columnas disponibles:", df.columns.tolist())
print(df.head(3))

# ════════════════════════════════════════════════════════════════════════════
# DEMO 1 — Layout automático, tema por defecto
# ════════════════════════════════════════════════════════════════════════════
HTML.auto_generate(
    df,
    title    = "Demo 1 · Auto Layout",
    filename = "demo1_auto.html",
)

# ════════════════════════════════════════════════════════════════════════════
# DEMO 2 — Solo algunas columnas + tema oscuro
# ════════════════════════════════════════════════════════════════════════════
HTML.auto_generate(
    df,
    columns  = ["fecha", "ventas", "utilidad", "region"],
    template = "dark_enterprise",
    title    = "Demo 2 · Columnas seleccionadas",
    filename = "demo2_cols.html",
    authors  = [
        {"name": "Ana García",  "email": "ana@empresa.com"},
        {"name": "Luis Torres", "email": "luis@empresa.com"},
    ]
)

# ════════════════════════════════════════════════════════════════════════════
# DEMO 3 — Preset kpi_focus + tema void_indigo
# ════════════════════════════════════════════════════════════════════════════
HTML.auto_generate(
    df,
    columns  = ["ventas", "utilidad", "unidades", "region", "producto"],
    template = "void_indigo",
    title    = "Demo 3 · KPI Focus",
    filename = "demo3_kpi_focus.html",
    layout   = "kpi_focus",
    authors  = "Carlos Méndez",
)

# ════════════════════════════════════════════════════════════════════════════
# DEMO 4 — Preset chart_focus + tema glass_ocean
# ════════════════════════════════════════════════════════════════════════════
HTML.auto_generate(
    df,
    columns  = ["fecha", "ventas", "utilidad", "region"],
    template = "glass_ocean",
    title    = "Demo 4 · Chart Focus",
    filename = "demo4_chart_focus.html",
    layout   = "chart_focus",
)

# ════════════════════════════════════════════════════════════════════════════
# DEMO 5 — Preset table_first + tema cyberpunk_neon
# ════════════════════════════════════════════════════════════════════════════
HTML.auto_generate(
    df,
    columns  = ["fecha", "region", "producto", "ventas", "unidades"],
    template = "cyberpunk_neon",
    title    = "Demo 5 · Table First",
    filename = "demo5_table_first.html",
    layout   = "table_first",
)

# ════════════════════════════════════════════════════════════════════════════
# DEMO 6 — Layout 100% personalizado
#   Diseño:
#   [KPI ventas] [KPI utilidad] [KPI unidades] | [Chart barras región]
#   [Chart línea temporal (ventas)            ] | [Chart scatter        ]
#   [Tabla completa                                                      ]
# ════════════════════════════════════════════════════════════════════════════
HTML.auto_generate(
    df,
    columns  = ["fecha", "region", "ventas", "utilidad", "unidades"],
    template = "modern_green",
    title    = "Demo 6 · Layout Personalizado",
    filename = "demo6_custom.html",
    authors  = [{"name": "Equipo BI", "email": "bi@empresa.com"}],
    layout   = [
        # Fila 1: 3 KPIs a la izquierda + 1 chart a la derecha
        {"type": "kpi",   "index": 0, "row": 1, "col": 1,  "height": 2, "width": 3},
        {"type": "kpi",   "index": 1, "row": 1, "col": 4,  "height": 2, "width": 3},
        {"type": "kpi",   "index": 2, "row": 1, "col": 7,  "height": 2, "width": 3},
        {"type": "chart", "index": 1, "row": 1, "col": 10, "height": 7, "width": 3},  # barras región

        # Fila 2: línea temporal grande + scatter
        {"type": "chart", "index": 0, "row": 3, "col": 1,  "height": 5, "width": 6},  # línea tiempo
        {"type": "chart", "index": 2, "row": 3, "col": 7,  "height": 5, "width": 3},  # scatter

        # Fila 3: tabla completa
        {"type": "table",             "row": 8, "col": 1,  "height": 4, "width": 12},
    ]
)

# ════════════════════════════════════════════════════════════════════════════
# DEMO 7 — DataFrame con strings numéricos (prueba parseo automático)
# ════════════════════════════════════════════════════════════════════════════
df_strings = pd.DataFrame({
    "mes"      : ["Ene", "Feb", "Mar", "Abr", "May", "Jun"],
    "ingresos" : ["$12,500", "$9,800", "$15,200", "$11,000", "$18,400", "$14,700"],
    "costos"   : ["8500",    "7200",   "9800",    "8100",    "12000",   "10500"],
    "margen%"  : ["32%",     "27%",    "36%",     "26%",     "35%",     "29%"],
    "ciudad"   : ["Bogotá",  "Medellín","Cali",   "Bogotá",  "Cali",    "Medellín"],
})

HTML.auto_generate(
    df_strings,
    template = "corporate_blue",
    title    = "Demo 7 · Parseo Automático de Strings",
    filename = "demo7_parseo.html",
)

print("\n✅ Todos los dashboards generados:")
for i, name in enumerate([
    "demo1_auto.html",
    "demo2_cols.html",
    "demo3_kpi_focus.html",
    "demo4_chart_focus.html",
    "demo5_table_first.html",
    "demo6_custom.html",
    "demo7_parseo.html",
], 1):
    print(f"   {i}. {name}")