import flet as ft
from datetime import date, datetime

from definiciones import (Venta, SistemaVentas, estado_plataformas, estado_logistica, tipo_logistica, plataforma)


def main(page: ft.Page):
    page.title = "Sistema de Ventas"
    page.window_maximized = True
    page.theme_mode = "light"
    page.horizontal_alignment = "center"
    page.vertical_alignment = "start"
    sistema = SistemaVentas()


    notificador = ft.Container(
    visible=False,
    bgcolor="#bbbbbb",
    border_radius=6,
    padding=10,
    content=ft.Row(
        [
            ft.Icon(name="check_circle"),
            ft.Text("", size=14, weight=ft.FontWeight.BOLD, expand=True),
            ft.IconButton(icon="close", on_click=lambda e: ocultar_mensaje()),
        ],
        alignment=ft.MainAxisAlignment.START,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    ),
)

    def mostrar_mensaje(texto, color="#bbbbbb", icono="check_circle"):
        notificador.bgcolor = color
        notificador.content.controls[0].name = icono
        notificador.content.controls[1].value = texto
        notificador.visible = True
        page.update()

    def ocultar_mensaje():
        notificador.visible = False
        page.update()

#Campos del formulario--

    tf_id = ft.TextField(label="ID de Venta*", width=150, label_style=ft.TextStyle(size=14))

    dd_plataforma = ft.Dropdown(
        label="Plataforma*",
        hint_text="Seleccioná...",
        value=None,
        options=[ft.dropdown.Option(p) for p in plataforma],
        width=200, label_style=ft.TextStyle(size=14),
    )

    tf_nombre = ft.TextField(label="Nombre*", width=200, label_style=ft.TextStyle(size=14))
    tf_apellido = ft.TextField(label="Apellido*", width=200, label_style=ft.TextStyle(size=14))


    tf_fecha = ft.TextField(
        label="Fecha (YYYY-MM-DD)*",
        width=260,
        label_style=ft.TextStyle(size=14),
        read_only=False,
        suffix_icon="calendar_month",
    )


    def validar_fecha(e):
        v = (tf_fecha.value or "").strip()
        if not v:
            tf_fecha.error_text = None
            page.update()
            return

        try:
            dt = datetime.strptime(v, "%Y-%m-%d").date()
            hoy = date.today()

            if dt > hoy:
                tf_fecha.error_text = "No se permiten fechas futuras."
            else:
                tf_fecha.error_text = None

        except ValueError:
            tf_fecha.error_text = "Formato: YYYY-MM-DD"

        page.update()

    tf_fecha.on_change = validar_fecha

    dd_estado_plataforma = ft.Dropdown(
        label="Estado plataforma (opcional)",
        hint_text="Seleccioná...",
        value=None,
        options=[ft.dropdown.Option(e) for e in estado_plataformas],
        width=240, label_style=ft.TextStyle(size=14),
    )

    dd_estado_logistica = ft.Dropdown(
        label="Estado logística (opcional)",
        hint_text="Seleccioná...",
        value=None,
        options=[ft.dropdown.Option(e) for e in estado_logistica],
        width=255, label_style=ft.TextStyle(size=14),
    )
    
    dd_tipo_logistica = ft.Dropdown(
        label="Tipo logística (opcional)",
        hint_text="Seleccioná...",
        value=None,
        options=[ft.dropdown.Option(e) for e in tipo_logistica],
        width=240, label_style=ft.TextStyle(size=14),
    )

    dd_plataforma_header = ft.Dropdown(
        hint_text="Plataforma",
        options=[ft.dropdown.Option(p) for p in plataforma],
        width=160,
        value=None,
        on_change=lambda e: poblar_tabla(),
        border=ft.InputBorder.NONE,)

    dd_plataforma_header.on_change = lambda e: poblar_tabla()

    dd_estado_plataforma_header = ft.Dropdown(
        hint_text="Estado plataformas",
        options=[ft.dropdown.Option("(Vacío)")] + [ft.dropdown.Option(e) for e in estado_plataformas],
        width=180,
        value=None,
        on_change=lambda e: poblar_tabla(),
        border=ft.InputBorder.NONE,)

    dd_estado_logistica_header = ft.Dropdown(
        hint_text="Estado logística",
        options=[ft.dropdown.Option("(Vacío)")] + [ft.dropdown.Option(e) for e in estado_logistica],
        width=180,
        value=None,
        on_change=lambda e: poblar_tabla(),
        border=ft.InputBorder.NONE,)

    dd_tipo_logistica_header = ft.Dropdown(
        hint_text="Tipo logística",
        options=[ft.dropdown.Option("(Vacío)")] + [ft.dropdown.Option(e) for e in tipo_logistica],
        width=180,
        value=None,
        on_change=lambda e: poblar_tabla(),
        border=ft.InputBorder.NONE,)

    tf_filtro_id = ft.TextField(
        hint_text="ID",
        on_change=lambda e: poblar_tabla(),
        border=ft.InputBorder.NONE,
        text_size=13,
        content_padding=0,)

    id_header = ft.Container(
        content=tf_filtro_id,
        width=120,
        height=36,
        alignment=ft.alignment.center_left,)

    dd_edit_estado_plataforma = ft.Dropdown(
        label="Estado plataforma",
        hint_text="Seleccioná...",
        options=[ft.dropdown.Option(e) for e in estado_plataformas],
        value=None, width=280,)

    dd_edit_estado_logistica = ft.Dropdown(
        label="Estado logística",
        hint_text="Seleccioná...",
        options=[ft.dropdown.Option(e) for e in estado_logistica],
        value=None, width=280,)

    dd_edit_tipo_logistica = ft.Dropdown(
        label="Tipo logística",
        hint_text="Seleccioná...",
        options=[ft.dropdown.Option(e) for e in tipo_logistica],
        value=None, width=280,)

    dlg_editar = ft.AlertDialog(
        modal=True,
        title=ft.Text("Editar estados"),
        content=ft.Column(
            [dd_edit_estado_plataforma, dd_edit_estado_logistica, dd_edit_tipo_logistica],
            tight=True,
            spacing=10,
        ),
        actions=[
            ft.TextButton("Cancelar", on_click=lambda e: cerrar_editor()),
            ft.ElevatedButton("Guardar cambios", icon="save", on_click=lambda e: guardar_editor()),
        ],
    )

    venta_en_edicion = {"id": None}

    def _find_venta_by_id(_id):
        
        for x in sistema.obtener_ventas():
            if str(x.id_venta) == str(_id):
                return x
        return None

    def abrir_editor(id_venta: str):
        mostrar_mensaje(f"abrir_editor -> id={id_venta}")  # ping
        v = _find_venta_by_id(id_venta)

        if not v:
            mostrar_mensaje("❌ Venta no encontrada.", color="#bbbbbb", icono="error_outline")
            return

        venta_en_edicion["id"] = str(id_venta)

        # precargar valores (pueden ser None)
        dd_edit_estado_plataforma.value = v.estado_plataforma
        dd_edit_estado_logistica.value = v.estado_logistica
        dd_edit_tipo_logistica.value = v.tipo_logistica

        dlg_editar.title = ft.Text(f"Editar estados - ID {venta_en_edicion['id']}")
        try:
            # Flet moderno
            page.open(dlg_editar)
            mostrar_mensaje("Editor abierto.")
        except Exception:
            # Flet clásico
            page.dialog = dlg_editar
            dlg_editar.open = True
            page.update()
            mostrar_mensaje("Editor abierto.")

    def cerrar_editor():
        try:
            
            dlg_editar.open = False
            page.close(dlg_editar)
        except Exception:
            
            dlg_editar.open = False
            page.update()

    def guardar_editor():
        v = _find_venta_by_id(venta_en_edicion["id"])
        if not v:
            mostrar_mensaje("❌ Venta no encontrada.", color="#bbbbbb", icono="error_outline")
            return

        try:
            # actualiza sólo lo que el usuario eligió
            if dd_edit_estado_plataforma.value is not None:
                v.actualizar_estado_plataforma(dd_edit_estado_plataforma.value)
            if dd_edit_estado_logistica.value is not None:
                v.actualizar_estado_logistica(dd_edit_estado_logistica.value)
            if dd_edit_tipo_logistica.value is not None:
                v.actualizar_tipo_logistica(dd_edit_tipo_logistica.value)

            sistema._guardar()
            cerrar_editor()
            poblar_tabla()
            mostrar_mensaje("✅ Estados actualizados.")

        except ValueError as ex:    #sin cerrar editor permite corregir.
            
            mostrar_mensaje(f"❌ {ex}", color="#bbbbbb", icono="error_outline")
            page.update()


