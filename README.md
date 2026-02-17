# 📦 ViewX — Librería de Visualización Adaptativa para Python

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
from viewx.datasets import load_dataset
from viewx import HTML

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
    template_color=1,
    num_divs=8,
    num_cols=4,
    num_rows=5
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
    "<h2>Iris Dataset Dashboard</h2><p>Este DashBoard fue desarrollado por Emmanuel Ascendra con Viewx</p>",
    slot_grid=("div4", 1, 4, 1, 1)
)

# ===== PLOTS =====
.add_plot(
    kind="scatter",
    x="sepal_length",
    y="sepal_width",
    title="Sepal Length vs Width",
    slot_grid=("div5", 2, 1, 2, 2)
)


.add_plot(
    kind="box",
    x="species",
    y="petal_width",
    title="Petal Width por especie",
    slot_grid=("div6", 4, 1, 2, 2)
)

.add_plot(
    kind="bar",
    x="species",
    y="sepal_length",
    title="Promedio Sepal Length",
    slot_grid=("div7", 4, 3, 2, 2)
)

# ===== TABLE =====
.add_table(
    columns="all",
    slot_grid=("div8", 2, 3, 2, 2)
)

.show("demo_viewx.html", port=8001)
)

```

![DashBoardIris](https://raw.githubusercontent.com/GhostAnalyst30/ViewX/main/images_for_git/DashBoard%20Iris.png
)

### Crear un DashBoard
```python
from viewx import DashBoard
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