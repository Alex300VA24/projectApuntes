import flet as ft
from datetime import datetime, timedelta
import json
from pathlib import Path
import threading
import time
from plyer import notification

class Tarea:
    """Modelo de datos para una tarea"""
    def __init__(self, id, titulo, descripcion, fecha_creacion, proyecto_id, 
                 completada=False, fecha_programada=None, notificacion_enviada=False, prioridad="Media"):
        self.id = id
        self.titulo = titulo
        self.descripcion = descripcion
        self.fecha_creacion = fecha_creacion
        self.proyecto_id = proyecto_id
        self.completada = completada
        self.fecha_programada = fecha_programada
        self.notificacion_enviada = notificacion_enviada
        self.prioridad = prioridad
    
    def to_dict(self):
        return {
            'id': self.id,
            'titulo': self.titulo,
            'descripcion': self.descripcion,
            'fecha_creacion': self.fecha_creacion,
            'proyecto_id': self.proyecto_id,
            'completada': self.completada,
            'fecha_programada': self.fecha_programada,
            'notificacion_enviada': self.notificacion_enviada,
            'prioridad': self.prioridad
        }
    
    @staticmethod
    def from_dict(data):
        return Tarea(
            data['id'],
            data['titulo'],
            data['descripcion'],
            data['fecha_creacion'],
            data['proyecto_id'],
            data.get('completada', False),
            data.get('fecha_programada'),
            data.get('notificacion_enviada', False),
            data.get('prioridad', 'Media')
        )

class Proyecto:
    """Modelo de datos para un proyecto"""
    def __init__(self, id, nombre, descripcion, color, fecha_creacion):
        self.id = id
        self.nombre = nombre
        self.descripcion = descripcion
        self.color = color
        self.fecha_creacion = fecha_creacion
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'color': self.color,
            'fecha_creacion': self.fecha_creacion
        }
    
    @staticmethod
    def from_dict(data):
        return Proyecto(
            data['id'],
            data['nombre'],
            data['descripcion'],
            data['color'],
            data['fecha_creacion']
        )

class GestorDatos:
    """Gestor de proyectos y tareas con persistencia en JSON"""
    def __init__(self):
        self.archivo_proyectos = Path("proyectos.json")
        self.archivo_tareas = Path("tareas.json")
        self.proyectos = []
        self.tareas = []
        self.cargar_datos()
    
    def cargar_datos(self):
        if self.archivo_proyectos.exists():
            with open(self.archivo_proyectos, 'r', encoding='utf-8') as f:
                datos = json.load(f)
                self.proyectos = [Proyecto.from_dict(p) for p in datos]
        
        if self.archivo_tareas.exists():
            with open(self.archivo_tareas, 'r', encoding='utf-8') as f:
                datos = json.load(f)
                self.tareas = [Tarea.from_dict(t) for t in datos]
    
    def guardar_proyectos(self):
        with open(self.archivo_proyectos, 'w', encoding='utf-8') as f:
            json.dump([p.to_dict() for p in self.proyectos], f, indent=2, ensure_ascii=False)
    
    def guardar_tareas(self):
        with open(self.archivo_tareas, 'w', encoding='utf-8') as f:
            json.dump([t.to_dict() for t in self.tareas], f, indent=2, ensure_ascii=False)
    
    # Métodos de Proyectos
    def agregar_proyecto(self, nombre, descripcion, color):
        nuevo_id = max([p.id for p in self.proyectos], default=0) + 1
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
        proyecto = Proyecto(nuevo_id, nombre, descripcion, color, fecha)
        self.proyectos.append(proyecto)
        self.guardar_proyectos()
        return proyecto
    
    def actualizar_proyecto(self, id, nombre, descripcion, color):
        for proyecto in self.proyectos:
            if proyecto.id == id:
                proyecto.nombre = nombre
                proyecto.descripcion = descripcion
                proyecto.color = color
                self.guardar_proyectos()
                return True
        return False
    
    def eliminar_proyecto(self, id):
        # Eliminar también todas las tareas del proyecto
        self.tareas = [t for t in self.tareas if t.proyecto_id != id]
        self.proyectos = [p for p in self.proyectos if p.id != id]
        self.guardar_proyectos()
        self.guardar_tareas()
    
    def obtener_proyecto(self, id):
        for proyecto in self.proyectos:
            if proyecto.id == id:
                return proyecto
        return None
    
    # Métodos de Tareas
    def agregar_tarea(self, titulo, descripcion, proyecto_id, fecha_programada=None, prioridad="Media"):
        nuevo_id = max([t.id for t in self.tareas], default=0) + 1
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
        tarea = Tarea(nuevo_id, titulo, descripcion, fecha, proyecto_id, 
                     fecha_programada=fecha_programada, prioridad=prioridad)
        self.tareas.append(tarea)
        self.guardar_tareas()
        return tarea
    
    def actualizar_tarea(self, id, titulo, descripcion, completada, fecha_programada=None, prioridad="Media"):
        for tarea in self.tareas:
            if tarea.id == id:
                tarea.titulo = titulo
                tarea.descripcion = descripcion
                tarea.completada = completada
                tarea.fecha_programada = fecha_programada
                tarea.prioridad = prioridad
                self.guardar_tareas()
                return True
        return False
    
    def eliminar_tarea(self, id):
        self.tareas = [t for t in self.tareas if t.id != id]
        self.guardar_tareas()
    
    def toggle_completada(self, id):
        for tarea in self.tareas:
            if tarea.id == id:
                tarea.completada = not tarea.completada
                self.guardar_tareas()
                return tarea.completada
        return None
    
    def obtener_tareas_proyecto(self, proyecto_id):
        return [t for t in self.tareas if t.proyecto_id == proyecto_id]
    
    def marcar_notificacion_enviada(self, tarea_id):
        for tarea in self.tareas:
            if tarea.id == tarea_id:
                tarea.notificacion_enviada = True
                self.guardar_tareas()
                break

