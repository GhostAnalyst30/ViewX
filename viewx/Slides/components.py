"""Componentes visuales para `viewx.Slides`."""

from __future__ import annotations

import html
from typing import Any, Dict, Iterable, List, Optional

from .slides_engine import ContextStack, Presentation, _css_value, _style_dict_to_string


ICON_MAP = {
    "gear": "&#9881;",
    "chart": "&#9635;",
    "star": "&#9733;",
    "check": "&#10003;",
    "bolt": "&#9889;",
    "user": "&#128100;",
    "users": "&#128101;",
    "database": "&#128451;",
    "cloud": "&#9729;",
    "rocket": "&#128640;",
    "warning": "&#9888;",
    "info": "i",
    "play": "&#9658;",
    "link": "&#128279;",
}


class Component:
    """Clase base de todos los componentes renderizables."""

    tag = "div"
    base_class = "vx-component"

    def __init__(self, **styles: Any) -> None:
        self.styles: Dict[str, Any] = {
            "position": "absolute",
            "left": "8%",
            "top": "12%",
            "z-index": "3",
        }
        self.styles.update(styles)
        self.classes: List[str] = [self.base_class]
        self.attrs: Dict[str, Any] = {}
        self.children: List[Component] = []
        self._animation: Optional[str] = None
        self._duration: float = 0.65
        self._delay: float = 0.0
        self._easing: str = "ease"
        self._loop: bool = False
        self._tooltip: str = ""
        self._register()

    def _register(self) -> None:
        parent = ContextStack.current()
        if parent is not None and hasattr(parent, "children"):
            parent.children.append(self)
            return
        pres = Presentation.active()
        if pres and pres.current_slide:
            pres.current_slide.add(self)

    def pos(self, left: Any = None, top: Any = None, right: Any = None, bottom: Any = None, unit: str = "%") -> "Component":
        for key, value in {"left": left, "top": top, "right": right, "bottom": bottom}.items():
            if value is not None:
                self.styles[key] = f"{value}{unit}" if isinstance(value, (int, float)) else value
        return self

    def size(self, width: Any = None, height: Any = None) -> "Component":
        if width is not None:
            self.styles["width"] = _css_value(width)
        if height is not None:
            self.styles["height"] = _css_value(height)
        return self

    def dimension(self, width: Any = None, height: Any = None) -> "Component":
        return self.size(width, height)

    def center(self, axis: str = "both") -> "Component":
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

    def align(self, text_align: str = "center") -> "Component":
        self.styles["text-align"] = text_align
        return self

    def z(self, value: int) -> "Component":
        self.styles["z-index"] = str(value)
        return self

    def opacity(self, value: float) -> "Component":
        self.styles["opacity"] = str(value)
        return self

    def color(self, value: str) -> "Component":
        self.styles["color"] = value
        return self

    def background(self, value: str) -> "Component":
        self.styles["background"] = value
        return self

    def font_size(self, value: Any) -> "Component":
        self.styles["font-size"] = _css_value(value)
        return self

    def weight(self, value: Any) -> "Component":
        self.styles["font-weight"] = str(value)
        return self

    def padding(self, top: Any = 16, right: Any = None, bottom: Any = None, left: Any = None) -> "Component":
        if right is None and bottom is None and left is None:
            self.styles["padding"] = _css_value(top)
        else:
            self.styles["padding"] = " ".join(_css_value(v if v is not None else top) for v in (top, right, bottom, left))
        return self

    def border(self, color: str = "var(--vx-border)", width: Any = 1, radius: Any = 14) -> "Component":
        self.styles["border"] = f"{_css_value(width)} solid {color}"
        self.styles["border-radius"] = _css_value(radius)
        return self

    def radius(self, value: Any) -> "Component":
        self.styles["border-radius"] = _css_value(value)
        return self

    def shadow(self, intensity: str = "md") -> "Component":
        shadows = {
            "sm": "0 5px 16px rgba(0,0,0,.18)",
            "md": "0 18px 48px var(--vx-shadow)",
            "lg": "0 28px 80px var(--vx-shadow)",
            "glow": "0 0 34px color-mix(in srgb, var(--vx-primary) 55%, transparent)",
        }
        self.styles["box-shadow"] = shadows.get(intensity, intensity)
        return self

    def card(self) -> "Component":
        if "vx-card" not in self.classes:
            self.classes.append("vx-card")
        self.padding(24)
        return self

    def tooltip(self, text: str) -> "Component":
        self._tooltip = text
        self.attrs["title"] = text
        return self

    def onclick(self, js: str) -> "Component":
        self.attrs["onclick"] = js
        return self

    def link_to_slide(self, slide_number: int) -> "Component":
        self.attrs["data-vx-slide"] = str(slide_number)
        return self

    def fade_in(self, delay: float = 0.0, duration: float = 0.65) -> "Component":
        return self._set_animation("fadeIn", delay, duration)

    def slide_in(self, direction: str = "left", delay: float = 0.0, duration: float = 0.65) -> "Component":
        name = {"left": "slideInLeft", "right": "slideInRight", "up": "slideInUp", "down": "slideInDown"}.get(direction, "slideInLeft")
        return self._set_animation(name, delay, duration)

    def zoom_in(self, delay: float = 0.0, duration: float = 0.65) -> "Component":
        return self._set_animation("zoomIn", delay, duration)

    def zoom_out(self, delay: float = 0.0, duration: float = 0.65) -> "Component":
        return self._set_animation("zoomOut", delay, duration)

    def bounce(self, delay: float = 0.0, duration: float = 0.8) -> "Component":
        return self._set_animation("bounce", delay, duration)

    def flip(self, delay: float = 0.0, duration: float = 0.75) -> "Component":
        return self._set_animation("flip", delay, duration)

    def spin(self, delay: float = 0.0, duration: float = 0.8) -> "Component":
        return self._set_animation("spin", delay, duration)

    def pulse_loop(self, duration: float = 1.6) -> "Component":
        self._loop = True
        return self._set_animation("pulse", 0, duration)

    def float_loop(self, duration: float = 3.0) -> "Component":
        self._loop = True
        return self._set_animation("float", 0, duration)

    def rotate_loop(self, duration: float = 3.0) -> "Component":
        self._loop = True
        return self._set_animation("rotate", 0, duration, "linear")

    def glow_loop(self, duration: float = 2.0) -> "Component":
        self._loop = True
        return self._set_animation("glow", 0, duration)

    def move_path(self, path_type: str = "float", speed: float = 3.0, delay: float = 0.0) -> "Component":
        mapping = {"float": "float", "x": "floatX", "orbit": "orbit", "drift": "drift", "wave": "wave", "heartbeat": "heartbeat", "pulse": "pulse", "rotate": "rotate"}
        self._loop = True
        easing = "linear" if path_type in ("rotate", "orbit") else "ease-in-out"
        return self._set_animation(mapping.get(path_type, "float"), delay, speed, easing)

    def _set_animation(self, name: str, delay: float, duration: float, easing: str = "ease") -> "Component":
        self._animation = name
        self._delay = delay
        self._duration = duration
        self._easing = easing
        return self

    def _style(self) -> str:
        styles = dict(self.styles)
        if self._animation:
            iteration = "infinite" if self._loop else "1"
            fill = "none" if self._loop else "both"
            styles["animation"] = f"{self._animation} {self._duration}s {self._easing} {self._delay}s {iteration} {fill}"
        return _style_dict_to_string(styles)

    def _attrs(self) -> str:
        attrs = {k: v for k, v in self.attrs.items() if v is not None}
        if self.classes:
            attrs["class"] = " ".join(self.classes)
        attrs["style"] = self._style()
        return " ".join(f'{html.escape(str(k), quote=True)}="{html.escape(str(v), quote=True)}"' for k, v in attrs.items())

    def _content(self) -> str:
        return "".join(child._render() for child in self.children)

    def _render(self) -> str:
        return f"<{self.tag} {self._attrs()}>{self._content()}</{self.tag}>"


