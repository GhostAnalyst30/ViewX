from viewx.DashBoard import DashBoard
from viewx.datasets import load_dataset

df = load_dataset("iris.csv")

db = DashBoard(df, title="StreamOps: Mini Dashboard", title_align="center")
db.set_theme(background="#071021", text="#E9F6F2", primary="#19D3A3", card="#0b1620")
# Sidebar
db.add_sidebar(db.comp_text("Parámetros del reporte"))
db.add_sidebar(db.comp_metric("Longitud del dataset", df.shape[0]))
db.add_sidebar(db.comp_metric("Cantidad de Flores", df["species"].unique().shape[0]))
# Main layout
db.add_blank()
db.add_row(
    col_widths=[1, 2, 1],
    components=[
        db.comp_blank(),
        db.comp_plot(x="sepal_length", y="sepal_width", kind="scatter", color="#FFB86B"),
        db.comp_metric("sepal_width", df["sepal_width"].sum(), delta="▲ 5%")
    ]
)

db.add_tabs({
    "Overview": [
        db.comp_title("Resumen por Región"),
        db.comp_table()
    ],
    "Details": [
        db.comp_title("Distribución de Flores"),
        db.comp_plot(x="species", y=None, kind="hist", color="#7C4DFF")
    ]
})

db.add_expander("Detalles técnicos", [
    db.comp_text("Este panel fue generado automáticamente."),
    db.comp_text("Metadata: filas=" + str(len(df)), size="12px")
], expanded=True)

db.run(open_browser=True)   