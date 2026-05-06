# Guía de Uso de `viewx.Slides`

`viewx.Slides` es un framework de Python diseñado para crear presentaciones HTML interactivas de forma programática. Permite definir slides con diversos componentes visuales, gráficos interactivos de Plotly, animaciones y temas personalizables, todo exportado a un único archivo HTML autocontenido.

## 1. Estructura del Módulo

El módulo `viewx.Slides` se organiza en los siguientes archivos:

*   `slides_engine.py`: Contiene las clases principales `Presentation`, `Slide` y `Grid`, así como la lógica de temas, animaciones CSS globales y la exportación final a HTML.
*   `components.py`: Define la clase base `Component` y todos los componentes visuales reutilizables como `Title`, `Text`, `Image`, `Button`, etc.
*   `charts.py`: Proporciona la clase base `PlotlyChart` y wrappers para diferentes tipos de gráficos interactivos de Plotly (`BarPlot`, `PiePlot`, `LinePlot`, etc.).
*   `__init__.py`: Expone la API pública del módulo, permitiendo importar las clases directamente desde `viewx.Slides`.

## 2. Instalación

Dado que `viewx.Slides` es un módulo local, la instalación consiste en colocar los archivos en la estructura de directorios correcta. Asumiendo que ya tienes los archivos `slides_engine.py`, `components.py`, `charts.py` y `__init__.py`:

1.  Crea una carpeta llamada `viewx` en tu directorio de trabajo.
2.  Dentro de `viewx`, crea otra carpeta llamada `Slides`.
3.  Coloca los archivos `slides_engine.py`, `components.py`, `charts.py` y `__init__.py` dentro de la carpeta `viewx/Slides/`.
4.  Asegúrate de que también exista un archivo `__init__.py` vacío directamente dentro de la carpeta `viewx/` (es decir, `viewx/__init__.py`).

Tu estructura de directorios debería verse así:

```
mi_proyecto/
├── tu_script.py
└── viewx/
    ├── __init__.py
    └── Slides/
        ├── __init__.py
        ├── slides_engine.py
        ├── components.py
        └── charts.py
```

## 3. Conceptos Fundamentales

### `Presentation`

La clase `Presentation` es el punto de entrada para crear tu presentación. Define propiedades globales como el título, el tema, el tamaño y la transición entre slides.

```python
from viewx.Slides import Presentation

# Inicializa una presentación con un título y un tema
pres = Presentation("Mi Primera Presentación", theme="dark")

# Configuración adicional
pres.font("Roboto").meta(author="Tu Nombre", date="2026-05-06")
pres.logo("https://ejemplo.com/logo.png")
pres.music("https://ejemplo.com/musica_fondo.mp3")
pres.auto_advance(seconds=5) # Avanza automáticamente cada 5 segundos
pres.kiosk(True) # Modo quiosco (sin controles de navegación)

# Puedes definir temas personalizados o modificar los existentes
pres.custom_theme("mi_tema", primary="#ff6347", text="#f0f0f0")
```

**Métodos clave de `Presentation`:**

*   `__init__(title, theme="dark", width=1280, height=720, transition="slide", show_numbers=True)`: Constructor.
*   `set_theme(name)`: Establece uno de los temas predefinidos (`dark`, `light`, `neon`, `ocean`, `sunset`, `corporate`).
*   `custom_theme(name="custom", **colors)`: Crea o modifica un tema con colores específicos (ej. `primary`, `accent`, `bg`, `text`).
*   `font(name, weights="...")`: Carga una fuente de Google Fonts y la aplica a la presentación.
*   `logo(url)`: Añade un logo a la presentación.
*   `music(url)`: Añade música de fondo.
*   `auto_advance(seconds)`: Configura el avance automático de slides.
*   `kiosk(value=True)`: Habilita o deshabilita el modo quiosco.
*   `meta(**metadata)`: Añade metadatos a la presentación (ej. `author`, `date`).
*   `add_css(css)`: Añade CSS personalizado a la presentación.
*   `export(filename="presentacion.html", open_browser=False)`: Genera el archivo HTML. Si `open_browser` es `True`, lo abre automáticamente.
*   `show(filename="presentacion.html")`: Exporta y abre la presentación en el navegador.

### `Slide`

Las slides se definen usando un `context manager` (`with Slide(...)`). Todos los componentes creados dentro de este bloque se añadirán automáticamente a esa slide.

```python
from viewx.Slides import Slide, Title, Text

with Slide(title="Mi Primera Slide", index=1, bg="#333", notes="Notas del presentador."):
    Title("Hola Mundo").center()
    Text("Este es un texto de ejemplo.").pos(top=50)

# También puedes usar imágenes o gradientes como fondo
with Slide(title="Fondo de Imagen", bg="https://ejemplo.com/imagen.jpg", overlay_opacity=0.5):
    # ... componentes

with Slide(title="Fondo Gradiente", bg="linear-gradient(45deg, #fe0000, #ff8c00)"):
    # ... componentes
```

