import os
from pylatex import (
    Document, Section, Subsection, Figure, Table, Tabular,
    NoEscape, Command, Itemize, Enumerate
)
from pylatex.utils import escape_latex
import shutil



class Report:
    def __init__(self, title="Reporte", author="Autor", outdir="output", twoColumn: bool = False, images_dir = "images"):

        self.outdir = outdir
        os.makedirs(outdir, exist_ok=True)

        # 📂 images dentro de output
        self.images_dir = os.path.join(outdir, images_dir)
        os.makedirs(self.images_dir, exist_ok=True)

        if twoColumn:
            self.doc = Document(
                documentclass="article",
                document_options=["10pt", "twocolumn"],
                lmodern=True
            )
        else:
            self.doc = Document(
                documentclass="article",
                lmodern=True
            )

        # ========= PAQUETES =========
        pkgs = [
            "geometry", "float", "caption", "xcolor",
            "graphicx", "multicol", "listings",
            "tikz", "pgfplots", "tcolorbox"
        ]
        for p in pkgs:
            self.doc.packages.append(Command("usepackage", p))
        self.doc.preamble.append(NoEscape(r"\usepackage[utf8]{inputenc}"))
        self.doc.preamble.append(NoEscape(r"\usepackage[T1]{fontenc}"))
        self.doc.preamble.append(NoEscape(r"""
        \lstset{
            basicstyle=\ttfamily\small,
            frame=single,
            breaklines=true,
            numbers=left,
            numberstyle=\tiny,
            keywordstyle=\color{blue},
            commentstyle=\color{green!50!black},
        }
        """))
        self.doc.packages.append(Command("usepackage", "graphicx"))
        self.doc.preamble.append(
            NoEscape(rf"\graphicspath{{{{{images_dir}/}}}}")
        )


        self.doc.append(NoEscape(r"\pgfplotsset{compat=1.18}"))

        # ========= METADATOS =========
        self.doc.preamble.append(Command("title", escape_latex(title)))
        self.doc.preamble.append(Command("author", escape_latex(author)))
        self.doc.preamble.append(Command("date", NoEscape(r"\today")))
        self.doc.append(NoEscape(r"\maketitle"))

    # ================== TEXTO ==================
    def add_text(self, text, bold=False):
        t = escape_latex(text)
        if bold:
            t = NoEscape(r"\textbf{" + t + "}")
        self.doc.append(t)

    # ================== SECCIONES ==================
    def add_section(self, title):
        return Section(escape_latex(title))

    def add_subsection(self, title):
        return Subsection(escape_latex(title))

    # ================== IMÁGENES ==================
    def add_image(
        self,
        filename,
        caption=None,
        width="0.6\\textwidth",
        placement="H"
    ):
        # 📂 Ruta destino (output/images)
        target_path = os.path.join(self.images_dir, filename)

        # 1️⃣ Caso ideal: ya existe en output/images
        if not os.path.exists(target_path):

            # 2️⃣ Buscar en directorio actual
            local_path = os.path.abspath(filename)

            if os.path.exists(local_path):
                # 🚚 Copiar automáticamente
                shutil.copy(local_path, target_path)
                print(f"[ViewX] 📸 Imagen copiada a images/: {filename}")

            else:
                # ❌ No existe en ningún lado
                raise FileNotFoundError(
                    f"[ViewX] ❌ Imagen '{filename}' no encontrada "
                    f"ni en output/images ni en el directorio actual."
                )

        # 3️⃣ Insertar imagen (LaTeX solo ve el nombre)
        with self.doc.create(Figure(position=placement)) as fig:
            fig.add_image(
                filename,
                width=NoEscape(width)
            )
            if caption:
                fig.add_caption(escape_latex(caption))




    # ================== TABLAS ==================
    def add_table(self, headers, rows, caption=""):
        cols = " | ".join(["l"] * len(headers))
        table_tex = r"\begin{table}[H]\centering" + "\n"
        table_tex += rf"\caption{{{escape_latex(caption)}}}" + "\n"
        table_tex += rf"\begin{{tabular}}{{{cols}}}\hline" + "\n"
        table_tex += " & ".join(escape_latex(h) for h in headers) + r"\\ \hline" + "\n"

        for row in rows:
            table_tex += " & ".join(escape_latex(str(c)) for c in row) + r"\\ \hline" + "\n"

        table_tex += r"\end{tabular}\end{table}"
        self.doc.append(NoEscape(table_tex))

    # ================== LISTAS ==================
    def add_itemize(self, items):
        with self.doc.create(Itemize()) as it:
            for i in items:
                it.add_item(escape_latex(i))

    def add_enumerate(self, items):
        with self.doc.create(Enumerate()) as it:
            for i in items:
                it.add_item(escape_latex(i))

    # ================== CÓDIGO ==================
    def add_code(self, code, language="python"):
        self.doc.append(NoEscape(rf"""
    \begin{{lstlisting}}[language={language}]
    {code}
    \end{{lstlisting}}
    """))


    # ================== MULTICOLUMNAS ==================
    def begin_multicols(self, n=2):
        self.doc.append(NoEscape(rf"\begin{{multicols}}{{{n}}}"))

    def end_multicols(self):
        self.doc.append(NoEscape(r"\end{multicols}"))

    # ================== CAJAS ==================
    def add_box(self, title, content, color="blue!15"):
        box = rf"""
\begin{{tcolorbox}}[
    colback={color},
    colframe=black,
    title={escape_latex(title)}
]
{escape_latex(content)}
\end{{tcolorbox}}
"""
        self.doc.append(NoEscape(box))

    # ================== GRÁFICO ==================
    def add_plot(self, x, y, caption=""):
        coords = " ".join(f"({xi},{yi})" for xi, yi in zip(x, y))
        plot = rf"""
\begin{{figure}}[H]
\centering
\begin{{tikzpicture}}
\begin{{axis}}[
    width=0.85\linewidth,
    height=6cm,
    grid=major
]
\addplot coordinates {{{coords}}};
\end{{axis}}
\end{{tikzpicture}}
\caption{{{escape_latex(caption)}}}
\end{{figure}}
"""
        self.doc.append(NoEscape(plot))

    # ================== MULTIPLOT ==================
    def add_multiplot(self, plots, caption=""):
        body = ""
        for x, y in plots:
            coords = " ".join(f"({xi},{yi})" for xi, yi in zip(x, y))
            body += rf"\addplot coordinates {{{coords}}};"

        tex = rf"""
\begin{{figure}}[H]
\centering
\begin{{tikzpicture}}
\begin{{axis}}[
    width=0.9\linewidth,
    height=6cm,
    grid=both
]
{body}
\end{{axis}}
\end{{tikzpicture}}
\caption{{{escape_latex(caption)}}}
\end{{figure}}
"""
        self.doc.append(NoEscape(tex))

    # ================== SALTO DE PÁGINA ==================
    def new_page(self):
        self.doc.append(NoEscape(r"\newpage"))

    # ================== BUILD ==================
    def build(self, filename="reporte_final"):
        path = os.path.join(self.outdir, filename)
        try:
            self.doc.generate_pdf(
                filepath=path,
                clean_tex=False,
                compiler="pdflatex"
            )
            print(f"[ViewX] ✅ PDF generado: {path}.pdf")

        except Exception as e:
            print("[ViewX] ❌ Error LaTeX")
            print(f"👉 Revisa {path}.log")

            # Evita crash por Unicode
            if hasattr(e, "output"):
                try:
                    print(e.output.decode("latin-1"))
                except:
                    pass

            raise



