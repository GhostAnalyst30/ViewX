# 📦 ViewX — v2.0

**ViewX** es un paquete moderno de Python diseñado para generar **páginas HTML interactivas**, **dashboards dinámicos** y **visualizaciones inteligentes** que se adaptan automáticamente a los objetos agregados por el usuario.

Este proyecto ofrece una solución **ligera, intuitiva y escalable**, ideal para crear interfaces visuales llamativas sin depender de frameworks pesados… aunque una parte se encuentra basada en Streamlit mediante dependencias opcionales.

---

## ✨ Características principales

- ⚡ **Rápido y minimalista**: cero dependencias pesadas por defecto.  
- 🧩 **API intuitiva**: crea páginas y dashboards en segundos.  
- 📐 **Diseño adaptativo**: cada componente se acomoda automáticamente.  
- 🌐 **Modo HTML**: genera páginas `.html` totalmente autónomas.  
- 📊 **Modo Dashboard**: plantillas escalables con soporte opcional para Streamlit/Dash.  
- 🛠️ **Extensible**: añade tus propias plantillas y módulos personalizados.  
- 🔮 **Visión a futuro**: pensado para expandirse a interfaces inteligentes.

---

## Instalacion
```python
pip install viewx
```

## 🚀 Ejemplo rápido

### Crear una página HTML
```python
import pandas as pd
import numpy as np
import plotly.express as px
from viewx.HTML import HTML

# 1. Datos de ejemplo (Ventas por Categoría y Región)
df_ventas = pd.DataFrame({
    'Categoría': ['Electrónica', 'Hogar', 'Moda', 'Deportes', 'Juguetes'],
    'Ventas': [12500, 8400, 15200, 6700, 4300],
    'Margen': [0.15, 0.22, 0.18, 0.12, 0.25]
})

df_mensual = pd.DataFrame({
    'Mes': ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun'],
    'Ingresos': [45000, 48000, 52000, 49000, 55000, 61000]
})

# 2. Gráficos estilo Power BI
fig_bar = px.bar(df_ventas, x='Categoría', y='Ventas', color='Categoría', 
                 title="Ventas por Categoría", template="plotly_white")
fig_line = px.line(df_mensual, x='Mes', y='Ingresos', markers=True, 
                  title="Evolución de Ingresos", template="plotly_white")
fig_pie = px.pie(df_ventas, values='Ventas', names='Categoría', hole=0.4,
                title="Distribución de Ventas")

# 3. Inicializar Dashboard con Estética Power BI
# Temas: corporate_blue, dark_enterprise, modern_green, void_indigo, glass_ocean, cyberpunk_neon
dash = HTML(
    title="Dashboard de Rendimiento Corporativo",
    theme="corporate_blue", 
    navbar={
        "title": "BI Analytics",
        "items": [
            {"label": "Global", "link": "#"},
            {"label": "Ventas", "link": "#"},
            {"label": "Reportes", "link": "#"}
        ]
    }
)

# 4. Añadir Componentes usando el sistema de slot_grid original
# slot_grid = (fila_inicio, columna_inicio, filas_que_ocupa, columnas_que_ocupa)

# Fila superior: KPIs
dash.add_valuebox("Ingresos Totales", "$310K", icon="💰", slot_grid=(1, 1, 2, 3))
dash.add_valuebox("Crecimiento", "+12.5%", icon="📈", color="#107C10", slot_grid=(1, 4, 2, 3))
dash.add_valuebox("Clientes Activos", "1,452", icon="👥", color="#0078D4", slot_grid=(1, 7, 2, 3))
dash.add_valuebox("Tasa de Conversión", "4.2%", icon="🎯", color="#E63946", slot_grid=(1, 10, 2, 3))

# Fila central: Gráficos principales
dash.add_plot(fig_line, title="Tendencia Mensual", slot_grid=(3, 1, 5, 8))
dash.add_plot(fig_pie, title="Mix de Productos", slot_grid=(3, 9, 5, 4))

# Fila inferior: Tabla y Texto
dash.add_table(df_ventas, title="Detalle de Categorías", slot_grid=(8, 1, 5, 7))
dash.add_text("""
    <h3>Resumen de Insights</h3>
    <p>El segmento de <b>Moda</b> lidera las ventas con un margen saludable del 18%.</p>
    <p>Se observa un crecimiento sostenido en los ingresos mensuales, alcanzando un pico en <b>Junio</b>.</p>
    <p><i>Recomendación:</i> Aumentar stock en la categoría 'Hogar' debido al incremento de demanda previsto.</p>
""", slot_grid=(8, 8, 5, 5))

# 5. Generar Dashboard
output = dash.generate("powerbi_dashboard_pro.html")
print(f"Dashboard profesional generado: {output}")

```

