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
