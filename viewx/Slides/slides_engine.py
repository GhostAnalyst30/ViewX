"""Motor HTML para presentaciones programáticas de Viewx.Slides.

Este archivo contiene el núcleo del paquete: `Presentation`, `Slide`, `Grid`,
el registro contextual de componentes, temas integrados y exportación HTML.
"""

from __future__ import annotations

import html
import json
import os
import warnings
import webbrowser
from dataclasses import dataclass
from typing import Any, ClassVar, Dict, List, Optional

import pandas as pd

from viewx.shared import PLOTLY_CDN
from viewx.shared.themes import (
    THEMES as SHARED_THEMES,
    LEGACY_ALIASES,
    get_theme,
    resolve_theme,
)


KEYFRAMES = """
@keyframes fadeIn { from { opacity:0; } to { opacity:1; } }
@keyframes slideInLeft { from { opacity:0; transform:translateX(-80px) var(--vx-transform, none); } to { opacity:1; transform:translateX(0) var(--vx-transform, none); } }
@keyframes slideInRight { from { opacity:0; transform:translateX(80px) var(--vx-transform, none); } to { opacity:1; transform:translateX(0) var(--vx-transform, none); } }
@keyframes slideInUp { from { opacity:0; transform:translateY(60px) var(--vx-transform, none); } to { opacity:1; transform:translateY(0) var(--vx-transform, none); } }
@keyframes slideInDown { from { opacity:0; transform:translateY(-60px) var(--vx-transform, none); } to { opacity:1; transform:translateY(0) var(--vx-transform, none); } }
@keyframes zoomIn { from { opacity:0; transform:scale(.55) var(--vx-transform, none); } to { opacity:1; transform:scale(1) var(--vx-transform, none); } }
@keyframes zoomOut { from { opacity:0; transform:scale(1.35) var(--vx-transform, none); } to { opacity:1; transform:scale(1) var(--vx-transform, none); } }
@keyframes bounce { 0% { opacity:0; transform:translateY(0); } 45% { opacity:1; transform:translateY(-22px) var(--vx-bounce,); } 70% { transform:translateY(7px); } 100% { opacity:1; transform:translateY(0); } }
@keyframes flip { from { opacity:0; transform:rotateX(-90deg) var(--vx-transform, none); } to { opacity:1; transform:rotateX(0) var(--vx-transform, none); } }
@keyframes spin { from { opacity:0; transform:rotate(-180deg) scale(.5) var(--vx-transform, none); } to { opacity:1; transform:rotate(0) scale(1) var(--vx-transform, none); } }
@keyframes shake { 0%,100% { transform:translateX(0); } 20% { transform:translateX(-10px); } 40% { transform:translateX(10px); } 60% { transform:translateX(-6px); } 80% { transform:translateX(6px); } }
@keyframes pulse { 0%,100% { transform:scale(1); opacity:1; } 50% { transform:scale(1.12); opacity:.86; } }
@keyframes glow { 0%,100% { filter:drop-shadow(0 0 4px currentColor); } 50% { filter:drop-shadow(0 0 22px currentColor); } }
@keyframes float { 0%,100% { transform:translateY(0); } 50% { transform:translateY(-16px); } }
@keyframes floatX { 0%,100% { transform:translateX(0); } 50% { transform:translateX(18px); } }
@keyframes rotate { from { transform:rotate(0deg); } to { transform:rotate(360deg); } }
@keyframes orbit { from { transform:rotate(0deg) translateX(70px) rotate(0deg); } to { transform:rotate(360deg) translateX(70px) rotate(-360deg); } }
@keyframes drift { 0%,100% { transform:translate(0,0); } 25% { transform:translate(28px,-18px); } 50% { transform:translate(-18px,28px); } 75% { transform:translate(18px,12px); } }
@keyframes wave { 0%,100% { transform:translateY(0); } 50% { transform:translateY(-28px); } }
@keyframes heartbeat { 0%,100% { transform:scale(1); } 50% { transform:scale(1.26); } }
@keyframes shimmer { from { background-position:-200% 0; } to { background-position:200% 0; } }
@keyframes morphIn { from { opacity:0; clip-path:circle(0% at 50% 50%); } to { opacity:1; clip-path:circle(100% at 50% 50%); } }
@keyframes blurIn { from { opacity:0; filter:blur(12px); transform:scale(.96); } to { opacity:1; filter:blur(0); transform:scale(1); } }
@keyframes revealUp { from { opacity:0; transform:translateY(40px) scale(.97); clip-path:inset(0 0 100% 0); } to { opacity:1; transform:translateY(0) scale(1); clip-path:inset(0 0 0 0); } }
@keyframes skewIn { from { opacity:0; transform:translateX(-40px) skewX(8deg); } to { opacity:1; transform:translateX(0) skewX(0); } }
"""

