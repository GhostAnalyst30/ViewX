"""
ViewX - Librería de Visualizacion para Python
Autor: Emmanuel Ascendra
Versión: 0.2.3
"""

__version__ = "0.2.3"
__author__ = "Emmanuel Ascendra"

# Importar las clases principales
from .HTML import HTML
from .Report import Report
from .Slides import Presentation, Slide
from .DataMatrix import DataMatrix
from .datasets import load_dataset

# Definir qué se expone cuando se hace: from statslib import *
__all__ = [
    # Clases principales
    'HTML',
    'Report',
    'Presentation',
    'Slide',
    'DataMatrix',
    # Funciones
    'load_dataset'
]

# Mensaje de bienvenida (opcional)
def welcome():
    """Muestra información sobre la librería"""
    print(f"ViewX v{__version__}")
    print(f"Librería de visualizacion")
    print(f"Autor: {__author__}")
    print(f"\nClases disponibles:")
    print(f" - HTML")
    print(f" - DashBoard")
    print(f" - Report")
    print(f" - Slides")
    print(f" - DataMatrix")
    print(f"\nPara más información: help(viewx)")
    print(f"\nO lee la información en: https://ghostanalyst30.github.io/ViewX/Documentation_Page/index.html")