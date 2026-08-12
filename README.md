# ViewX — v0.3.0

**ViewX** es una librería de visualización para Python enfocada en **analistas de datos e ingenieros**: gráficas interactivas y estáticas en una línea, dashboards HTML, reportes EDA, presentaciones y PDFs — todo con una API unificada y mínima.

```python
import viewx as vx
df = vx.load_dataset("iris.csv")

vx.plot(df, x="sepal_length", y="petal_length")           # gráfica interactiva en 1 línea
vx.Dashboard.auto(df).save("dash.html")                   # dashboard automático
vx.DataMatrix(df).analyze().save("eda.html")              # reporte EDA interactivo
vx.Presentation.auto(df).save("slides.html")              # slides automáticas
vx.Report.auto(df).save("reporte.pdf")                    # PDF (requiere pdflatex)
```

---

## Características principales

- **`vx.plot()`**: una llamada para 14 tipos de gráfica, interactiva (Plotly) o estática (matplotlib).
- **API unificada**: todos los motores exportan con `.save(path)` y `.show()`.
- **Temas compartidos**: un mismo nombre de tema (`dark_enterprise`, `glass_ocean`, …) funciona en dashboards, slides, EDA y gráficas. `vx.set_theme()` lo fija globalmente.
- **Modo automático**: `Dashboard.auto()`, `Presentation.auto()`, `Report.auto()` analizan el DataFrame y eligen KPIs y gráficas por ti.
- **Pensado para datasets grandes**: downsampling automático (>10k puntos), WebGL para scatter grandes, muestreo estratificado en el explorador EDA.
- **Ligero**: núcleo con solo numpy + pandas + plotly. matplotlib y pylatex son extras opcionales.

---

## Instalación

```bash
pip install viewx              # núcleo interactivo
pip install viewx[static]      # + gráficas estáticas (matplotlib)
pip install viewx[pdf]         # + reportes PDF (pylatex; requiere pdflatex)
pip install viewx[all]         # todo
```

---

## Gráficas rápidas: `vx.plot()`

```python
import viewx as vx

# Interactiva (Plotly). En notebook se muestra sola.
vx.plot(df, kind="bar", x="region", y="revenue", title="Ventas por región")

# El tipo se infiere de los dtypes si no pasas `kind`
vx.plot(df, x="date", y="revenue")            # datetime -> line
vx.plot(df, x="precio", y="margen")           # num-num -> scatter

# Estática (matplotlib) para papers / PDFs
vx.plot(df, kind="histogram", x="edad", static=True).save("hist.png")

# Objeto Chart: .save(), .show(), .fig (figura Plotly/matplotlib subyacente)
chart = vx.plot(df, kind="donut", x="pais", y="ventas")
chart.save("donut.html")
```

Tipos disponibles: `line`, `bar`, `bar_h`, `scatter`, `area`, `pie`, `donut`, `histogram`, `box`, `violin`, `heatmap`, `funnel`, `treemap`, `bubble`.

Series con más de 10.000 puntos se reducen automáticamente (desactivable con `downsample=False`); los scatter grandes usan WebGL.

---

## Temas

Seis temas canónicos válidos en **todos** los motores:
`corporate_blue` · `dark_enterprise` · `modern_green` · `void_indigo` · `glass_ocean` · `cyberpunk_neon`

```python
vx.set_theme("dark_enterprise")     # tema global por defecto
vx.Dashboard.auto(df).save("a.html")            # usa el tema global
vx.Presentation.auto(df, theme="glass_ocean")   # o por artefacto
```

---

## Dashboards HTML

```python
import viewx as vx

# Automático: analiza el DataFrame y arma KPIs + gráficas
vx.Dashboard.auto(df, theme="modern_green", title="Ventas").save("dash.html")

# Manual: grid de 12 columnas
dash = vx.Dashboard(
    title="Manual Dashboard", theme="modern_green",
    cols=12, rows=9,
    navbar={"title": "Manual Dashboard", "items": [{"label": "Home", "link": "#"}]},
    authors=[{"name": "Data Team", "email": "data@acme.com"}],
    data_button=True, df=df,
)
dash.add_valuebox("Total Revenue", "$2.4M", icon_key="dollar", row=1, col=1, height=2, width=3)
dash.add_infobox(df=df, variable="revenue", info=["mean", "median", "std"], row=3, col=1, height=4, width=3)
dash.add_chart(vx.plot(df, kind="bar_h", x="region", y="revenue"),      # acepta Charts de vx.plot
               title="Revenue by Region", row=3, col=4, height=4, width=9)
dash.add_chart(data=df, chart_type="line", x="date", y="revenue",       # o data + chart_type
               title="Daily Trend", row=7, col=1, height=3, width=12)
dash.save("demo_manual.html")     # dash.show() para abrir en el navegador
```

