import pandas as pd
import subprocess
import sys
from pathlib import Path
import tempfile
import textwrap
import json
from typing import List, Dict, Any, Optional, Union


class DashBoard:
    """
    DashBoard v2 (fix): Generador de apps Streamlit dinámicas con control de layout y estilo.
    - Soporta: theme, rows (cols), tabs, expanders, sidebar
    - Componentes: title, text, table, metric, plot
    """

    VALID_PLOTS = {"scatter", "line", "hist", "bar"}

    def __init__(self, data: pd.DataFrame, title: str = "ViewX Dashboard", title_align: str = "center"):
        self.data = data.copy()
        self.title = title
        self.title_align = title_align
        self.components: List[Dict[str, Any]] = []
        self.sidebar_components: List[Dict[str, Any]] = []
        # theme defaults
        self.theme = {
            "background": "#0b1220",
            "text": "#E6EEF3",
            "primary": "#00E0A8",
            "card": "#0f1720"
        }
        self.custom_css: Optional[str] = None
        self.page_config = {"layout": "wide", "initial_sidebar_state": "auto"}

    # -----------------------------
    # Theme & Page config
    # -----------------------------
    def set_theme(self, background: str = None, text: str = None, primary: str = None, card: str = None):
        if background:
            self.theme["background"] = background
        if text:
            self.theme["text"] = text
        if primary:
            self.theme["primary"] = primary
        if card:
            self.theme["card"] = card
        return self

    def set_custom_css(self, css: str):
        self.custom_css = css
        return self

    def set_page(self, layout: str = "wide", initial_sidebar_state: str = "auto"):
        self.page_config["layout"] = layout
        self.page_config["initial_sidebar_state"] = initial_sidebar_state
        return self

    # -----------------------------
    # Basic components
    # -----------------------------
    def add_title(self, text: str, color: str = None, size: str = "28px", align: str = "left"):
        self.components.append({
            "type": "title",
            "text": str(text),
            "color": color or self.theme["primary"],
            "size": size,
            "align": align
        })
        return self

    def add_text(self, text: str, color: str = None, size: str = "14px"):
        self.components.append({
            "type": "text",
            "text": str(text),
            "color": color or self.theme["text"],
            "size": size
        })
        return self

    def add_table(self, columns: Optional[List[str]] = None):
        self.components.append({
            "type": "table",
            "columns": columns  # None => all
        })
        return self

    def add_metric(self, label: str, value: Union[str, int, float], delta: Optional[Union[str, int, float]] = None):
        self.components.append({
            "type": "metric",
            "label": str(label),
            "value": str(value),
            "delta": None if delta is None else str(delta)
        })
        return self

    # -----------------------------
    # Plots
    # -----------------------------
    def add_plot(self, x: Optional[str] = None, y: Optional[str] = None, kind: str = "scatter", color: Optional[str] = None):
        kind = kind.lower()
        if kind not in self.VALID_PLOTS:
            raise ValueError(f"Tipo de gráfico '{kind}' no soportado.")
        if x and x not in self.data.columns:
            raise ValueError(f"La columna '{x}' no existe en el DataFrame.")
        if y and y not in self.data.columns and y is not None:
            raise ValueError(f"La columna '{y}' no existe en el DataFrame.")
        self.components.append({
            "type": "plot",
            "kind": kind,
            "x": x,
            "y": y,
            "color": color or self.theme["primary"]
        })
        return self

    # -----------------------------
    # Layout helpers
    # -----------------------------
    def add_row(self, col_widths: List[int], components: List[Dict[str, Any]]):
        """
        col_widths: list of ints (ratio) e.g. [2,1]
        components: list of component dicts (each dict is a mini spec like {"type":"plot", ...})
        The components list length should match len(col_widths).
        """
        # AÑADE ESTA VALIDACIÓN
        for i, comp in enumerate(components):
            if not isinstance(comp, dict):
                raise TypeError(
                    f"Componente en posición {i} no es un diccionario. "
                    f"Tipo recibido: {type(comp)}. "
                    f"Usa db.comp_*() para crear componentes (ej: db.comp_plot(), db.comp_metric())."
                )
        
        if len(col_widths) != len(components):
            raise ValueError("col_widths length must equal components length.")
        
        self.components.append({
            "type": "row",
            "widths": col_widths,
            "components": components
        })
        return self

    def add_tabs(self, tab_dict: Dict[str, List[Dict[str, Any]]]):
        """
        tab_dict: {"Tab name": [component_dicts], ...}
        """
        # Validación para tabs
        for tab_name, tab_components in tab_dict.items():
            for i, comp in enumerate(tab_components):
                if not isinstance(comp, dict):
                    raise TypeError(
                        f"En tab '{tab_name}', componente en posición {i} no es un diccionario. "
                        f"Tipo recibido: {type(comp)}."
                    )
        
        self.components.append({
            "type": "tabs",
            "tabs": tab_dict
        })
        return self

    def add_expander(self, label: str, components: List[Dict[str, Any]], expanded: bool = False):
        # Validación para expander
        for i, comp in enumerate(components):
            if not isinstance(comp, dict):
                raise TypeError(
                    f"En expander '{label}', componente en posición {i} no es un diccionario. "
                    f"Tipo recibido: {type(comp)}."
                )
        
        self.components.append({
            "type": "expander",
            "label": label,
            "components": components,
            "expanded": bool(expanded)
        })
        return self
    
    def add_blank(self, height: int = 20):
        """Agrega un espacio vertical directamente al dashboard"""
        self.components.append({
            "type": "spacer",
            "height": height
        })
        return self  # ← Retorna self para encadenamiento

    def comp_blank(self, height: int = 20):
        """Retorna un diccionario de spacer para usar en rows/tabs"""
        return {"type": "spacer", "height": height}

    # -----------------------------
    # Sidebar
    # -----------------------------
    def add_sidebar(self, comp: Dict[str, Any]):
        self.sidebar_components.append(comp)
        return self

    # -----------------------------
    # Internal: component builders for user convenience
    # -----------------------------
    def comp_title(self, text: str, color: str = None, size: str = "20px"):
        return {"type": "title", "text": text, "color": color or self.theme["primary"], "size": size}

    def comp_text(self, text: str, color: str = None, size: str = "14px"):
        return {"type": "text", "text": text, "color": color or self.theme["text"], "size": size}

    def comp_table(self, columns: Optional[List[str]] = None):
        return {"type": "table", "columns": columns}

    def comp_plot(self, x: Optional[str], y: Optional[str], kind: str = "scatter", color: Optional[str] = None):
        return {"type": "plot", "kind": kind, "x": x, "y": y, "color": color or self.theme["primary"]}

    def comp_metric(self, label: str, value: Any, delta: Any = None):
        return {"type": "metric", "label": label, "value": str(value), "delta": None if delta is None else str(delta)}

    # -----------------------------
    # Helper: render a component dict to streamlit python source code (string)
    # -----------------------------
    def _render_component_to_code(self, comp: Dict[str, Any], indent: int = 0) -> str:
        pad = " " * indent
        t = comp.get("type")

        if t == "title":
            text = comp.get("text", "")
            color = comp.get("color", self.theme["primary"])
            size = comp.get("size", "20px")
            text_align = comp.get("align", "left")
            html = f'''st.markdown(f\"\"\"<div style="display: flex; justify-content: {text_align};"><div class="viewx-card"><h1 class="viewx-title" style="font-size:{size}; color:{color}; margin:0;">{text}</h1></div></div>\"\"\", unsafe_allow_html=True)\n'''
            return textwrap.indent(html, prefix=pad)

        if t == "text":
            text = comp.get("text", "")
            size = comp.get("size", "14px")
            color = comp.get("color", self.theme["text"])
            html = f'''st.markdown(f\"\"\"<div class="viewx-card"><p class="viewx-small" style="font-size:{size}; color:{color}; margin:0;">{text}</p></div>\"\"\", unsafe_allow_html=True)\n'''
            return textwrap.indent(html, prefix=pad)

        if t == "table":
            cols = comp.get("columns")
            if cols:
                cols_py = json.dumps(cols, ensure_ascii=False)
                return textwrap.indent(f"st.dataframe(data[{cols_py}])\n", prefix=pad)
            return textwrap.indent("st.dataframe(data)\n", prefix=pad)

        if t == "metric":
            label = comp.get("label", "")
            value = comp.get("value", "")
            delta = comp.get("delta")
            if delta is not None:
                return textwrap.indent(f"st.metric({json.dumps(label)}, {json.dumps(value)}, delta={json.dumps(delta)})\n", prefix=pad)
            return textwrap.indent(f"st.metric({json.dumps(label)}, {json.dumps(value)})\n", prefix=pad)

        if t == "plot":
            kind = comp.get("kind", "scatter")
            x = comp.get("x")
            y = comp.get("y")
            color = comp.get("color", self.theme["primary"])
            # Build plotly code depending on kind
            if kind == "scatter":
                code = f"fig = px.scatter(data, x={json.dumps(x) if x else 'None'}, y={json.dumps(y) if y else 'None'})\n"
                code += f"fig.update_traces(marker=dict(color={json.dumps(color)}))\n"
            elif kind == "line":
                code = f"fig = px.line(data, x={json.dumps(x) if x else 'None'}, y={json.dumps(y) if y else 'None'})\n"
                code += f"fig.update_traces(line=dict(color={json.dumps(color)}))\n"
            elif kind == "hist":
                code = f"fig = px.histogram(data, x={json.dumps(x)})\n"
                code += f"fig.update_traces(marker=dict(color={json.dumps(color)}))\n"
            elif kind == "bar":
                code = f"fig = px.bar(data, x={json.dumps(x) if x else 'None'}, y={json.dumps(y) if y else 'None'})\n"
                code += f"fig.update_traces(marker=dict(color={json.dumps(color)}))\n"
            code += "st.plotly_chart(fig, width=\"stretch\")\n"
            return textwrap.indent(code, prefix=pad)

        if t == "row":
            widths = comp.get("widths", [1])
            comps = comp.get("components", [])
            widths_py = json.dumps(widths)
            row_code = f"cols = st.columns({widths_py})\n"
            for i, inner in enumerate(comps):
                row_code += f"with cols[{i}]:\n"
                row_code += self._render_component_to_code(inner, indent=4)
            return textwrap.indent(row_code, prefix=pad)

        if t == "tabs":
            tabs = comp.get("tabs", {})
            names = list(tabs.keys())
            names_py = json.dumps(names, ensure_ascii=False)
            tab_code = f"tab_objs = st.tabs({names_py})\n"
            for i, (name, inner_comps) in enumerate(tabs.items()):
                tab_code += f"with tab_objs[{i}]:\n"
                for inner in inner_comps:
                    tab_code += self._render_component_to_code(inner, indent=4)
            return textwrap.indent(tab_code, prefix=pad)

        if t == "expander":
            label = comp.get("label", "Expander")
            expanded = comp.get("expanded", False)
            exp_code = f"with st.expander({json.dumps(label)}, expanded={expanded}):\n"
            for inner in comp.get("components", []):
                exp_code += self._render_component_to_code(inner, indent=4)
            return textwrap.indent(exp_code, prefix=pad)
        
        if t == "spacer":
            height = comp.get("height", 20)
            html = f'''st.markdown(f\"\"\"<div style="height: {height}px;"></div>\"\"\", unsafe_allow_html=True)\n'''
            return textwrap.indent(html, prefix=pad)

        # fallback (unknown)
        return textwrap.indent(f"# Unknown component type: {t}\n", prefix=pad)

    # -----------------------------
    # Run: genera app y la ejecuta
    # -----------------------------
    def run(self, open_browser: bool = True):
        """Genera una app temporal y la ejecuta con Streamlit."""
        temp_dir = Path(tempfile.mkdtemp())
        app_file = temp_dir / "viewx_app.py"

        # Serializar dataframe a JSON seguro (listas)
        df_dict = self.data.to_dict(orient="list")
        json_str = json.dumps(df_dict, ensure_ascii=False)

        # Page config
        layout = self.page_config.get("layout", "wide")
        sidebar_state = self.page_config.get("initial_sidebar_state", "auto")

        # Start building app code
        code_parts = []
        
        # Imports and setup
        code_parts.append(f'''import streamlit as st\nimport pandas as pd\nimport plotly.express as px \
\nimport json

st.set_page_config(page_title={json.dumps(self.title)}, layout="{layout}", initial_sidebar_state="{sidebar_state}")

# --- Load data (from JSON embedded) ---
data = pd.DataFrame(json.loads(r\'\'\'{json_str}\'\'\'))

# --- Theme CSS injection ---
def _inject_css():
    base_css = \"\"\"
    <style>
    .stApp {{ background-color: {self.theme['background']}; color: {self.theme['text']} !important; }}
    .viewx-card {{ background: {self.theme['card']}; padding: 10px; border-radius: 8px; margin-bottom: 10px; }}
    .viewx-title {{ color: {self.theme['primary']}; font-weight:700; }}
    .viewx-small {{ color: {self.theme['text']}; }}
    
    </style>
    \"\"\"
    st.markdown(base_css, unsafe_allow_html=True)

_inject_css()''')

        # Add custom CSS if provided
        if self.custom_css:
            # Escape any triple quotes in the CSS
            safe_css = self.custom_css.replace("'''", "'''\"\"\"'''")
            code_parts.append(f'\n# Custom CSS\nst.markdown(r"""\n{safe_css}\n""", unsafe_allow_html=True)')

        # Title of page
        code_parts.append(f'\n# Page title\nst.title({json.dumps(self.title)})\n')

        # Sidebar components
        if self.sidebar_components:
            code_parts.append("with st.sidebar:")
            for comp in self.sidebar_components:
                sidebar_code = self._render_component_to_code(comp, indent=4)
                code_parts.append(sidebar_code.rstrip())
            code_parts.append("")

        # Main components rendering
        if self.components:
            code_parts.append("# Main components")
            for comp in self.components:
                component_code = self._render_component_to_code(comp, indent=0)
                code_parts.append(component_code.rstrip())

        # Footer
        code_parts.append('\nst.markdown("<hr style=\\"opacity:0.2\\">", unsafe_allow_html=True)')
        code_parts.append('st.caption("Generated by ViewX DashBoard Streamlit — StreamOps tooling")')

        # Join all code parts
        code = "\n".join(code_parts)

        # Write file
        app_file.write_text(code, encoding="utf-8")

        # Execute streamlit
        args = [
            sys.executable, "-m", "streamlit", "run", str(app_file)
        ]
        if not open_browser:
            args += ["--server.headless=true"]
        else:
            args += ["--server.headless=false"]

        process = subprocess.Popen(args)
        print(f"\n🔥 ViewX Dashboard corriendo...")
        print(f"→ Archivo temporal: {app_file}")
        print(f"→ Process ID: {process.pid}")
        
        # Keep reference to process
        self.process = process
        return process



