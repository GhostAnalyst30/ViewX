"""
ViewX - Librería de Visualizacion para Python
Autor: Emmanuel Ascendra
Versión: 0.1.6
"""

__version__ = "0.1.6"
__author__ = "Emmanuel Ascendra"

# Importar las clases principales
from .html_engine import HTML
from .dashboard_engine import DashBoard
from .report_engine import Report
from .datasets import load_dataset

# Definir qué se expone cuando se hace: from statslib import *
__all__ = [
    # Clases principales
    'HTML',
    'DashBoard',
    'Report',
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
    print(f"\nPara más información: help(statslibx)")