#!/usr/bin/env python3
"""
Módulo de base de datos para Sistema QUIRA
"""

import psycopg2
from psycopg2 import sql
import bcrypt
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Variable global para el usuario actual
USUARIO_ACTUAL = None

def connect_db():
    """
    Conectar a la base de datos PostgreSQL
    
    Returns:
        psycopg2.connection: Conexión a la base de datos
    """
    try:
        # Conectar directamente con la contraseña correcta
        conn = psycopg2.connect(
            dbname="sistema_postulantes",
            user="postgres",
            password="decfespa67",  # Contraseña del servidor remoto
            host="decfespaxsilco.ddns.net",
            port="5432"
        )
        return conn
    except psycopg2.OperationalError as e:
        logger.error("Error de conexión a PostgreSQL. Verifique:")
        logger.error("1. PostgreSQL esté instalado y ejecutándose")
        logger.error("2. Base de datos 'sistema_postulantes' exista")
        logger.error("3. Usuario 'postgres' tenga permisos")
        logger.error("4. Configure la contraseña en database.py si es necesario")
        return None
    except Exception as e:
        logger.error(f"Error al conectar a la base de datos: {e}")
        return None

def validate_user(username, password):
    """
    Validar credenciales de usuario
    
    Args:
        username (str): Nombre de usuario
        password (str): Contraseña
        
    Returns:
        dict: Datos del usuario si es válido, None en caso contrario
    """
    global USUARIO_ACTUAL
    
    try:
        conn = connect_db()
        if not conn:
            return None
            
        cursor = conn.cursor()
        
        # Buscar usuario en la base de datos
        query = sql.SQL("""
            SELECT id, usuario, contrasena, rol, nombre, apellido, grado, 
                   cedula, numero_credencial, telefono, primer_inicio 
            FROM usuarios 
            WHERE usuario = %s
        """)
        cursor.execute(query, (username,))
        user = cursor.fetchone()
        
        if user:
            stored_password = user[2]
            
            # Verificar contraseña con bcrypt
            if bcrypt.checkpw(password.encode(), stored_password.encode()):
                USUARIO_ACTUAL = {
                    'id': user[0],
                    'usuario': user[1],
                    'rol': user[3],
                    'nombre': user[4],
                    'apellido': user[5],
                    'grado': user[6],
                    'cedula': user[7],
                    'numero_credencial': user[8],
                    'telefono': user[9],
                    'primer_inicio': user[10]
                }
                
                logger.info(f"Usuario autenticado: {USUARIO_ACTUAL['nombre']} {USUARIO_ACTUAL['apellido']}")
                return USUARIO_ACTUAL
            else:
                logger.warning(f"Contraseña incorrecta para usuario: {username}")
                return None
        else:
            logger.warning(f"Usuario no encontrado: {username}")
            return None
            
    except Exception as e:
        logger.error(f"Error en validación de usuario: {e}")
        return None
    finally:
        if conn:
            conn.close()

def update_password(user_id, new_password):
    """
    Actualizar contraseña de usuario
    
    Args:
        user_id (int): ID del usuario
        new_password (str): Nueva contraseña
    """
    try:
        conn = connect_db()
        if not conn:
            return False
            
        cursor = conn.cursor()
        
        # Encriptar nueva contraseña
        hashed_password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
        
        # Actualizar en base de datos
        query = sql.SQL("""
            UPDATE usuarios 
            SET contrasena = %s, primer_inicio = FALSE 
            WHERE id = %s
        """)
        cursor.execute(query, (hashed_password, user_id))
        
        conn.commit()
        logger.info(f"Contraseña actualizada para usuario ID: {user_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error al actualizar contraseña: {e}")
        return False
    finally:
        if conn:
            conn.close()

def create_default_admin():
    """
    Crear usuario administrador por defecto si no existe
    """
    try:
        conn = connect_db()
        if not conn:
            return False
            
        cursor = conn.cursor()
        
        # Verificar si ya existe un usuario admin
        cursor.execute("SELECT * FROM usuarios WHERE usuario = 'admin'")
        existing_admin = cursor.fetchone()
        
        if not existing_admin:
            # Crear usuario admin por defecto
            hashed_password = bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()).decode()
            
            query = sql.SQL("""
                INSERT INTO usuarios (usuario, contrasena, rol, nombre, apellido, 
                                    grado, cedula, numero_credencial, telefono, 
                                    primer_inicio) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """)
            
            cursor.execute(query, (
                "admin", hashed_password, "SUPERADMIN", "Admin", "General",
                "Comisario", "00000000", "CRED-ADMIN", "0000000000", True
            ))
            
            conn.commit()
            logger.info("✅ Usuario admin creado con éxito")
            return True
        else:
            logger.info("Usuario admin ya existe")
            return True
            
    except Exception as e:
        logger.error(f"Error al crear usuario admin: {e}")
        return False
    finally:
        if conn:
            conn.close()

