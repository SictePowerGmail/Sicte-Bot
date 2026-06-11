import os
import pandas as pd
import pymysql
from datetime import datetime
from database.db_usuarios import obtener_conexion_usuarios

# Nombre de la tabla (también configurado en .env como referencia)
TABLA_OPERACIONES = 'wfm_operaciones_norte_actividades'

# Mapeo de columnas del Excel a columnas de la tabla en BD (snake_case)
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

# Columnas de la BD en el orden de inserción (sin 'id' que es AUTO_INCREMENT)
COLUMNAS_BD = list(COLUMNAS_EXCEL_A_BD.values())

# Nombre de la tabla de recurso
TABLA_RECURSO = 'recurso_operaciones_norte'


def crear_tabla_si_no_existe():
    """Crea la tabla wfm_operaciones_norte_actividad en la BD si no existe."""
    sql = f"""
    CREATE TABLE IF NOT EXISTS {TABLA_OPERACIONES} (
        id INT AUTO_INCREMENT PRIMARY KEY,
        `intervalos de tiempo` VARCHAR(255),
        `id aliado` VARCHAR(100),
        fecha DATE NULL,
        nombre VARCHAR(500),
        `Dirección campo 1` TEXT,
        `nombre completo` VARCHAR(500),
        `tipo de actividad` VARCHAR(255),
        `subtipo de la orden de trabajo` VARCHAR(500),
        `orden de trabajo` VARCHAR(100),
        `zonas de trabajo` VARCHAR(500),
        zona VARCHAR(255),
        ciudad VARCHAR(255),
        nodo VARCHAR(100),
        `Número de cuenta` VARCHAR(100),
        `estado sla` VARCHAR(100),
        regional VARCHAR(100),
        `asesor comercial` VARCHAR(500),
        `tipo de red` VARCHAR(255),
        `fecha creacion ot` DATE NULL,
        `external id` VARCHAR(100),
        `actividad id` VARCHAR(100),
        tecnico VARCHAR(500),
        inicio VARCHAR(100),
        fin VARCHAR(100),
        estado VARCHAR(100),
        `fecha de agendamiento` VARCHAR(100),
        `coordenada x` VARCHAR(100),
        `coordenada y` VARCHAR(100),
        archivo VARCHAR(255),
        razon TEXT
    );
    """
    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion_usuarios()
        cursor = conexion.cursor()
        cursor.execute(sql)
        conexion.commit()
        print(f"Tabla '{TABLA_OPERACIONES}' verificada/creada correctamente.")
    except pymysql.MySQLError as e:
        print(f"Error creando tabla {TABLA_OPERACIONES}: {e}")
        raise
    finally:
        if cursor: cursor.close()
        if conexion: conexion.close()


