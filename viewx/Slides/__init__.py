"""API pública de `viewx.Slides`.

Uso típico:

```python
from viewx.Slides import Presentation, Slide, Title, BarPlot
```
"""

from .slides_engine import ContextStack, Grid, Presentation, Slide, THEMES
from .components import (
    Button,
    BulletList,
    Component,
    Hyperlink,
    IconStat,
    Image,
    Link,
    MovingFigure,
    RotatingIcon,
    Subtitle,
    Text,
    Title,
    Video,
)
from .charts import AreaPlot, BarPlot, DonutPlot, LinePlot, PiePlot, PlotlyChart, ScatterPlot

__all__ = [
    "Presentation",
    "Slide",
    "Grid",
    "ContextStack",
    "THEMES",
    "Component",
    "Title",
    "Subtitle",
    "Text",
    "BulletList",
    "Image",
    "Video",
    "Hyperlink",
    "Link",
    "Button",
    "IconStat",
    "RotatingIcon",
    "MovingFigure",
    "PlotlyChart",
    "BarPlot",
    "PiePlot",
    "DonutPlot",
    "LinePlot",
    "ScatterPlot",
    "AreaPlot",
]
