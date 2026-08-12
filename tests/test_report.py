import shutil

import pytest

pytest.importorskip("pylatex")

from viewx import Report  # noqa: E402


def test_report_assembly_without_latex_strings(tmp_path):
    r = Report("Demo", author="Test", outdir=str(tmp_path))
    with r.section("Intro"):
        r.text("Texto principal", bold=True)
        r.bullets(["uno", "dos"])
        with r.subsection("Detalle"):
            r.text("sub texto")
    r.add_table(["A", "B"], [[1, 2]], caption="tabla")
    r.add_box("Nota", "contenido", color="#DBEAFE")
    r.add_box("Nota2", "contenido", color="green")
    r.add_line_plot([0, 1, 2], [0, 1, 4], caption="linea")

    tex = r.doc.dumps()
    assert "section{Intro}" in tex
    assert "subsection{Detalle}" in tex
    assert "vxbox1" in tex          # hex color converted via \definecolor
    assert "green!15" in tex        # css name mapped to a LaTeX tint
    assert "addplot" in tex


def test_report_auto_returns_report(tmp_path, iris):
    pytest.importorskip("matplotlib")
    rpt = Report.auto(iris, title="Auto", outdir=str(tmp_path))
    assert isinstance(rpt, Report)
    tex = rpt.doc.dumps()
    assert "Column Profiles" in tex


@pytest.mark.skipif(shutil.which("pdflatex") is None, reason="pdflatex not installed")
def test_report_save_compiles_pdf(tmp_path):
    import os
    r = Report("Mini", author="Test", outdir=str(tmp_path))
    with r.section("Uno"):
        r.text("hola")
    pdf = r.save(str(tmp_path / "mini.pdf"))
    assert pdf.endswith(".pdf")
    assert os.path.getsize(pdf) > 0