def get_postulantes(limit=None, offset=None):
    """
    Obtener lista de postulantes con soporte para paginación
    
    Args:
        limit (int, optional): Número máximo de registros a retornar
        offset (int, optional): Número de registros a saltar
        
    Returns:
        list: Lista de postulantes
    """
    try:
        conn = connect_db()
        if not conn:
            return []
            
        cursor = conn.cursor()
        
        # Construir query base
        query = """
            SELECT id, nombre, apellido, cedula, fecha_nacimiento, 
                   telefono, fecha_registro, usuario_registrador, id_k40, 
                   huella_dactilar, observaciones, edad, unidad, dedo_registrado, 
                   registrado_por, aparato_id, uid_k40, usuario_ultima_edicion, 
                   fecha_ultima_edicion
            FROM postulantes 
            ORDER BY fecha_registro DESC
        """
        
        # Agregar paginación si se especifica
        if limit is not None:
            query += f" LIMIT {limit}"
            if offset is not None:
                query += f" OFFSET {offset}"
        
        cursor.execute(query)
        postulantes = cursor.fetchall()
        
        return postulantes
        
    except Exception as e:
        logger.error(f"Error al obtener postulantes: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_total_postulantes():
    """
    Obtener el total de postulantes sin cargar todos los datos
    
    Returns:
        int: Total de postulantes
    """
    try:
        conn = connect_db()
        if not conn:
            return 0
            
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM postulantes")
        total = cursor.fetchone()[0]
        
        return total
        
    except Exception as e:
        logger.error(f"Error al obtener total de postulantes: {e}")
        return 0
    finally:
        if conn:
            conn.close()

def verificar_cedula_problema_judicial(cedula, cursor=None):
    """
    Verificar si una cédula tiene problemas judiciales
    
    Args:
        cedula (str): Número de cédula a verificar
        cursor: Cursor de base de datos opcional (para usar conexión existente)
        
    Returns:
        bool: True si la cédula tiene problemas judiciales, False en caso contrario
    """
    try:
        # Si se proporciona un cursor, usarlo (para conexión existente)
        if cursor:
            cursor.execute("""
                SELECT id FROM cedulas_problema_judicial 
                WHERE cedula = %s
            """, (cedula,))
            
            resultado = cursor.fetchone()
            return resultado is not None
        
        # Si no se proporciona cursor, crear nueva conexión
        else:
            conn = connect_db()
            if not conn:
                return False
                
            cursor = conn.cursor()
            
            # Verificar si la cédula existe en la tabla de problemas judiciales
            cursor.execute("""
                SELECT id FROM cedulas_problema_judicial 
                WHERE cedula = %s
            """, (cedula,))
            
            resultado = cursor.fetchone()
            
            return resultado is not None
            
    except Exception as e:
        logger.error(f"Error al verificar cédula problema judicial: {e}")
        return False
    finally:
        if not cursor and 'conn' in locals():
            conn.close()

def agregar_postulante(postulante_data):
    """
    Agregar nuevo postulante
    
    Args:
        postulante_data (dict): Datos del postulante
        
    Returns:
        dict: {'success': bool, 'message': str}
    """
    try:
        conn = connect_db()
        if not conn:
            return {'success': False, 'message': 'Error de conexión a la base de datos'}
            
        cursor = conn.cursor()
        
        # Obtener el nombre completo del usuario registrador
        nombre_registrador = "Desconocido"
        
        # Opción 1: Usar el nombre proporcionado directamente (más confiable)
        if postulante_data.get('nombre_registrador'):
            nombre_registrador = postulante_data['nombre_registrador']
            logger.info(f"✅ Usando nombre proporcionado: {nombre_registrador}")
        
        # Opción 2: Buscar por ID como fallback
        elif postulante_data.get('usuario_registrador'):
            logger.info(f"🔍 Buscando usuario registrador ID: {postulante_data['usuario_registrador']}")
            cursor.execute("""
                SELECT grado, nombre, apellido FROM usuarios 
                WHERE id = %s
            """, (postulante_data['usuario_registrador'],))
            
            usuario_data = cursor.fetchone()
            if usuario_data:
                grado = usuario_data[0] or ""
                nombre = usuario_data[1] or ""
                apellido = usuario_data[2] or ""
                nombre_registrador = f"{grado} {nombre} {apellido}".strip()
                logger.info(f"✅ Usuario encontrado por ID: {nombre_registrador}")
            else:
                logger.warning(f"⚠️ Usuario con ID {postulante_data['usuario_registrador']} no encontrado en la base de datos")
        else:
            logger.warning("⚠️ No se proporcionó usuario_registrador ni nombre_registrador en los datos")
        
        query = sql.SQL("""
            INSERT INTO postulantes (
                nombre, apellido, cedula, fecha_nacimiento, telefono, 
                fecha_registro, usuario_registrador, registrado_por, edad, sexo, unidad, 
                dedo_registrado, aparato_id, uid_k40
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """)
        
        cursor.execute(query, (
            postulante_data['nombre'],
            postulante_data['apellido'],
            postulante_data['cedula'],
            postulante_data['fecha_nacimiento'],
            postulante_data['telefono'],
            postulante_data['fecha_registro'],
            postulante_data['usuario_registrador'],
            nombre_registrador,
            postulante_data.get('edad'),
            postulante_data.get('sexo'),
            postulante_data.get('unidad'),
            postulante_data.get('dedo_registrado'),
            postulante_data.get('aparato_id'),
            postulante_data.get('uid_k40')
        ))
        
        conn.commit()
        logger.info(f"Postulante agregado: {postulante_data['nombre']} {postulante_data['apellido']} por {nombre_registrador}")
        
        return {
            'success': True, 
            'message': "Postulante agregado correctamente"
        }
        
    except Exception as e:
        logger.error(f"Error al agregar postulante: {e}")
        return {'success': False, 'message': f'Error al agregar postulante: {e}'}
    finally:
        if conn:
            conn.close()

def buscar_postulante(cedula=None, nombre=None):
    """
    Buscar postulante por cédula o nombre (OPTIMIZADO)
    
    Args:
        cedula (str): Número de cédula
        nombre (str): Nombre del postulante
        
    Returns:
        list: Lista de postulantes encontrados
    """
    try:
        conn = connect_db()
        if not conn:
            return []
            
        cursor = conn.cursor()
        
        if cedula:
            # Búsqueda optimizada por cédula con ordenamiento por relevancia (case-insensitive)
            query = sql.SQL("""
                SELECT id, nombre, apellido, cedula, fecha_nacimiento, 
                       telefono, fecha_registro, usuario_registrador, registrado_por, aparato_id, dedo_registrado,
                       usuario_ultima_edicion, fecha_ultima_edicion
                FROM postulantes 
                WHERE LOWER(CAST(cedula AS TEXT)) LIKE LOWER(%s)
                ORDER BY 
                    CASE 
                        WHEN LOWER(CAST(cedula AS TEXT)) = LOWER(%s) THEN 1  -- Coincidencia exacta
                        WHEN LOWER(CAST(cedula AS TEXT)) LIKE LOWER(%s) THEN 2  -- Empieza con
                        ELSE 3  -- Contiene
                    END,
                    fecha_registro DESC
                LIMIT 100
            """)
            search_term = f"%{cedula}%"
            starts_with = f"{cedula}%"
            cursor.execute(query, (search_term, cedula, starts_with))
        elif nombre:
            # Búsqueda optimizada por nombre con ordenamiento por relevancia
            search_terms = nombre.strip().split()
            
            if len(search_terms) > 1:
                # Búsqueda con múltiples palabras
                conditions = []
                params = []
                
                for term in search_terms:
                    if term.strip():
                        conditions.append("(LOWER(nombre) LIKE LOWER(%s) OR LOWER(apellido) LIKE LOWER(%s))")
                        params.extend([f"%{term}%", f"%{term}%"])
                
                if conditions:
                    query = sql.SQL(f"""
                        SELECT id, nombre, apellido, cedula, fecha_nacimiento, 
                               telefono, fecha_registro, usuario_registrador, registrado_por, aparato_id, dedo_registrado,
                               usuario_ultima_edicion, fecha_ultima_edicion
                        FROM postulantes 
                        WHERE {' AND '.join(conditions)}
                        ORDER BY 
                            CASE 
                                WHEN LOWER(nombre) LIKE LOWER(%s) THEN 1  -- Nombre empieza con
                                WHEN LOWER(apellido) LIKE LOWER(%s) THEN 2  -- Apellido empieza con
                                ELSE 3
                            END,
                            fecha_registro DESC
                        LIMIT 100
                    """)
                    params.extend([f"{nombre}%", f"{nombre}%"])
                    cursor.execute(query, params)
                else:
                    return []
            else:
                # Búsqueda con una sola palabra optimizada
                query = sql.SQL("""
                    SELECT id, nombre, apellido, cedula, fecha_nacimiento, 
                           telefono, fecha_registro, usuario_registrador, registrado_por, aparato_id, dedo_registrado,
                           usuario_ultima_edicion, fecha_ultima_edicion
                    FROM postulantes 
                    WHERE LOWER(nombre) LIKE LOWER(%s) OR LOWER(apellido) LIKE LOWER(%s)
                    ORDER BY 
                        CASE 
                            WHEN LOWER(nombre) LIKE LOWER(%s) THEN 1  -- Nombre empieza con
                            WHEN LOWER(apellido) LIKE LOWER(%s) THEN 2  -- Apellido empieza con
                            WHEN LOWER(nombre) LIKE LOWER(%s) THEN 3  -- Nombre contiene
                            WHEN LOWER(apellido) LIKE LOWER(%s) THEN 4  -- Apellido contiene
                            ELSE 5
                        END,
                        fecha_registro DESC
                    LIMIT 100
                """)
                search_term = f"%{nombre}%"
                starts_with = f"{nombre}%"
                cursor.execute(query, (search_term, search_term, starts_with, starts_with, search_term, search_term))
        else:
            return []
        
        postulantes = cursor.fetchall()
        return postulantes
        
    except Exception as e:
        logger.error(f"Error al buscar postulante: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_usuarios():
    """
    Obtener lista de usuarios del sistema
    
    Returns:
        list: Lista de usuarios
    """
    try:
        conn = connect_db()
        if not conn:
            return []
            
        cursor = conn.cursor()
        
        query = sql.SQL("""
            SELECT id, usuario, rol, nombre, apellido, grado, cedula, 
                   numero_credencial, telefono, primer_inicio
            FROM usuarios 
            ORDER BY nombre, apellido
        """)
        
        cursor.execute(query)
        usuarios = cursor.fetchall()
        
        return usuarios
        
    except Exception as e:
        logger.error(f"Error al obtener usuarios: {e}")
        return []
    finally:
        if conn:
            conn.close()

def crear_usuario(usuario_data):
    """
    Crear nuevo usuario
    
    Args:
        usuario_data (dict): Datos del usuario
        
    Returns:
        bool: True si se creó correctamente
    """
    try:
        conn = connect_db()
        if not conn:
            return False
            
        cursor = conn.cursor()
        
        # Encriptar contraseña
        hashed_password = bcrypt.hashpw(usuario_data['contrasena'].encode(), bcrypt.gensalt()).decode()
        
        query = sql.SQL("""
            INSERT INTO usuarios (
                usuario, contrasena, rol, nombre, apellido, grado, 
                cedula, numero_credencial, telefono, primer_inicio
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """)
        
        cursor.execute(query, (
            usuario_data['usuario'],
            hashed_password,
            usuario_data['rol'],
            usuario_data['nombre'],
            usuario_data['apellido'],
            usuario_data['grado'],
            usuario_data['cedula'],
            usuario_data['numero_credencial'],
            usuario_data['telefono'],
            True  # primer_inicio = True para nuevos usuarios
        ))
        
        conn.commit()
        logger.info(f"Usuario creado: {usuario_data['nombre']} {usuario_data['apellido']}")
        return True
        
    except Exception as e:
        logger.error(f"Error al crear usuario: {e}")
        return False
    finally:
        if conn:
            conn.close()

def actualizar_postulante(postulante_id, postulante_data, user_data=None):
    """
    Actualizar datos de un postulante existente
    
    Args:
        postulante_id (int): ID del postulante a actualizar
        postulante_data (dict): Nuevos datos del postulante
        user_data (dict): Datos del usuario que realiza la edición
        
    Returns:
        bool: True si se actualizó correctamente
    """
    try:
        conn = connect_db()
        if not conn:
            return False
            
        cursor = conn.cursor()
        
        # Obtener datos actuales del postulante para comparar cambios
        cursor.execute("""
            SELECT nombre, apellido, cedula, fecha_nacimiento, telefono, 
                   edad, unidad, dedo_registrado, observaciones
            FROM postulantes WHERE id = %s
        """, (postulante_id,))
        
        datos_actuales = cursor.fetchone()
        if not datos_actuales:
            logger.error(f"Postulante con ID {postulante_id} no encontrado")
            return False
        
        # Preparar información del usuario que edita
        usuario_editor = "Desconocido"
        if user_data and 'nombre' in user_data and 'apellido' in user_data:
            usuario_editor = f"{user_data['nombre']} {user_data['apellido']}"
        
        # Detectar cambios en cada campo
        cambios = []
        campos_actuales = {
            'nombre': datos_actuales[0],
            'apellido': datos_actuales[1],
            'cedula': datos_actuales[2],
            'fecha_nacimiento': datos_actuales[3],
            'telefono': datos_actuales[4],
            'edad': datos_actuales[5],
            'unidad': datos_actuales[6],
            'dedo_registrado': datos_actuales[7],
            'observaciones': datos_actuales[8]
        }
        
        campos_nuevos = {
            'nombre': postulante_data['nombre'],
            'apellido': postulante_data['apellido'],
            'cedula': postulante_data['cedula'],
            'fecha_nacimiento': postulante_data['fecha_nacimiento'],
            'telefono': postulante_data['telefono'],
            'edad': postulante_data.get('edad'),
            'unidad': postulante_data.get('unidad'),
            'dedo_registrado': postulante_data.get('dedo_registrado'),
            'observaciones': postulante_data.get('observaciones', '')
        }
        
        # Mapeo de nombres de campos para mostrar
        nombres_campos = {
            'nombre': 'Nombre',
            'apellido': 'Apellido',
            'cedula': 'Cédula',
            'fecha_nacimiento': 'Fecha de Nacimiento',
            'telefono': 'Teléfono',
            'edad': 'Edad',
            'unidad': 'Unidad',
            'dedo_registrado': 'Dedo Registrado',
            'observaciones': 'Observaciones'
        }
        
        # Comparar campos y registrar cambios (excluyendo observaciones)
        for campo, valor_actual in campos_actuales.items():
            # Excluir observaciones del historial de ediciones
            if campo == 'observaciones':
                continue
                
            valor_nuevo = campos_nuevos[campo]
            # Convertir a string para comparación consistente
            valor_actual_str = str(valor_actual) if valor_actual is not None else ''
            valor_nuevo_str = str(valor_nuevo) if valor_nuevo is not None else ''
            
            if valor_actual_str != valor_nuevo_str:
                # Solo registrar si realmente hay un cambio
                if valor_actual_str.strip() != valor_nuevo_str.strip():
                    nombre_campo = nombres_campos.get(campo, campo.title())
                    cambios.append(f"{nombre_campo}: '{valor_actual_str}' → '{valor_nuevo_str}'")
        
        # Actualizar postulante
        query = sql.SQL("""
            UPDATE postulantes SET
                nombre = %s,
                apellido = %s,
                cedula = %s,
                fecha_nacimiento = %s,
                telefono = %s,
                edad = %s,
                unidad = %s,
                dedo_registrado = %s,
                observaciones = %s,
                usuario_ultima_edicion = %s,
                fecha_ultima_edicion = CURRENT_TIMESTAMP
            WHERE id = %s
        """)
        
        cursor.execute(query, (
            postulante_data['nombre'],
            postulante_data['apellido'],
            postulante_data['cedula'],
            postulante_data['fecha_nacimiento'],
            postulante_data['telefono'],
            postulante_data.get('edad'),
            postulante_data.get('unidad'),
            postulante_data.get('dedo_registrado'),
            postulante_data.get('observaciones', ''),
            usuario_editor,
            postulante_id
        ))
        
        # Registrar en historial de ediciones si hay cambios
        if cambios:
            # Crear tabla de historial si no existe
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS historial_ediciones_postulantes (
                    id SERIAL PRIMARY KEY,
                    postulante_id INTEGER NOT NULL,
                    usuario_editor VARCHAR(100) NOT NULL,
                    fecha_edicion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    cambios TEXT NOT NULL,
                    FOREIGN KEY (postulante_id) REFERENCES postulantes(id) ON DELETE CASCADE
                )
            """)
            
            # Insertar registro en historial con hora local
            cambios_texto = "; ".join(cambios)
            from datetime import datetime
            hora_local = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute("""
                INSERT INTO historial_ediciones_postulantes 
                (postulante_id, usuario_editor, fecha_edicion, cambios) 
                VALUES (%s, %s, %s, %s)
            """, (postulante_id, usuario_editor, hora_local, cambios_texto))
        
        conn.commit()
        logger.info(f"Postulante actualizado: {postulante_data['nombre']} {postulante_data['apellido']} por {usuario_editor}")
        return True
        
    except Exception as e:
        logger.error(f"Error al actualizar postulante: {e}")
        return False
    finally:
        if conn:
            conn.close()

def eliminar_postulante(postulante_id):
    """
    Eliminar un postulante de la base de datos
    
    Args:
        postulante_id (int): ID del postulante a eliminar
        
    Returns:
        bool: True si se eliminó correctamente
    """
    try:
        conn = connect_db()
        if not conn:
            return False
            
        cursor = conn.cursor()
        
        # Primero obtener los datos del postulante para el log
        cursor.execute("SELECT nombre, apellido FROM postulantes WHERE id = %s", (postulante_id,))
        postulante = cursor.fetchone()
        
        if not postulante:
            logger.error(f"Postulante con ID {postulante_id} no encontrado")
            return False
        
        # Eliminar el postulante
        cursor.execute("DELETE FROM postulantes WHERE id = %s", (postulante_id,))
        
        conn.commit()
        logger.info(f"Postulante eliminado: {postulante[0]} {postulante[1]}")
        return True
        
    except Exception as e:
        logger.error(f"Error al eliminar postulante: {e}")
        return False
    finally:
        if conn:
            conn.close()

def obtener_postulante_por_id(postulante_id):
    """
    Obtener un postulante específico por su ID
    
    Args:
        postulante_id (int): ID del postulante
        
    Returns:
        tuple: Datos del postulante o None si no se encuentra
    """
    try:
        conn = connect_db()
        if not conn:
            return None
            
        cursor = conn.cursor()
        
        query = sql.SQL("""
            SELECT id, nombre, apellido, cedula, fecha_nacimiento, 
                   telefono, fecha_registro, usuario_registrador, edad, unidad, 
                   dedo_registrado, registrado_por, aparato_id, uid_k40, 
                   huella_dactilar, observaciones, usuario_ultima_edicion, 
                   fecha_ultima_edicion
            FROM postulantes 
            WHERE id = %s
        """)
        
        cursor.execute(query, (postulante_id,))
        postulante = cursor.fetchone()
        
        return postulante
        
    except Exception as e:
        logger.error(f"Error al obtener postulante: {e}")
        return None
    finally:
        if conn:
            conn.close()

def obtener_historial_ediciones(postulante_id):
    """
    Obtener historial completo de ediciones de un postulante
    
    Args:
        postulante_id (int): ID del postulante
        
    Returns:
        list: Lista de ediciones ordenadas por fecha (más reciente primero)
    """
    try:
        conn = connect_db()
        if not conn:
            return []
            
        cursor = conn.cursor()
        
        # Verificar si la tabla existe
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'historial_ediciones_postulantes'
            )
        """)
        
        if not cursor.fetchone()[0]:
            return []  # Tabla no existe, no hay historial
        
        query = sql.SQL("""
            SELECT usuario_editor, fecha_edicion, cambios
            FROM historial_ediciones_postulantes 
            WHERE postulante_id = %s
            ORDER BY fecha_edicion DESC
        """)
        
        cursor.execute(query, (postulante_id,))
        historial = cursor.fetchall()
        
        return historial
        
    except Exception as e:
        logger.error(f"Error al obtener historial de ediciones: {e}")
        return []
    finally:
        if conn:
            conn.close()

def actualizar_usuario(user_id, usuario_data):
    """
    Actualizar datos de un usuario existente
    
    Args:
        user_id (int): ID del usuario a actualizar
        usuario_data (dict): Nuevos datos del usuario
        
    Returns:
        bool: True si se actualizó correctamente
    """
    try:
        conn = connect_db()
        if not conn:
            return False
            
        cursor = conn.cursor()
        
        # Construir query dinámicamente
        update_fields = []
        values = []
        
        # Campos que siempre se actualizan
        update_fields.extend([
            "usuario = %s",
            "rol = %s", 
            "nombre = %s",
            "apellido = %s",
            "grado = %s",
            "cedula = %s",
            "numero_credencial = %s",
            "telefono = %s"
        ])
        values.extend([
            usuario_data['usuario'],
            usuario_data['rol'],
            usuario_data['nombre'],
            usuario_data['apellido'],
            usuario_data['grado'],
            usuario_data['cedula'],
            usuario_data['numero_credencial'],
            usuario_data['telefono']
        ])
        
        # Si se proporcionó nueva contraseña, actualizarla
        if 'contrasena' in usuario_data and usuario_data['contrasena']:
            hashed_password = bcrypt.hashpw(usuario_data['contrasena'].encode(), bcrypt.gensalt()).decode()
            update_fields.append("contrasena = %s")
            values.append(hashed_password)
        
        # Si se especificó el estado de primer_inicio, actualizarlo
        if 'primer_inicio' in usuario_data:
            update_fields.append("primer_inicio = %s")
            values.append(usuario_data['primer_inicio'])
        
        # Agregar ID al final
        values.append(user_id)
        
        query = sql.SQL(f"""
            UPDATE usuarios SET
                {', '.join(update_fields)}
            WHERE id = %s
        """)
        
        cursor.execute(query, values)
        conn.commit()
        
        logger.info(f"Usuario actualizado: {usuario_data['nombre']} {usuario_data['apellido']}")
        return True
        
    except Exception as e:
        logger.error(f"Error al actualizar usuario: {e}")
        return False
    finally:
        if conn:
            conn.close()

def eliminar_usuario(user_id):
    """
    Eliminar un usuario del sistema
    
    Args:
        user_id (int): ID del usuario a eliminar
        
    Returns:
        bool: True si se eliminó correctamente
    """
    try:
        conn = connect_db()
        if not conn:
            return False
            
        cursor = conn.cursor()
        
        # Primero obtener los datos del usuario para el log
        cursor.execute("SELECT nombre, apellido, usuario FROM usuarios WHERE id = %s", (user_id,))
        usuario = cursor.fetchone()
        
        if not usuario:
            logger.error(f"Usuario con ID {user_id} no encontrado")
            return False
        
        # Verificar que no sea el último SUPERADMIN
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE rol = 'SUPERADMIN'")
        superadmin_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT rol FROM usuarios WHERE id = %s", (user_id,))
        user_role = cursor.fetchone()[0]
        
        if user_role == 'SUPERADMIN' and superadmin_count <= 1:
            logger.error("No se puede eliminar el último SUPERADMIN")
            return False
        
        # Eliminar el usuario
        cursor.execute("DELETE FROM usuarios WHERE id = %s", (user_id,))
        
        conn.commit()
        logger.info(f"Usuario eliminado: {usuario[0]} {usuario[1]} ({usuario[2]})")
        return True
        
    except Exception as e:
        logger.error(f"Error al eliminar usuario: {e}")
        return False
    finally:
        if conn:
            conn.close()

def obtener_usuario_por_id(user_id):
    """
    Obtener un usuario específico por su ID
    
    Args:
        user_id (int): ID del usuario
        
    Returns:
        tuple: Datos del usuario o None si no se encuentra
    """
    try:
        conn = connect_db()
        if not conn:
            return None
            
        cursor = conn.cursor()
        
        query = sql.SQL("""
            SELECT id, usuario, rol, nombre, apellido, grado, cedula, 
                   numero_credencial, telefono, primer_inicio
            FROM usuarios 
            WHERE id = %s
        """)
        
        cursor.execute(query, (user_id,))
        usuario = cursor.fetchone()
        
        return usuario
        
    except Exception as e:
        logger.error(f"Error al obtener usuario: {e}")
        return None
    finally:
        if conn:
            conn.close()

def obtener_nombre_registrador(user_id):
    """
    Obtener el nombre completo del registrador (grado + nombre + apellido)
    
    Args:
        user_id (int): ID del usuario registrador
        
    Returns:
        str: Nombre completo del registrador o "Desconocido" si no se encuentra
    """
    try:
        if not user_id:
            return "Desconocido"
            
        usuario = obtener_usuario_por_id(user_id)
        if usuario:
            grado = usuario[5] or ""  # grado
            nombre = usuario[3] or ""  # nombre
            apellido = usuario[4] or ""  # apellido
            
            nombre_completo = f"{grado} {nombre} {apellido}".strip()
            return nombre_completo if nombre_completo else "Desconocido"
        else:
            return "Desconocido"
            
    except Exception as e:
        logger.error(f"Error al obtener nombre del registrador: {e}")
        return "Desconocido"

def obtener_nombre_aparato(aparato_id):
    """
    Obtener el nombre del aparato biométrico
    
    Args:
        aparato_id (int): ID del aparato biométrico
        
    Returns:
        str: Nombre del aparato o "Desconocido" si no se encuentra
    """
    try:
        if not aparato_id:
            return "Desconocido"
            
        conn = connect_db()
        if not conn:
            return "Desconocido"
            
        cursor = conn.cursor()
        
        query = sql.SQL("""
            SELECT nombre FROM aparatos_biometricos 
            WHERE id = %s
        """)
        
        cursor.execute(query, (aparato_id,))
        resultado = cursor.fetchone()
        
        if resultado:
            return resultado[0]
        else:
            return "Desconocido"
            
    except Exception as e:
        logger.error(f"Error al obtener nombre del aparato: {e}")
        return "Desconocido"
    finally:
        if conn:
            conn.close()

def update_postulantes_table_structure(cursor, conn):
    """
    Actualizar la estructura de la tabla postulantes para agregar campos de seguimiento
    """
    try:
        # Verificar si existen los campos de seguimiento
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'postulantes' 
            AND column_name IN ('usuario_ultima_edicion', 'fecha_ultima_edicion', 'sexo')
        """)
        existing_columns = [row[0] for row in cursor.fetchall()]
        
        # Agregar campos si no existen
        if 'usuario_ultima_edicion' not in existing_columns:
            cursor.execute("""
                ALTER TABLE postulantes 
                ADD COLUMN usuario_ultima_edicion VARCHAR(100)
            """)
            logger.info("✅ Campo usuario_ultima_edicion agregado")
            
        if 'fecha_ultima_edicion' not in existing_columns:
            cursor.execute("""
                ALTER TABLE postulantes 
                ADD COLUMN fecha_ultima_edicion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            """)
            logger.info("✅ Campo fecha_ultima_edicion agregado")
            
        if 'sexo' not in existing_columns:
            cursor.execute("""
                ALTER TABLE postulantes 
                ADD COLUMN sexo VARCHAR(10)
            """)
            logger.info("✅ Campo sexo agregado")
            
        conn.commit()
        
    except Exception as e:
        logger.error(f"Error al actualizar estructura de tabla postulantes: {e}")
        conn.rollback()

def init_database():
    """
    Inicializar la base de datos con tablas necesarias
    """
    try:
        conn = connect_db()
        if not conn:
            return False
            
        cursor = conn.cursor()
        
        # Crear tabla de usuarios si no existe
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id SERIAL PRIMARY KEY,
                usuario VARCHAR(50) UNIQUE NOT NULL,
                contrasena VARCHAR(255) NOT NULL,
                rol VARCHAR(20) NOT NULL DEFAULT 'USUARIO',
                nombre VARCHAR(100) NOT NULL,
                apellido VARCHAR(100) NOT NULL,
                grado VARCHAR(50),
                cedula VARCHAR(20),
                numero_credencial VARCHAR(50),
                telefono VARCHAR(20),
                primer_inicio BOOLEAN DEFAULT TRUE,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Crear tabla de postulantes si no existe
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS postulantes (
                id SERIAL PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                apellido VARCHAR(100) NOT NULL,
                cedula VARCHAR(20) UNIQUE NOT NULL,
                fecha_nacimiento DATE,
                telefono VARCHAR(20),
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                usuario_registrador INTEGER,
                edad INTEGER,
                unidad VARCHAR(50),
                dedo_registrado VARCHAR(20),
                registrado_por VARCHAR(100),
                aparato_id INTEGER REFERENCES aparatos_biometricos(id),
                uid_k40 INTEGER,
                huella_dactilar BYTEA,
                observaciones TEXT
            )
        """)
        
        # Crear tabla de aparatos biométricos si no existe
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS aparatos_biometricos (
                id SERIAL PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                serial VARCHAR(100) UNIQUE NOT NULL,
                ip_address VARCHAR(15),
                puerto INTEGER DEFAULT 4370,
                ubicacion VARCHAR(200),
                estado VARCHAR(20) DEFAULT 'ACTIVO',
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Crear tabla de privilegios si no existe
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS privilegios (
                id SERIAL PRIMARY KEY,
                rol VARCHAR(20) NOT NULL,
                permiso VARCHAR(50) NOT NULL,
                descripcion TEXT,
                activo BOOLEAN DEFAULT TRUE,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(rol, permiso)
            )
        """)
        
        # Crear tabla de problemas judiciales si no existe
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cedulas_problema_judicial (
                id SERIAL PRIMARY KEY,
                cedula VARCHAR(20) UNIQUE NOT NULL
            )
        """)

        
        conn.commit()
        logger.info("✅ Base de datos inicializada correctamente")
        
        # Actualizar estructura de tabla postulantes si es necesario
        update_postulantes_table_structure(cursor, conn)
        
        # Crear usuario admin por defecto
        create_default_admin()
        
        # Inicializar privilegios por defecto
        init_default_privileges(cursor, conn)
        
        return True
        
    except Exception as e:
        logger.error(f"Error al inicializar base de datos: {e}")
        return False
    finally:
        if conn:
            conn.close()