class Text(Component):
    def __init__(self, text: str, color: Optional[str] = None, **styles: Any) -> None:
        super().__init__(**styles)
        self.text = text
        self.classes.append("vx-text")
        if color:
            self.color(color)

    def _content(self) -> str:
        return html.escape(self.text).replace("\n", "<br>")


class Title(Text):
    def __init__(self, text: str, **styles: Any) -> None:
        super().__init__(text, **styles)
        self.classes.append("vx-title")
        self.styles.setdefault("top", "10%")
        self.styles.setdefault("left", "7%")
        self.styles.setdefault("width", "86%")


class Subtitle(Text):
    def __init__(self, text: str, **styles: Any) -> None:
        super().__init__(text, **styles)
        self.classes.append("vx-subtitle")
        self.styles.setdefault("top", "26%")
        self.styles.setdefault("left", "7%")
        self.styles.setdefault("width", "82%")


class BulletList(Component):
    def __init__(self, items: Iterable[str], ordered: bool = False, **styles: Any) -> None:
        super().__init__(**styles)
        self.items = list(items)
        self.ordered = ordered
        self.classes.append("vx-bullets")
        self.styles.setdefault("left", "10%")
        self.styles.setdefault("top", "36%")
        self.styles.setdefault("width", "72%")

    def _render(self) -> str:
        tag = "ol" if self.ordered else "ul"
        items = "".join(f"<li>{html.escape(str(item))}</li>" for item in self.items)
        return f"<{tag} {self._attrs()}>{items}</{tag}>"