#Tabla de ventas--
    tabla = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Fecha")),
            ft.DataColumn(label=id_header),
            ft.DataColumn(label=dd_plataforma_header),
            ft.DataColumn(ft.Text("Nombre")),
            ft.DataColumn(ft.Text("Apellido")),
            ft.DataColumn(label=dd_estado_plataforma_header),
            ft.DataColumn(label=dd_estado_logistica_header),
            ft.DataColumn(label=dd_tipo_logistica_header),
            ft.DataColumn(ft.Text("Acciones")),
        ],
        rows=[],
    )
    def _fmt(v):        #deja prolijo el campo fecha

        if v is None or str(v).strip() == "":
            return ""
        return str(v)

    def poblar_tabla():
        tabla.rows.clear()

        ventas = sistema.obtener_ventas()

        try:        #ordena por fecha
            ventas.sort(
                key=lambda v: datetime.strptime((v.fecha or "1900-01-01"), "%Y-%m-%d"),
                reverse=True,
            )
        except Exception:
            pass    #evita crashear si alguna fecha es inválida

        f_id = (tf_filtro_id.value or "")            #filtro por ID
        if f_id:
            ventas = [v for v in ventas if f_id.lower() in str(v.id_venta or "").lower()]


        f_plat_raw = dd_plataforma_header.value         #filtro plataforma
        f_plat = (f_plat_raw or "")

        if f_plat:
            ventas = [
                v for v in ventas
                if (v.plataforma or "")== f_plat]


        f_estado_raw = dd_estado_plataforma_header.value        #filtro por estado de plat
        f_estado = (f_estado_raw or "")
        if f_estado:
            if f_estado == "(Vacío)":
                ventas = [v for v in ventas if not (v.estado_plataforma or "")]
            else:
                ventas = [v for v in ventas if (v.estado_plataforma or "") == f_estado]


        f_log_raw = dd_estado_logistica_header.value        #filtro por estado log.
        f_log = (f_log_raw or "")
        if f_log:
            if f_log == "(Vacío)":
                ventas = [v for v in ventas if not (v.estado_logistica or "")]
            else:
                ventas = [v for v in ventas if (v.estado_logistica or "") == f_log]


        f_tipo_raw = dd_tipo_logistica_header.value        #filtro por tipo log
        f_tipo = (f_tipo_raw or "")

        if f_tipo:
            if f_tipo == "(Vacío)":
                ventas = [v for v in ventas if not (v.tipo_logistica or "")]
            else:
                ventas = [
                    v for v in ventas
                    if (v.tipo_logistica or "") == f_tipo
                ]

        for ven in ventas:          #rellena la tabla
            tabla.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(_fmt(ven.fecha))),
                        ft.DataCell(ft.Text(_fmt(ven.id_venta))),
                        ft.DataCell(ft.Text(_fmt(ven.plataforma))),
                        ft.DataCell(ft.Text(_fmt(ven.nombre))),
                        ft.DataCell(ft.Text(_fmt(ven.apellido))),
                        ft.DataCell(ft.Text(_fmt(ven.estado_plataforma))),
                        ft.DataCell(ft.Text(_fmt(ven.estado_logistica))),
                        ft.DataCell(ft.Text(_fmt(ven.tipo_logistica))),
                        ft.DataCell(
                            ft.IconButton(
                                icon="edit",
                                tooltip="Editar estados",
                                on_click=lambda e, _id=str(ven.id_venta): abrir_editor(_id),
                            )
                        ),
                    ]
                )
            )

        if not ventas:
            mostrar_mensaje("🔎 No se encontraron ventas con los filtros aplicados.", color="#bbbbbb", icono="info_outline")
        else:
            notificador.visible = False  # oculta mensaje anterior si existía

        tabla.update()      #refresca
        page.update()


    def limpiar_filtros(e=None):
        # Resetear todos los dropdowns
        for dd in [
            dd_plataforma_header,
            dd_estado_plataforma_header,
            dd_estado_logistica_header,
            dd_tipo_logistica_header,]:
            dd.value = None
            dd.update()

        # Resetear filtro por ID
        tf_filtro_id.value = ""
        if getattr(tf_filtro_id, "page", None):
            tf_filtro_id.update()

        poblar_tabla()
        page.update()
        mostrar_mensaje("Filtros limpiados.")


    # Acciones
    def limpiar_form():

        tf_id.value = ""
        tf_id.error_text = None

        tf_nombre.value = ""
        tf_nombre.error_text = None

        tf_apellido.value = ""
        tf_apellido.error_text = None

        tf_fecha.value = ""
        tf_fecha.error_text = None

        for dd in [dd_plataforma, dd_estado_plataforma, dd_estado_logistica, dd_tipo_logistica]:    #no funciona..
            dd.value = None          # sin selección
            dd.error_text = None
            dd.update()              # refresco inmediato del control

        page.update()


    def guardar_click(e):
        try:
            errores = False

            if not tf_id.value or not str(tf_id.value):
                tf_id.error_text = "Ingresá un ID."
                errores = True
            else:
                tf_id.error_text = None

            if not dd_plataforma.value:
                dd_plataforma.error_text = "Seleccioná una plataforma."
                errores = True
            else:
                dd_plataforma.error_text = None

            if not tf_nombre.value or not str(tf_nombre.value):
                tf_nombre.error_text = "Ingresá un nombre."
                errores = True
            else:
                tf_nombre.error_text = None

            if not tf_apellido.value or not str(tf_apellido.value):
                tf_apellido.error_text = "Ingresá un apellido."
                errores = True
            else:
                tf_apellido.error_text = None

            if not tf_fecha.value or not str(tf_fecha.value).strip():
                tf_fecha.error_text = "Ingresá la fecha (YYYY-MM-DD)."
                errores = True

            if tf_fecha.error_text:
                errores = True

            if errores:
                page.update()
                mostrar_mensaje("❌ Completá los campos obligatorios.", color="#bbbbbb", icono="error_outline")
                return

            venta = Venta(      #si pasa todos los filtros, guarda
                id_venta=tf_id.value,
                plataforma=dd_plataforma.value,
                nombre=tf_nombre.value,
                apellido=tf_apellido.value,
                fecha=tf_fecha.value,
                estado_plataforma=dd_estado_plataforma.value,
                estado_logistica=dd_estado_logistica.value,
                tipo_logistica=dd_tipo_logistica.value,
            )

            sistema.agregar_venta(venta)
            mostrar_mensaje("✅ Venta agregada correctamente.")

            limpiar_form()
            poblar_tabla()

        except Exception as ex:
            mostrar_mensaje(f"❌ {str(ex)}", color="#bbbbbb", icono="error_outline")

#Botones--
    btn_guardar = ft.ElevatedButton("Guardar", icon="save", on_click=guardar_click)
    btn_limpiar = ft.OutlinedButton("Limpiar", icon="cancel", on_click=lambda _: limpiar_form())

#Layout--
    formulario = ft.Column(
        [
            ft.Text("Registrar nueva venta", size=19, weight=ft.FontWeight.BOLD),
            ft.Row([tf_id, dd_plataforma, tf_nombre, tf_apellido, tf_fecha], wrap=True, spacing=10),
            ft.Row([dd_estado_plataforma, dd_estado_logistica, dd_tipo_logistica], wrap=True, spacing=10),
            ft.Row([btn_guardar, btn_limpiar], spacing=10),
        ],
        spacing=10,
    )

    page.add(
        notificador,
        formulario,
        ft.Divider(),
        ft.Row(
            [ft.Text("Ventas cargadas", size=18, weight=ft.FontWeight.BOLD, expand=True),
                ft.ElevatedButton(
                    "Limpiar filtros",
                    icon="cleaning_services",
                    on_click=limpiar_filtros,
                    bgcolor="#E0E0E0",
                    color="black",),],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),

        tabla,
    )

    # Carga inicial desde JSON
    poblar_tabla()


ft.app(target=main)