# ============================================================================
# FUNCIONES PARA PRIVILEGIOS
# ============================================================================

def init_default_privileges(cursor, conn):
    """
    Inicializar privilegios por defecto para cada rol
    """
    try:
        # Definir TODOS los privilegios disponibles para TODOS los roles
        todos_los_privilegios = [
            ('buscar_postulantes', 'Puede buscar y ver postulantes'),
            ('agregar_postulante', 'Puede agregar nuevos postulantes'),
            ('lista_postulantes', 'Puede ver la lista de postulantes'),
            ('estadisticas_basicas', 'Puede ver estadísticas básicas'),
            ('estadisticas_completas', 'Puede ver todas las estadísticas'),
            ('gestion_zkteco_basica', 'Puede usar dispositivos ZKTeco'),
            ('gestion_zkteco_completa', 'Puede gestionar dispositivos ZKTeco'),
            ('editar_postulantes_propios', 'Puede editar sus propios postulantes'),
            ('editar_postulantes_otros', 'Puede editar postulantes de otros usuarios'),
            ('eliminar_postulantes_propios', 'Puede eliminar sus propios postulantes'),
            ('eliminar_postulantes_otros', 'Puede eliminar postulantes de otros usuarios'),
            ('eliminar_postulantes', 'Puede eliminar postulantes (permiso general)'),
            ('gestion_usuarios', 'Puede gestionar usuarios del sistema'),
            ('gestion_privilegios', 'Puede gestionar privilegios del sistema'),
        ]
        
        # Crear privilegios para todos los roles con la misma lista completa
        default_privileges = []
        roles = ['USUARIO', 'ADMIN', 'SUPERADMIN']
        
        for rol in roles:
            for permiso, descripcion in todos_los_privilegios:
                default_privileges.append((rol, permiso, descripcion))
        
        # Insertar privilegios por defecto
        for rol, permiso, descripcion in default_privileges:
            cursor.execute("""
                INSERT INTO privilegios (rol, permiso, descripcion, activo)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (rol, permiso) DO NOTHING
            """, (rol, permiso, descripcion, True))
        
        conn.commit()
        logger.info("✅ Privilegios por defecto inicializados correctamente")
        
    except Exception as e:
        logger.error(f"Error al inicializar privilegios: {e}")
        conn.rollback()