![DashBoardIris](https://raw.githubusercontent.com/GhostAnalyst30/ViewX/main/images_for_git/DashBoard_Example.png
)

### Crear un DashBoard
```python
from viewx.DashBoard import DashBoard
from viewx.datasets import load_dataset

df = load_dataset("iris.csv")

db = DashBoard(df, title="StreamOps: Mini Dashboard", title_align="center")
db.set_theme(background="#071021", text="#E9F6F2", primary="#19D3A3", card="#0b1620")
# Sidebar
db.add_sidebar(db.comp_text("Parámetros del reporte"))
db.add_sidebar(db.comp_metric("Longitud del dataset", df.shape[0]))
db.add_sidebar(db.comp_metric("Cantidad de Flores", df["species"].unique().shape[0]))
# Main layout
db.add_blank()
db.add_row(
    col_widths=[1, 2, 1],
    components=[
        db.comp_blank(),
        db.comp_plot(x="sepal_length", y="sepal_width", kind="scatter", color="#FFB86B"),
        db.comp_metric("sepal_width", df["sepal_width"].sum(), delta="▲ 5%")
    ]
)

db.add_tabs({
    "Overview": [
        db.comp_title("Resumen por Región"),
        db.comp_table()
    ],
    "Details": [
        db.comp_title("Distribución de Flores"),
        db.comp_plot(x="species", y=None, kind="hist", color="#7C4DFF")
    ]
})

db.add_expander("Detalles técnicos", [
    db.comp_text("Este panel fue generado automáticamente."),
    db.comp_text("Metadata: filas=" + str(len(df)), size="12px")
], expanded=True)

db.run(open_browser=True)   
```