class NotificadorTareas:
    """Servicio de notificaciones en segundo plano"""
    def __init__(self, gestor):
        self.gestor = gestor
        self.activo = True
        self.thread = None
    
    def iniciar(self):
        self.thread = threading.Thread(target=self._verificar_notificaciones, daemon=True)
        self.thread.start()
    
    def detener(self):
        self.activo = False
    
    def _verificar_notificaciones(self):
        while self.activo:
            try:
                ahora = datetime.now()
                for tarea in self.gestor.tareas:
                    if (not tarea.completada and 
                        tarea.fecha_programada and 
                        not tarea.notificacion_enviada):
                        
                        fecha_prog = datetime.strptime(tarea.fecha_programada, "%Y-%m-%d %H:%M")
                        
                        # Notificar si ya pasó la hora o está dentro de los próximos 5 minutos
                        if ahora >= fecha_prog or (fecha_prog - ahora).total_seconds() <= 300:
                            proyecto = self.gestor.obtener_proyecto(tarea.proyecto_id)
                            proyecto_nombre = proyecto.nombre if proyecto else "Sin proyecto"
                            
                            try:
                                notification.notify(
                                    title=f"⏰ Recordatorio: {tarea.titulo}",
                                    message=f"Proyecto: {proyecto_nombre}\n{tarea.descripcion[:100]}",
                                    app_name="Agenda de Proyectos",
                                    timeout=10
                                )
                                self.gestor.marcar_notificacion_enviada(tarea.id)
                            except Exception as e:
                                print(f"Error al enviar notificación: {e}")
                
                time.sleep(60)  # Verificar cada minuto
            except Exception as e:
                print(f"Error en verificación de notificaciones: {e}")
                time.sleep(60)

