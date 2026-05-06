import pandas as pd
import numpy as np
from viewx.DataMatrix import DataMatrix

# 1. Crear un Dataset sintético que simule datos bibliométricos
data = {
    'Authors': [
        'Aria, M; Cuccurullo, C', 'Aria, M; Smith, J', 'Cuccurullo, C', 
        'Doe, J', 'Smith, J; Doe, J', 'Aria, M', 'Brown, A', 'Brown, A; Smith, J',
        'Gomez, P', 'Gomez, P; Aria, M', 'Doe, J', 'White, S', 'White, S; Brown, A',
        'Black, R', 'Black, R; Gomez, P', 'Green, T', 'Green, T; Aria, M',
        'Doe, J', 'Smith, J', 'Cuccurullo, C'
    ],
    'Year': [2017, 2017, 2018, 2018, 2019, 2019, 2020, 2020, 2021, 2021, 2022, 2022, 2023, 2023, 2024, 2024, 2025, 2025, 2026, 2026],
    'Journal': [
        'Journal of Informetrics', 'Journal of Informetrics', 'Scientometrics', 
        'Scientometrics', 'Nature', 'Nature', 'Science', 'Science',
        'Journal of Informetrics', 'Scientometrics', 'Nature', 'Science',
        'Journal of Informetrics', 'Scientometrics', 'Nature', 'Science',
        'Journal of Informetrics', 'Scientometrics', 'Nature', 'Science'
    ],
    'Citations': np.random.randint(0, 100, size=20),
    'Abstract': ['Resumen de prueba ' + str(i) for i in range(20)],
    'Keywords': ['bibliometrics; R', 'python; data science', 'metrics; science', 'analysis', 'data', 'python', 'r', 'metrics', 'science', 'mapping', 'analysis', 'data', 'python', 'r', 'metrics', 'science', 'mapping', 'analysis', 'data', 'python'],
    'Duplicate_Col': [1] * 20, # Columna constante para alerta
    'Missing_Col': [np.nan] * 15 + [1, 2, 3, 4, 5] # Columna con muchos nulos
}

df = pd.DataFrame(data)

# Añadir filas duplicadas para probar limpieza
df = pd.concat([df, df.iloc[:2]], ignore_index=True)

print("Dataset creado con", len(df), "filas.")

# 2. Usar DataMatrix
dm = DataMatrix(df)

# Limpiar datos
dm.clean_data(drop_duplicates=True, fill_na=True)

# Generar reporte
report_path = dm.generate_report("demo_datamatrix_report.html", title="Análisis Bibliométrico de Prueba")

print(f"Reporte generado exitosamente en: {report_path}")