def procesar_archivo_excel(file_path, tipo_archivo):
    """
    Lee un archivo Excel (.xlsx, .xls) o CSV (.csv), aplica las transformaciones
    de datos requeridas y retorna el DataFrame listo para insertar.
    
    Transformaciones:
    1. Fecha: si viene como texto con año corto (ej: '05/30/26'), anteponer '20' al año
    2. Fecha de creación de la OT: se genera desde 'Fecha de agendamiento' en formato YYYY-MM-DD
    3. Archivo: se genera como '{Tipo}_{DD}_{MM}_{YYYY}' con fecha actual
    """
    # 1. Leer archivo según extensión
    extension = os.path.splitext(file_path)[1].lower()
    if extension == '.csv':
        df = pd.read_csv(file_path, dtype=str)
    elif extension == '.xlsx':
        # Leer directamente con openpyxl para evitar el bug 'io.excel.zip.reader' de pandas
        import openpyxl
        wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
        ws = wb.active
        datos = list(ws.values)
        wb.close()
        if len(datos) < 2:
            raise ValueError("El archivo está vacío o solo tiene encabezados.")
        columnas = [str(c) if c is not None else f'col_{i}' for i, c in enumerate(datos[0])]
        df = pd.DataFrame(datos[1:], columns=columnas)
        # Convertir todo a string para uniformidad
        df = df.astype(str)
        df = df.replace('None', None).replace('none', None)
    elif extension == '.xls':
        df = pd.read_excel(file_path, dtype=str, engine='xlrd')
    else:
        raise ValueError(f"Formato de archivo no soportado: {extension}. Usa .xlsx, .xls o .csv")

    # 2. Validar que existan las columnas mínimas requeridas
    columnas_requeridas = ['Fecha', 'Fecha de agendamiento']
    faltantes = [col for col in columnas_requeridas if col not in df.columns]
    if faltantes:
        raise ValueError(f"El archivo no contiene las columnas requeridas: {', '.join(faltantes)}")

    # 3. Transformar columna Fecha
    df['Fecha'] = df['Fecha'].apply(_corregir_fecha)

    # 4. Generar columna "Fecha de creación de la OT YYYY-MM-DD" desde "Fecha de agendamiento"
    df['Fecha de creación de la OT YYYY-MM-DD'] = df['Fecha de agendamiento'].apply(_convertir_fecha_agendamiento)

    # 5. Generar columna Archivo: "{Prefijo}_{DD}_{MM}_{YYYY}" usando la fecha corregida de cada fila
    prefijo_archivo = 'PY' if tipo_archivo == 'Pymes' else tipo_archivo
    def _generar_nombre_archivo(fecha_str):
        if fecha_str and isinstance(fecha_str, str):
            try:
                fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d')
                return f"{prefijo_archivo}_{fecha_obj.strftime('%d_%m_%Y')}"
            except (ValueError, TypeError):
                pass
        # Fallback: usar fecha actual si no se puede parsear
        return f"{prefijo_archivo}_{datetime.now().strftime('%d_%m_%Y')}"
    df['Archivo'] = df['Fecha'].apply(_generar_nombre_archivo)
    # Tomar el primer nombre de archivo generado para la deduplicación
    nombre_archivo = df['Archivo'].iloc[0] if not df.empty else f"{prefijo_archivo}_{datetime.now().strftime('%d_%m_%Y')}"

    # 6. Renombrar columnas del Excel a snake_case para mapear con la BD
    df = df.rename(columns=COLUMNAS_EXCEL_A_BD)

    # 7. Eliminar columnas duplicadas (el archivo puede traer "Ciudad" dos veces, etc.)
    df = df.loc[:, ~df.columns.duplicated(keep='first')]

    # 8. Filtrar solo las columnas que existen en la BD (ignorar columnas extra)
    columnas_validas = [col for col in COLUMNAS_BD if col in df.columns]
    df = df[columnas_validas]

    # 8. Reemplazar NaN por None para MySQL
    df = df.where(pd.notnull(df), None)

    return df, nombre_archivo


def _corregir_fecha(valor):
    """
    Corrige la columna Fecha:
    - Si es texto con año corto (ej: '05/30/26' o '30/05/26'), antepone '20' al año.
    - Si ya es un datetime válido o texto con año completo, lo convierte directamente.
    Retorna la fecha en formato 'YYYY-MM-DD' como string, o None si no se puede parsear.
    """
    if pd.isna(valor) or valor is None or str(valor).strip() == '':
        return None

    valor_str = str(valor).strip()

    # Si ya tiene formato YYYY-MM-DD (año completo con 4 dígitos al inicio)
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

    # Si tiene formato con año corto de 2 dígitos (ej: '07/06/26' → DD/MM/YY)
    # Intentar con separadores comunes: /, -, .
    for sep in ['/', '-', '.']:
        partes = valor_str.split(sep)
        if len(partes) == 3:
            # Verificar si la última parte es el año corto (2 dígitos)
            if len(partes[2]) == 2:
                partes[2] = '20' + partes[2]
                valor_corregido = sep.join(partes)
                # Intentar primero DD/MM/YYYY (dayfirst=True) ya que el archivo viene en ese formato
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
            # Verificar si la primera parte es el año corto
            elif len(partes[0]) == 2 and int(partes[0]) > 12:
                partes[0] = '20' + partes[0]
                valor_corregido = sep.join(partes)
                try:
                    fecha = pd.to_datetime(valor_corregido)
                    return fecha.strftime('%Y-%m-%d')
                except (ValueError, TypeError):
                    pass

    # Último intento: parseo genérico
    try:
        fecha = pd.to_datetime(valor_str)
        return fecha.strftime('%Y-%m-%d')
    except (ValueError, TypeError):
        print(f"Advertencia: No se pudo parsear la fecha '{valor_str}'")
        return None


