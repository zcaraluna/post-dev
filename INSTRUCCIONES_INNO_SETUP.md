# 📦 INSTRUCCIONES PARA CREAR INSTALADOR CON INNO SETUP

## **🎯 REQUISITOS PREVIOS**

### **1. Descargar Inno Setup**
- **Descarga:** https://jrsoftware.org/isdl.php
- **Versión recomendada:** 6.2.2 o superior
- **Instalación:** Ejecutar el instalador y seguir las instrucciones

### **2. Preparar los archivos**
- ✅ Asegúrate de que la carpeta `dist/Sistema_Postulantes` existe
- ✅ Verifica que `quira.ico` esté en la raíz del proyecto
- ✅ Confirma que todos los archivos necesarios están presentes

## **🛠️ PASOS PARA CREAR EL INSTALADOR**

### **Paso 1: Abrir Inno Setup Compiler**
1. Busca "Inno Setup Compiler" en el menú de inicio
2. Ábrelo como administrador (recomendado)

### **Paso 2: Cargar el script**
1. En Inno Setup, ve a **File → Open**
2. Navega hasta tu proyecto y selecciona `Sistema_Postulantes_Setup.iss`
3. Haz clic en **Abrir**

### **Paso 3: Compilar el instalador**
1. Ve a **Build → Compile** (o presiona `Ctrl+F9`)
2. Espera a que termine la compilación
3. El instalador se creará en la carpeta `Output/`

## **📁 ESTRUCTURA DEL INSTALADOR**

### **Archivos incluidos:**
```
Sistema_Postulantes_Setup_v1.0.exe
├── Sistema_Postulantes.exe (ejecutable principal)
├── quira.png (logo institucional)
├── instituto.png (imagen adicional)
├── zkteco_connector_v2.py (módulo ZKTeco)
├── gestion_zkteco.py (gestión ZKTeco)
├── _internal/ (todas las dependencias)
└── install_info.txt (información de instalación)
```

### **Características del instalador:**
- ✅ **Interfaz en español**
- ✅ **Verificación de requisitos** (Windows 10+, 64-bit)
- ✅ **Accesos directos** (Escritorio, Menú Inicio)
- ✅ **Integración con Windows** (Panel de Control)
- ✅ **Desinstalación limpia**
- ✅ **Icono personalizado** (quira.ico)

## **⚙️ CONFIGURACIÓN PERSONALIZABLE**

### **Cambiar información del desarrollador:**
```pascal
#define MyAppPublisher "Tu Nombre"
#define MyAppURL "https://tu-sitio-web.com"
```

### **Cambiar versión:**
```pascal
#define MyAppVersion "1.1"
```

### **Cambiar nombre del archivo de salida:**
```pascal
OutputBaseFilename=Sistema_Postulantes_Setup_v{#MyAppVersion}
```

### **Agregar archivos adicionales:**
```pascal
Source: "ruta\al\archivo.ext"; DestDir: "{app}"; Flags: ignoreversion
```

## **🔧 OPCIONES AVANZADAS**

### **Instalación silenciosa:**
```bash
Sistema_Postulantes_Setup_v1.0.exe /SILENT
```

### **Instalación con parámetros:**
```bash
Sistema_Postulantes_Setup_v1.0.exe /DIR="C:\MiCarpeta" /TASKS="desktopicon"
```

### **Desinstalación silenciosa:**
```bash
"C:\Program Files\Sistema de Postulantes\unins000.exe" /SILENT
```

## **📋 VERIFICACIÓN POST-INSTALACIÓN**

### **Después de instalar, verifica:**
1. ✅ El programa se ejecuta correctamente
2. ✅ Los accesos directos funcionan
3. ✅ Aparece en "Agregar o quitar programas"
4. ✅ La desinstalación funciona correctamente
5. ✅ No hay errores en el registro de Windows

## **🚨 SOLUCIÓN DE PROBLEMAS**

### **Error: "Cannot find source file"**
- Verifica que la carpeta `dist/Sistema_Postulantes` existe
- Confirma que todos los archivos están en su lugar

### **Error: "Setup requires Windows 10 or later"**
- El script está configurado para Windows 10+
- Si necesitas soporte para versiones anteriores, modifica `MinVersion`

### **Error: "Setup requires 64-bit Windows"**
- El sistema está compilado para 64-bit
- No es compatible con Windows de 32-bit

### **El instalador no se crea**
- Verifica que Inno Setup esté instalado correctamente
- Ejecuta como administrador
- Revisa los logs de compilación

## **📞 SOPORTE TÉCNICO**

### **Para problemas con Inno Setup:**
- **Documentación oficial:** https://jrsoftware.org/ishelp/
- **Foro de la comunidad:** https://groups.google.com/g/innosetup

### **Para problemas con el script:**
- Contacta al desarrollador: Guillermo Recalde a.k.a. 's1mple'
- Revisa los logs de compilación en Inno Setup

## **🎉 ¡LISTO!**

Una vez que tengas el archivo `Sistema_Postulantes_Setup_v1.0.exe`, puedes distribuirlo a tus usuarios. El instalador se encargará de todo automáticamente.

**¡Tu sistema ahora tiene una instalación profesional!** 🚀
