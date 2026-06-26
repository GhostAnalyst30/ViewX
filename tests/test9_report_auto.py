"""Auto-generated PDF quality report from a DataFrame."""

import shutil

from viewx.datasets import load_iris
from viewx import Report

if not shutil.which("pdflatex"):
    print("SKIP: pdflatex not found — install a LaTeX distribution to run this test.")
    raise SystemExit(0)

df = load_iris()

path = Report.auto_generate(
    df,
    title="Iris Dataset Quality Report",
    author="ViewX Test",
    filename="test9_auto_report",
    outdir="output",
    include_plots=True,
)
print(f"Report.auto_generate -> {path}")