def verificar_privilegio(rol, permiso):
    """
    Verificar si un rol tiene un privilegio específico
    
    Args:
        rol (str): Rol del usuario
        permiso (str): Permiso a verificar
        
    Returns:
        bool: True si tiene el privilegio, False en caso contrario
    """
    try:
        conn = connect_db()
        if not conn:
            return False
            
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT activo FROM privilegios 
            WHERE rol = %s AND permiso = %s
        """, (rol, permiso))
        
        result = cursor.fetchone()
        
        if result:
            return result[0]  # Retorna el valor de 'activo'
        else:
            # Si no existe el privilegio, SUPERADMIN tiene todos los permisos
            return rol == 'SUPERADMIN'
            
    except Exception as e:
        logger.error(f"Error al verificar privilegio: {e}")
        return False
    finally:
        if conn:
            conn.close()

def obtener_privilegios_rol(rol):
    """
    Obtener todos los privilegios de un rol específico
    
    Args:
        rol (str): Rol del usuario
        
    Returns:
        list: Lista de privilegios del rol
    """
    try:
        conn = connect_db()
        if not conn:
            return []
            
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT permiso, descripcion, activo 
            FROM privilegios 
            WHERE rol = %s
            ORDER BY permiso
        """, (rol,))
        
        privilegios = cursor.fetchall()
        return privilegios
        
    except Exception as e:
        logger.error(f"Error al obtener privilegios del rol: {e}")
        return []
    finally:
        if conn:
            conn.close()

