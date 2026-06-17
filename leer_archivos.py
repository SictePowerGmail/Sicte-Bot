import pandas as pd

df = pd.read_csv(
    "c:/Users/Usuario/Downloads/KPI Efectividad_Datos completos_data junio.csv",
    sep=";",
    encoding="utf-8",
    low_memory=False
)

print(df.shape)
print(df.head())
print(df.columns)