import os
import pandas as pd
from datetime import datetime
from repositories.operaciones_repository import OperacionesRepository

class OperacionesService:
    """Servicio para procesar archivos y manejar la lógica de negocio de Operaciones."""
    
    COLUMNAS_EXCEL_A_BD = {
        'Intervalos de tiempo': 'Intervalos de tiempo',
        'ID Aliado': 'ID Aliado',
        'Fecha': 'Fecha',
        'Nombre': 'Nombre',
        'Dirección campo 1': 'Dirección campo 1',
        'Nombre Completo': 'Nombre Completo',
        'Tipo de Actividad': 'Tipo de Actividad',
        'Subtipo de la Orden de Trabajo': 'Subtipo de la Orden de Trabajo',
        'Orden de trabajo': 'Orden de trabajo',
        'Zonas de trabajo': 'Zonas de trabajo',
        'Zona': 'Zona',
        'Ciudad': 'Ciudad',
        'Nodo': 'Nodo',
        'Número de cuenta': 'Número de cuenta',
        'Estado SLA': 'Estado SLA',
        'Regional': 'Regional',
        'Asesor comercial': 'Asesor comercial',
        'Tipo de Red': 'Tipo de Red',
        'Fecha de creación de la OT YYYY-MM-DD': 'Fecha de creación de la OT YYYY-MM-DD',
        'External ID': 'External ID',
        'Actividad ID': 'Actividad ID',
        'Técnico': 'Técnico',
        'Inicio': 'Inicio',
        'Fin': 'Fin',
        'Estado': 'Estado',
        'Fecha de agendamiento': 'Fecha de agendamiento',
        'Coordenada X': 'Coordenada X',
        'Coordenada Y': 'Coordenada Y',
        'Archivo': 'Archivo',
        'Razón': 'Razón',
    }
    
    COLUMNAS_BD = list(COLUMNAS_EXCEL_A_BD.values())
    
    def __init__(self):
        self.repo = OperacionesRepository()

    def inicializar_bd(self):
        self.repo.crear_tabla_operaciones_si_no_existe()

    def procesar_archivo_excel(self, file_path, tipo_archivo):
        extension = os.path.splitext(file_path)[1].lower()
        if extension == '.csv':
            df = pd.read_csv(file_path, dtype=str)
        elif extension == '.xlsx':
            import openpyxl
            wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
            ws = wb.active
            datos = list(ws.values)
            wb.close()
            if len(datos) < 2:
                raise ValueError("El archivo está vacío o solo tiene encabezados.")
            columnas = [str(c) if c is not None else f'col_{i}' for i, c in enumerate(datos[0])]
            df = pd.DataFrame(datos[1:], columns=columnas)
            df = df.astype(str)
            df = df.replace('None', None).replace('none', None)
        elif extension == '.xls':
            df = pd.read_excel(file_path, dtype=str, engine='xlrd')
        else:
            raise ValueError(f"Formato de archivo no soportado: {extension}")

        columnas_requeridas = ['Fecha', 'Fecha de agendamiento']
        faltantes = [col for col in columnas_requeridas if col not in df.columns]
        if faltantes:
            raise ValueError(f"El archivo no contiene las columnas requeridas: {', '.join(faltantes)}")

        df['Fecha'] = df['Fecha'].apply(self._corregir_fecha)
        df['Fecha de creación de la OT YYYY-MM-DD'] = df['Fecha de agendamiento'].apply(self._convertir_fecha_agendamiento)

        prefijo_archivo = 'PY' if tipo_archivo == 'Pymes' else tipo_archivo
        
        def _generar_nombre_archivo(fecha_str):
            if fecha_str and isinstance(fecha_str, str):
                try:
                    fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d')
                    return f"{prefijo_archivo}_{fecha_obj.strftime('%d_%m_%Y')}"
                except (ValueError, TypeError):
                    pass
            return f"{prefijo_archivo}_{datetime.now().strftime('%d_%m_%Y')}"
            
        df['Archivo'] = df['Fecha'].apply(_generar_nombre_archivo)
        nombre_archivo = df['Archivo'].iloc[0] if not df.empty else f"{prefijo_archivo}_{datetime.now().strftime('%d_%m_%Y')}"

        df = df.rename(columns=self.COLUMNAS_EXCEL_A_BD)
        df = df.loc[:, ~df.columns.duplicated(keep='first')]
        
        columnas_validas = [col for col in self.COLUMNAS_BD if col in df.columns]
        df = df[columnas_validas]
        df = df.where(pd.notnull(df), None)

        # Usar repositorio para eliminar y guardar
        eliminados = self.repo.eliminar_registros_por_archivo(nombre_archivo)
        datos = [tuple(row) for row in df.values]
        insertados = self.repo.insertar_datos_operaciones(datos, df.columns.tolist())
        
        return df, nombre_archivo, eliminados, insertados

    def _corregir_fecha(self, valor):
        if pd.isna(valor) or valor is None or str(valor).strip() == '':
            return None

        valor_str = str(valor).strip()
        try:
            fecha = pd.to_datetime(valor_str, format='%Y-%m-%d %H:%M:%S', errors='raise')
            return fecha.strftime('%Y-%m-%d')
        except (ValueError, TypeError):
            pass

        try:
            fecha = pd.to_datetime(valor_str, format='%Y-%m-%d', errors='raise')
            return fecha.strftime('%Y-%m-%d')
        except (ValueError, TypeError):
            pass

        for sep in ['/', '-', '.']:
            partes = valor_str.split(sep)
            if len(partes) == 3:
                if len(partes[2]) == 2:
                    partes[2] = '20' + partes[2]
                    valor_corregido = sep.join(partes)
                    try:
                        fecha = pd.to_datetime(valor_corregido, dayfirst=True)
                        return fecha.strftime('%Y-%m-%d')
                    except (ValueError, TypeError):
                        pass
                    try:
                        fecha = pd.to_datetime(valor_corregido, dayfirst=False)
                        return fecha.strftime('%Y-%m-%d')
                    except (ValueError, TypeError):
                        pass
                elif len(partes[0]) == 2 and int(partes[0]) > 12:
                    partes[0] = '20' + partes[0]
                    valor_corregido = sep.join(partes)
                    try:
                        fecha = pd.to_datetime(valor_corregido)
                        return fecha.strftime('%Y-%m-%d')
                    except (ValueError, TypeError):
                        pass

        try:
            fecha = pd.to_datetime(valor_str)
            return fecha.strftime('%Y-%m-%d')
        except (ValueError, TypeError):
            return None

    def _convertir_fecha_agendamiento(self, valor):
        if pd.isna(valor) or valor is None or str(valor).strip() == '':
            return None
        valor_str = str(valor).strip()
        try:
            fecha = pd.to_datetime(valor_str)
            return fecha.strftime('%Y-%m-%d')
        except (ValueError, TypeError):
            return None

    def procesar_archivo_recurso(self, file_path):
        columnas_a_conservar = ['ALIADO', 'CIUDAD', 'NOMINA', 'CEDULA', 'NOMBRE DEL TECNICO', 
                                'FECHA INGRESO', 'CARPETA RECURSO CLARO', 'CARGO PLANTA', 
                                'CELULAR CORPORATIVO', 'CORREO PERSONAL', 'CEDULA SUPERVISOR', 
                                'SUPERVISOR ALIADO', 'CONTACTO DEL SUPERVISOR', 'COORDINADOR', 
                                'COMPOSICIÓN', 'VEHICULO', 'CODIGO SAP','ESTADO EN EL RECURSO', 
                                'PLACA VEHICULO TECNICO', 'NOMINA AYUDANTE', 'CEDULA  AYUDANTE', 
                                'NOMBRE AYUDANTE', 'PLACA VEHICULO AYUDANTE', 'HÍBRIDO', 'FECHA RETIRO', 
                                'NOVEDAD DEL RECURSO', 'DASH BOARD', 'CEDULA RADIO 1', 'RADIO 1', 'CEDULA RADIO 2', 'RADIO 2',
                                'PREOPERACIONAL TECNICO', 'PREOPERACIONAL AYUDANTE', 'FECHA DE PRESENTACIÓN  A INTERVENTORIA','Trabajos Dobles o Sencillos']

        recurso_actual = pd.read_excel(file_path, sheet_name='RECURSO ACTUAL')
        recurso_actual.columns = recurso_actual.columns.str.strip()
        recurso_actual = recurso_actual.rename(columns={'NOMBRE DEL TÉCNICO': 'NOMBRE DEL TECNICO'})
        recurso_actual["FECHA RETIRO"] = ""
        recurso_actual["NOVEDAD DEL RECURSO"] = ""
        recurso_actual = recurso_actual.reindex(columns=columnas_a_conservar)

        recurso_admon = pd.read_excel(file_path, sheet_name='RECURSO ADMON')
        recurso_admon.columns = recurso_admon.columns.str.strip()
        recurso_admon = recurso_admon.rename(columns={'NOMBRE DEL TÉCNICO': 'NOMBRE DEL TECNICO'})
        recurso_admon["FECHA RETIRO"] = ""
        recurso_admon["NOVEDAD DEL RECURSO"] = ""
        recurso_admon = recurso_admon.drop('ESTADO EN EL RECURSO', axis=1, errors='ignore')
        recurso_admon["ESTADO EN EL RECURSO"] = "ADMON"
        if 'FECHA INGRESO' in recurso_admon.columns:
            recurso_admon['FECHA DE PRESENTACIÓN  A INTERVENTORIA'] = recurso_admon['FECHA INGRESO']
        recurso_admon = recurso_admon.reindex(columns=columnas_a_conservar)

        recurso_retirados = pd.read_excel(file_path, sheet_name='RETIROS')
        recurso_retirados.columns = recurso_retirados.columns.str.strip()
        recurso_retirados = recurso_retirados.rename(columns={'PLACA AYUDANTE': 'PLACA VEHICULO AYUDANTE'})
        recurso_retirados["HÍBRIDO"] = ""
        recurso_retirados["CEDULA RADIO 1"] = ""
        recurso_retirados["RADIO 1"] = ""
        recurso_retirados["CEDULA RADIO 2"] = ""
        recurso_retirados["RADIO 2"] = ""
        recurso_retirados["PREOPERACIONAL TECNICO"] = "No"
        recurso_retirados["PREOPERACIONAL AYUDANTE"] = "No"
        recurso_retirados["Trabajos Dobles o Sencillos"] = ""
        if 'FECHA INGRESO' in recurso_retirados.columns:
            recurso_retirados['FECHA DE PRESENTACIÓN  A INTERVENTORIA'] = recurso_retirados['FECHA INGRESO']
        recurso_retirados = recurso_retirados.drop(columns=["MES", "AÑO"], errors='ignore')
        recurso_retirados = recurso_retirados.reindex(columns=columnas_a_conservar)

        recurso = pd.concat([recurso_actual, recurso_retirados, recurso_admon], ignore_index=True)
        recurso.columns = recurso.columns.str.strip()
        recurso = recurso.drop_duplicates(subset=['CEDULA'], keep='first')

        for col in ["Trabajos Dobles o Sencillos", "COMPOSICIÓN"]:
            if col in recurso.columns:
                recurso[col] = (
                    recurso[col]
                    .astype(str)
                    .str.strip()
                    .replace({
                        "Sencillo": "SENCILLA", "Doble": "DOBLE", "Dobles": "DOBLE",
                        "Sencillas": "SENCILLA", "SENCILLAS": "SENCILLA", "SOLO": "SENCILLA",
                        "nan": None, "None": None
                    })
                )

        recurso = recurso.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
        recurso = recurso.astype(str)

        for col in ['FECHA INGRESO']:
            if col in recurso.columns:
                recurso[col] = recurso[col].replace('', None).replace('nan', None).replace('None', None)

        recurso = recurso.replace('nan', None).replace('None', None)
        
        datos = [tuple(row) for row in recurso.values]
        insertados = self.repo.insertar_datos_recurso(datos, recurso.columns.tolist())
        
        return recurso, insertados
    
    def procesar_archivo_calidad(self, file_path):
        columnas_a_conservar = ['MUNICIPIO','NODO', 'REGION', 'Subtipo_Actividad',
        'Tecnología', 'Tipo Trabajo', 'Tipo_Actividad', 'TIPO_OPERACION',
         'KPI Q30 I&M', 'Corte Dia', 'Grupo Aliado', 'ID_EXTERNO_DE_RECURSO',
         'NÚMERO_DE_CUENTA', 'ORDEN_DE_TRABAJO']
        calidad_operaciones_norte = pd.read_excel(file_path)
        calidad_operaciones_norte = calidad_operaciones_norte.reindex(columns=columnas_a_conservar)
        calidad_operaciones_norte["KPI Q30 I&M"] = (
            pd.to_numeric(
                calidad_operaciones_norte["KPI Q30 I&M"]
                .fillna("0")
                .astype(str)
                .str.replace("%", "", regex=False)
                .str.replace(",", ".", regex=False),
                errors="coerce"
            )
            .fillna(0)
            / 100
        )

        # Convertir a número
        calidad_operaciones_norte["ID_EXTERNO_DE_RECURSO"] = pd.to_numeric(calidad_operaciones_norte["ID_EXTERNO_DE_RECURSO"], errors="coerce")
        calidad_operaciones_norte["NÚMERO_DE_CUENTA"] = pd.to_numeric(calidad_operaciones_norte["NÚMERO_DE_CUENTA"], errors="coerce")
        calidad_operaciones_norte["ORDEN_DE_TRABAJO"] = pd.to_numeric(calidad_operaciones_norte["ORDEN_DE_TRABAJO"], errors="coerce")

        # Eliminar filas con valores no numéricos
        calidad_operaciones_norte = calidad_operaciones_norte[calidad_operaciones_norte["ID_EXTERNO_DE_RECURSO"].notna()]

        # Convertir a entero
        calidad_operaciones_norte["ID_EXTERNO_DE_RECURSO"] = calidad_operaciones_norte["ID_EXTERNO_DE_RECURSO"].astype(int)
        calidad_operaciones_norte["NÚMERO_DE_CUENTA"] = (pd.to_numeric(calidad_operaciones_norte["NÚMERO_DE_CUENTA"], errors="coerce").astype("Int64"))
        calidad_operaciones_norte["ORDEN_DE_TRABAJO"] = (pd.to_numeric(calidad_operaciones_norte["ORDEN_DE_TRABAJO"], errors="coerce").astype("Int64"))

        #Ajuste fecha
        calidad_operaciones_norte["Corte Dia"] = pd.to_datetime(
            calidad_operaciones_norte["Corte Dia"].astype(str),
            format="%Y%m%d",
            errors="coerce"
        ).dt.date
        calidad_operaciones_norte.rename(columns={"Corte Dia": "Fecha"}, inplace=True)
        fechas_unicas = calidad_operaciones_norte["Fecha"].drop_duplicates().tolist()
        # Usar repositorio para eliminar y guardar
        eliminados = self.repo.eliminar_registros_por_fecha_calidad_operaciones_norte(fechas_unicas)
        datos = [tuple(row) for row in calidad_operaciones_norte.values]
        insertados = self.repo.insertar_datos_calidad_operaciones_norte(datos, calidad_operaciones_norte.columns.tolist())
        
        return calidad_operaciones_norte, eliminados, insertados
# Instancia global del servicio
operaciones_service_instance = OperacionesService()