if __name__ == "__main__":
    # from viewx.report_engine import ViewXReport

    # ===============================
    # 1️⃣ CREAR REPORTE
    # ===============================
    r = Report(
        title="Reporte Técnico ViewX",
        author="Emmanuel Ascendra"
    )

    # ===============================
    # 2️⃣ TEXTO
    # ===============================
    r.add_text("Este reporte demuestra todas las capacidades del motor ViewX.\n")
    r.add_text("Texto importante en negrita.", bold=True)

    # ===============================
    # 3️⃣ SECCIONES
    # ===============================
    with r.doc.create(r.add_section("Introducción")):
        r.add_text(
            "ViewX es un motor de generación de reportes científicos "
            "capaz de producir documentos profesionales usando Python."
        )

    # ===============================
    # 4️⃣ SUBSECCIÓN
    # ===============================
    with r.doc.create(r.add_subsection("Características principales")):
        r.add_itemize([
            "Texto estructurado",
            "Imágenes",
            "Tablas",
            "Código",
            "Gráficos científicos",
            "Multicolumnas",
            "Cajas de información"
        ])

    # ===============================
    # 5️⃣ TABLA
    # ===============================
    with r.doc.create(r.add_section("Tabla de resultados")):
        r.add_table(
            headers=["Modelo", "Accuracy", "F1"],
            rows=[
                ["Regresión", 0.82, 0.79],
                ["Árbol", 0.91, 0.88],
                ["Red neuronal", 0.94, 0.92],
            ],
            caption="Comparación de modelos"
        )

    # ===============================
    # 6️⃣ IMAGEN
    # ===============================
        # Copia o guarda la imagen aquí:
        # output/images/Python-Emblem.png
    # Puedes dejar la imagen junto al script
    # o ya dentro de output/images

    with r.doc.create(r.add_section("Visualización")):
        r.add_image(
            "Python-Emblem.png",
            caption="Logo oficial de Python"
        )




    # ===============================
    # 7️⃣ CÓDIGO
    # ===============================
    with r.doc.create(r.add_section("Código de ejemplo")):
        r.add_code("""
    import numpy as np

    x = np.linspace(0, 10, 50)
    y = np.sin(x)
    """)

    # ===============================
    # 8️⃣ MULTICOLUMNAS
    # ===============================
    with r.doc.create(r.add_section("Análisis en dos columnas")):
        r.begin_multicols(2)

        r.add_text(
            "Este bloque demuestra cómo dividir el contenido "
            "en múltiples columnas dentro del mismo documento."
        )

        r.add_itemize([
            "Ideal para papers",
            "Mejora lectura",
            "Ahorra espacio"
        ])

        r.end_multicols()

    # ===============================
    # 9️⃣ CAJA DESTACADA
    # ===============================
    with r.doc.create(r.add_section("Nota importante")):
        r.add_box(
            title="Observación clave",
            content="Todos los elementos se generan directamente desde Python.",
            color="green!20"
        )

    # ===============================
    # 🔟 GRÁFICO SIMPLE
    # ===============================
    with r.doc.create(r.add_section("Gráfico simple")):
        r.add_plot(
            x=[0, 1, 2, 3, 4],
            y=[0, 1, 4, 9, 16],
            caption="Crecimiento cuadrático"
        )

    # ===============================
    # 1️⃣1️⃣ MULTIGRÁFICO
    # ===============================
    with r.doc.create(r.add_section("Gráficos múltiples")):
        r.add_multiplot(
            plots=[
                ([0, 1, 2, 3], [0, 1, 4, 9]),
                ([0, 1, 2, 3], [0, 1, 8, 27]),
            ],
            caption="Comparación de funciones"
        )

    # ===============================
    # 1️⃣2️⃣ SALTO DE PÁGINA
    # ===============================
    r.new_page()
    r.add_text("Contenido en una nueva página.")

    # ===============================
    # 1️⃣3️⃣ GENERAR PDF
    # ===============================
    r.build("reporte_demo")
