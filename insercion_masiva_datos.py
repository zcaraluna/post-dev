#!/usr/bin/env python3
"""
Script para inserción masiva de datos ficticios en el Sistema QUIRA
Genera 10,000+ registros de postulantes con datos realistas
"""

import random
import string
from datetime import datetime, timedelta, date
from database import connect_db
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Datos ficticios para generar registros realistas
NOMBRES_MASCULINOS = [
    "Juan", "Carlos", "Luis", "Miguel", "Jorge", "Roberto", "Fernando", "Ricardo", "Eduardo", "Alberto",
    "Diego", "Andrés", "Santiago", "Gabriel", "Daniel", "Francisco", "Manuel", "José", "Pedro", "Antonio",
    "Mario", "Rafael", "Alejandro", "Cristian", "Marcelo", "Felipe", "Sebastián", "Nicolás", "Matías", "Gustavo",
    "Hugo", "Oscar", "Víctor", "Pablo", "Adrián", "Leonardo", "Rodrigo", "Federico", "Emilio", "Ignacio",
    "Tomás", "Bruno", "Lucas", "Martín", "Agustín", "Facundo", "Maximiliano", "Thiago", "Benjamín", "Valentín"
]

NOMBRES_FEMENINOS = [
    "María", "Ana", "Carmen", "Isabel", "Rosa", "Patricia", "Silvia", "Elena", "Lucía", "Sofía",
    "Valentina", "Camila", "Martina", "Victoria", "Emilia", "Valeria", "Natalia", "Gabriela", "Carolina", "Daniela",
    "Florencia", "Agustina", "Antonella", "Julieta", "Micaela", "Bianca", "Lola", "Catalina", "Renata", "Abril",
    "Sara", "Paula", "Andrea", "Claudia", "Laura", "Cecilia", "Verónica", "Mónica", "Adriana", "Beatriz",
    "Diana", "Eva", "Julia", "Lorena", "Marcela", "Natalia", "Pamela", "Rocío", "Tatiana", "Yamila"
]

APELLIDOS = [
    "González", "Rodríguez", "Gómez", "Fernández", "López", "Díaz", "Martínez", "Pérez", "García", "Sánchez",
    "Romero", "Sosa", "Torres", "Álvarez", "Ruiz", "Ramírez", "Flores", "Acosta", "Benítez", "Silva",
    "Rojas", "Molina", "Castro", "Ortiz", "Herrera", "Suárez", "Aguirre", "Giménez", "Gutiérrez", "Moreno",
    "Jiménez", "Pereyra", "Ríos", "Luna", "Vargas", "Cáceres", "Mendoza", "Vera", "Ramos", "Córdoba",
    "Coronel", "Villalba", "Cardozo", "Bogado", "Aguayo", "Barreto", "Caballero", "Dávalos", "Espínola", "Fleitas"
]

UNIDADES_ISEPOL = [
    "Escuela de Formación Básica",
    "Escuela de Formación de Oficiales", 
    "Instituto de Especialización Técnica",
    "Centro de Perfeccionamiento Profesional",
    "Unidad de Educación Continua",
    "Escuela de Tránsito",
    "Escuela de Criminalística",
    "Escuela de Investigación",
    "Centro de Capacitación Especializada",
    "Instituto de Formación Superior"
]

# Abreviaciones de dedos (máximo 10 caracteres para VARCHAR(10))
# PD=Pulgar Derecho, ID=Índice Derecho, MD=Medio Derecho, AD=Anular Derecho, MND=Meñique Derecho
# PI=Pulgar Izquierdo, II=Índice Izquierdo, MI=Medio Izquierdo, AI=Anular Izquierdo, MNI=Meñique Izquierdo
DEDOS = ["PD", "ID", "MD", "AD", "MND", "PI", "II", "MI", "AI", "MNI"]

# Valores correctos para sexo según la base de datos real
SEXOS = ["Hombre", "Mujer"]

