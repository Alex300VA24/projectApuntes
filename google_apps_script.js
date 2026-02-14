/**
 * GOOGLE APPS SCRIPT - Agenda de Proyectos
 * 
 * Pasos de configuración:
 * 1. Crear nueva Google Sheet vacía
 * 2. Copiar este código en Apps Script (Extensiones > Apps Script)
 * 3. Crear los siguientes apartados:
 *    - Hoja "TAREAS" con columnas: id, titulo, descripcion, fecha_creacion, proyecto_id, completada, fecha_programada, notificacion_enviada, prioridad
 *    - Hoja "PROYECTOS" con columnas: id, nombre, descripcion, color, fecha_creacion
 * 4. Ejecutar function doGet() una vez
 * 5. Deploy > New deployment > Web app
 *    - Execute as: Tu usuario
 *    - Who has access: Anyone (para testing)
 * 6. Copiar URL del deployment y usarlo como GOOGLE_SHEETS_URL en cliente
 * 7. ¡Listo! Tu app ahora usa Google Sheets como backend
 */

// Configuración
const SHEET_TAREAS = "TAREAS";
const SHEET_PROYECTOS = "PROYECTOS";
const SPREADSHEET_ID = SpreadsheetApp.getActiveSpreadsheet().getId();

// ========== UTILIDADES ==========

function log(msg) {
  console.log("[" + new Date().toLocaleTimeString() + "] " + msg);
}

function getOrCreateSheet(name) {
  let sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(name);
  if (!sheet) {
    sheet = SpreadsheetApp.getActiveSpreadsheet().insertSheet(name);
  }
  return sheet;
}

function rowToObject(row, headers) {
  let obj = {};
  for (let i = 0; i < headers.length; i++) {
    obj[headers[i]] = row[i];
  }
  return obj;
}

function objectToRow(obj, headers) {
  return headers.map(h => obj[h] || "");
}

// ========== TAREAS CRUD ==========

function getTareas() {
  const sheet = getOrCreateSheet(SHEET_TAREAS);
  const data = sheet.getDataRange().getValues();
  
  if (data.length < 2) return [];
  
  const headers = data[0];
  const tareas = [];
  
  for (let i = 1; i < data.length; i++) {
    const tarea = rowToObject(data[i], headers);
    if (tarea.id) tareas.push(tarea);
  }
  
  return tareas;
}

function crearTarea(tarea) {
  const sheet = getOrCreateSheet(SHEET_TAREAS);
  const data = sheet.getDataRange().getValues();
  
  // Si la hoja está vacía, crear headers
  if (data.length === 0) {
    const headers = ["id", "titulo", "descripcion", "fecha_creacion", "proyecto_id", "completada", "fecha_programada", "notificacion_enviada", "prioridad"];
    sheet.appendRow(headers);
  }
  
  // Obtener headers
  const headers = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
  
  // Agregar fila
  const row = objectToRow(tarea, headers);
  sheet.appendRow(row);
  
  log("Tarea creada: " + tarea.titulo);
  return tarea;
}

function actualizarTarea(tarea_id, tarea) {
  const sheet = getOrCreateSheet(SHEET_TAREAS);
  const data = sheet.getDataRange().getValues();
  
  if (data.length < 2) return null;
  
  const headers = data[0];
  
  // Buscar la fila
  for (let i = 1; i < data.length; i++) {
    if (data[i][0] == tarea_id) {
      const row = objectToRow(tarea, headers);
      sheet.getRange(i + 1, 1, 1, headers.length).setValues([row]);
      
      log("Tarea actualizada: " + tarea.titulo);
      return tarea;
    }
  }
  
  return null;
}

function eliminarTarea(tarea_id) {
  const sheet = getOrCreateSheet(SHEET_TAREAS);
  const data = sheet.getDataRange().getValues();
  
  if (data.length < 2) return false;
  
  // Buscar la fila
  for (let i = 1; i < data.length; i++) {
    if (data[i][0] == tarea_id) {
      sheet.deleteRow(i + 1);
      log("Tarea eliminada: " + tarea_id);
      return true;
    }
  }
  
  return false;
}

// ========== PROYECTOS CRUD ==========

function getProyectos() {
  const sheet = getOrCreateSheet(SHEET_PROYECTOS);
  const data = sheet.getDataRange().getValues();
  
  if (data.length < 2) return [];
  
  const headers = data[0];
  const proyectos = [];
  
  for (let i = 1; i < data.length; i++) {
    const proyecto = rowToObject(data[i], headers);
    if (proyecto.id) proyectos.push(proyecto);
  }
  
  return proyectos;
}

function crearProyecto(proyecto) {
  const sheet = getOrCreateSheet(SHEET_PROYECTOS);
  const data = sheet.getDataRange().getValues();
  
  // Si la hoja está vacía, crear headers
  if (data.length === 0) {
    const headers = ["id", "nombre", "descripcion", "color", "fecha_creacion"];
    sheet.appendRow(headers);
  }
  
  // Obtener headers
  const headers = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
  
  // Agregar fila
  const row = objectToRow(proyecto, headers);
  sheet.appendRow(row);
  
  log("Proyecto creado: " + proyecto.nombre);
  return proyecto;
}

