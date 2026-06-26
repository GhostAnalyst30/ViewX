from __future__ import annotations

from typing import Dict


def modal_attrs(modal_id: str, title_id: str) -> Dict[str, str]:
    return {
        "role": "dialog",
        "aria-modal": "true",
        "aria-labelledby": title_id,
        "id": modal_id,
    }


def overlay_attrs(label: str = "Close dialog") -> Dict[str, str]:
    return {
        "role": "button",
        "aria-label": label,
        "tabindex": "0",
    }


def attrs_to_html(attrs: Dict[str, str]) -> str:
    return " ".join(f'{k}="{v}"' for k, v in attrs.items())
