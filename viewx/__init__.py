"""
ViewX - Librería de Visualización para Python
Autor: Emmanuel Ascendra
Versión: 0.3.0

Quick start
-----------
import viewx as vx
df = vx.load_dataset("iris.csv")

vx.plot(df, x="sepal_length", y="petal_length")          # gráfica en 1 línea
vx.Dashboard.auto(df).save("dash.html")                  # dashboard automático
vx.DataMatrix(df).analyze().save("eda.html")             # reporte EDA
vx.Presentation.auto(df).save("slides.html")             # slides automáticas
vx.Report.auto(df).save("reporte.pdf")                   # PDF (requiere pdflatex)
"""

__version__ = "0.3.0"
__author__ = "Emmanuel Ascendra"

from .HTML import Dashboard, HTML  # HTML is a legacy alias of Dashboard
from .Slides import Presentation, Slide
from .DataMatrix import DataMatrix
from .datasets import load_dataset, generate_dataset
from .plot import Chart, plot
from .shared.themes import get_theme, set_theme
from .shared.stats_payload import from_report_payload, ReportTarget

__all__ = [
    # Engines
    "Dashboard",
    "HTML",
    "Report",
    "Presentation",
    "Slide",
    "DataMatrix",
    # Quick charts
    "plot",
    "Chart",
    # Themes
    "set_theme",
    "get_theme",
    # Data helpers
    "load_dataset",
    "generate_dataset",
    # StatsLibX bridge
    "from_report_payload",
    "ReportTarget",
]


def __getattr__(name):
    # Report pulls in pylatex; import lazily so the PDF extra stays optional.
    if name == "Report":
        from .Report import Report as _Report
        # Overwrite the submodule binding created by the import machinery so
        # `viewx.Report` / `from viewx import Report` resolve to the class.
        globals()["Report"] = _Report
        return _Report
    raise AttributeError(f"module 'viewx' has no attribute {name!r}")


def welcome():
    """Muestra información sobre la librería."""
    print(f"ViewX v{__version__}")
    print("Librería de visualización para analistas e ingenieros de datos")
    print(f"Autor: {__author__}")
    print("\nAPI principal:")
    print(" - vx.plot(df, kind=..., x=..., y=...)   -> gráfica en 1 paso")
    print(" - vx.Dashboard / Dashboard.auto(df)     -> dashboards HTML")
    print(" - vx.DataMatrix(df).analyze()           -> reporte EDA")
    print(" - vx.Presentation / Presentation.auto() -> slides HTML")
    print(" - vx.Report / Report.auto(df)           -> PDF (pdflatex)")
    print(" - vx.set_theme('dark_enterprise')       -> tema global")
    print("\nTodos los motores exportan con .save(path) y .show()")
    print("\nIntegración StatsLibX: from_report_payload()")
    print("\nDocumentación: https://viewx.vercel.app/")
