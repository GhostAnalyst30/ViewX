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

# ============================================================
# DATOS DE EJEMPLO
# ============================================================

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