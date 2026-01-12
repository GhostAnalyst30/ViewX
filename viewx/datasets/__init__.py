import pandas as pd
import pkgutil
import io

def load_dataset(name: str):
    """Carga un dataset interno del paquete.
    Datasets Disponibles:
    - iris.csv
    - penguins.csv
    - sp500_companies.csv
    - titanic.csv
    - course_completion.csv
    """
    data_bytes = pkgutil.get_data("statslibx.datasets", name)
    if data_bytes is None:
        raise FileNotFoundError(f"Dataset '{name}' no encontrado.")
    return pd.read_csv(io.BytesIO(data_bytes))