def main(page: ft.Page):
    page.title = "Agenda de Proyectos y Tareas"
    page.window_width = 1100
    page.window_height = 750
    page.padding = 20
    page.theme_mode = ft.ThemeMode.LIGHT
    
    gestor = GestorDatos()
    notificador = NotificadorTareas(gestor)
    notificador.iniciar()
    
    # Estado de la aplicación
    proyecto_seleccionado = None
    tarea_editando = None
    proyecto_editando = None
    
    # Colores disponibles para proyectos
    COLORES_PROYECTO = {
        "Azul": ft.Colors.BLUE_400,
        "Verde": ft.Colors.GREEN_400,
        "Naranja": ft.Colors.ORANGE_400,
        "Rojo": ft.Colors.RED_400,
        "Morado": ft.Colors.PURPLE_400,
        "Cyan": ft.Colors.CYAN_400,
        "Rosa": ft.Colors.PINK_400,
        "Amarillo": ft.Colors.AMBER_400,
    }
    
    # ========== FORMULARIOS DE PROYECTO ==========
    proyecto_nombre_field = ft.TextField(label="Nombre del proyecto", filled=True, expand=True)
    proyecto_desc_field = ft.TextField(label="Descripción", multiline=True, min_lines=2, filled=True)
    proyecto_color_dropdown = ft.Dropdown(
        label="Color",
        options=[ft.dropdown.Option(c) for c in COLORES_PROYECTO.keys()],
        value="Azul",
        filled=True
    )
    
    def cerrar_dialogo_proyecto(e):
        dialogo_proyecto.open = False
        page.update()
    
    def guardar_proyecto(e):
        if not proyecto_nombre_field.value or not proyecto_nombre_field.value.strip():
            proyecto_nombre_field.error_text = "El nombre es requerido"
            page.update()
            return
        
        proyecto_nombre_field.error_text = None
        
        if proyecto_editando:
            gestor.actualizar_proyecto(
                proyecto_editando.id,
                proyecto_nombre_field.value.strip(),
                proyecto_desc_field.value.strip() if proyecto_desc_field.value else "",
                proyecto_color_dropdown.value
            )
        else:
            gestor.agregar_proyecto(
                proyecto_nombre_field.value.strip(),
                proyecto_desc_field.value.strip() if proyecto_desc_field.value else "",
                proyecto_color_dropdown.value
            )
        
        cerrar_dialogo_proyecto(e)
        actualizar_proyectos()
    
    dialogo_proyecto = ft.AlertDialog(
        modal=True,
        title=ft.Text("Nuevo Proyecto"),
        content=ft.Container(
            content=ft.Column([
                proyecto_nombre_field,
                proyecto_desc_field,
                proyecto_color_dropdown,
            ], tight=True, spacing=15),
            # Ancho flexible pero limitado
            width=min(500, page.window_width - 50) if page.window_width else 500,
        ),
        actions=[
            ft.TextButton("Cancelar", on_click=cerrar_dialogo_proyecto),
            ft.FilledButton("Guardar", on_click=guardar_proyecto),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    page.overlay.append(dialogo_proyecto)
    
    def abrir_formulario_proyecto(proyecto=None):
        nonlocal proyecto_editando
        proyecto_editando = proyecto
        
        # Actualizar ancho al abrir
        if dialogo_proyecto.content:
             dialogo_proyecto.content.width = min(500, page.window_width - 50) if page.window_width else 500

        if proyecto:
            dialogo_proyecto.title = ft.Text("Editar Proyecto")
            proyecto_nombre_field.value = proyecto.nombre
            proyecto_desc_field.value = proyecto.descripcion
            proyecto_color_dropdown.value = proyecto.color
        else:
            dialogo_proyecto.title = ft.Text("Nuevo Proyecto")
            proyecto_nombre_field.value = ""
            proyecto_desc_field.value = ""
            proyecto_color_dropdown.value = "Azul"
        
        proyecto_nombre_field.error_text = None
        dialogo_proyecto.open = True
        page.update()
    
    # ========== FORMULARIOS DE TAREA ==========
    tarea_titulo_field = ft.TextField(label="Título de la tarea", filled=True, expand=True)
    tarea_desc_field = ft.TextField(label="Descripción", multiline=True, min_lines=3, filled=True)
    tarea_prioridad_dropdown = ft.Dropdown(
        label="Prioridad",
        options=[
            ft.dropdown.Option("Alta"),
            ft.dropdown.Option("Media"),
            ft.dropdown.Option("Baja"),
        ],
        value="Media",
        filled=True,
        width=150
    )
    
    # Campos para fecha y hora programada
    fecha_programada_field = ft.TextField(
        label="Fecha (YYYY-MM-DD)",
        hint_text="2025-01-15",
        filled=True,
        width=200
    )
    hora_programada_field = ft.TextField(
        label="Hora (HH:MM)",
        hint_text="14:30",
        filled=True,
        width=150
    )
    
    def cerrar_dialogo_tarea(e):
        dialogo_tarea.open = False
        page.update()
    
    def guardar_tarea(e):
        if not tarea_titulo_field.value or not tarea_titulo_field.value.strip():
            tarea_titulo_field.error_text = "El título es requerido"
            page.update()
            return
        
        if not proyecto_seleccionado:
            return
        
        tarea_titulo_field.error_text = None
        
        # Construir fecha programada si hay valores
        fecha_prog = None
        if fecha_programada_field.value and hora_programada_field.value:
            try:
                fecha_prog = f"{fecha_programada_field.value.strip()} {hora_programada_field.value.strip()}"
                # Validar formato
                datetime.strptime(fecha_prog, "%Y-%m-%d %H:%M")
            except:
                fecha_programada_field.error_text = "Formato inválido"
                page.update()
                return
        
        if tarea_editando:
            gestor.actualizar_tarea(
                tarea_editando.id,
                tarea_titulo_field.value.strip(),
                tarea_desc_field.value.strip() if tarea_desc_field.value else "",
                tarea_editando.completada,
                fecha_prog,
                tarea_prioridad_dropdown.value
            )
        else:
            gestor.agregar_tarea(
                tarea_titulo_field.value.strip(),
                tarea_desc_field.value.strip() if tarea_desc_field.value else "",
                proyecto_seleccionado.id,
                fecha_prog,
                tarea_prioridad_dropdown.value
            )
        
        cerrar_dialogo_tarea(e)
        actualizar_tareas()
    
    dialogo_tarea = ft.AlertDialog(
        modal=True,
        title=ft.Text("Nueva Tarea"),
        content=ft.Container(
            content=ft.Column([
                tarea_titulo_field,
                tarea_desc_field,
                tarea_prioridad_dropdown,
                ft.Text("Programar notificación (opcional):", size=12, weight=ft.FontWeight.BOLD),
                ft.Row([fecha_programada_field, hora_programada_field], spacing=10, wrap=True),
            ], tight=True, spacing=15, scroll=ft.ScrollMode.AUTO),
            width=min(550, page.window_width - 50) if page.window_width else 550,
            # Altura máxima para evitar desbordamiento vertical en móviles apaisados
            height=min(600, page.window_height - 100) if page.window_height else None, 
        ),
        actions=[
            ft.TextButton("Cancelar", on_click=cerrar_dialogo_tarea),
            ft.FilledButton("Guardar", on_click=guardar_tarea),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    page.overlay.append(dialogo_tarea)
    
    def abrir_formulario_tarea(tarea=None):
        nonlocal tarea_editando
        tarea_editando = tarea

        # Actualizar dimensiones al abrir
        if dialogo_tarea.content:
            dialogo_tarea.content.width = min(550, page.window_width - 50) if page.window_width else 550
            if page.window_height:
                dialogo_tarea.content.height = min(600, page.window_height - 100)
        
        if tarea:
            dialogo_tarea.title = ft.Text("Editar Tarea")
            tarea_titulo_field.value = tarea.titulo
            tarea_desc_field.value = tarea.descripcion
            
            if tarea.fecha_programada:
                partes = tarea.fecha_programada.split(" ")
                fecha_programada_field.value = partes[0]
                hora_programada_field.value = partes[1] if len(partes) > 1 else ""
            else:
                fecha_programada_field.value = ""
                hora_programada_field.value = ""
        else:
            dialogo_tarea.title = ft.Text("Nueva Tarea")
            tarea_titulo_field.value = ""
            tarea_desc_field.value = ""
            fecha_programada_field.value = ""
            hora_programada_field.value = ""
        
        tarea_titulo_field.error_text = None
        fecha_programada_field.error_text = None
        dialogo_tarea.open = True
        page.update()
    
    # ========== VISTA DE PROYECTOS ==========
    def crear_tarjeta_proyecto(proyecto):
        tareas_proyecto = gestor.obtener_tareas_proyecto(proyecto.id)
        total = len(tareas_proyecto)
        completadas = sum(1 for t in tareas_proyecto if t.completada)
        progreso = completadas / total if total > 0 else 0
        
        def seleccionar_proyecto(e):
            nonlocal proyecto_seleccionado
            proyecto_seleccionado = proyecto
            actualizar_tareas()
            actualizar_layout()
        
        def editar_proyecto(e):
            abrir_formulario_proyecto(proyecto)
        
        def eliminar_proyecto(e):
            def confirmar(e):
                gestor.eliminar_proyecto(proyecto.id)
                dialogo_conf.open = False
                nonlocal proyecto_seleccionado
                if proyecto_seleccionado and proyecto_seleccionado.id == proyecto.id:
                    proyecto_seleccionado = None
                actualizar_proyectos()
                actualizar_tareas()
            
            def cancelar(e):
                dialogo_conf.open = False
                page.update()
            
            dialogo_conf = ft.AlertDialog(
                modal=True,
                title=ft.Text("Confirmar eliminación"),
                content=ft.Text(f"¿Eliminar el proyecto '{proyecto.nombre}' y todas sus tareas?"),
                actions=[
                    ft.TextButton("Cancelar", on_click=cancelar),
                    ft.FilledButton("Eliminar", on_click=confirmar,
                                   style=ft.ButtonStyle(bgcolor=ft.Colors.RED_400)),
                ],
            )
            page.overlay.append(dialogo_conf)
            dialogo_conf.open = True
            page.update()
        
        es_seleccionado = proyecto_seleccionado and proyecto_seleccionado.id == proyecto.id
        color_proyecto = COLORES_PROYECTO.get(proyecto.color, ft.Colors.BLUE_400)
        
        return ft.GestureDetector(
            content=ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Container(
                                width=4, 
                                height=40, 
                                bgcolor=color_proyecto, 
                                border_radius=2
                            ),
                            ft.Column([
                                ft.Text(proyecto.nombre, size=15, weight=ft.FontWeight.BOLD),
                                ft.Row([
                                    ft.Text(f"{completadas}/{total}", size=11, color=ft.Colors.GREY_600, weight=ft.FontWeight.BOLD),
                                    ft.Text(f"tareas completadas", size=11, color=ft.Colors.GREY_600),
                                ], spacing=4),
                                ft.ProgressBar(
                                    value=progreso, 
                                    color=color_proyecto, 
                                    bgcolor=ft.Colors.GREY_200, 
                                    height=4,
                                    border_radius=2
                                ),
                            ], spacing=4, expand=True),
                            ft.Column([
                                ft.IconButton(icon=ft.Icons.EDIT, icon_size=18, on_click=editar_proyecto, tooltip="Editar"),
                                ft.IconButton(icon=ft.Icons.DELETE, icon_size=18, 
                                            icon_color=ft.Colors.RED_400, on_click=eliminar_proyecto, tooltip="Eliminar"),
                            ], spacing=0, alignment=ft.MainAxisAlignment.CENTER),
                        ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    ], spacing=5),
                    padding=12,
                    bgcolor=ft.Colors.BLUE_50 if es_seleccionado else ft.Colors.WHITE,
                    border=ft.border.all(2, color_proyecto) if es_seleccionado else ft.border.all(1, ft.Colors.TRANSPARENT),
                    border_radius=8,
                ),
                elevation=4 if es_seleccionado else 1,
            ),
            on_tap=seleccionar_proyecto,
        )
    
    lista_proyectos = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO)
    
    def actualizar_proyectos():
        lista_proyectos.controls.clear()
        
        if not gestor.proyectos:
            lista_proyectos.controls.append(
                ft.Container(
                    content=ft.Text("No hay proyectos", size=12, color=ft.Colors.GREY_500),
                    padding=20,
                )
            )
        else:
            for proyecto in sorted(gestor.proyectos, key=lambda p: -p.id):
                lista_proyectos.controls.append(crear_tarjeta_proyecto(proyecto))
        
        page.update()
    
    # ========== VISTA DE TAREAS ==========
    def crear_tarjeta_tarea(tarea):
        def toggle_check(e):
            gestor.toggle_completada(tarea.id)
            actualizar_tareas()
            actualizar_proyectos()
        
        def editar_click(e):
            abrir_formulario_tarea(tarea)
        
        def eliminar_click(e):
            def confirmar(e):
                gestor.eliminar_tarea(tarea.id)
                dialogo_conf.open = False
                actualizar_tareas()
                actualizar_proyectos()
            
            def cancelar(e):
                dialogo_conf.open = False
                page.update()
            
            dialogo_conf = ft.AlertDialog(
                modal=True,
                title=ft.Text("Confirmar eliminación"),
                content=ft.Text(f"¿Eliminar la tarea '{tarea.titulo}'?"),
                actions=[
                    ft.TextButton("Cancelar", on_click=cancelar),
                    ft.FilledButton("Eliminar", on_click=confirmar,
                                   style=ft.ButtonStyle(bgcolor=ft.Colors.RED_400)),
                ],
            )
            page.overlay.append(dialogo_conf)
            dialogo_conf.open = True
            page.update()
        
        # Mostrar icono de notificación si está programada
        notif_icon = None
        if tarea.fecha_programada:
            notif_icon = ft.Icon(
                ft.Icons.NOTIFICATIONS_ACTIVE if not tarea.notificacion_enviada else ft.Icons.NOTIFICATIONS,
                size=16,
                color=ft.Colors.ORANGE_400 if not tarea.notificacion_enviada else ft.Colors.GREY_400,
                tooltip=f"Programada: {tarea.fecha_programada}"
            )
        
        return ft.Card(
            content=ft.Container(
                content=ft.Row([
                    ft.Checkbox(value=tarea.completada, on_change=toggle_check),
                    ft.Column([
                        ft.Row([
                            ft.Text(
                                tarea.titulo,
                                size=15,
                                weight=ft.FontWeight.BOLD,
                                expand=True,  # Ocupar espacio disponible
                                max_lines=2,  # Máximo 2 líneas
                                overflow=ft.TextOverflow.ELLIPSIS,  # Puntos suspensivos si excede
                                style=ft.TextStyle(
                                    decoration=ft.TextDecoration.LINE_THROUGH if tarea.completada else None
                                )
                            ),
                            notif_icon if notif_icon else ft.Container(),
                        ], spacing=8),
                        ft.Text(
                            tarea.descripcion if tarea.descripcion else "Sin descripción",
                            size=12,
                            color=ft.Colors.GREY_700,
                            italic=not tarea.descripcion,
                            max_lines=3,  # Limitar líneas de descripción
                            overflow=ft.TextOverflow.ELLIPSIS
                        ),
                        ft.Text(f"Creada: {tarea.fecha_creacion}", size=10, color=ft.Colors.GREY_500),
                    ], spacing=3, expand=True),
                    ft.Row([
                        ft.IconButton(icon=ft.Icons.EDIT, icon_size=20, 
                                    icon_color=ft.Colors.BLUE_400, on_click=editar_click),
                        ft.IconButton(icon=ft.Icons.DELETE, icon_size=20,
                                    icon_color=ft.Colors.RED_400, on_click=eliminar_click),
                    ], spacing=0),
                ], alignment=ft.MainAxisAlignment.START),
                padding=12,
            ),
            elevation=1,
        )
    
    # Botón volver para móvil
    def volver_a_proyectos(e):
        nonlocal proyecto_seleccionado
        proyecto_seleccionado = None
        actualizar_tareas()
        actualizar_layout()

    boton_volver = ft.IconButton(
        icon=ft.Icons.ARROW_BACK,
        icon_size=24,
        on_click=volver_a_proyectos,
        visible=False,
        tooltip="Volver a proyectos"
    )

    # Botón de nueva tarea (creado una vez para poder actualizarlo)
    boton_nueva_tarea = ft.FilledButton(
        "Nueva Tarea",
        icon=ft.Icons.ADD,
        on_click=lambda e: abrir_formulario_tarea(),
        disabled=True,
    )

    # Botón flotante para móvil
    fab_nueva_tarea = ft.FloatingActionButton(
        icon=ft.Icons.ADD,
        on_click=lambda e: abrir_formulario_tarea(),
        bgcolor=ft.Colors.BLUE_400,
    )
    
    # Título dinámico del panel de tareas
    titulo_tareas = ft.Text("Tareas", size=22, weight=ft.FontWeight.BOLD)
    
    lista_tareas = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)
    
    def actualizar_tareas():
        lista_tareas.controls.clear()
        
        if not proyecto_seleccionado:
            boton_nueva_tarea.disabled = True
            titulo_tareas.value = "Tareas"
            lista_tareas.controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Icon(ft.Icons.FOLDER_OPEN, size=80, color=ft.Colors.GREY_300),
                            ft.Text("Selecciona un proyecto", size=16, color=ft.Colors.GREY_500),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=10,
                        alignment=ft.MainAxisAlignment.CENTER,  # centra verticalmente
                    ),
                    expand=True,
                )
            )
        else:
            boton_nueva_tarea.disabled = False
            fab_nueva_tarea.disabled = False # Habilitar FAB también
            titulo_tareas.value = proyecto_seleccionado.nombre
            tareas = gestor.obtener_tareas_proyecto(proyecto_seleccionado.id)
            
            if not tareas:
                lista_tareas.controls.append(
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Icon(ft.Icons.CHECK_CIRCLE, size=80, color=ft.Colors.GREY_300),
                                ft.Text("No hay tareas en este proyecto", size=16, color=ft.Colors.GREY_500),
                                ft.Text("Haz clic en '+' para agregar", size=12, color=ft.Colors.GREY_400),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=8,
                            alignment=ft.MainAxisAlignment.CENTER,  # centra verticalmente
                        ),
                        expand=True,
                    )
                )
            else:
                tareas_ordenadas = sorted(tareas, key=lambda t: (t.completada, -t.id))
                for tarea in tareas_ordenadas:
                    lista_tareas.controls.append(crear_tarjeta_tarea(tarea))
        
        page.update()
    
    # ========== DEFINICIÓN DE PANELES ==========
    
    # Panel izquierdo - Proyectos
    panel_proyectos = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Text("Proyectos", size=20, weight=ft.FontWeight.BOLD),
                ft.IconButton(
                    icon=ft.Icons.ADD,
                    icon_size=20,
                    tooltip="Nuevo Proyecto",
                    on_click=lambda e: abrir_formulario_proyecto(),
                ),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Divider(height=1),
            ft.Container(content=lista_proyectos, expand=True),
        ], spacing=10),
        width=300,
        padding=15,
        bgcolor=ft.Colors.GREY_100,
        border_radius=10,
        expand=False, 
    )
    
    # Panel derecho - Tareas
    panel_tareas = ft.Container(
        content=ft.Column([
            ft.Row([
                boton_volver,
                ft.Icon(ft.Icons.LIST_ALT, size=28, color=ft.Colors.BLUE_400),
                ft.Container(content=titulo_tareas, expand=True), # Título envuelto para expandir
                boton_nueva_tarea,
            ], alignment=ft.MainAxisAlignment.START),
            ft.Divider(height=1),
            ft.Container(content=lista_tareas, expand=True),
        ], spacing=15),
        padding=20,
        expand=True,
    )
    
    # Layout principal
    layout_principal = ft.Row([panel_proyectos, panel_tareas], spacing=15, expand=True)
    page.add(layout_principal)
    
    # ========== LÓGICA RESPONSIVE ==========
    def actualizar_layout(e=None):
        # Definir punto de quiebre para móvil (ej. 800px)
        is_mobile = page.width < 800 if page.width else False
        
        # Actualizar dimensiones de diálogos si están abiertos
        if dialogo_proyecto.open and dialogo_proyecto.content:
             dialogo_proyecto.content.width = min(500, page.window_width - 50) if page.window_width else 500
        
        if dialogo_tarea.open and dialogo_tarea.content:
             dialogo_tarea.content.width = min(550, page.window_width - 50) if page.window_width else 550
             if page.window_height:
                 dialogo_tarea.content.height = min(600, page.window_height - 100)

        if is_mobile:
            # Modo Móvil
            panel_proyectos.width = None 
            panel_proyectos.expand = True
            
            # Ocultar botón "Nueva Tarea" normal en móvil
            boton_nueva_tarea.visible = False
            
            if proyecto_seleccionado:
                panel_proyectos.visible = False
                panel_tareas.visible = True
                boton_volver.visible = True
                # Mostrar FAB en móvil cuando hay proyecto seleccionado
                page.floating_action_button = fab_nueva_tarea
            else:
                panel_proyectos.visible = True
                panel_tareas.visible = False
                boton_volver.visible = False
                page.floating_action_button = None
        else:
            # Modo Desktop
            panel_proyectos.width = 300
            panel_proyectos.expand = False
            panel_proyectos.visible = True
            panel_tareas.visible = True
            boton_volver.visible = False
            # Mostrar botón normal y ocultar FAB
            boton_nueva_tarea.visible = True
            page.floating_action_button = None
            
        page.update()

    page.on_resize = actualizar_layout
    actualizar_layout()
    
    actualizar_proyectos()
    actualizar_tareas()
    
    # Manejar cierre de ventana
    def window_event(e):
        if e.data == "close":
            notificador.detener()
            page.window_destroy()
    
    page.window_prevent_close = True
    page.on_window_event = window_event

ft.run(main)