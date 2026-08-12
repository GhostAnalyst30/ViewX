"""
Convert statslibx report payloads into ViewX artifacts (HTML, PDF, Presentation).
"""

from __future__ import annotations

import os
import tempfile
import warnings
from typing import Any, Dict, List, Literal

import pandas as pd

ReportTarget = Literal["html", "report", "presentation"]

HTMLTheme = Literal[
    "corporate_blue",
    "dark_enterprise",
    "modern_green",
    "void_indigo",
    "glass_ocean",
    "cyberpunk_neon",
]

PresentationTheme = Literal["dark", "light", "neon", "ocean", "sunset", "corporate"]


def _validate_payload(payload: Dict[str, Any]) -> None:
    """
    Ensure a statslibx payload has minimum required structure.

    Parameters
    ----------
    payload : dict
        Serialized stats result.

    Raises
    ------
    ValueError
        If ``title`` is missing.
    """
    if not isinstance(payload, dict):
        raise ValueError("payload must be a dict")
    if "title" not in payload:
        raise ValueError("payload must include a 'title' key")


def _table_to_dataframe(table: Dict[str, Any]) -> pd.DataFrame:
    """Convert a payload table entry to a DataFrame."""
    data = table.get("data", [])
    if not data:
        return pd.DataFrame()
    return pd.DataFrame(data)


def _build_html(
    payload: Dict[str, Any],
    filename: str,
    theme: str,
    show: bool = False,
) -> str:
    """
    Build an HTML dashboard from a statslibx payload.

    Returns
    -------
    str
        Path to generated HTML file.
    """
    from viewx.HTML import Dashboard

    dash = Dashboard(title=payload.get("title", "Stats Report"), theme=theme, cols=12, rows=12)

    row = 1
    col = 1
    for vb in payload.get("valueboxes", []):
        dash.add_valuebox(
            title=str(vb.get("label", "Metric")),
            value=str(vb.get("value", "")),
            row=row,
            col=col,
            height=2,
            width=3,
        )
        col += 3
        if col > 10:
            col = 1
            row += 1

    text_row = max(row, 1)
    for i, section in enumerate(payload.get("sections", [])):
        heading = section.get("heading", "Section")
        body = section.get("body", "")
        content = f"<h3>{heading}</h3><p>{body}</p>"
        dash.add_text(content=content, row=text_row + i, col=1, height=2, width=12)

    table_row = text_row + len(payload.get("sections", [])) + 1
    for i, table in enumerate(payload.get("tables", [])):
        df = _table_to_dataframe(table)
        if df.empty:
            continue
        dash.add_table(
            df=df,
            title=str(table.get("name", "Table")),
            row=table_row + i,
            col=1,
            height=4,
            width=12,
        )

    fig_row = table_row + len(payload.get("tables", [])) + 1
    for i, fig_item in enumerate(payload.get("figures", [])):
        fig = fig_item.get("fig")
        if fig is None:
            continue
        dash.add_chart(
            fig=fig,
            title=str(fig_item.get("title", "Chart")),
            row=fig_row + i,
            col=1,
            height=5,
            width=12,
        )

    return dash.save(filename, open_browser=show)


def _build_report(
    payload: Dict[str, Any],
    filename: str,
    outdir: str = "output",
    **kwargs: Any,
) -> str:
    """
    Build a PDF report from a statslibx payload.

    Returns
    -------
    str
        Path to generated PDF.
    """
    from viewx.Report import Report

    report = Report(title=payload.get("title", "Stats Report"), outdir=outdir)
    report.add_text(payload.get("title", "Stats Report"), bold=True)

    for section in payload.get("sections", []):
        heading = section.get("heading", "Section")
        body = section.get("body", "")
        report.add_box(heading, body)

    for table in payload.get("tables", []):
        df = _table_to_dataframe(table)
        if df.empty:
            continue
        headers = list(df.columns)
        rows = df.astype(str).values.tolist()
        report.add_table(headers, rows, caption=str(table.get("name", "Table")))

    for fig_item in payload.get("figures", []):
        fig = fig_item.get("fig")
        if fig is None:
            continue
        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                tmp_path = tmp.name
            fig.write_image(tmp_path)
            import shutil

            dest_name = os.path.basename(tmp_path)
            dest = os.path.join(report.images_dir, dest_name)
            shutil.copy(tmp_path, dest)
            report.add_image(dest_name, caption=str(fig_item.get("title", "Chart")))
        except Exception as exc:
            # Skip figures when kaleido/image export is unavailable.
            warnings.warn(f"Skipping figure export ({exc}).", RuntimeWarning)
        finally:
            if tmp_path and os.path.exists(tmp_path):
                os.remove(tmp_path)

    return report.save(os.path.join(outdir, f"{filename}.pdf"))