USUARIOS_REGISTRADORES = [
    "Téc. Juan Pérez", "Téc. María González", "Téc. Carlos López", "Téc. Ana Rodríguez",
    "Téc. Roberto Silva", "Téc. Patricia Castro", "Téc. Fernando Ríos", "Téc. Lucía Mendoza",
    "Téc. Ricardo Vera", "Téc. Carmen Bogado", "Téc. Eduardo Coronel", "Téc. Isabel Villalba",
    "Téc. Miguel Cardozo", "Téc. Rosa Aguayo", "Téc. Jorge Barreto", "Téc. Elena Caballero"
]

OBSERVACIONES_POSIBLES = [
    "Registro normal", "Huella de buena calidad", "Requiere nueva captura", "Postulante cooperativo",
    "Proceso sin complicaciones", "Verificación exitosa", "Datos completos", "Documentación en orden",
    "Sin observaciones", "Proceso estándar", "Captura exitosa", "Verificación biométrica correcta"
]

# Conjunto para almacenar cédulas ya generadas y evitar duplicados
cedulas_generadas = set()

def generar_cedula_unica():
    """Generar cédula paraguaya ficticia única"""
    max_intentos = 1000
    intentos = 0
    
    while intentos < max_intentos:
        cedula = ''.join(random.choices(string.digits, k=8))
        if cedula not in cedulas_generadas:
            cedulas_generadas.add(cedula)
            return cedula
        intentos += 1
    
    # Si se agotan los intentos, usar timestamp como base
    timestamp = str(int(datetime.now().timestamp()))[-8:]
    cedula = timestamp.zfill(8)
    cedulas_generadas.add(cedula)
    return cedula

def generar_telefono():
    """Generar teléfono paraguayo ficticio"""
    # Formato: 0981-XXXXXX o 0982-XXXXXX o 0983-XXXXXX
    prefijos = ["0981", "0982", "0983", "0984", "0985", "0986"]
    prefijo = random.choice(prefijos)
    numero = ''.join(random.choices(string.digits, k=6))
    return f"{prefijo}-{numero}"

def generar_fecha_nacimiento():
    """Generar fecha de nacimiento realista (18-65 años)"""
    # Calcular edad entre 18 y 65 años
    edad = random.randint(18, 65)
    # Calcular fecha de nacimiento
    fecha_actual = date.today()
    fecha_nacimiento = fecha_actual - timedelta(days=edad*365 + random.randint(0, 365))
    return fecha_nacimiento

def generar_fecha_registro():
    """Generar fecha de registro en los últimos 2 años"""
    fecha_actual = datetime.now()
    dias_atras = random.randint(0, 730)  # Últimos 2 años
    fecha_registro = fecha_actual - timedelta(days=dias_atras)
    
    # Ajustar hora entre 7:00 y 23:00
    hora = random.randint(7, 23)
    minuto = random.randint(0, 59)
    segundo = random.randint(0, 59)
    
    return fecha_registro.replace(hour=hora, minute=minuto, second=segundo)

def generar_huella_dactilar_ficticia():
    """Generar datos ficticios de huella dactilar (BYTEA)"""
    # Generar 512 bytes aleatorios para simular template biométrico
    return bytes(random.getrandbits(8) for _ in range(512))