# Slide palettes derive from the canonical shared registry so one theme name
# works everywhere. Legacy slide names (dark, light, ocean, ...) keep working.
THEMES: Dict[str, Dict[str, str]] = {
    name: dict(spec["slides"]) for name, spec in SHARED_THEMES.items()
}
for _alias, _target in LEGACY_ALIASES.items():
    THEMES.setdefault(_alias, THEMES[_target])


def _css_value(value: Any, default_unit: str = "px") -> str:
    if value is None:
        return ""
    if isinstance(value, (int, float)):
        return f"{value}{default_unit}"
    return str(value)


def _style_dict_to_string(styles: Dict[str, Any]) -> str:
    return ";".join(f"{k}:{v}" for k, v in styles.items() if v is not None and v != "") + ";"


class ContextStack:
    """Pila interna para registrar hijos dentro de contenedores como `Grid`."""

    _stack: ClassVar[List[Any]] = []

    @classmethod
    def push(cls, component: Any) -> None:
        cls._stack.append(component)

    @classmethod
    def pop(cls) -> Optional[Any]:
        return cls._stack.pop() if cls._stack else None

    @classmethod
    def current(cls) -> Optional[Any]:
        return cls._stack[-1] if cls._stack else None


@dataclass
class Slide:
    """Representa una diapositiva de la presentación."""

    title: str = ""
    index: Optional[int] = None
    bg: str = ""
    overlay_opacity: float = 0.0
    notes: str = ""
    transition: Optional[str] = None

    def __post_init__(self) -> None:
        self.elements: List[Any] = []

    def __enter__(self) -> "Slide":
        pres = Presentation.active()
        if pres is None:
            pres = Presentation("Presentación")
        pres.current_slide = self
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        pres = Presentation.active()
        if pres is not None:
            if self.index is None:
                self.index = len(pres.slides) + 1
            pres.slides.append(self)
            pres.current_slide = None

    def add(self, component: Any) -> Any:
        self.elements.append(component)
        return component

    def _background_style(self) -> str:
        if not self.bg:
            return ""
        if self.bg.startswith(("http://", "https://", "/", "./", "../")) or any(self.bg.lower().endswith(ext) for ext in (".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg")):
            safe = html.escape(self.bg, quote=True)
            return f"background-image:url('{safe}');background-size:cover;background-position:center;"
        return f"background:{self.bg};"

    def _render(self, number: int, total: int, show_numbers: bool = True) -> str:
        body = "".join(getattr(el, "_render")() for el in self.elements)
        overlay = ""
        if self.overlay_opacity:
            overlay = f'<div class="vx-slide-overlay" style="background:rgba(0,0,0,{self.overlay_opacity});"></div>'
        notes = html.escape(self.notes, quote=False)
        num = f'<div class="vx-slide-number">{number} / {total}</div>' if show_numbers else ""
        title_attr = html.escape(self.title, quote=True)
        trans = f' data-transition="{self.transition}"' if self.transition else ""
        return f'<section class="vx-slide" id="slide-{number}" data-title="{title_attr}" data-notes="{notes}"{trans} style="{self._background_style()}">{overlay}<div class="vx-layer">{body}</div>{num}</section>'


