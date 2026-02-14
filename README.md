# 📋 Agenda de Proyectos y Tareas - Google Sheets + Flet

Aplicación de gestión de proyectos y tareas **sincronizada con Google Sheets en la nube**.

## ✨ Características

✅ Sincronización bidireccional con Google Sheets  
✅ Interfaz gráfica moderna con Flet  
✅ Funciona en Windows, Mac y Linux  
✅ Gratis y escalable  
✅ Acceso desde PC y móvil  

---

## ⚡ Instalación Rápida

### Windows (Automático):
```bash
# 1. Haz doble clic en:
setup_sheets.bat

# El script te pedirá la URL de Google Sheets
```

### Mac/Linux (Manual):
```bash
# 1. Instalar dependencias
python instalar_dependencias.py

# 2. Configurar URL (editar config.py o variable de entorno)
export GOOGLE_SHEETS_URL="https://script.google.com/macros/s/TU_ID/exec"

# 3. Ejecutar
python main.py
```

---

## 🚀 Inicio Rápido (5 minutos)

### Paso 1: Crear Google Sheet

1. Ve a [Google Sheets](https://sheets.google.com)
2. Crea nuevo documento: `Ctrl+Alt+N`
3. Nómbralo: **"Agenda de Proyectos"**

### Paso 2: Configurar hojas

En el mismo documento, crea **dos hojas** con estos nombres:

#### Hoja 1: `TAREAS`
Encabezados (primera fila):
```
id | titulo | descripcion | fecha_creacion | proyecto_id | completada | fecha_programada | notificacion_enviada | prioridad
```

#### Hoja 2: `PROYECTOS`
Encabezados (primera fila):
```
id | nombre | descripcion | color | fecha_creacion
```

### Paso 3: Agregar código Google Apps Script

En tu Google Sheet:
1. Menú → **Extensiones → Apps Script**
2. Borra todo lo que hay
3. Copia el contenido de `google_apps_script.js` (este proyecto)
4. Pega en Apps Script
5. Guarda: `Ctrl+S`

### Paso 4: Publicar el script

En Apps Script (pestaña Deployment):
1. **Deploy → New deployment**
2. Type: **Web app**
3. Execute as: Tu email
4. Who has access: **Anyone**
5. Click **Deploy**
6. **Copia la URL** que aparece (necesitarás esto!)

### Paso 5: Configurar el proyecto

**En Windows:**
1. Haz doble clic en `setup_sheets.bat`
2. Pega la URL del deployment anterior
3. ¡Listo!

**En Mac/Linux:**
```bash
python probar_sheets.py
# Sigue las instrucciones
```

### Paso 6: Ejecutar la app

```bash
python main.py
```

¡Tu app está lista! Los cambios se sincronizarán automáticamente con Google Sheets.

---

## 📁 Archivos Necesarios

| Archivo | Propósito |
|---------|-----------|
| `main.py` | Interfaz gráfica (Flet) |
| `cliente_google_sheets.py` | Cliente para conectar con Google Sheets |
| `google_apps_script.js` | Backend en Google Apps Script (copiar a Google) |
| `config.py` | Configuración (URL de Google Sheets) |
| `probar_sheets.py` | Script para verificar conexión |
| `setup_sheets.bat` | Configuración automática (Windows) |

---

## ✅ Verificar que Funciona

### 1️⃣ En la terminal

```bash
$ python probar_sheets.py

[✓] URL configurada
[✓] Conexión exitosa
[✓] Hojas: TAREAS, PROYECTOS
```

Si ves todo ✓, ¡está funcionando!

### 2️⃣ En la app

Abre `main.py` y verifica que:
- ✅ Se cargan los proyectos
- ✅ Se cargan las tareas
- ✅ Puedes crear proyectos nuevos
- ✅ Puedes crear tareas nuevas

### 3️⃣ En Google Sheets

Abre tu Google Sheet y verifica que:
- ✅ Los datos que agregaste en la app aparecen

---

## 🔧 ¿Problemas Comunes?

### "Error 401 - Unauthorized"
- **Causa**: URL incorrecto o sin publicar
- **Solución**: Verifica que copiaste toda la URL y que hiciste Deploy

### "No se conecta"
- **Causa**: Puede ser error de internet o timeout
- **Solución**: `python probar_sheets.py` para diagnosticar

### "Sheet no encontrada"
- **Causa**: Los nombres de las hojas no están configurados
- **Solución**: Revisa que se llamen exactamente `TAREAS` y `PROYECTOS`

---

## 🎯 Próximos Pasos

### ¿Quieres sincronización en tiempo real?

Si necesitas cambios más rápidos (<1 segundo), podés cambiar a **FastAPI local**.

Revisa: [MIGRAR_A_FASTAPI.md](MIGRAR_A_FASTAPI.md) para instrucciones detalladas.

### Ventajas de FastAPI:
✅ Sincronización tiempo real (WebSocket)  
✅ Control total del backend  
✅ Sin límites de velocidad  

### Desventajas:
❌ Requiere mantener el servidor corriendo  
❌ Más complejo de configurar en móvil  

---

## 📚 Documentación

- [GOOGLE_SHEETS_SETUP.md](GOOGLE_SHEETS_SETUP.md) - Guía detallada de Google Sheets
- [EMPEZAR_AQUI_SHEETS.md](EMPEZAR_AQUI_SHEETS.md) - Resumen super rápido
- [MIGRAR_A_FASTAPI.md](MIGRAR_A_FASTAPI.md) - Cómo cambiar a backend propio

---

## 📦 Requirements

```
flet>=0.0.1
google-api-python-client>=2.96.0
google-auth-oauthlib>=1.2.0
google-auth-httplib2>=0.2.0
python-dotenv>=1.0.0
requests>=2.31.0
```

Instalar: `pip install -r requirements.txt`

---

**¿Preguntas?** Revisa la [documentación detallada](GOOGLE_SHEETS_SETUP.md) o el [manual de migración a FastAPI](MIGRAR_A_FASTAPI.md).
