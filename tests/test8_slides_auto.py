"""Auto-generated slides from a DataFrame."""

from viewx.datasets import load_iris
from viewx.Slides import Presentation

df = load_iris()

path = Presentation.auto_generate(
    df,
    title="Iris Dataset Overview",
    theme="ocean",
    filename="output/test8_auto_slides.html",
    show=False,
)
print(f"Presentation.auto_generate -> {path}")
