"""PDF report engine (LaTeX under the hood, no LaTeX knowledge required).

Requires a LaTeX distribution with ``pdflatex`` on PATH, and the ``pylatex``
package (``pip install viewx[pdf]``).

Usage
-----
r = Report("Reporte técnico", author="Ana")
with r.section("Introducción"):
    r.text("Resumen del análisis.", bold=True)
    r.bullets(["Punto uno", "Punto dos"])
r.add_table(["A", "B"], [[1, 2], [3, 4]], caption="Datos")
r.save("reporte.pdf")
"""

from __future__ import annotations

import os
import shutil
import warnings
from contextlib import contextmanager
from typing import Iterable, List, Optional, Sequence, Tuple, Union

from pylatex import (
    Command, Document, Enumerate, Figure, Itemize, NoEscape, Section, Subsection,
)
from pylatex.utils import escape_latex

# Basic CSS color names mapped to soft LaTeX tints for add_box()
_CSS_BOX_COLORS = {
    "blue": "blue!15", "green": "green!15", "red": "red!15",
    "yellow": "yellow!20", "orange": "orange!20", "purple": "violet!15",
    "gray": "gray!15", "grey": "gray!15", "cyan": "cyan!15",
}


class Report:
    def __init__(
        self,
        title: str = "Reporte",
        author: str = "Autor",
        outdir: str = "output",
        two_column: bool = False,
        images_dir: str = "images",
    ):
        self.outdir = outdir
        os.makedirs(outdir, exist_ok=True)

        # images live inside outdir so LaTeX can resolve them at compile time
        self.images_dir = os.path.join(outdir, images_dir)
        os.makedirs(self.images_dir, exist_ok=True)
        self._box_counter = 0

        if two_column:
            self.doc = Document(
                documentclass="article",
                document_options=["10pt", "twocolumn"],
                lmodern=True,
            )
        else:
            self.doc = Document(documentclass="article", lmodern=True)

        # ========= PACKAGES =========
        pkgs = [
            "geometry", "float", "caption", "xcolor",
            "graphicx", "multicol", "listings",
            "tikz", "pgfplots", "tcolorbox",
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
        self.doc.preamble.append(
            NoEscape(rf"\graphicspath{{{{{images_dir}/}}}}")
        )
        self.doc.append(NoEscape(r"\pgfplotsset{compat=1.18}"))

        # ========= METADATA =========
        self.doc.preamble.append(Command("title", escape_latex(title)))
        self.doc.preamble.append(Command("author", escape_latex(author)))
        self.doc.preamble.append(Command("date", NoEscape(r"\today")))
        self.doc.append(NoEscape(r"\maketitle"))

    # ================== SECTIONS (context managers) ==================
    @contextmanager
    def section(self, title: str):
        """Open a section; everything added inside the ``with`` block nests in it.

        >>> with r.section("Results"):
        ...     r.text("...")
        """
        with self.doc.create(Section(escape_latex(title))):
            yield self

    @contextmanager
    def subsection(self, title: str):
        with self.doc.create(Subsection(escape_latex(title))):
            yield self

    # Low-level builders kept for advanced use (return pylatex containers)
    def add_section(self, title: str) -> Section:
        return Section(escape_latex(title))

    def add_subsection(self, title: str) -> Subsection:
        return Subsection(escape_latex(title))

    # ================== TEXT ==================
    def add_text(self, text: str, bold: bool = False) -> "Report":
        t = escape_latex(text)
        if bold:
            t = NoEscape(r"\textbf{" + t + "}")
        self.doc.append(t)
        return self

    text = add_text

    # ================== IMAGES ==================
    def add_image(
        self,
        filename: str,
        caption: Optional[str] = None,
        width: Union[float, str] = 0.6,
        placement: str = "H",
    ) -> "Report":
        """Insert an image. ``width`` is a fraction of the line width (0-1)
        or a raw LaTeX length string for advanced use."""
        if isinstance(width, (int, float)):
            width_tex = rf"{width}\linewidth"
        else:
            width_tex = width

        target_path = os.path.join(self.images_dir, os.path.basename(filename))

        if not os.path.exists(target_path):
            local_path = os.path.abspath(filename)
            if os.path.exists(local_path):
                shutil.copy(local_path, target_path)
            else:
                raise FileNotFoundError(
                    f"[ViewX] Image '{filename}' not found in "
                    f"'{self.images_dir}' nor in the current directory."
                )

        with self.doc.create(Figure(position=placement)) as fig:
            fig.add_image(os.path.basename(filename), width=NoEscape(width_tex))
            if caption:
                fig.add_caption(escape_latex(caption))
        return self

    # ================== TABLES ==================
    def add_table(
        self,
        headers: Sequence[str],
        rows: Iterable[Sequence],
        caption: str = "",
    ) -> "Report":
        cols = " | ".join(["l"] * len(headers))
        table_tex = r"\begin{table}[H]\centering" + "\n"
        table_tex += rf"\caption{{{escape_latex(caption)}}}" + "\n"
        table_tex += rf"\begin{{tabular}}{{{cols}}}\hline" + "\n"
        table_tex += " & ".join(escape_latex(str(h)) for h in headers) + r"\\ \hline" + "\n"

        for row in rows:
            table_tex += " & ".join(escape_latex(str(c)) for c in row) + r"\\ \hline" + "\n"

        table_tex += r"\end{tabular}\end{table}"
        self.doc.append(NoEscape(table_tex))
        return self

    # ================== LISTS ==================
    def add_itemize(self, items: Iterable[str]) -> "Report":
        with self.doc.create(Itemize()) as it:
            for i in items:
                it.add_item(escape_latex(str(i)))
        return self

    def add_enumerate(self, items: Iterable[str]) -> "Report":
        with self.doc.create(Enumerate()) as it:
            for i in items:
                it.add_item(escape_latex(str(i)))
        return self

    bullets = add_itemize
    numbered = add_enumerate

    # ================== CODE ==================
    def add_code(self, code: str, language: str = "python") -> "Report":
        self.doc.append(NoEscape(rf"""
    \begin{{lstlisting}}[language={language}]
    {code}
    \end{{lstlisting}}
    """))
        return self

    # ================== MULTI-COLUMN ==================
    def begin_multicols(self, n: int = 2) -> "Report":
        self.doc.append(NoEscape(rf"\begin{{multicols}}{{{n}}}"))
        return self

    def end_multicols(self) -> "Report":
        self.doc.append(NoEscape(r"\end{multicols}"))
        return self

    # ================== BOXES ==================
    def add_box(self, title: str, content: str, color: str = "#DBEAFE") -> "Report":
        """Colored callout box. ``color`` accepts a CSS hex value ("#DBEAFE"),
        a basic color name ("green"), or a raw LaTeX color spec ("green!20")."""
        colback = self._resolve_box_color(color)
        box = rf"""
\begin{{tcolorbox}}[
    colback={colback},
    colframe=black,
    title={escape_latex(title)}
]
{escape_latex(content)}
\end{{tcolorbox}}
"""
        self.doc.append(NoEscape(box))
        return self

    def _resolve_box_color(self, color: str) -> str:
        if color.startswith("#") and len(color) == 7:
            self._box_counter += 1
            name = f"vxbox{self._box_counter}"
            self.doc.preamble.append(
                NoEscape(rf"\definecolor{{{name}}}{{HTML}}{{{color[1:].upper()}}}")
            )
            return name
        return _CSS_BOX_COLORS.get(color.lower(), color)

    # ================== PLOTS (static, TikZ) ==================
    def add_line_plot(
        self,
        x: Sequence[float],
        y: Sequence[float],
        caption: str = "",
    ) -> "Report":
        """Simple static line plot rendered natively in LaTeX (pgfplots)."""
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
        return self

    def add_plot(self, x, y, caption: str = "") -> "Report":
        """Deprecated: use ``add_line_plot()`` instead."""
        warnings.warn(
            "Report.add_plot() is deprecated; use add_line_plot().",
            DeprecationWarning, stacklevel=2,
        )
        return self.add_line_plot(x, y, caption=caption)

    def add_multiplot(
        self,
        plots: Sequence[Tuple[Sequence[float], Sequence[float]]],
        caption: str = "",
    ) -> "Report":
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
        return self

    # ================== PAGE BREAK ==================
    def new_page(self) -> "Report":
        self.doc.append(NoEscape(r"\newpage"))
        return self

    # ================== SAVE ==================
    def save(self, path: str = "reporte.pdf") -> str:
        """Compile the report to PDF. ``path`` may include a directory;
        otherwise the report's ``outdir`` is used. Returns the PDF path."""
        if shutil.which("pdflatex") is None:
            raise RuntimeError(
                "pdflatex was not found on PATH. Install a LaTeX distribution "
                "(TeX Live / MiKTeX) to build PDF reports."
            )

        stem = os.path.splitext(os.path.basename(path))[0]
        directory = os.path.dirname(path) or self.outdir
        os.makedirs(directory, exist_ok=True)

        # Keep relative image references valid when compiling somewhere else
        if os.path.abspath(directory) != os.path.abspath(self.outdir) and os.listdir(self.images_dir):
            dest_images = os.path.join(directory, os.path.basename(self.images_dir))
            shutil.copytree(self.images_dir, dest_images, dirs_exist_ok=True)

        filepath = os.path.join(directory, stem)
        try:
            self.doc.generate_pdf(
                filepath=filepath,
                clean_tex=False,
                compiler="pdflatex",
            )
        except Exception as e:
            print(f"[ViewX] LaTeX build failed. Check {filepath}.log")
            output = getattr(e, "output", None)
            if output:
                try:
                    print(output.decode("latin-1"))
                except (AttributeError, UnicodeDecodeError):
                    pass
            raise
        return f"{filepath}.pdf"

    def show(self, path: str = "reporte.pdf") -> str:
        """Compile the report and open the resulting PDF."""
        pdf_path = self.save(path)
        import webbrowser
        webbrowser.open("file://" + os.path.abspath(pdf_path))
        return pdf_path

    def build(self, filename: str = "reporte_final") -> str:
        """Deprecated: use ``save(path)`` instead."""
        warnings.warn(
            "Report.build() is deprecated; use save(path).",
            DeprecationWarning, stacklevel=2,
        )
        return self.save(os.path.join(self.outdir, f"{filename}.pdf"))

    # ================== AUTO ==================
    @classmethod
    def auto(
        cls,
        df,
        title: str = "Dataset Quality Report",
        author: str = "ViewX",
        outdir: str = "output",
        columns: Optional[List[str]] = None,
        include_plots: bool = True,
        show_warnings: bool = True,
        show_highlights: bool = True,
    ) -> "Report":
        """Build an automatic quality report from a DataFrame.

        Returns the Report; call ``.save(path)`` on it to compile the PDF.
        """
        from .auto_builder import build_auto_report

        return build_auto_report(
            df,
            cls,
            title=title,
            author=author,
            outdir=outdir,
            columns=columns,
            include_plots=include_plots,
            show_warnings=show_warnings,
            show_highlights=show_highlights,
        )

    @classmethod
    def auto_generate(
        cls,
        df,
        title: str = "Dataset Quality Report",
        author: str = "ViewX",
        filename: str = "auto_report",
        outdir: str = "output",
        columns=None,
        include_plots: bool = True,
        show_warnings: bool = True,
        show_highlights: bool = True,
    ) -> str:
        """Deprecated: use ``Report.auto(df, ...).save(path)`` instead."""
        warnings.warn(
            "Report.auto_generate() is deprecated; use Report.auto(df).save(path).",
            DeprecationWarning, stacklevel=2,
        )
        rpt = cls.auto(
            df, title=title, author=author, outdir=outdir, columns=columns,
            include_plots=include_plots, show_warnings=show_warnings,
            show_highlights=show_highlights,
        )
        return rpt.save(os.path.join(outdir, f"{filename}.pdf"))
