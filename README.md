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
from viewx.datasets import load_iris
from viewx.HTML import HTML

df = load_iris()

page = HTML(
    data=df,
    title="ViewX",
    template_color=0,
    num_divs=8,
    num_cols=4,
    num_rows=5,
    gap=8,
    padding=8,
    navbar={
        "title": "ViewX v2.0",
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
# Atributos
print("Colores: ", page.templates)
print("Altura Barra de Navegacion (px):", page.navbar_height)
print("Tamaño de fuente del titulo (px):", page.title_font_size)
print("Tamaño de fuente de los items (px):", page.items_font_size)

page.add_valuebox(
    title="Registros",
    value=f"{df['species'].count()}",
    icon="🌸",
    slot_grid=("div1", 1, 1, 1, 1),
    subtitle=f"{df['species'].unique().shape[0]} especies",
)
# slot_grid = ("div#", fila_inicial, columna_inicial, alto, ancho)

page.add_valuebox(
    title="Promedio Sepal Length",
    value=f"{round(df['sepal_length'].mean(), 2)}",
    icon="🌸",
    slot_grid=("div2", 1, 2, 1, 1)
)

page.add_valuebox(
    title="Promedio Petal Width",
    value=round(df["petal_width"].mean(), 2),
    icon="🌸",
    slot_grid=("div3", 1, 3, 1, 1)
)

page.add_text(
    """
    <h2>ViewX v2.0</h2>
    <p>Iris Dataset Dashboard</p>
    <p>Este DashBoard fue desarrollado por Emmanuel Ascendra con ViewX</p>
    """,
    slot_grid=("div4", 1, 4, 1, 1),
    align="center",
    glass=False,
    border_accent=True
)

page.add_plot(
    kind="scatter",
    x="sepal_length",
    y="sepal_width",
    title="Sepal Length vs Width",
    slot_grid=("div5", 2, 1, 2, 2)
)

page.add_table(
    columns="all",
    searchable=True,
    striped=True,
    slot_grid=("div6", 2, 3, 2, 2)
)   

page.add_plot(
    kind="box",
    x="species",
    y="petal_width",
    title="Petal Width por especie",
    slot_grid=("div7", 4, 1, 2, 2)
)

page.add_plot(
    kind="bar",
    x="species",
    y="sepal_length",
    title="Promedio Sepal Length",
    slot_grid=("div8", 4, 3, 2, 2)
)

page.show("demo_iris.html", port=8000)

```

![DashBoardIris](https://raw.githubusercontent.com/GhostAnalyst30/ViewX/main/images_for_git/DashBoard%20Iris.png
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
# demo_plotly.py
from viewx.Slides import *
import pandas as pd
import numpy as np

# Configurar tema oscuro/neón
Presentation.theme("neon").transition("slide").meta(
    title="Gráficos Plotly",
    author="Data Science",
    date="2024"
)

# DataFrame para scatter
df_scatter = pd.DataFrame({
    'x': np.random.randn(100) * 10 + 50,
    'y': np.random.randn(100) * 5 + 30,
    'categoria': np.random.choice(['A', 'B', 'C'], 100)
})

# Datos para pie chart
ventas_por_producto = {
    'Electrónica': 35000,
    'Ropa': 28000,
    'Hogar': 22000,
    'Deportes': 18000
}

# Datos para barras (múltiples series)
ventas_mensuales = {
    'Producto A': [10, 20, 15, 30, 25, 40],
    'Producto B': [15, 25, 20, 35, 30, 45],
    'Producto C': [5, 10, 8, 15, 12, 20]
}
meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun']

# Datos para boxplot
df_boxplot = pd.DataFrame({
    'Grupo 1': np.random.normal(50, 10, 100),
    'Grupo 2': np.random.normal(60, 15, 100),
    'Grupo 3': np.random.normal(45, 8, 100)
})

# Datos para línea
df_line = pd.DataFrame({
    'fecha': pd.date_range('2024-01-01', periods=12, freq='M'),
    'ventas': np.cumsum(np.random.randint(100, 500, 12)),
    'costos': np.cumsum(np.random.randint(50, 300, 12))
})

# ============================================================
# SLIDES
# ============================================================

with Slide("Scatter Plot", index=1):
    Title("📈 Scatter Plot Interactivo").center("x").pos(top=10)
    
    # Gráfico con tamaño personalizado
    ScatterPlot(
        df_scatter, x_col="x", y_col="y", color_col="categoria",
        title="Distribución de Datos", x_label="Eje X", y_label="Eje Y"
    ).size(width="80%", height="400px").center("x").pos(top=25).zoom_in()

with Slide("Pie Chart", index=2):
    Title("🥧 Gráfico de Pastel").center("x").pos(top=10)
    
    PieChart(
        ventas_por_producto,
        title="Ventas por Categoría",
        hole=0.3  # Donut chart
    ).size(width="500px", height="450px").center().zoom_in().pos(top=60)

with Slide("Barras Múltiples", index=3):
    Title("📊 Barras Agrupadas").center("x").pos(top=10)
    
    BarChart(
        ventas_mensuales, x_labels=meses,
        title="Ventas Mensuales por Producto",
        x_label="Mes", y_label="Ventas (k$)",
        barmode='group'
    ).size(width="80%", height="420px").center("x").pos(top=25).slide_in("left")

with Slide("Boxplot", index=4):
    Title("📦 Diagrama de Caja").center("x").pos(top=10)
    
    BoxPlot(
        df_boxplot,
        title="Comparación de Grupos",
        y_label="Valores"
    ).size(width="85%", height="450px").center("x").pos(top=25).fade_in()

with Slide("Histograma", index=5):
    Title("📊 Histograma").center("x").pos(top=10)
    
    Histogram(
        df_scatter, column="x", bins=20,
        title="Distribución de frecuencia",
        x_label="Valor", y_label="Frecuencia"
    ).size(width="75%", height="420px").center("x").pos(top=25).zoom_in()

with Slide("Líneas", index=6):
    Title("📈 Series Temporales").center("x").pos(top=10)
    
    LineChart(
        df_line, x_col="fecha", y_cols=["ventas", "costos"],
        title="Evolución mensual", x_label="Fecha", y_label="Monto (k$)"
    ).size(width="85%", height="450px").center("x").pos(top=25).slide_in("right")

# ============================================================
# EJEMPLO CON pos() Y size() PERSONALIZADOS
# ============================================================

with Slide("Personalizado", index=7):
    Title("🎨 Gráficos a Medida").center("x").pos(top=10)
    
    # Gráfico pequeño en esquina superior derecha
    PieChart(ventas_por_producto, hole=0).size(width="30%", height="350px").center("x").pos(top=20, right=20)
    
    # Gráfico grande centrado
    BarChart(
        {"A": [10, 20, 30, 40], "B": [15, 25, 35, 45]}, 
        x_labels=["Q1", "Q2", "Q3", "Q4"]
    ).size(width="30%", height="350px").center("x").pos(top=20, left=20)
    
    Text("Gráficos respetan pos() y size()", size=12).center("y").pos(top=20).fade_in(delay=0.5)

# ============================================================
# EJECUTAR
# ================ ============================================
if __name__ == "__main__":
    Presentation.show("plotly_demo.html")
    print("\n✅ Demo Plotly generada! Los gráficos respetan el tema y las dimensiones.")
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

## 🤝 Contribuciones

¡Todas las ideas, mejoras y plantillas son bienvenidas!
ViewX está diseñado para crecer y evolucionar con la comunidad.

## 📬 Contacto:
ascendraemmanuel@gmail.com