![DashBoard Streamlit](https://raw.githubusercontent.com/GhostAnalyst30/ViewX/main/images_for_git/DashBoard_Streamlit_1.png)

### Crear una Presentacion

```python
from viewx.Slides import (
    Presentation, Slide, Grid,
    Title, Subtitle, Text, BulletList,
    BarPlot, PiePlot, IconStat, RotatingIcon, MovingFigure,
    Button, Link
)

pres = Presentation("Demo Viewx.Slides", theme="dark")
pres.font("Inter").meta(author="Viewx", date="2026")

with Slide(title="Bienvenida al Motor", index=1, notes="Slide de portada del motor Viewx.Slides."):
    Title("Slides Engine v1.0").center("x").pos(top=10).zoom_in(duration=1.2)
    Subtitle("Framework de presentaciones dinámicas en Python").center("x").pos(top=26).slide_in("right")
    Text(
        "Este motor permite crear presentaciones HTML interactivas de forma programática, con posicionamiento, dimensiones, animaciones y componentes reutilizables.",
        color="#ffffff",
    ).center("x").pos(top=42).size(width="68%").align("center").fade_in(delay=0.3)
    RotatingIcon("gear", size=64, color="#00f2ff").pos(right=6, top=8)
    MovingFigure("circle", color="rgba(0,242,255,.22)", size=180, path="drift").pos(left=8, bottom=10).z(1)
    Button("Ver GitHub", href="https://github.com/").center("x").pos(top=68).fade_in(delay=0.55)

with Slide(title="Componentes", index=2, bg="linear-gradient(135deg,#111827,#312e81)"):
    Title("Componentes incluidos").pos(left=6, top=8).slide_in("left")
    BulletList([
        "Textos, títulos, subtítulos y listas.",
        "Imágenes, vídeos, hipervínculos y botones.",
        "Estadísticas con iconos y figuras animadas.",
        "Gráficos interactivos basados en Plotly.",
    ]).pos(left=8, top=30).size(width="48%")
    with Grid(columns=3, gap=18).pos(left=58, top=26).size(width="36%"):
        IconStat("check", "12+", "Componentes")
        IconStat("chart", "4", "Gráficos")
        IconStat("bolt", "CSS", "Animaciones")
    Link("Ir a la portada", href="#").pos(left=8, bottom=12).link_to_slide(1)

with Slide(title="Gráficos", index=3):
    Title("Plotly integrado").pos(left=6, top=7).zoom_in()
    Text("Los gráficos se exportan como HTML interactivo usando Plotly por CDN.").pos(left=7, top=22).size(width="42%")
    BarPlot(["A", "B", "C", "D"], [24, 38, 31, 45], title="BarPlot").pos(left=7, top=38).size(width="40%", height="42%")
    PiePlot(["Python", "HTML", "CSS"], [55, 30, 15], title="PiePlot", hole=0.35).pos(left=54, top=25).size(width="38%", height="52%")

path = pres.export("viewx_slides_demo.html")
print(path) 
```

### Crear un Reporte

```python
from viewx.datasets import load_dataset
import seaborn as sns
import matplotlib.pyplot as plt
    
# ===============================
# 1️⃣ CREAR REPORTE
# ===============================
r = Report(
    title="Reporte Técnico ViewX",
    author="Emmanuel Ascendra"
)

# ===============================
# 2️⃣ TEXTO
# ===============================
r.add_text("Este reporte demuestra todas las capacidades del motor ViewX.\n")
r.add_text("Texto importante en negrita.", bold=True)

# ===============================
# 3️⃣ SECCIONES
# ===============================
with r.doc.create(r.add_section("Introducción")):
    r.add_text(
        "ViewX es un motor de generación de reportes científicos "
        "capaz de producir documentos profesionales usando Python."
    )

# ===============================
# 4️⃣ SUBSECCIÓN
# ===============================
with r.doc.create(r.add_subsection("Características principales")):
    r.add_itemize([
        "Texto estructurado",
        "Imágenes",
        "Tablas",
        "Código",
        "Gráficos científicos",
        "Multicolumnas",
        "Cajas de información"
    ])

# ===============================
# 5️⃣ TABLA
# ===============================
with r.doc.create(r.add_section("Tabla de resultados")):
    r.add_table(
        headers=["Modelo", "Accuracy", "F1"],
        rows=[
            ["Regresión", 0.82, 0.79],
            ["Árbol", 0.91, 0.88],
            ["Red neuronal", 0.94, 0.92],
        ],
        caption="Comparación de modelos"
    )

# ===============================
# 6️⃣ IMAGEN
# ===============================
with r.doc.create(r.add_section("Visualización")):
    r.add_image(
        path="assets/ejemplo.png",
        caption="Imagen de prueba",
        width="0.6\\linewidth"
    )

# ===============================
# 7️⃣ CÓDIGO
# ===============================
with r.doc.create(r.add_section("Código de ejemplo")):
    r.add_code("""
import numpy as np

x = np.linspace(0, 10, 50)
y = np.sin(x)
""")

# ===============================
# 8️⃣ MULTICOLUMNAS
# ===============================
with r.doc.create(r.add_section("Análisis en dos columnas")):
    r.begin_multicols(2)

    r.add_text(
        "Este bloque demuestra cómo dividir el contenido "
        "en múltiples columnas dentro del mismo documento."
    )

    r.add_itemize([
        "Ideal para papers",
        "Mejora lectura",
        "Ahorra espacio"
    ])

    r.end_multicols()

# ===============================
# 9️⃣ CAJA DESTACADA
# ===============================
with r.doc.create(r.add_section("Nota importante")):
    r.add_box(
        title="Observación clave",
        content="Todos los elementos se generan directamente desde Python.",
        color="green!20"
    )

# ===============================
# 🔟 GRÁFICO SIMPLE
# ===============================
with r.doc.create(r.add_section("Gráfico simple")):
    r.add_plot(
        x=[0, 1, 2, 3, 4],
        y=[0, 1, 4, 9, 16],
        caption="Crecimiento cuadrático"
    )

# ===============================
# 1️⃣1️⃣ MULTIGRÁFICO
# ===============================
with r.doc.create(r.add_section("Gráficos múltiples")):
    r.add_multiplot(
        plots=[
            ([0, 1, 2, 3], [0, 1, 4, 9]),
            ([0, 1, 2, 3], [0, 1, 8, 27]),
        ],
        caption="Comparación de funciones"
    )

# ===============================
# 1️⃣2️⃣ SALTO DE PÁGINA
# ===============================
r.new_page()
r.add_text("Contenido en una nueva página.")

# ===============================
# 1️⃣3️⃣ GENERAR PDF
# ===============================
r.build("reporte_demo")

```

![Report PDF](https://raw.githubusercontent.com/GhostAnalyst30/ViewX/main/images_for_git/Report_pdf_1.png)

### Analizar Datos en DataMatrix

```python
import pandas as pd
import numpy as np
from viewx.DataMatrix import DataMatrix

# 1. Crear un Dataset sintético que simule datos bibliométricos
data = {
    'Authors': [
        'Aria, M; Cuccurullo, C', 'Aria, M; Smith, J', 'Cuccurullo, C', 
        'Doe, J', 'Smith, J; Doe, J', 'Aria, M', 'Brown, A', 'Brown, A; Smith, J',
        'Gomez, P', 'Gomez, P; Aria, M', 'Doe, J', 'White, S', 'White, S; Brown, A',
        'Black, R', 'Black, R; Gomez, P', 'Green, T', 'Green, T; Aria, M',
        'Doe, J', 'Smith, J', 'Cuccurullo, C'
    ],
    'Year': [2017, 2017, 2018, 2018, 2019, 2019, 2020, 2020, 2021, 2021, 2022, 2022, 2023, 2023, 2024, 2024, 2025, 2025, 2026, 2026],
    'Journal': [
        'Journal of Informetrics', 'Journal of Informetrics', 'Scientometrics', 
        'Scientometrics', 'Nature', 'Nature', 'Science', 'Science',
        'Journal of Informetrics', 'Scientometrics', 'Nature', 'Science',
        'Journal of Informetrics', 'Scientometrics', 'Nature', 'Science',
        'Journal of Informetrics', 'Scientometrics', 'Nature', 'Science'
    ],
    'Citations': np.random.randint(0, 100, size=20),
    'Abstract': ['Resumen de prueba ' + str(i) for i in range(20)],
    'Keywords': ['bibliometrics; R', 'python; data science', 'metrics; science', 'analysis', 'data', 'python', 'r', 'metrics', 'science', 'mapping', 'analysis', 'data', 'python', 'r', 'metrics', 'science', 'mapping', 'analysis', 'data', 'python'],
    'Duplicate_Col': [1] * 20, # Columna constante para alerta
    'Missing_Col': [np.nan] * 15 + [1, 2, 3, 4, 5] # Columna con muchos nulos
}

df = pd.DataFrame(data)

# Añadir filas duplicadas para probar limpieza
df = pd.concat([df, df.iloc[:2]], ignore_index=True)

print("Dataset creado con", len(df), "filas.")

# 2. Usar DataMatrix
dm = DataMatrix(df)

# Limpiar datos
dm.clean_data(drop_duplicates=True, fill_na=True)

# Generar reporte
report_path = dm.generate_report("demo_datamatrix_report.html", title="Análisis Bibliométrico de Prueba")

print(f"Reporte generado exitosamente en: {report_path}")
```

## 🤝 Contribuciones

¡Todas las ideas, mejoras y plantillas son bienvenidas!
ViewX está diseñado para crecer y evolucionar con la comunidad.

## 📬 Contacto:
ascendraemmanuel@gmail.com