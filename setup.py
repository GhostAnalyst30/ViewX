from setuptools import setup, find_packages

# Leer README si existe
try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = "Librería de visualización adaptable para Python."

setup(
    name="viewx",
    version="0.3.0",
    author="Emmanuel Ascendra Perez",
    author_email="ascendraemmanuel@gmail.com",
    description="Librería de visualización adaptable para HTML, Dashboards y PDFs en Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/GhostAnalyst30/ViewX",
    packages=find_packages(),
    include_package_data=True,

    package_data={
        "viewx": ["datasets/*.csv"]
    },

    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Visualization",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],

    python_requires=">=3.8",

    # Dependencias mínimas (núcleo interactivo)
    install_requires=[
        "numpy>=1.25.0",
        "pandas>=2.1.0",
        "plotly>=6.0.0",
    ],

    # Dependencias opcionales
    extras_require={
        # Gráficas estáticas (vx.plot(..., static=True)) y auto-reportes PDF
        "static": ["matplotlib>=3.8.0"],
        # Reportes PDF vía LaTeX (requiere pdflatex instalado en el sistema)
        "pdf": ["pylatex>=1.4.2", "matplotlib>=3.8.0"],
        # Exportar figuras Plotly a PNG/SVG
        "export": ["kaleido>=0.2.1"],
        "all": [
            "matplotlib>=3.8.0",
            "pylatex>=1.4.2",
            "kaleido>=0.2.1",
        ],
    },
)