class Grid:
    """Contenedor CSS Grid para posicionar varios componentes dentro de una slide."""

    def __init__(self, columns: int | str = 2, rows: int | str = "auto", gap: int | str = 24, **styles: Any) -> None:
        self.children: List[Any] = []
        self.styles: Dict[str, Any] = {
            "position": "absolute",
            "display": "grid",
            "grid-template-columns": f"repeat({columns}, 1fr)" if isinstance(columns, int) else columns,
            "grid-template-rows": f"repeat({rows}, auto)" if isinstance(rows, int) else rows,
            "gap": _css_value(gap),
            "left": "5%",
            "top": "20%",
            "width": "90%",
        }
        self.styles.update(styles)
        self._register()

    def _register(self) -> None:
        parent = ContextStack.current()
        if parent is not None and hasattr(parent, "children"):
            parent.children.append(self)
            return
        pres = Presentation.active()
        if pres and pres.current_slide:
            pres.current_slide.add(self)

    def __enter__(self) -> "Grid":
        ContextStack.push(self)
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        ContextStack.pop()

    def pos(self, left: Any = None, top: Any = None, right: Any = None, bottom: Any = None, unit: str = "%") -> "Grid":
        for key, value in {"left": left, "top": top, "right": right, "bottom": bottom}.items():
            if value is not None:
                self.styles[key] = f"{value}{unit}" if isinstance(value, (int, float)) else value
        return self

    def size(self, width: Any = None, height: Any = None) -> "Grid":
        if width is not None:
            self.styles["width"] = _css_value(width)
        if height is not None:
            self.styles["height"] = _css_value(height)
        return self

    def center(self, axis: str = "both") -> "Grid":
        if axis in ("both", "x"):
            self.styles["left"] = "50%"
        if axis in ("both", "y"):
            self.styles["top"] = "50%"
        if axis == "both":
            self.styles["transform"] = "translate(-50%, -50%)"
        elif axis == "x":
            self.styles["transform"] = "translateX(-50%)"
        elif axis == "y":
            self.styles["transform"] = "translateY(-50%)"
        return self

    def _render(self) -> str:
        children = "".join(child._render() for child in self.children)
        return f'<div class="vx-grid" style="{_style_dict_to_string(self.styles)}">{children}</div>'