function actualizarProyecto(proyecto_id, proyecto) {
  const sheet = getOrCreateSheet(SHEET_PROYECTOS);
  const data = sheet.getDataRange().getValues();
  
  if (data.length < 2) return null;
  
  const headers = data[0];
  
  // Buscar la fila
  for (let i = 1; i < data.length; i++) {
    if (data[i][0] == proyecto_id) {
      const row = objectToRow(proyecto, headers);
      sheet.getRange(i + 1, 1, 1, headers.length).setValues([row]);
      
      log("Proyecto actualizado: " + proyecto.nombre);
      return proyecto;
    }
  }
  
  return null;
}

function eliminarProyecto(proyecto_id) {
  const sheet = getOrCreateSheet(SHEET_PROYECTOS);
  const data = sheet.getDataRange().getValues();
  
  if (data.length < 2) return false;
  
  // Buscar la fila
  for (let i = 1; i < data.length; i++) {
    if (data[i][0] == proyecto_id) {
      sheet.deleteRow(i + 1);
      log("Proyecto eliminado: " + proyecto_id);
      
      // También eliminar tareas del proyecto
      const tareas = getTareas();
      for (let tarea of tareas) {
        if (tarea.proyecto_id == proyecto_id) {
          eliminarTarea(tarea.id);
        }
      }
      
      return true;
    }
  }
  
  return false;
}

// ========== API REST ==========

function doGet(e) {
  // Manejar caso donde e es undefined (ejecución manual)
  e = e || {};
  e.parameter = e.parameter || {};
  const path = e.parameter.path || "";
  
  try {
    if (path === "tareas") {
      return ContentService
        .createTextOutput(JSON.stringify({ tareas: getTareas() }))
        .setMimeType(ContentService.MimeType.JSON);
    } else if (path === "proyectos") {
      return ContentService
        .createTextOutput(JSON.stringify({ proyectos: getProyectos() }))
        .setMimeType(ContentService.MimeType.JSON);
    } else if (path === "salud") {
      return ContentService
        .createTextOutput(JSON.stringify({ estado: "ok" }))
        .setMimeType(ContentService.MimeType.JSON);
    } else {
      return ContentService
        .createTextOutput(JSON.stringify({
          nombre: "Backend Google Sheets",
          version: "1.0",
          endpoints: {
            "GET?path=tareas": "Lista de tareas",
            "GET?path=proyectos": "Lista de proyectos",
            "GET?path=salud": "Health check"
          }
        }))
        .setMimeType(ContentService.MimeType.JSON);
    }
  } catch (error) {
    return ContentService
      .createTextOutput(JSON.stringify({ error: error.toString() }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

function doPost(e) {
  // Manejar caso donde e es undefined (ejecución manual)
  e = e || {};
  e.parameter = e.parameter || {};
  e.postData = e.postData || {};
  const path = e.parameter.path || "";
  const data = e.postData.contents ? JSON.parse(e.postData.contents) : {};
  
  try {
    if (path === "tareas") {
      return ContentService
        .createTextOutput(JSON.stringify(crearTarea(data)))
        .setMimeType(ContentService.MimeType.JSON);
    } else if (path === "proyectos") {
      return ContentService
        .createTextOutput(JSON.stringify(crearProyecto(data)))
        .setMimeType(ContentService.MimeType.JSON);
    }
  } catch (error) {
    return ContentService
      .createTextOutput(JSON.stringify({ error: error.toString() }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

function doPut(e) {
  // Manejar caso donde e es undefined (ejecución manual)
  e = e || {};
  e.parameter = e.parameter || {};
  e.postData = e.postData || {};
  const path = e.parameter.path || "";
  const id = e.parameter.id;
  const data = e.postData.contents ? JSON.parse(e.postData.contents) : {};
  
  try {
    if (path === "tareas") {
      return ContentService
        .createTextOutput(JSON.stringify(actualizarTarea(id, data)))
        .setMimeType(ContentService.MimeType.JSON);
    } else if (path === "proyectos") {
      return ContentService
        .createTextOutput(JSON.stringify(actualizarProyecto(id, data)))
        .setMimeType(ContentService.MimeType.JSON);
    }
  } catch (error) {
    return ContentService
      .createTextOutput(JSON.stringify({ error: error.toString() }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

function doDelete(e) {
  // Manejar caso donde e es undefined (ejecuci\u00f3n manual)
  e = e || {};
  e.parameter = e.parameter || {};
  const path = e.parameter.path || "";
  const id = e.parameter.id;
  
  try {
    if (path === "tareas") {
      return ContentService
        .createTextOutput(JSON.stringify({ ok: eliminarTarea(id) }))
        .setMimeType(ContentService.MimeType.JSON);
    } else if (path === "proyectos") {
      return ContentService
        .createTextOutput(JSON.stringify({ ok: eliminarProyecto(id) }))
        .setMimeType(ContentService.MimeType.JSON);
    }
  } catch (error) {
    return ContentService
      .createTextOutput(JSON.stringify({ error: error.toString() }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}
