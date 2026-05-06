"""
Slides - Presentaciones HTML con animaciones
"""

# Clases principales del motor
from .slides_engine import (
    Presentation,
    Slide,
    Component,
    GradientSlide,
    ParticleSlide,
    SplitSlide,
)

# Componentes animados
from .slides_engine import (
    MovingFigure,
    RotatingIcon,
    OrbitingObject,
    GlowText,
    ParticleSystem,
)

from .charts import (
    BarChart,
    ScatterPlot,
    PieChart,
    LineChart,
    Histogram,
    BoxPlot,
)

# Componentes de texto
from .slides_engine import (
    Title,
    Subtitle,
    Text,
    Quote,
    Shape,
    Code,
    BulletList,
    Button,
    Badge,
)

# Componentes visuales
from .slides_engine import (
    Divider,
    Image,
    Card,
    IconStat,
    Timeline,
    Table,
    Columns,
    QRCode,
    Tooltip,
    ProgressCircle,
    CountUp,
)

# Constantes
from .slides_engine import (
    THEMES,
    TRANSITION_CSS,
    KEYFRAMES,
)

__all__ = [
    # Clases principales
    "Presentation",
    "Slide",
    "Component",
    "GradientSlide",
    "ParticleSlide",
    "SplitSlide",
    
    # Componentes animados
    "MovingFigure",
    "RotatingIcon",
    "OrbitingObject",
    "GlowText",
    "ParticleSystem",
    
    # Componentes de texto
    "Title",
    "Subtitle",
    "Text",
    "Quote",
    "Shape",
    "Code",
    "BulletList",
    "Button",
    "Badge",
    
    # Componentes visuales
    "Divider",
    "Image",
    "Card",
    "BarChart",
    "ScatterPlot",
    "PieChart",
    "LineChart",
    "Histogram",
    "BoxPlot",
    "IconStat",
    "Timeline",
    "Table",
    "Columns",
    "QRCode",
    "Tooltip",
    "ProgressCircle",
    "CountUp",
    
    # Constantes
    "THEMES",
    "TRANSITION_CSS",
    "KEYFRAMES",
]