def _build_presentation(
    payload: Dict[str, Any],
    filename: str,
    theme: str,
    open_browser: bool = False,
) -> str:
    """
    Build an HTML slide deck from a statslibx payload.

    Returns
    -------
    str
        Path to generated presentation HTML.
    """
    from viewx import Presentation, Slide
    from viewx.Slides.charts import PlotlyChart
    from viewx.Slides.components import BulletList, IconStat, Text, Title

    pres = Presentation(title=payload.get("title", "Stats Report"), theme=theme)

    with Slide(title="Intro") as slide:
        Title(payload.get("title", "Stats Report"))
        Text("Generated from StatsLibX results via ViewX.")

    valueboxes: List[Dict[str, Any]] = payload.get("valueboxes", [])
    if valueboxes:
        with Slide(title="Key metrics") as slide:
            Title("Key metrics")
            for vb in valueboxes[:4]:
                IconStat(
                    icon="📊",
                    value=str(vb.get("value", "")),
                    label=str(vb.get("label", "Metric")),
                )

    for section in payload.get("sections", []):
        with Slide(title=str(section.get("heading", "Section"))) as slide:
            Title(str(section.get("heading", "Section")))
            body = str(section.get("body", ""))
            if body:
                Text(body)
            bullets = []
            if section.get("statistic") is not None:
                bullets.append(f"Statistic: {section['statistic']}")
            if section.get("pvalue") is not None:
                bullets.append(f"p-value: {section['pvalue']}")
            if bullets:
                BulletList(bullets)

    for table in payload.get("tables", []):
        df = _table_to_dataframe(table)
        if df.empty:
            continue
        with Slide(title=str(table.get("name", "Table"))) as slide:
            Title(str(table.get("name", "Table")))
            preview = df.head(8).to_string(index=False)
            Text(preview)

    for fig_item in payload.get("figures", []):
        fig = fig_item.get("fig")
        if fig is None:
            continue
        with Slide(title=str(fig_item.get("title", "Chart"))) as slide:
            Title(str(fig_item.get("title", "Chart")))
            fig_dict = fig.to_plotly_json() if hasattr(fig, "to_plotly_json") else fig.to_dict()
            PlotlyChart(
                data=fig_dict.get("data", []),
                layout=fig_dict.get("layout", {}),
            )

    return pres.save(filename, open_browser=open_browser)


def from_report_payload(
    payload: Dict[str, Any],
    target: ReportTarget = "html",
    filename: str = "report.html",
    theme: str = "dark_enterprise",
    outdir: str = "output",
    show: bool = False,
    open_browser: bool = False,
    **kwargs: Any,
) -> str:
    """
    Convert a statslibx ``to_report_data()`` payload into a ViewX artifact.

    Parameters
    ----------
    payload : dict
        Output of ``statslibx.to_report_data()`` with keys ``title``, ``sections``,
        ``tables``, and optional ``valueboxes``, ``figures``, ``metadata``.
    target : {'html', 'report', 'presentation'}
        ViewX engine to use.
    filename : str
        Output filename (HTML) or base name (PDF).
    theme : str
        Theme name for HTML dashboards or Presentation decks.
    outdir : str
        Output directory for PDF reports.
    show : bool
        Open HTML dashboard in browser after generation.
    open_browser : bool
        Open presentation in browser after export.
    **kwargs
        Reserved for future options.

    Returns
    -------
    str
        Path to the generated file.

    Raises
    ------
    ValueError
        If the payload structure is invalid.
    """
    _validate_payload(payload)

    if target == "html":
        return _build_html(payload, filename=filename, theme=theme, show=show)
    if target == "report":
        base = filename.replace(".pdf", "").replace(".html", "")
        return _build_report(payload, filename=base, outdir=outdir, **kwargs)
    if target == "presentation":
        return _build_presentation(
            payload,
            filename=filename,
            theme=theme,
            open_browser=open_browser,
        )
    raise ValueError(f"Unsupported target: {target!r}. Use 'html', 'report', or 'presentation'.")