def actualizar_privilegio(rol, permiso, activo):
    """
    Actualizar el estado de un privilegio
    
    Args:
        rol (str): Rol del usuario
        permiso (str): Permiso a actualizar
        activo (bool): Estado del privilegio
        
    Returns:
        bool: True si se actualizó correctamente
    """
    try:
        conn = connect_db()
        if not conn:
            return False
            
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE privilegios 
            SET activo = %s 
            WHERE rol = %s AND permiso = %s
        """, (activo, rol, permiso))
        
        conn.commit()
        logger.info(f"Privilegio {permiso} para rol {rol} actualizado a {activo}")
        return True
        
    except Exception as e:
        logger.error(f"Error al actualizar privilegio: {e}")
        return False
    finally:
        if conn:
            conn.close()

def obtener_todos_privilegios():
    """
    Obtener todos los privilegios de todos los roles
    
    Returns:
        list: Lista de todos los privilegios organizados por rol
    """
    try:
        conn = connect_db()
        if not conn:
            return {}
            
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT rol, permiso, descripcion, activo 
            FROM privilegios 
            ORDER BY rol, permiso
        """)
        
        privilegios = cursor.fetchall()
        
        # Organizar por rol
        privilegios_por_rol = {}
        for rol, permiso, descripcion, activo in privilegios:
            if rol not in privilegios_por_rol:
                privilegios_por_rol[rol] = []
            privilegios_por_rol[rol].append({
                'permiso': permiso,
                'descripcion': descripcion,
                'activo': activo
            })
        
        return privilegios_por_rol
        
    except Exception as e:
        logger.error(f"Error al obtener todos los privilegios: {e}")
        return {}
    finally:
        if conn:
            conn.close()

# ============================================================================
# FUNCIONES PARA COMUNICADOS
# ============================================================================



if __name__ == "__main__":
    # Prueba de inicialización
    if init_database():
        print("✅ Base de datos inicializada correctamente")
    else:
        print("❌ Error al inicializar base de datos") 