![DashBoardViewX](https://raw.githubusercontent.com/GhostAnalyst30/ViewX/main/images_for_git/DashBoard_Example.png)

---

## Presentaciones

```python
from viewx import Presentation, Slide
from viewx.Slides import Title, Subtitle, BulletList, BarPlot, PlotlyChart

# Automática
Presentation.auto(df, title="Dataset Overview", theme="void_indigo").save("auto_slides.html")

# Manual
pres = Presentation("Demo ViewX Slides", theme="dark_enterprise")
pres.font("Inter").meta(author="ViewX", date="2026")

with Slide(title="Bienvenida", notes="Portada"):
    Title("Slides Engine").center("x").pos(top=10).zoom_in(duration=1.2)
    Subtitle("Presentaciones HTML desde Python").center("x").pos(top=26)
    BulletList(["Animaciones CSS", "Gráficos Plotly", "Componentes reutilizables"]).pos(left=8, top=42)

with Slide(title="Gráficos"):
    Title("Plotly integrado").pos(left=6, top=7)
    BarPlot(["A", "B", "C"], [24, 38, 31], title="BarPlot").pos(left=7, top=30).size(width="40%", height="50%")
    PlotlyChart.from_figure(vx.plot(df, kind="donut", x="region", y="revenue"))  # embebe un Chart

pres.save("viewx_slides_demo.html")
```

---

## Reportes PDF

Requiere `pip install viewx[pdf]` y `pdflatex` en el sistema. Sin strings LaTeX: fracciones para anchos, colores CSS en cajas.

```python
from viewx import Report

# Automático: reporte de calidad del dataset
Report.auto(df, title="Quality Report").save("reporte.pdf")

# Manual
r = Report(title="Reporte Técnico", author="Emmanuel Ascendra")
r.text("Este reporte demuestra el motor ViewX.", bold=True)

with r.section("Introducción"):
    r.text("ViewX genera documentos profesionales desde Python.")
    with r.subsection("Características"):
        r.bullets(["Texto estructurado", "Tablas", "Gráficos", "Cajas de información"])

with r.section("Resultados"):
    r.add_table(
        headers=["Modelo", "Accuracy", "F1"],
        rows=[["Regresión", 0.82, 0.79], ["Red neuronal", 0.94, 0.92]],
        caption="Comparación de modelos",
    )
    r.add_image("assets/ejemplo.png", caption="Imagen", width=0.6)   # fracción del ancho
    r.add_line_plot(x=[0, 1, 2, 3], y=[0, 1, 4, 9], caption="Crecimiento cuadrático")
    r.add_box("Observación", "Todo se genera desde Python.", color="#DBEAFE")  # color CSS

r.save("reporte_demo.pdf")
```

![Report PDF](https://raw.githubusercontent.com/GhostAnalyst30/ViewX/main/images_for_git/Report_pdf_1.png)

---

## Análisis EDA con DataMatrix

```python
from viewx import DataMatrix

dm = DataMatrix(df)
dm.clean_data(drop_duplicates=True, fill_na=True)
dm.analyze()

print(dm.summary())        # métricas clave
print(dm.alerts())         # advertencias de calidad
print(dm.highlights())     # fortalezas del dataset

dm.save("eda.html", theme="dark_enterprise")   # reporte completo con explorador interactivo
# En una línea: DataMatrix(df).analyze().save("eda.html")
```

El reporte incluye Overview, perfil por variable, correlaciones, explorador interactivo con filtros (muestreo estratificado para datasets grandes) y muestra paginada.

---

## Integración StatsLibX

ViewX recibe payloads de StatsLibX vía `from_report_payload()`:

```python
from statslibx import DescriptiveStats, to_report_data, load_iris
from viewx import from_report_payload

df = load_iris()
summary = DescriptiveStats(df).summary()

# Opción 1 — método directo en el resultado
summary.to_html("iris.html", theme="dark_enterprise", data=df)

# Opción 2 — pipeline manual
payload = to_report_data(summary, include_figures=True, data=df)
from_report_payload(payload, target="html", filename="iris.html")
```

---

## Migración desde v0.2.x

| Antes (v0.2.x) | Ahora (v0.3.0) |
|---|---|
| `HTML(...)` | `Dashboard(...)` (`HTML` sigue siendo alias) |
| `dash.generate("f.html", show=True)` | `dash.save("f.html")` / `dash.show()` |
| `HTML.auto_generate(df, template=...)` | `Dashboard.auto(df, theme=...).save(path)` |
| `pres.export("f.html")` | `pres.save("f.html")` |
| `Presentation.auto_generate(df, ...)` | `Presentation.auto(df).save(path)` |
| `report.build("nombre")` | `report.save("nombre.pdf")` |
| `Report(twoColumn=True)` | `Report(two_column=True)` |
| `report.add_plot(x, y)` | `report.add_line_plot(x, y)` |
| `with r.doc.create(r.add_section(...))` | `with r.section(...)` |
| `dm.generate_report(path, show=...)` | `dm.save(path)` / `dm.show()` |
| Temas de slides `dark`/`ocean`/… | Alias que resuelven a los 6 temas canónicos |

Los métodos antiguos siguen funcionando con `DeprecationWarning`.

## Contribuciones

¡Todas las ideas, mejoras y plantillas son bienvenidas!
ViewX está diseñado para crecer y evolucionar con la comunidad.

## Contacto

ascendraemmanuel@gmail.com