**Parámetros clave de `Slide`:**

*   `title`: Título de la slide (usado en metadatos y navegación).
*   `index`: Número de la slide (opcional, se asigna automáticamente).
*   `bg`: Fondo de la slide (color CSS, gradiente CSS o URL de imagen).
*   `overlay_opacity`: Opacidad de una capa oscura sobre el fondo (útil para imágenes de fondo).
*   `notes`: Notas del presentador para esta slide.
*   `transition`: Transición específica para esta slide (anula la global de `Presentation`).

### `Grid`

El componente `Grid` permite organizar otros componentes en un layout de cuadrícula CSS, facilitando la creación de diseños complejos sin posicionamiento absoluto manual.

```python
from viewx.Slides import Grid, IconStat

with Slide(title="Layout con Grid"):
    with Grid(columns=2, gap=30).center().size(width="80%", height="60%"):
        IconStat("user", "1.2M", "Usuarios Activos")
        IconStat("database", "50TB", "Datos Almacenados")
        IconStat("rocket", "99.9%", "Uptime")
        IconStat("cloud", "Global", "Cobertura")
```

**Parámetros clave de `Grid`:**

*   `columns`: Número de columnas (ej. `2`, `"1fr 2fr"`).
*   `rows`: Número de filas (ej. `2`, `"auto 1fr"`).
*   `gap`: Espacio entre celdas de la cuadrícula.
*   `**styles`: Estilos CSS adicionales para el contenedor `Grid`.

## 4. Componentes Visuales

Todos los componentes heredan de la clase `Component` y comparten métodos para posicionamiento, tamaño, estilo y animaciones.

### Métodos Comunes de `Component`

| Método | Descripción | Ejemplo |
|---|---|---|
| `pos(left, top, right, bottom, unit="%")` | Posiciona el componente. | `.pos(left=10, top=20)` |
| `size(width, height)` | Establece las dimensiones. | `.size(width=300, height="auto")` |
| `dimension(width, height)` | Alias de `size`. | `.dimension(width="50%", height=200)` |
| `center(axis="both")` | Centra el componente (`"x"`, `"y"`, `"both"`). | `.center("x")` |
| `align(text_align="center")` | Alinea el texto dentro del componente. | `.align("left")` |
| `z(value)` | Establece el `z-index`. | `.z(10)` |
| `opacity(value)` | Establece la opacidad (0.0 a 1.0). | `.opacity(0.7)` |
| `color(value)` | Establece el color del texto. | `.color("#ff0000")` |
| `background(value)` | Establece el color de fondo. | `.background("blue")` |
| `font_size(value)` | Establece el tamaño de la fuente. | `.font_size(24)` |
| `weight(value)` | Establece el peso de la fuente. | `.weight(700)` |
| `padding(top, right, bottom, left)` | Establece el padding. | `.padding(20)` o `.padding(10, 20, 10, 20)` |
| `border(color, width, radius)` | Añade un borde. | `.border(color="red", width=2)` |
| `radius(value)` | Establece el `border-radius`. | `.radius(10)` |
| `shadow(intensity="md")` | Añade una sombra (`sm`, `md`, `lg`, `glow`). | `.shadow("lg")` |
| `card()` | Aplica estilos de tarjeta predefinidos. | `.card()` |
| `tooltip(text)` | Añade un tooltip al pasar el ratón. | `.tooltip("Información extra")` |
| `onclick(js)` | Ejecuta JavaScript al hacer clic. | `.onclick("alert(\'Clic!\\'")` |
| `link_to_slide(slide_number)` | Crea un enlace a otra slide. | `.link_to_slide(3)` |

**Animaciones de Entrada:**

*   `fade_in(delay=0.0, duration=0.65)`
*   `slide_in(direction="left", delay=0.0, duration=0.65)` (`left`, `right`, `up`, `down`)
*   `zoom_in(delay=0.0, duration=0.65)`
*   `zoom_out(delay=0.0, duration=0.65)`
*   `bounce(delay=0.0, duration=0.8)`
*   `flip(delay=0.0, duration=0.75)`
*   `spin(delay=0.0, duration=0.8)`

**Animaciones en Bucle:**

*   `pulse_loop(duration=1.6)`
*   `float_loop(duration=3.0)`
*   `rotate_loop(duration=3.0)`
*   `glow_loop(duration=2.0)`
*   `move_path(path_type="float", speed=3.0, delay=0.0)` (`float`, `x`, `orbit`, `drift`, `wave`, `heartbeat`, `pulse`, `rotate`)