def _convertir_fecha_agendamiento(valor):
    """
    Convierte la columna 'Fecha de agendamiento' a formato YYYY-MM-DD.
    Puede venir como string 'YYYY-MM-DD' o en otros formatos.
    """
    if pd.isna(valor) or valor is None or str(valor).strip() == '':
        return None

    valor_str = str(valor).strip()
    try:
        fecha = pd.to_datetime(valor_str)
        return fecha.strftime('%Y-%m-%d')
    except (ValueError, TypeError):
        print(f"Advertencia: No se pudo parsear fecha de agendamiento '{valor_str}'")
        return None


def eliminar_registros_por_archivo(nombre_archivo):
    """
    Elimina todos los registros de la tabla donde la columna 'archivo' 
    coincida con el nombre_archivo dado. Retorna la cantidad de registros eliminados.
    Esto permite re-subir el mismo archivo sin generar duplicados.
    """
    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion_usuarios()
        cursor = conexion.cursor()
        sql = f"DELETE FROM {TABLA_OPERACIONES} WHERE archivo = %s"
        cursor.execute(sql, (nombre_archivo,))
        eliminados = cursor.rowcount
        conexion.commit()
        print(f"Se eliminaron {eliminados} registros con archivo='{nombre_archivo}'")
        return eliminados
    except pymysql.MySQLError as e:
        print(f"Error eliminando registros por archivo: {e}")
        raise
    finally:
        if cursor: cursor.close()
        if conexion: conexion.close()


def procesar_archivo_recurso(file_path):
    """
    Procesa el archivo de Recurso basándose en la lógica de recurso_operaciones_norte.py
    """
    columnas_a_conservar = ['ALIADO', 'CIUDAD', 'NOMINA', 'CEDULA', 'NOMBRE DEL TECNICO', 
                            'FECHA INGRESO', 'CARPETA RECURSO CLARO', 'CARGO PLANTA', 
                            'CELULAR CORPORATIVO', 'CORREO PERSONAL', 'CEDULA SUPERVISOR', 
                            'SUPERVISOR ALIADO', 'CONTACTO DEL SUPERVISOR', 'COORDINADOR', 
                            'COMPOSICIÓN', 'VEHICULO', 'CODIGO SAP','ESTADO EN EL RECURSO', 
                            'PLACA VEHICULO TECNICO', 'NOMINA AYUDANTE', 'CEDULA  AYUDANTE', 
                            'NOMBRE AYUDANTE', 'PLACA VEHICULO AYUDANTE', 'HÍBRIDO', 'FECHA RETIRO', 
                            'NOVEDAD DEL RECURSO', 'DASH BOARD', 'CEDULA RADIO 1', 'RADIO 1', 'CEDULA RADIO 2', 'RADIO 2',
                            'PREOPERACIONAL TECNICO', 'PREOPERACIONAL AYUDANTE', 'FECHA DE PRESENTACIÓN  A INTERVENTORIA','Trabajos Dobles o Sencillos']

    # Leer las diferentes hojas del Excel
    recurso_actual = pd.read_excel(file_path, sheet_name='RECURSO ACTUAL')
    recurso_actual.columns = recurso_actual.columns.str.strip()
    recurso_actual = recurso_actual.rename(columns={'NOMBRE DEL TÉCNICO': 'NOMBRE DEL TECNICO'})
    recurso_actual["FECHA RETIRO"] = ""
    recurso_actual["NOVEDAD DEL RECURSO"] = ""
    cols_actual = [col for col in columnas_a_conservar if col in recurso_actual.columns]
    recurso_actual = recurso_actual.reindex(columns=columnas_a_conservar) # Rellena con NaN lo que falte

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

    # Concatenar y limpiar
    recurso = pd.concat([recurso_actual, recurso_retirados, recurso_admon], ignore_index=True)
    recurso.columns = recurso.columns.str.strip()
    recurso = recurso.drop_duplicates(subset=['CEDULA'], keep='first')

    # Limpiar columnas específicas
    for col in ["Trabajos Dobles o Sencillos", "COMPOSICIÓN"]:
        if col in recurso.columns:
            recurso[col] = (
                recurso[col]
                .astype(str)
                .str.strip()
                .replace({
                    "Sencillo": "SENCILLA",
                    "Doble": "DOBLE",
                    "Dobles": "DOBLE",
                    "Sencillas": "SENCILLA",
                    "SENCILLAS": "SENCILLA",
                    "SOLO": "SENCILLA",
                    "nan": None,
                    "None": None
                })
            )

    recurso = recurso.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
    recurso = recurso.astype(str)

    # Reemplazar strings vacíos por None o string vacío para BD
    columnas_fecha = ['FECHA INGRESO']
    for col in columnas_fecha:
        if col in recurso.columns:
            recurso[col] = recurso[col].replace('', None).replace('nan', None).replace('None', None)

    # Reemplazar todos los 'nan' como strings que quedan por None
    recurso = recurso.replace('nan', None).replace('None', None)
    
    return recurso