class Presentation:
    """Presentación HTML interactiva creada desde Python."""

    _active: ClassVar[Optional["Presentation"]] = None

    def __init__(
        self,
        title: str = "Presentación",
        theme: Optional[str] = None,
        width: int = 1280,
        height: int = 720,
        transition: str = "slide",
        show_numbers: bool = True,
    ) -> None:
        self.title = title
        self.theme_name = theme if theme is not None else get_theme()
        self.width = width
        self.height = height
        self.transition = transition
        self.show_numbers = show_numbers
        self.slides: List[Slide] = []
        self.current_slide: Optional[Slide] = None
        self.metadata: Dict[str, str] = {"title": title}
        self.font_url = ""
        self.font_name = ""
        self.logo_url = ""
        self.music_url = ""
        self.auto_seconds = 0
        self.kiosk_mode = False
        self.custom_css = ""
        self.extra_head = ""
        Presentation._active = self

    @classmethod
    def active(cls) -> Optional["Presentation"]:
        return cls._active

    def set_theme(self, name: str) -> "Presentation":
        self.theme_name = name
        return self

    def custom_theme(self, name: str = "custom", **colors: str) -> "Presentation":
        THEMES[name] = {**THEMES.get(self.theme_name, THEMES["dark"]), **colors}
        self.theme_name = name
        return self

    def font(self, name: str, weights: str = "400;500;600;700;800") -> "Presentation":
        family = name.replace(" ", "+")
        self.font_url = f"https://fonts.googleapis.com/css2?family={family}:wght@{weights}&display=swap"
        self.font_name = f"'{name}', sans-serif"
        return self

    def logo(self, url: str) -> "Presentation":
        self.logo_url = url
        return self

    def music(self, url: str) -> "Presentation":
        self.music_url = url
        return self

    def auto_advance(self, seconds: int) -> "Presentation":
        self.auto_seconds = seconds
        return self

    def kiosk(self, value: bool = True) -> "Presentation":
        self.kiosk_mode = value
        return self

    def meta(self, **metadata: str) -> "Presentation":
        self.metadata.update(metadata)
        return self

    def add_css(self, css: str) -> "Presentation":
        self.custom_css += "\n" + css
        return self

    def add_slide(self, slide: Slide) -> Slide:
        if slide.index is None:
            slide.index = len(self.slides) + 1
        self.slides.append(slide)
        return slide

    @property
    def theme(self) -> Dict[str, str]:
        if self.theme_name in THEMES:
            return THEMES[self.theme_name]
        return THEMES[resolve_theme(self.theme_name)]

    def _controls_html(self) -> str:
        if self.kiosk_mode:
            return ""
        return """
<div id="vx-controls">
  <button type="button" onclick="prevSlide()" title="Anterior">&#8592;</button>
  <button type="button" onclick="toggleFullscreen()" title="Pantalla completa">&#9974;</button>
  <span id="vx-counter">1 / 1</span>
  <button type="button" onclick="toggleNotes()" title="Notas">N</button>
  <button type="button" onclick="nextSlide()" title="Siguiente">&#8594;</button>
</div>
"""

    def _base_css(self) -> str:
        t = self.theme
        font = self.font_name or t["font"]
        return f"""
*{{box-sizing:border-box;margin:0;padding:0}}
{KEYFRAMES}
:root{{--vx-bg:{t['bg']};--vx-surface:{t['surface']};--vx-primary:{t['primary']};--vx-accent:{t['accent']};--vx-text:{t['text']};--vx-muted:{t['muted']};--vx-border:{t['border']};--vx-shadow:{t['shadow']};--vx-font:{font};--vx-ease: cubic-bezier(0.32,0.72,0,1);--vx-ease-out: cubic-bezier(0.16,1,0.3,1);}}
html,body{{width:100%;height:100%;overflow:hidden;background:var(--vx-bg);color:var(--vx-text);font-family:var(--vx-font);-webkit-font-smoothing:antialiased;-moz-osx-font-smoothing:grayscale;}}
body{{background:radial-gradient(circle at top right, color-mix(in srgb, var(--vx-accent) 22%, transparent), transparent 34%), radial-gradient(circle at bottom left, color-mix(in srgb, var(--vx-primary) 12%, transparent), transparent 28%), var(--vx-bg);}}
#vx-deck{{width:100vw;height:100vh;position:relative;overflow:hidden;perspective:1200px;}}
.vx-slide{{position:absolute;inset:0;display:none;overflow:hidden;background:var(--vx-bg);will-change:transform,opacity,filter;}}
.vx-slide.active{{display:block;animation:blurIn .55s var(--vx-ease) both;}}
.vx-slide[data-transition="fade"].active{{animation:fadeIn .5s var(--vx-ease) both;}}
.vx-slide[data-transition="slide"].active{{animation:slideInUp .55s var(--vx-ease) both;}}
.vx-slide[data-transition="zoom"].active{{animation:zoomIn .55s var(--vx-ease) both;}}
.vx-slide[data-transition="morph"].active{{animation:morphIn .6s var(--vx-ease) both;}}
.vx-slide.exit{{display:block;animation:blurIn .3s var(--vx-ease) reverse both;pointer-events:none;}}
.vx-slide[data-transition="fade"].exit{{animation:fadeIn .25s var(--vx-ease) reverse both;}}
.vx-slide[data-transition="slide"].exit{{animation:slideInUp .3s var(--vx-ease) reverse both;}}
.vx-slide[data-transition="zoom"].exit{{animation:zoomIn .3s var(--vx-ease) reverse both;}}
.vx-layer{{position:absolute;inset:0;z-index:2;}}
.vx-slide-overlay{{position:absolute;inset:0;z-index:1;}}
.vx-component{{position:absolute;max-width:100%;color:var(--vx-text);will-change:transform,opacity;}}
.vx-grid .vx-component{{position:relative;left:auto!important;top:auto!important;right:auto!important;bottom:auto!important;}}
.vx-card{{background:linear-gradient(180deg, color-mix(in srgb, var(--vx-surface) 94%, white), var(--vx-surface));border:1px solid var(--vx-border);border-radius:22px;box-shadow:0 18px 55px var(--vx-shadow);transition:transform .45s var(--vx-ease), box-shadow .45s var(--vx-ease);}}
.vx-card:hover{{transform:translateY(-3px);box-shadow:0 28px 72px var(--vx-shadow);}}
.vx-title{{font-size:clamp(42px,6vw,86px);font-weight:800;letter-spacing:-.055em;line-height:.98;}}
.vx-title::after{{content:'';display:block;width:clamp(60px,8vw,120px);height:4px;border-radius:2px;background:linear-gradient(90deg,var(--vx-primary),var(--vx-accent));margin-top:clamp(16px,2vw,28px);}}
.vx-subtitle{{font-size:clamp(22px,3vw,42px);font-weight:600;color:var(--vx-muted);line-height:1.18;margin-top:clamp(10px,1vw,18px);}}
.vx-text{{font-size:clamp(17px,1.6vw,24px);line-height:1.58;}}
.vx-bullets{{font-size:clamp(18px,1.7vw,25px);line-height:1.55;padding-left:1.2em;}}
.vx-bullets li{{margin:.36em 0;transition:transform .3s var(--vx-ease);}}
.vx-bullets li:hover{{transform:translateX(6px);}}
.vx-button{{display:inline-flex;align-items:center;justify-content:center;gap:.55em;text-decoration:none;border:0;border-radius:999px;padding:14px 28px;background:linear-gradient(135deg,var(--vx-primary),var(--vx-accent));color:white;font-weight:800;cursor:pointer;box-shadow:0 12px 28px var(--vx-shadow);transition:transform .35s var(--vx-ease), filter .35s var(--vx-ease), box-shadow .35s var(--vx-ease);position:relative;overflow:hidden;}}
.vx-button::before{{content:'';position:absolute;inset:0;background:linear-gradient(135deg,transparent 40%,rgba(255,255,255,.15) 50%,transparent 60%);transform:translateX(-100%);transition:transform .6s var(--vx-ease);}}
.vx-button:hover{{transform:translateY(-3px) scale(1.02);filter:brightness(1.08);box-shadow:0 18px 40px var(--vx-shadow);}}
.vx-button:hover::before{{transform:translateX(100%);}}
.vx-button:active{{transform:translateY(-1px) scale(.98);}}
.vx-link{{color:var(--vx-accent);text-decoration:none;font-weight:700;border-bottom:1px solid currentColor;transition:border-color .25s var(--vx-ease);}}
.vx-link:hover{{border-bottom-color:transparent;}}
.vx-media{{object-fit:cover;border-radius:22px;box-shadow:0 18px 48px var(--vx-shadow);transition:transform .45s var(--vx-ease), box-shadow .45s var(--vx-ease);}}
.vx-media:hover{{transform:scale(1.02);box-shadow:0 28px 64px var(--vx-shadow);}}
.vx-iconstat{{text-align:center;padding:28px 32px;transition:transform .35s var(--vx-ease);}}
.vx-iconstat:hover{{transform:scale(1.04);}}
.vx-iconstat .icon{{font-size:48px;display:block;margin-bottom:12px;}}
.vx-iconstat .value{{font-size:54px;font-weight:900;color:var(--vx-primary);line-height:1;letter-spacing:-.03em;}}
.vx-iconstat .label{{font-size:15px;color:var(--vx-muted);margin-top:10px;font-weight:600;text-transform:uppercase;letter-spacing:.08em;}}
.vx-plot{{background:var(--vx-surface);border:1px solid var(--vx-border);border-radius:22px;padding:12px;box-shadow:0 18px 55px var(--vx-shadow);}}
.vx-slide-number{{position:absolute;right:24px;bottom:22px;color:var(--vx-muted);font-size:13px;z-index:8;opacity:.5;font-weight:500;letter-spacing:.04em;}}
#vx-progress{{position:fixed;left:0;top:0;height:3px;width:0;background:linear-gradient(90deg,var(--vx-primary),var(--vx-accent));z-index:99;transition:width .55s var(--vx-ease);box-shadow:0 0 12px var(--vx-primary);}}
#vx-controls{{position:fixed;left:50%;bottom:22px;transform:translateX(-50%);z-index:100;display:flex;align-items:center;gap:6px;padding:6px 8px;border:1px solid var(--vx-border);border-radius:999px;background:rgba(0,0,0,.55);backdrop-filter:blur(16px) saturate(180%);-webkit-backdrop-filter:blur(16px) saturate(180%);opacity:0;transition:opacity .35s var(--vx-ease), transform .35s var(--vx-ease);transform-origin:bottom center;}}
body:hover #vx-controls{{opacity:1;}}
#vx-controls button{{border:0;background:transparent;color:white;font-size:16px;cursor:pointer;padding:8px 12px;border-radius:999px;transition:background .2s var(--vx-ease), transform .2s var(--vx-ease);}}
#vx-controls button:hover{{background:rgba(255,255,255,.12);transform:scale(1.1);}}
#vx-controls button:active{{transform:scale(.95);}}
#vx-counter{{min-width:54px;text-align:center;font-size:12px;color:#fff;opacity:.7;font-weight:500;letter-spacing:.03em;}}
#vx-dots{{position:fixed;left:50%;bottom:82px;transform:translateX(-50%);display:flex;gap:6px;z-index:100;opacity:0;transition:opacity .35s var(--vx-ease);}}
body:hover #vx-dots{{opacity:1;}}
.vx-dot{{width:6px;height:6px;border-radius:99px;background:rgba(255,255,255,.25);cursor:pointer;transition:all .45s var(--vx-ease);position:relative;}}
.vx-dot::after{{content:'';position:absolute;inset:-4px;border-radius:99px;}}
.vx-dot:hover{{background:rgba(255,255,255,.45);transform:scale(1.2);}}
.vx-dot.active{{width:28px;background:var(--vx-primary);box-shadow:0 0 8px var(--vx-primary);}}
#vx-notes{{display:none;position:fixed;left:0;right:0;bottom:0;z-index:101;max-height:34vh;overflow:auto;padding:22px 28px;background:rgba(0,0,0,.92);border-top:2px solid var(--vx-primary);color:#fff;font-size:14px;line-height:1.6;backdrop-filter:blur(8px);}}
#vx-notes.visible{{display:block;animation:slideInUp .3s var(--vx-ease) both;}}
#vx-logo{{position:fixed;top:20px;left:22px;max-height:40px;z-index:80;opacity:.85;transition:opacity .3s var(--vx-ease);}}
#vx-logo:hover{{opacity:1;}}
@media print{{#vx-controls,#vx-dots,#vx-progress,#vx-notes{{display:none!important}}.vx-slide{{display:block!important;position:relative;page-break-after:always;width:100vw;height:100vh;animation:none!important;}}}}
{self.custom_css}
"""

    def save(self, path: str = "presentacion.html", open_browser: bool = False) -> str:
        """Write the presentation to an HTML file. Returns the absolute path."""
        total = len(self.slides)
        if total == 0:
            raise ValueError("La presentación no contiene slides. Usa `with Slide(...):` antes de guardar.")
        filename = path
        slides_html = "\n".join(slide._render(i + 1, total, self.show_numbers) for i, slide in enumerate(self.slides))
        dots = "".join(f'<button class="vx-dot" type="button" onclick="goToSlide({i})" title="Slide {i+1}"></button>' for i in range(total))
        font_link = f'<link rel="stylesheet" href="{html.escape(self.font_url, quote=True)}">' if self.font_url else ""
        logo = f'<img id="vx-logo" src="{html.escape(self.logo_url, quote=True)}" alt="Logo">' if self.logo_url else ""
        music = f'<audio id="vx-audio" src="{html.escape(self.music_url, quote=True)}" autoplay loop></audio>' if self.music_url else ""
        auto_js = f"setInterval(nextSlide, {int(self.auto_seconds) * 1000});" if self.auto_seconds else ""
        titles_json = json.dumps([s.title for s in self.slides], ensure_ascii=False)
        html_doc = f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(self.title)}</title>
{font_link}
<script src="{PLOTLY_CDN}"></script>
<style>{self._base_css()}</style>
{self.extra_head}
</head>
<body>
{music}
{logo}
<div id="vx-progress"></div>
<div id="vx-deck">{slides_html}</div>
<div id="vx-dots">{dots}</div>
{self._controls_html()}
<div id="vx-notes"></div>
<script>
const slides = Array.from(document.querySelectorAll('.vx-slide'));
const dots = Array.from(document.querySelectorAll('.vx-dot'));
const progress = document.getElementById('vx-progress');
const counter = document.getElementById('vx-counter');
const notesPanel = document.getElementById('vx-notes');
const titles = {titles_json};
let current = 0;
let isTransitioning = false;
function restartAnimations(slide) {{
  slide.querySelectorAll('[style*=animation]').forEach(el => {{ const a = el.style.animation; el.style.animation = 'none'; void el.offsetWidth; el.style.animation = a; }});
  slide.querySelectorAll('.js-plotly-plot').forEach(el => {{ if (window.Plotly) Plotly.Plots.resize(el); }});
}}
function updateUI(direction) {{
  slides.forEach((s,i) => {{
    s.classList.toggle('active', i===current);
    s.classList.remove('exit');
  }});
  dots.forEach((d,i)=>d.classList.toggle('active', i===current));
  if(progress) progress.style.width = ((current+1)/slides.length*100)+'%';
  if(counter) counter.textContent = (current+1)+' / '+slides.length;
  if(notesPanel && notesPanel.classList.contains('visible')) notesPanel.innerHTML = slides[current].dataset.notes || '<em>Sin notas.</em>';
  setTimeout(()=>{{ restartAnimations(slides[current]); isTransitioning = false; }}, 80);
}}
function goToSlide(i) {{
  if(isTransitioning || i < 0 || i >= slides.length || i === current) return;
  isTransitioning = true;
  slides[current].classList.add('exit');
  current = i;
  setTimeout(() => updateUI(), 300);
}}
function nextSlide() {{ goToSlide(current+1); }}
function prevSlide() {{ goToSlide(current-1); }}
function toggleFullscreen() {{ if(!document.fullscreenElement) document.documentElement.requestFullscreen(); else document.exitFullscreen(); }}
function toggleNotes() {{ notesPanel.classList.toggle('visible'); notesPanel.innerHTML = slides[current].dataset.notes || '<em>Sin notas.</em>'; if(notesPanel.classList.contains('visible')) setTimeout(()=>notesPanel.scrollTop=0,50); }}
document.addEventListener('keydown', e => {{
  if(['INPUT','TEXTAREA','SELECT'].includes(e.target.tagName)) return;
  if(e.key === 'ArrowRight' || e.key === ' ' || e.key === 'PageDown') {{ e.preventDefault(); nextSlide(); }}
  if(e.key === 'ArrowLeft' || e.key === 'PageUp') {{ e.preventDefault(); prevSlide(); }}
  if(e.key === 'Home') goToSlide(0);
  if(e.key === 'End') goToSlide(slides.length-1);
  if(e.key.toLowerCase() === 'f') toggleFullscreen();
  if(e.key.toLowerCase() === 'n') toggleNotes();
}});
let touchX = 0, touchY = 0;
document.addEventListener('touchstart', e => {{ touchX = e.touches[0].clientX; touchY = e.touches[0].clientY; }});
document.addEventListener('touchend', e => {{
  const dx = e.changedTouches[0].clientX - touchX;
  const dy = e.changedTouches[0].clientY - touchY;
  if(Math.abs(dx) > Math.abs(dy) && Math.abs(dx) > 50) {{ if(dx < -50) nextSlide(); if(dx > 50) prevSlide(); }}
}});
let wheelTimeout;
document.addEventListener('wheel', e => {{
  if(e.target.closest('.js-plotly-plot, .vx-plot')) return;
  if(wheelTimeout) return;
  wheelTimeout = setTimeout(()=>{{ wheelTimeout = null; }}, 600);
  if(e.deltaY > 20) nextSlide();
  else if(e.deltaY < -20) prevSlide();
}}, {{passive:true}});
document.querySelectorAll('[data-vx-slide]').forEach(a => a.addEventListener('click', e => {{ e.preventDefault(); goToSlide(parseInt(a.dataset.vxSlide, 10)-1); }}));
updateUI();
{auto_js}
</script>
</body>
</html>"""
        directory = os.path.dirname(filename)
        if directory:
            os.makedirs(directory, exist_ok=True)
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html_doc)
        if open_browser:
            webbrowser.open("file://" + os.path.abspath(filename))
        return os.path.abspath(filename)

    def export(self, filename: str = "presentacion.html", open_browser: bool = False) -> str:
        """Deprecated: use ``save()`` instead."""
        warnings.warn(
            "Presentation.export() is deprecated; use save(path) or show().",
            DeprecationWarning, stacklevel=2,
        )
        return self.save(filename, open_browser=open_browser)

    def show(self, path: str = "presentacion.html") -> str:
        """Write the presentation and open it in the default browser."""
        return self.save(path, open_browser=True)

    @classmethod
    def auto(
        cls,
        df: "pd.DataFrame",
        title: str = "Dataset Overview",
        theme: Optional[str] = None,
        columns: Optional[List[str]] = None,
        max_slides: int = 8,
    ) -> "Presentation":
        """Build an auto-generated slide deck from a DataFrame.

        Returns the Presentation; call ``.save(path)`` or ``.show()`` on it.
        """
        from .auto_builder import build_auto_presentation

        return build_auto_presentation(
            df, title=title, theme=theme, columns=columns, max_slides=max_slides,
        )

    @classmethod
    def auto_generate(
        cls,
        df: "pd.DataFrame",
        title: str = "Dataset Overview",
        theme: Optional[str] = None,
        filename: str = "auto_slides.html",
        columns: Optional[List[str]] = None,
        max_slides: int = 8,
        show: bool = True,
    ) -> str:
        """Deprecated: use ``Presentation.auto(df, ...).save(path)`` instead."""
        warnings.warn(
            "Presentation.auto_generate() is deprecated; use Presentation.auto(df).save(path).",
            DeprecationWarning, stacklevel=2,
        )
        pres = cls.auto(df, title=title, theme=theme, columns=columns, max_slides=max_slides)
        return pres.save(filename, open_browser=show)


__all__ = ["Presentation", "Slide", "Grid", "ContextStack", "THEMES"]