def generar_postulante_ficticio():
    """Generar un postulante ficticio completo"""
    # Generar género
    es_masculino = random.choice([True, False])
    
    # Seleccionar nombre según género
    if es_masculino:
        nombre = random.choice(NOMBRES_MASCULINOS)
        sexo = "Hombre"
    else:
        nombre = random.choice(NOMBRES_FEMENINOS)
        sexo = "Mujer"
    
    # Generar datos básicos
    apellido = random.choice(APELLIDOS)
    cedula = generar_cedula_unica()
    fecha_nacimiento = generar_fecha_nacimiento()
    telefono = generar_telefono()
    fecha_registro = generar_fecha_registro()
    
    # Calcular edad
    edad = (date.today() - fecha_nacimiento).days // 365
    
    # Generar datos específicos del sistema
    unidad = random.choice(UNIDADES_ISEPOL)
    dedo_registrado = random.choice(DEDOS)
    registrado_por = random.choice(USUARIOS_REGISTRADORES)
    aparato_id = random.choice([4, 5, 6, 7, 8, 9, 10])  # IDs reales de aparatos_biometricos
    uid_k40 = random.randint(1000, 9999)
    observaciones = random.choice(OBSERVACIONES_POSIBLES)
    
    return {
        'nombre': nombre,
        'apellido': apellido,
        'cedula': cedula,
        'fecha_nacimiento': fecha_nacimiento,
        'telefono': telefono,
        'fecha_registro': fecha_registro,
        'usuario_registrador': random.choice([1, 4, 5, 6, 8]),  # IDs reales de usuarios
        'edad': edad,
        'unidad': unidad,
        'dedo_registrado': dedo_registrado,
        'registrado_por': registrado_por,
        'aparato_id': aparato_id,
        'uid_k40': uid_k40,
        'huella_dactilar': generar_huella_dactilar_ficticia(),
        'observaciones': observaciones,
        'sexo': sexo,
        'usuario_ultima_edicion': registrado_por,
        'fecha_ultima_edicion': fecha_registro
    }

def insertar_postulante_individual(cursor, postulante):
    """Insertar un postulante individual con manejo de errores"""
    try:
        cursor.execute("""
            INSERT INTO postulantes (
                nombre, apellido, cedula, fecha_nacimiento, telefono, 
                fecha_registro, usuario_registrador, edad, unidad, 
                dedo_registrado, registrado_por, aparato_id, uid_k40, 
                huella_dactilar, observaciones, sexo, usuario_ultima_edicion, 
                fecha_ultima_edicion
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """, (
            postulante['nombre'], postulante['apellido'], postulante['cedula'],
            postulante['fecha_nacimiento'], postulante['telefono'], postulante['fecha_registro'],
            postulante['usuario_registrador'], postulante['edad'], postulante['unidad'],
            postulante['dedo_registrado'], postulante['registrado_por'], postulante['aparato_id'],
            postulante['uid_k40'], postulante['huella_dactilar'], postulante['observaciones'],
            postulante['sexo'], postulante['usuario_ultima_edicion'], postulante['fecha_ultima_edicion']
        ))
        return True
    except Exception as e:
        logger.error(f"Error al insertar postulante {postulante['cedula']}: {e}")
        return False

def crear_aparatos_biometricos(cursor):
    """Verificar aparatos biométricos existentes"""
    try:
        # Verificar aparatos existentes
        cursor.execute("SELECT id, nombre FROM aparatos_biometricos ORDER BY id")
        aparatos = cursor.fetchall()
        
        if aparatos:
            logger.info(f"✅ Aparatos biométricos disponibles: {len(aparatos)}")
            for id_aparato, nombre in aparatos:
                logger.info(f"   • ID {id_aparato}: {nombre}")
        else:
            logger.warning("⚠️ No hay aparatos biométricos registrados")
            
    except Exception as e:
        logger.error(f"Error al verificar aparatos biométricos: {e}")

def crear_usuarios_ficticios(cursor):
    """Verificar usuarios existentes"""
    try:
        # Verificar usuarios existentes
        cursor.execute("SELECT id, usuario, nombre, apellido FROM usuarios ORDER BY id")
        usuarios = cursor.fetchall()
        
        if usuarios:
            logger.info(f"✅ Usuarios disponibles: {len(usuarios)}")
            for id_usuario, usuario, nombre, apellido in usuarios:
                logger.info(f"   • ID {id_usuario}: {usuario} ({nombre} {apellido})")
        else:
            logger.warning("⚠️ No hay usuarios registrados")
            
    except Exception as e:
        logger.error(f"Error al verificar usuarios: {e}")