### Componentes Específicos

*   `Title(text, **styles)`: Título principal de la slide.
*   `Subtitle(text, **styles)`: Subtítulo de la slide.
*   `Text(text, color=None, **styles)`: Bloque de texto general.
*   `BulletList(items, ordered=False, **styles)`: Lista de elementos (ordenada o desordenada).
*   `Image(src, alt="", **styles)`: Inserta una imagen.
*   `Video(src, controls=True, autoplay=False, loop=False, muted=False, poster="", **styles)`: Inserta un video.
*   `Hyperlink(text, href, target="_blank", **styles)` / `Link(...)`: Enlace de texto.
*   `Button(text, href="#", target="_self", **styles)`: Botón con enlace.
*   `IconStat(icon, value, label, prefix="", suffix="", **styles)`: Muestra una estadística con un icono, valor y etiqueta. Los iconos se pueden especificar por nombre (`gear`, `chart`, `star`, `check`, `bolt`, `user`, `users`, `database`, `cloud`, `rocket`, `warning`, `info`, `play`, `link`) o directamente como entidad HTML.
*   `RotatingIcon(icon, size=50, color="var(--vx-primary)", speed=4.0, **styles)`: Un icono que rota continuamente.
*   `MovingFigure(shape="circle", color="var(--vx-primary)", size=80, path="float", **styles)`: Una figura geométrica animada (`circle`, `rounded`, `diamond`, `square`).

## 5. Gráficos Interactivos (`charts.py`)

Los gráficos se basan en Plotly.js y se renderizan como HTML interactivo. Utilizan el tema de la presentación para una integración visual coherente.

*   `PlotlyChart(data, layout=None, config=None, **styles)`: Clase base para gráficos Plotly. Permite pasar directamente la estructura de datos, layout y configuración de Plotly.
*   `BarPlot(x, y, orientation="v", name="", color="#4f46e5", title="", **styles)`: Gráfico de barras.
*   `PiePlot(labels, values, title="", hole=0.0, colors=None, **styles)`: Gráfico de pastel (circular).
*   `DonutPlot(labels, values, title="", colors=None, **styles)`: Gráfico de dona (circular con agujero central).
*   `LinePlot(x, y, name="", color="#06b6d4", title="", fill=False, **styles)`: Gráfico de líneas (con opción de área rellena).
*   `ScatterPlot(x, y, labels=None, name="", color="#22c55e", title="", **styles)`: Gráfico de dispersión.
*   `AreaPlot(x, y, name="", color="#a855f7", title="", **styles)`: Gráfico de área (línea con área rellena).

## 6. Ejemplo Completo

Aquí tienes un ejemplo que demuestra el uso de varios componentes y gráficos:

