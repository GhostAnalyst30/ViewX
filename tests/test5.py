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