def cargar_cedulas_existentes(cursor):
    """Cargar cédulas existentes en la base de datos para evitar duplicados"""
    try:
        cursor.execute("SELECT cedula FROM postulantes")
        cedulas_existentes = {row[0] for row in cursor.fetchall()}
        cedulas_generadas.update(cedulas_existentes)
        logger.info(f"✅ Cargadas {len(cedulas_existentes)} cédulas existentes")
    except Exception as e:
        logger.error(f"Error al cargar cédulas existentes: {e}")

def insercion_masiva(cantidad=10000):
    """Realizar inserción masiva de datos ficticios"""
    try:
        logger.info(f"🚀 Iniciando inserción masiva de {cantidad:,} postulantes...")
        
        conn = connect_db()
        if not conn:
            logger.error("❌ No se pudo conectar a la base de datos")
            return False
        
        cursor = conn.cursor()
        
        # Verificar aparatos y usuarios existentes
        crear_aparatos_biometricos(cursor)
        crear_usuarios_ficticios(cursor)
        
        # Cargar cédulas existentes para evitar duplicados
        cargar_cedulas_existentes(cursor)
        
        # Contador de registros insertados
        insertados = 0
        errores = 0
        
        # Insertar uno por uno para mejor control de errores
        for i in range(cantidad):
            try:
                postulante = generar_postulante_ficticio()
                
                if insertar_postulante_individual(cursor, postulante):
                    insertados += 1
                    # Commit individual para evitar pérdida de datos
                    conn.commit()
                else:
                    errores += 1
                    # Rollback en caso de error
                    conn.rollback()
                
                # Mostrar progreso cada 100 registros
                if (i + 1) % 100 == 0:
                    logger.info(f"📊 Progreso: {i + 1:,}/{cantidad:,} registros procesados")
                
            except Exception as e:
                logger.error(f"Error al generar/insertar postulante {i + 1}: {e}")
                errores += 1
                conn.rollback()
        
        # Mostrar resumen final
        logger.info(f"✅ Inserción masiva completada:")
        logger.info(f"   📈 Registros insertados: {insertados:,}")
        logger.info(f"   ❌ Errores: {errores:,}")
        if insertados + errores > 0:
            logger.info(f"   📊 Tasa de éxito: {(insertados/(insertados+errores)*100):.2f}%")
        
        # Verificar total en base de datos
        cursor.execute("SELECT COUNT(*) FROM postulantes")
        total_bd = cursor.fetchone()[0]
        logger.info(f"   🗄️ Total en base de datos: {total_bd:,}")
        
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en inserción masiva: {e}")
        return False

def main():
    """Función principal"""
    print("=" * 60)
    print("🚀 SISTEMA QUIRA - INSERCIÓN MASIVA DE DATOS FICTICIOS")
    print("=" * 60)
    
    try:
        cantidad = int(input("Ingrese la cantidad de registros a generar (default: 10000): ") or "10000")
        
        if cantidad <= 0:
            print("❌ La cantidad debe ser mayor a 0")
            return
        
        print(f"\n📋 Configuración:")
        print(f"   • Cantidad de registros: {cantidad:,}")
        print(f"   • Base de datos: sistema_postulantes")
        print(f"   • Usuario: postgres")
        print(f"   • Host: localhost")
        
        confirmacion = input("\n¿Desea continuar? (s/N): ").lower()
        if confirmacion not in ['s', 'si', 'sí', 'y', 'yes']:
            print("❌ Operación cancelada")
            return
        
        print("\n🔄 Iniciando proceso...")
        if insercion_masiva(cantidad):
            print("\n✅ ¡Inserción masiva completada exitosamente!")
        else:
            print("\n❌ Error en la inserción masiva")
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Operación interrumpida por el usuario")
    except ValueError:
        print("❌ Cantidad inválida")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    main()