```python
from viewx.Slides import (
    Presentation, Slide, Grid,
    Title, Subtitle, Text, BulletList,
    BarPlot, PiePlot, IconStat, RotatingIcon, MovingFigure,
    Button, Link, Image, Video, LinePlot
)
import pandas as pd
import numpy as np

# 1. Inicializar la presentación
pres = Presentation("Demo Avanzada Viewx.Slides", theme="ocean")
pres.font("Montserrat").meta(author="Manus AI", date="2026-05-06")
pres.logo("https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_92x30dp.png")
pres.music("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3")

# --- SLIDE 1: PORTADA --- 
with Slide(title="Bienvenida", index=1, bg="linear-gradient(135deg, #07172f, #102544)"):
    Title("Viewx.Slides").center("x").pos(top=10).zoom_in(duration=1.2)
    Subtitle("Presentaciones Interactivas con Python").center("x").pos(top=26).slide_in("right")
    Text(
        "Crea slides dinámicas, visualmente atractivas y totalmente personalizables con facilidad.",
        color="#e0e7ff",
    ).center("x").pos(top=42).size(width="68%").align("center").fade_in(delay=0.3)
    RotatingIcon("gear", size=70, color="var(--vx-primary)").pos(right=8, top=8).z(10)
    MovingFigure("circle", color="rgba(100,255,218,.15)", size=150, path="float").pos(left=10, bottom=10).z(1)
    Button("Empezar", href="#").center("x").pos(top=68).fade_in(delay=0.55).link_to_slide(2)

# --- SLIDE 2: CARACTERÍSTICAS --- 
with Slide(title="Características Clave", index=2, bg="#102544"):
    Title("Potencia y Flexibilidad").pos(left=6, top=8).slide_in("left")
    BulletList([
        "Componentes personalizables (texto, imágenes, videos, botones).",
        "Posicionamiento absoluto y layouts de cuadrícula (Grid).",
        "Animaciones de entrada y en bucle para elementos dinámicos.",
        "Gráficos interactivos con Plotly (barras, pastel, líneas, dispersión).",
        "Temas integrados y personalización de colores/fuentes.",
        "Exportación a un único archivo HTML autocontenido.",
    ]).pos(left=8, top=30).size(width="48%").fade_in(delay=0.2)
    
    with Grid(columns=2, gap=24).pos(left=55, top=28).size(width="40%", height="60%"):
        IconStat("check", "Fácil", "Sintaxis Python").card().zoom_in(delay=0.4)
        IconStat("chart", "Potente", "Visualización de Datos").card().zoom_in(delay=0.6)
        IconStat("bolt", "Rápido", "Generación HTML").card().zoom_in(delay=0.8)
        IconStat("star", "Flexible", "Diseño Personalizado").card().zoom_in(delay=1.0)

# --- SLIDE 3: GRÁFICOS DE DATOS --- 
with Slide(title="Análisis de Datos", index=3, bg="#07172f"):
    Title("Visualización Interactiva").pos(left=6, top=7).zoom_in()
    Text("Integra fácilmente gráficos de Plotly para presentar tus datos de forma clara y dinámica.").pos(left=7, top=22).size(width="42%").fade_in(delay=0.2)

    # Datos de ejemplo
    categorias = ['Producto A', 'Producto B', 'Producto C', 'Producto D']
    ventas = [400, 550, 300, 620]
    beneficios = [80, 120, 60, 150]
    meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun']
    datos_linea = np.random.randint(10, 100, size=6)

    BarPlot(categorias, ventas, title="Ventas por Producto", color="var(--vx-primary)")\
        .pos(left=7, top=38).size(width="40%", height="42%").fade_in(delay=0.4)
    
    PiePlot(categorias, beneficios, title="Distribución de Beneficios", hole=0.4, colors=["#64ffda", "#48cae4", "#00b4d8", "#0077b6"])\
        .pos(left=54, top=25).size(width="38%", height="52%").fade_in(delay=0.6)

# --- SLIDE 4: IMAGEN Y VIDEO --- 
with Slide(title="Contenido Multimedia", index=4, bg="#102544"):
    Title("Imágenes y Videos").pos(left=6, top=8).slide_in("left")
    Text("Añade elementos visuales para enriquecer tu mensaje.").pos(left=7, top=22).size(width="42%").fade_in(delay=0.2)

    Image("https://picsum.photos/id/237/600/400", alt="Perro", width=400, height=260)\
        .pos(left=55, top=18).radius(18).shadow("md").zoom_in(delay=0.4)
    
    Video("https://www.w3schools.com/html/mov_bbb.mp4", controls=True, autoplay=False, muted=True, poster="https://www.w3schools.com/html/pic_trulli.jpg")\
        .pos(left=10, top=45).size(width=500, height=280).radius(18).shadow("md").slide_in("up", delay=0.6)

# --- SLIDE 5: LLAMADA A LA ACCIÓN --- 
with Slide(title="Prueba Viewx.Slides", index=5, bg="linear-gradient(135deg, #0077b6, #00b4d8)"):
    Title("¡Crea tu Presentación Hoy!").center("x").pos(top=20).bounce()
    Text("Descarga el módulo y empieza a construir presentaciones impactantes con código Python.")\
        .center("x").pos(top=40).size(width="70%").align("center").fade_in(delay=0.5)
    Button("Ver Demo HTML", href="viewx_slides_demo.html", target="_self")\
        .center("x").pos(top=60).shadow("glow").pulse_loop()
    Link("Más información", href="https://github.com/tu_usuario/viewx-slides")\
        .center("x").pos(top=75).fade_in(delay=0.8)

# 7. Exportar la presentación
output_path = pres.export("/home/ubuntu/viewx_slides_advanced_demo.html", open_browser=True)
print(f"Presentación exportada a: {output_path}")
```

## 7. Consejos Adicionales

*   **Unidades de Medida**: Puedes usar `px`, `%`, `vw`, `vh`, `em`, `rem` para `pos` y `size` pasando el valor como string (ej. `width="50vw"`). Para valores numéricos, `px` es el predeterminado.
*   **Colores**: Usa nombres de colores CSS, códigos hexadecimales (`#RRGGBB`), `rgb()`, `rgba()`, `hsl()`, `hsla()`, o las variables CSS del tema (ej. `var(--vx-primary)`).
*   **Iconos**: Para `IconStat` y `RotatingIcon`, puedes usar los nombres predefinidos o cualquier entidad HTML de icono (ej. `&#128187;` para un ordenador).
*   **Depuración**: Abre el archivo HTML generado en tu navegador y usa las herramientas de desarrollador (F12) para inspeccionar el CSS y JavaScript si encuentras problemas de layout o estilo.

¡Esperamos que disfrutes creando presentaciones con `viewx.Slides`!
