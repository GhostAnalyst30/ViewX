from viewx.datasets import load_dataset
from viewx import Report
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
# with r.doc.create(r.add_section("Visualización")):
#     r.add_image(
#         path="assets/ejemplo.png",
#         caption="Imagen de prueba",
#         width="0.6\\linewidth"
#     )

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