class Image(Component):
    tag = "img"

    def __init__(self, src: str, alt: str = "", **styles: Any) -> None:
        super().__init__(**styles)
        self.attrs.update({"src": src, "alt": alt})
        self.classes.append("vx-media")
        self.styles.setdefault("width", "360px")
        self.styles.setdefault("height", "240px")

    def _render(self) -> str:
        return f"<img {self._attrs()}>"


class Video(Component):
    tag = "video"

    def __init__(self, src: str, controls: bool = True, autoplay: bool = False, loop: bool = False, muted: bool = False, poster: str = "", **styles: Any) -> None:
        super().__init__(**styles)
        self.attrs["src"] = src
        if controls:
            self.attrs["controls"] = "controls"
        if autoplay:
            self.attrs["autoplay"] = "autoplay"
        if loop:
            self.attrs["loop"] = "loop"
        if muted:
            self.attrs["muted"] = "muted"
        if poster:
            self.attrs["poster"] = poster
        self.classes.append("vx-media")
        self.styles.setdefault("width", "520px")
        self.styles.setdefault("height", "292px")


class Hyperlink(Component):
    tag = "a"

    def __init__(self, text: str, href: str, target: str = "_blank", **styles: Any) -> None:
        super().__init__(**styles)
        self.text = text
        self.attrs.update({"href": href, "target": target, "rel": "noopener noreferrer"})
        self.classes.append("vx-link")

    def _content(self) -> str:
        return html.escape(self.text)


Link = Hyperlink


class Button(Component):
    tag = "a"

    def __init__(self, text: str, href: str = "#", target: str = "_self", **styles: Any) -> None:
        super().__init__(**styles)
        self.text = text
        self.attrs.update({"href": href, "target": target})
        self.classes.append("vx-button")

    def _content(self) -> str:
        return html.escape(self.text)


class IconStat(Component):
    def __init__(self, icon: str, value: Any, label: str, prefix: str = "", suffix: str = "", **styles: Any) -> None:
        super().__init__(**styles)
        self.icon = ICON_MAP.get(icon, html.escape(icon))
        self.value = value
        self.label = label
        self.prefix = prefix
        self.suffix = suffix
        self.classes.append("vx-iconstat")
        self.card()
        self.styles.setdefault("width", "230px")

    def _content(self) -> str:
        return f'<span class="icon">{self.icon}</span><div class="value">{html.escape(str(self.prefix))}{html.escape(str(self.value))}{html.escape(str(self.suffix))}</div><div class="label">{html.escape(self.label)}</div>'


class RotatingIcon(Component):
    def __init__(self, icon: str, size: Any = 50, color: str = "var(--vx-primary)", speed: float = 4.0, **styles: Any) -> None:
        super().__init__(**styles)
        self.icon = ICON_MAP.get(icon, html.escape(icon))
        self.styles.update({"font-size": _css_value(size), "color": color, "line-height": "1", "width": _css_value(size), "height": _css_value(size), "display": "flex", "align-items": "center", "justify-content": "center"})
        self.rotate_loop(speed)

    def _content(self) -> str:
        return self.icon


class MovingFigure(Component):
    def __init__(self, shape: str = "circle", color: str = "var(--vx-primary)", size: Any = 80, path: str = "float", **styles: Any) -> None:
        super().__init__(**styles)
        self.shape = shape
        self.styles.update({"width": _css_value(size), "height": _css_value(size), "background": color})
        if shape == "circle":
            self.styles["border-radius"] = "50%"
        elif shape == "rounded":
            self.styles["border-radius"] = "24px"
        elif shape == "diamond":
            self.styles["transform"] = "rotate(45deg)"
        else:
            self.styles.setdefault("border-radius", "8px")
        self.shadow("glow")
        self.move_path(path)


__all__ = [
    "Component", "Title", "Subtitle", "Text", "BulletList", "Image", "Video", "Hyperlink", "Link", "Button",
    "IconStat", "RotatingIcon", "MovingFigure",
]