def insertar_datos_recurso(df):
    """
    Trunca la tabla recurso_operaciones_norte e inserta los nuevos datos.
    Retorna la cantidad de filas insertadas.
    """
    if df.empty:
        return 0

    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion_usuarios()
        cursor = conexion.cursor()

        # Truncar tabla antes de insertar
        cursor.execute(f"TRUNCATE TABLE {TABLA_RECURSO}")
        conexion.commit()

        columnas = df.columns.tolist()
        placeholders = ', '.join(['%s'] * len(columnas))
        columnas_sql = ', '.join([f"`{col}`" for col in columnas])
        sql = f"INSERT INTO {TABLA_RECURSO} ({columnas_sql}) VALUES ({placeholders})"

        datos = [tuple(row) for row in df.values]

        BATCH_SIZE = 500
        total_insertados = 0
        for i in range(0, len(datos), BATCH_SIZE):
            lote = datos[i:i + BATCH_SIZE]
            cursor.executemany(sql, lote)
            total_insertados += len(lote)

        conexion.commit()
        print(f"Se insertaron {total_insertados} registros en {TABLA_RECURSO}")
        return total_insertados

    except pymysql.MySQLError as e:
        if conexion:
            conexion.rollback()
        print(f"Error insertando datos en {TABLA_RECURSO}: {e}")
        raise
    finally:
        if cursor: cursor.close()
        if conexion: conexion.close()



def insertar_datos_operaciones(df):
    """
    Inserta las filas del DataFrame en la tabla wfm_operaciones_norte_actividad.
    Retorna la cantidad de filas insertadas.
    """
    if df.empty:
        return 0

    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion_usuarios()
        cursor = conexion.cursor()

        columnas = df.columns.tolist()
        placeholders = ', '.join(['%s'] * len(columnas))
        #columnas_sql = ', '.join(columnas)
        columnas_sql = ', '.join([f"`{col}`" for col in columnas])
        sql = f"INSERT INTO {TABLA_OPERACIONES} ({columnas_sql}) VALUES ({placeholders})"

        # Convertir DataFrame a lista de tuplas
        datos = [tuple(row) for row in df.values]

        # Insertar en lotes de 500 filas
        BATCH_SIZE = 500
        total_insertados = 0
        for i in range(0, len(datos), BATCH_SIZE):
            lote = datos[i:i + BATCH_SIZE]
            cursor.executemany(sql, lote)
            total_insertados += len(lote)

        conexion.commit()
        print(f"Se insertaron {total_insertados} registros en {TABLA_OPERACIONES}")
        return total_insertados

    except pymysql.MySQLError as e:
        if conexion:
            conexion.rollback()
        print(f"Error insertando datos en {TABLA_OPERACIONES}: {e}")
        raise
    finally:
        if cursor: cursor.close()
        if conexion: conexion.close()
