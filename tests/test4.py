import pandas as pd
from viewx.HTML import HTML

# 1. Crear datos de ejemplo
df_ventas = pd.DataFrame({
    'Mes': ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'],
    'Ventas': [120, 135, 148, 170, 195, 210, 245, 268, 290, 310, 335, 400],
    'Beneficio': [30, 35, 42, 51, 58, 63, 73, 80, 87, 93, 100, 120],
    'Clientes': [45, 48, 52, 58, 65, 72, 80, 88, 95, 102, 110, 125]
})

# Datos para gráfico de barras
df_productos = pd.DataFrame({
    'Producto': ['Producto A', 'Producto B', 'Producto C', 'Producto D', 'Producto E'],
    'Ventas': [450, 320, 280, 190, 150]
})

# Datos para scatter
df_clientes = pd.DataFrame({
    'Edad': [25, 32, 28, 45, 38, 29, 51, 42, 35, 30],
    'Gasto': [120, 200, 150, 300, 250, 180, 400, 320, 220, 160],
    'Segmento': ['Joven', 'Adulto', 'Joven', 'Senior', 'Adulto', 'Joven', 'Senior', 'Adulto', 'Adulto', 'Joven']
})

# 2. Configurar el dashboard
dashboard = HTML(
    title="📊 Dashboard Ejecutivo - Demo",
    theme="corporate_blue",  # Temas: corporate_blue, dark_enterprise, modern_green, void_indigo, glass_ocean, cyberpunk_neon
    cols=12,  # Grid de 12 columnas
    rows=12,  # 12 filas de altura
    gap=16,
    padding=20,
    navbar={
        "title": "📈 ViewX PRO",
        "items": [
            {"label": "Inicio", "link": "#"},
            {"label": "Ventas", "link": "#"},
            {"label": "Clientes", "link": "#"},
            {"label": "Reportes", "link": "#"}
        ]
    }
)

# 3. Añadir componentes (row, col, height, width)
# Fila 1: KPIs
dashboard.add_valuebox("Ventas Totales", "$2.8M", "💰", row=1, col=1, height=2, width=3)
dashboard.add_valuebox("Beneficio Neto", "$942K", "📈", "#00A86B", row=1, col=4, height=2, width=3)
dashboard.add_valuebox("Clientes Activos", "1,247", "👥", "#FF6B35", row=1, col=7, height=2, width=3)
dashboard.add_valuebox("Tasa Conversión", "24.5%", "🎯", "#9B59B6", row=1, col=10, height=2, width=3)

# Fila 2-5: Gráfico de líneas (ventas mensuales) - Método sencillo con datos
dashboard.add_chart(
    data=df_ventas,
    chart_type="line",
    x="Mes",
    y="Ventas",
    title="📈 Evolución de Ventas 2024",
    row=3, col=1, height=10, width=6
)

# Fila 2-5: Gráfico de barras (productos) - Otro ejemplo sencillo
dashboard.add_chart(
    data=df_productos,
    chart_type="bar",
    x="Producto",
    y="Ventas",
    title="🏷️ Ventas por Producto",
    row=3, col=7, height=10, width=6
)

# 4. Generar el archivo
dashboard.generate("mi_dashboard.html")