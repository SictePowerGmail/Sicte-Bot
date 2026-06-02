import pymysql
from database.db_enel import obtener_conexion_enel

def consultar_orden(orden):
    """Consulta la información de una orden específica, incluyendo baremos y materiales."""
    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion_enel()
        cursor = conexion.cursor()
        
        sql = """
        SELECT ORDEN, ROTULO, ESTADO, FECHA_ESTADO, LOCALIDAD, TIPO_MOVIL
        FROM vw_ordenes WHERE ORDEN = %s ORDER BY FECHA_ESTADO DESC LIMIT 1
        """
        sql_baremos = """
        SELECT Id_Item_3, Cantidad_Instalada, amap, Item
        FROM vw_baremos WHERE orden = %s
        """
        sql_material = """
        SELECT Id_Item_3, Cantidad_Instalada, Item
        FROM vw_material_instalado
        WHERE orden = %s AND Id_Item_3 <> 0
        """
        
        cursor.execute(sql, (orden,))
        resultado = cursor.fetchone()
        
        cursor.execute(sql_baremos, (orden,))
        resultado_baremos = cursor.fetchall()
        
        cursor.execute(sql_material, (orden,))
        resultado_material = cursor.fetchall()
        
        return resultado, resultado_baremos, resultado_material
    except pymysql.MySQLError as e:
        raise Exception(f"Error de base de datos:\n{e}")
    finally:
        if cursor: cursor.close()
        if conexion: conexion.close()

def consultar_rotulo(rotulo):
    """Consulta todas las órdenes asociadas a un rótulo."""
    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion_enel()
        cursor = conexion.cursor()
        
        sql_ordenes = "SELECT DISTINCT ORDEN FROM vw_ordenes WHERE ROTULO = %s"
        cursor.execute(sql_ordenes, (rotulo,))
        ordenes = cursor.fetchall()
        
        if not ordenes:
            return None, []
        
        detalles = []
        sql_detalle = """
        SELECT ORDEN, ROTULO, ESTADO, FECHA_ESTADO, LOCALIDAD, TIPO_MOVIL
        FROM vw_ordenes WHERE ORDEN = %s ORDER BY FECHA_ESTADO DESC LIMIT 1
        """
        sql_baremos = """
        SELECT Id_Item_3, Cantidad_Instalada, amap, Item
        FROM vw_baremos WHERE orden = %s
        """
        sql_material = """
        SELECT Id_Item_3, Cantidad_Instalada, Item
        FROM vw_material_instalado
        WHERE orden = %s AND Id_Item_3 <> 0
        """
        
        for fila_orden in ordenes:
            orden = fila_orden[0]
            cursor.execute(sql_detalle, (orden,))
            resultado = cursor.fetchone()
            if not resultado: continue
            
            cursor.execute(sql_baremos, (orden,))
            resultado_baremos = cursor.fetchall()
            
            cursor.execute(sql_material, (orden,))
            resultado_material = cursor.fetchall()
            
            detalles.append((resultado, resultado_baremos, resultado_material))
            
        return len(ordenes), detalles
    except pymysql.MySQLError as e:
        raise Exception(f"Error de base de datos:\n{e}")
    finally:
        if cursor: cursor.close()
        if conexion: conexion.close()
