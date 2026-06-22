import pymysql
from database.db_railway import RailwayDBManager

class OperacionesRepository:
    """Repositorio para manejar el acceso a datos de Operaciones."""
    
    def __init__(self):
        self.db = RailwayDBManager()
        self.tabla_operaciones = 'wfm_operaciones_norte_actividades'
        self.tabla_recurso = 'recurso_operaciones_norte'
        self.tabla_calidad_operaciones_norte = 'operaciones_indicadores_calidad_norte'

    def crear_tabla_operaciones_si_no_existe(self):
        sql = f"""
        CREATE TABLE IF NOT EXISTS {self.tabla_operaciones} (
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
        with self.db.get_connection() as conexion:
            with conexion.cursor() as cursor:
                cursor.execute(sql)
                conexion.commit()

    def eliminar_registros_por_archivo(self, nombre_archivo):
        with self.db.get_connection() as conexion:
            with conexion.cursor() as cursor:
                sql = f"DELETE FROM {self.tabla_operaciones} WHERE archivo = %s"
                cursor.execute(sql, (nombre_archivo,))
                eliminados = cursor.rowcount
                conexion.commit()
                return eliminados
            
    def eliminar_registros_por_fecha_calidad_operaciones_norte(self, fechas_unicas):
        eliminados = 0
        with self.db.get_connection() as conexion:
            with conexion.cursor() as cursor:
                sql = f"DELETE FROM {self.tabla_calidad_operaciones_norte} WHERE Fecha = %s"

                for fecha in fechas_unicas:
                    cursor.execute(sql, (fecha,))
                    eliminados += cursor.rowcount

                conexion.commit()
                return eliminados

    def insertar_datos_operaciones(self, datos, columnas):
        if not datos:
            return 0
            
        placeholders = ', '.join(['%s'] * len(columnas))
        columnas_sql = ', '.join([f"`{col}`" for col in columnas])
        sql = f"INSERT INTO {self.tabla_operaciones} ({columnas_sql}) VALUES ({placeholders})"
        
        total_insertados = 0
        BATCH_SIZE = 500
        
        with self.db.get_connection() as conexion:
            try:
                with conexion.cursor() as cursor:
                    for i in range(0, len(datos), BATCH_SIZE):
                        lote = datos[i:i + BATCH_SIZE]
                        cursor.executemany(sql, lote)
                        total_insertados += len(lote)
                conexion.commit()
                return total_insertados
            except pymysql.MySQLError as e:
                conexion.rollback()
                raise e

    def insertar_datos_recurso(self, datos, columnas):
        if not datos:
            return 0
            
        placeholders = ', '.join(['%s'] * len(columnas))
        columnas_sql = ', '.join([f"`{col}`" for col in columnas])
        sql = f"INSERT INTO {self.tabla_recurso} ({columnas_sql}) VALUES ({placeholders})"
        
        total_insertados = 0
        BATCH_SIZE = 500
        
        with self.db.get_connection() as conexion:
            try:
                with conexion.cursor() as cursor:
                    cursor.execute(f"TRUNCATE TABLE {self.tabla_recurso}")
                    for i in range(0, len(datos), BATCH_SIZE):
                        lote = datos[i:i + BATCH_SIZE]
                        cursor.executemany(sql, lote)
                        total_insertados += len(lote)
                conexion.commit()
                return total_insertados
            except pymysql.MySQLError as e:
                conexion.rollback()
                raise e
            
    def insertar_datos_calidad_operaciones_norte(self, datos, columnas):
        if not datos:
            return 0
            
        placeholders = ', '.join(['%s'] * len(columnas))
        columnas_sql = ', '.join([f"`{col}`" for col in columnas])
        sql = f"INSERT INTO {self.tabla_calidad_operaciones_norte} ({columnas_sql}) VALUES ({placeholders})"
        
        total_insertados = 0
        BATCH_SIZE = 500
        
        with self.db.get_connection() as conexion:
            try:
                with conexion.cursor() as cursor:
                    cursor.execute(f"TRUNCATE TABLE {self.tabla_calidad_operaciones_norte}")
                    for i in range(0, len(datos), BATCH_SIZE):
                        lote = datos[i:i + BATCH_SIZE]
                        cursor.executemany(sql, lote)
                        total_insertados += len(lote)
                conexion.commit()
                return total_insertados
            except pymysql.MySQLError as e:
                conexion.rollback()
                raise e
