from viewx.Slides import *

Presentation.reset()

Presentation.theme("neon") \
    .transition("zoom") \
    .meta(title="Demo Brutal 🚀", author="Emmanuel", date="2026") \
    .auto_advance(0)

# ─────────────────────────────
# SLIDE 1 — PORTADA
# ─────────────────────────────
with GradientSlide("Inicio", 1, ["#0f2027", "#203a43", "#2c5364"]):
    Title("Slides Framework").center().slide_in("down")
    Subtitle("Demo completo de componentes").center().pos(top=60).fade_in(0.5)

    GlowText("🔥 Animaciones 🔥").center().pos(top=75)

    Shape("circle", 120, 120, "#00ff88").pos(left=10, top=20).float_loop()
    Shape("rect", 80, 80, "#ff006e").pos(right=10, bottom=20).rotate_loop()

# ─────────────────────────────
# SLIDE 2 — TEXTO + LISTA
# ─────────────────────────────
with Slide("Texto", 2):
    Title("Componentes de Texto").center().pos(top=10)

    Text("Este framework es absurdamente flexible 😎", 22).center().pos(top=30)

    BulletList([
        "Animaciones CSS",
        "Layouts dinámicos",
        "Componentes reutilizables",
        "Exportación HTML"
    ]).center().pos(top=45).slide_in("left")

# ─────────────────────────────
# SLIDE 3 — CARDS
# ─────────────────────────────
with Slide("Cards", 3):
    Title("Cards").center().pos(top=10)

    Columns(
        [Card("Rápido", "Genera slides en segundos", "⚡")],
        [Card("Flexible", "Customizable total", "🎨")],
        [Card("Potente", "Animaciones incluidas", "🚀")]
    ).center().pos(top=35)

# ─────────────────────────────
# SLIDE 4 — CÓDIGO
# ─────────────────────────────
with Slide("Código", 4):
    Title("Código").center().pos(top=10)

    Code("""
for i in range(5):
    print("🔥 Python + Slides")
""", line_numbers=True).center().pos(top=35)

# ─────────────────────────────
# SLIDE 5 — STATS
# ─────────────────────────────
with Slide("Stats", 5):
    Title("Estadísticas").center().pos(top=10)

    IconStat("🚀", "100%", "Velocidad").pos(left=20, top=40)
    IconStat("🔥", "999", "Energía").pos(left=40, top=40)
    IconStat("💡", "∞", "Ideas").pos(left=60, top=40)

# ─────────────────────────────
# SLIDE 6 — BAR CHART
# ─────────────────────────────
with Slide("BarChart", 6):
    Title("Gráfico de Barras").center().pos(top=10)

    BarChart([
        {"label": "Python", "value": 90},
        {"label": "JS", "value": 75},
        {"label": "C++", "value": 60}
    ]).center().pos(top=35).animate_bars()

# ─────────────────────────────
# SLIDE 7 — TIMELINE
# ─────────────────────────────
with Slide("Timeline", 7):
    Title("Timeline").center().pos(top=10)

    Timeline([
        {"year": "2024", "title": "Inicio", "desc": "Aprendiendo"},
        {"year": "2025", "title": "Progreso", "desc": "Proyectos"},
        {"year": "2026", "title": "Dominio", "desc": "Modo dios 😎"}
    ]).center().pos(top=30)

# ─────────────────────────────
# SLIDE 8 — EFECTOS LOCOS
# ─────────────────────────────
with ParticleSlide("Animaciones", 8):
    Title("Animaciones").center().pos(top=10)

    MovingFigure("circle", 60).pos(left=20, top=40).move_path("orbit", 4)
    MovingFigure("rect", 60).pos(left=60, top=50).bounce_continuous()

    RotatingIcon("⚙️", 60).pos(left=45, top=70)

# ─────────────────────────────
# SLIDE 9 — PROGRESS
# ─────────────────────────────
with Slide("Progress", 9):
    Title("Progreso").center().pos(top=10)

    ProgressCircle(85, "Proyecto").pos(left=30, top=40)
    ProgressCircle(60, "IA").pos(left=55, top=40)

# ─────────────────────────────
# SLIDE FINAL
# ─────────────────────────────
with Slide("Final", 10):
    Title("FIN 🚀").center().pos(top=40).pulse_loop()

Presentation.show()