import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()

#Variables__________________________________________________________________________________________________________

#Variables SQL
host_SQL = os.getenv('host_railway')
user_SQL = os.getenv('user_railway')
password_SQL = os.getenv('password_railway')
puerto = os.getenv('port_railway')
db = os.getenv('db')

tabla = 'recurso_operaciones_norte'

tablaActualizado = "actualizado"
ColumnaActualizado = "Actualizado"
Columna_ID_Actualizado = "Base"
ID_Actualizado = "recurso_operaciones_norte"

columnas_a_conservar = ['ALIADO', 'CIUDAD', 'NOMINA', 'CEDULA', 'NOMBRE DEL TECNICO', 
                        'FECHA INGRESO', 'CARPETA RECURSO CLARO', 'CARGO PLANTA', 
                        'CELULAR CORPORATIVO', 'CORREO PERSONAL', 'CEDULA SUPERVISOR', 
                        'SUPERVISOR ALIADO', 'CONTACTO DEL SUPERVISOR', 'COORDINADOR', 
                        'COMPOSICIÓN', 'VEHICULO', 'CODIGO SAP','ESTADO EN EL RECURSO', 
                        'PLACA VEHICULO TECNICO', 'NOMINA AYUDANTE', 'CEDULA  AYUDANTE', 
                        'NOMBRE AYUDANTE', 'PLACA VEHICULO AYUDANTE', 'HÍBRIDO', 'FECHA RETIRO', 
                        'NOVEDAD DEL RECURSO', 'DASH BOARD', 'CEDULA RADIO 1', 'RADIO 1', 'CEDULA RADIO 2', 'RADIO 2',
                        'PREOPERACIONAL TECNICO', 'PREOPERACIONAL AYUDANTE', 'FECHA DE PRESENTACIÓN  A INTERVENTORIA','Trabajos Dobles o Sencillos']


archivo_reciente = "recurso_operaciones_norte.xlsx"
print(archivo_reciente)
if archivo_reciente and os.path.exists(archivo_reciente):
    recurso_actual = pd.read_excel(archivo_reciente, sheet_name='RECURSO ACTUAL')
    recurso_actual = recurso_actual.rename(columns={'NOMBRE DEL TÉCNICO': 'NOMBRE DEL TECNICO'})
    recurso_actual["FECHA RETIRO"] = ""
    recurso_actual["FECHA RETIRO"] = ""
    recurso_actual["NOVEDAD DEL RECURSO"] = ""
    recurso_actual = recurso_actual[columnas_a_conservar]

    recurso_admon = pd.read_excel(archivo_reciente, sheet_name='RECURSO ADMON')
    recurso_admon = recurso_admon.rename(columns={'NOMBRE DEL TÉCNICO': 'NOMBRE DEL TECNICO'})
    recurso_admon["FECHA RETIRO"] = ""
    recurso_admon["FECHA RETIRO"] = ""
    recurso_admon["NOVEDAD DEL RECURSO"] = ""
    recurso_admon = recurso_admon.drop('ESTADO EN EL RECURSO', axis=1)
    recurso_admon["ESTADO EN EL RECURSO"] = "ADMON"
    recurso_admon['FECHA DE PRESENTACIÓN  A INTERVENTORIA'] = recurso_admon['FECHA INGRESO']
    recurso_admon = recurso_admon[columnas_a_conservar]

    recurso_retirados = pd.read_excel(archivo_reciente, sheet_name='RETIROS')
    recurso_retirados = recurso_retirados.rename(columns={'PLACA AYUDANTE': 'PLACA VEHICULO AYUDANTE'})
    recurso_retirados["HÍBRIDO"] = ""
    recurso_retirados["CEDULA RADIO 1"] = ""
    recurso_retirados["RADIO 1"] = ""
    recurso_retirados["CEDULA RADIO 2"] = ""
    recurso_retirados["RADIO 2"] = ""
    recurso_retirados["PREOPERACIONAL TECNICO"] = "No"
    recurso_retirados["PREOPERACIONAL AYUDANTE"] = "No"
    recurso_retirados["Trabajos Dobles o Sencillos"] = ""
    recurso_retirados['FECHA DE PRESENTACIÓN  A INTERVENTORIA'] = recurso_retirados['FECHA INGRESO']
    recurso_retirados = recurso_retirados.drop(columns=["MES", "AÑO"])
    columnas_a_conservar = [col for col in columnas_a_conservar if col in recurso_retirados.columns]
    recurso_retirados = recurso_retirados[columnas_a_conservar]

    recurso = pd.concat([recurso_actual, recurso_retirados, recurso_admon], ignore_index=True)
    #recurso = recurso.drop(columns=["Unnamed: 27"])
    recurso.columns = recurso.columns.str.strip()
    recurso = recurso.drop_duplicates(subset=['CEDULA'], keep='first')


    recurso["Trabajos Dobles o Sencillos"] = (
        recurso["Trabajos Dobles o Sencillos"]
        .str.strip()
        .replace({
            "Sencillo": "SENCILLA",
            "Doble": "DOBLE",
            "Dobles": "DOBLE",
            "Sencillas": "SENCILLA",
            "SENCILLAS": "SENCILLA",
            "SOLO": "SENCILLA"
        })
    )

    recurso["COMPOSICIÓN"] = (
        recurso["COMPOSICIÓN"]
        .str.strip()
        .replace({
            "Sencillo": "SENCILLA",
            "Doble": "DOBLE",
            "Dobles": "DOBLE",
            "Sencillas": "SENCILLA",
            "SENCILLAS": "SENCILLA",
            "SOLO": "SENCILLA"
        })
    )
    recurso = recurso.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
    recurso = recurso.astype(str)
    print(recurso)

    # Reemplazar strings vacíos por None en columnas de fecha
    columnas_fecha = ['FECHA INGRESO']
    for col in columnas_fecha:
        recurso[col] = recurso[col].replace('', None)

    if os.path.exists(archivo_reciente):
        os.remove(archivo_reciente)
    else:
        pass
else:
    pass
