# 🖊️ Generador de Documentos Word con Frase Repetida

Este script de Python te permite generar un documento Word con una frase repetida el número de veces que especifiques (por defecto 1000 veces).

## 📋 Características

- ✅ Genera documentos Word (.docx) con formato profesional
- ✅ Permite personalizar la frase a repetir
- ✅ Configurable número de repeticiones
- ✅ Numeración automática de líneas
- ✅ Espaciado para mejor legibilidad
- ✅ Interfaz de usuario amigable
- ✅ Validación de datos de entrada

## 🚀 Instalación

### Opción 1: Instalación automática
```bash
python instalar_word_deps.py
```

### Opción 2: Instalación manual
```bash
pip install python-docx==0.8.11
```

## 📖 Uso

### Ejecutar el script
```bash
python generar_documento_word.py
```

### Proceso de uso

1. **Ejecuta el script** - Se abrirá una interfaz interactiva
2. **Ingresa la frase** - Escribe la frase que quieres repetir
3. **Especifica repeticiones** - Indica cuántas veces repetir (por defecto 1000)
4. **Nombra el archivo** - Elige el nombre del documento (por defecto: documento_frase.docx)
5. **Confirma** - Revisa el resumen y confirma la generación
6. **¡Listo!** - El documento se generará en la misma carpeta

### Ejemplo de uso
```
🖊️  GENERADOR DE DOCUMENTO WORD CON FRASE REPETIDA
============================================================

📝 Ingresa la frase que deseas repetir:
Frase: Hola mundo

🔢 ¿Cuántas veces quieres repetir la frase? (por defecto: 1000)
Número de repeticiones: 100

📁 ¿Qué nombre quieres darle al archivo? (por defecto: documento_frase.docx)
Nombre del archivo: mi_documento

📋 Resumen:
   • Frase: 'Hola mundo'
   • Repeticiones: 100
   • Archivo: mi_documento.docx

¿Proceder con la generación? (s/n): s

🔄 Generando documento...
✅ Documento generado exitosamente: mi_documento.docx
📄 Ubicación: C:\Users\usuario\Documents\mi_documento.docx
📊 Total de frases escritas: 100

🎉 ¡Documento generado exitosamente!
📂 Puedes abrir el archivo: mi_documento.docx
```

## 📄 Estructura del documento generado

El documento incluye:
- **Título** con información del documento
- **Información** de la frase y número de repeticiones
- **Frases numeradas** con formato organizado
- **Espaciado** cada 10 líneas para mejor legibilidad

## 🔧 Personalización

### Modificar el script
Puedes editar `generar_documento_word.py` para:
- Cambiar el formato del documento
- Modificar el espaciado entre líneas
- Agregar estilos personalizados
- Incluir encabezados o pies de página

### Usar como módulo
```python
from generar_documento_word import generar_documento_con_frase

# Generar documento con parámetros específicos
generar_documento_con_frase(
    frase="Mi frase personalizada",
    num_repeticiones=500,
    nombre_archivo="mi_documento.docx"
)
```

## ⚠️ Consideraciones

- **Tamaño del archivo**: Documentos con muchas repeticiones pueden ser grandes
- **Tiempo de generación**: Para miles de repeticiones, puede tomar algunos segundos
- **Memoria**: El script mantiene todo en memoria durante la generación

## 🐛 Solución de problemas

### Error: "No module named 'docx'"
```bash
pip install python-docx==0.8.11
```

### Error de permisos al guardar
- Verifica que tengas permisos de escritura en la carpeta
- Intenta guardar en una ubicación diferente

### Documento no se abre
- Verifica que el archivo se generó correctamente
- Asegúrate de tener Microsoft Word o un visor compatible

## 📝 Archivos incluidos

- `generar_documento_word.py` - Script principal
- `instalar_word_deps.py` - Instalador de dependencias
- `requirements_word.txt` - Lista de dependencias
- `README_GENERADOR_WORD.md` - Este archivo de documentación

## 🤝 Contribuciones

Si encuentras algún problema o tienes sugerencias de mejora, no dudes en reportarlo.

---

**¡Disfruta generando tus documentos con frases repetidas!** 📄✨ 