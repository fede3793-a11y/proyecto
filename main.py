import flet as ft
from datetime import date, datetime

from definiciones import (Venta, SistemaVentas, estado_plataformas, estado_logistica, tipo_logistica, plataforma)


def main(page: ft.Page):
    page.title = "Sistema de Gestión de Ventas"
    page.window_maximized = True
    page.window_resizable = True
    page.padding = 20
    page.scroll = "auto"

    sistema = SistemaVentas()  # carga JSON -> objetos Venta

    # ---------- CAMPOS DEL FORM ----------
    tf_id = ft.TextField(label="ID de Venta*", width=150, label_style=ft.TextStyle(size=14))

    dd_plataforma = ft.Dropdown(
        label="Plataforma*",
        options=[ft.dropdown.Option(p) for p in plataforma],
        width=200, label_style=ft.TextStyle(size=14)
    )

    tf_nombre = ft.TextField(label="Nombre*", width=200, label_style=ft.TextStyle(size=14))
    tf_apellido = ft.TextField(label="Apellido*", width=200, label_style=ft.TextStyle(size=14))

    # ---- DatePicker (popup) ----
    hoy = date.today()
    dp = ft.DatePicker(first_date=date(2025, 1, 1), last_date=hoy, value=hoy)
    page.overlay.append(dp)

    # Campo visible de fecha (permite escribir y/o abrir el picker)
    tf_fecha = ft.TextField(
        label="Fecha (YYYY-MM-DD)*",
        width=260, label_style=ft.TextStyle(size=14),
        read_only=False,          # permitir tipeo manual
        suffix_icon="calendar_month",
    )
    tf_fecha.on_tap = lambda e: dp.pick_date()

    # Validación "live" del formato al escribir
    def validar_fecha_live(e):
        v = (tf_fecha.value or "").strip()
        if not v:
            tf_fecha.error_text = None
            page.update()
            return

        try:
            dt = datetime.strptime(v, "%Y-%m-%d").date()
            hoy = date.today()

            # Solo controlás que no sea futura
            if dt > hoy:
                tf_fecha.error_text = "No se permiten fechas futuras."
            else:
                tf_fecha.error_text = None

        except ValueError:
            tf_fecha.error_text = "Formato: YYYY-MM-DD"

        page.update()

    tf_fecha.on_change = validar_fecha_live

    # Cuando el usuario elige en el DatePicker, reflejar en el TextField
    def on_date_changed(e):
        if dp.value:
            tf_fecha.value = dp.value.strftime("%Y-%m-%d")
            tf_fecha.error_text = None
            page.update()

    dp.on_change = on_date_changed

    dd_estado_plataforma = ft.Dropdown(
        label="Estado plataforma (opcional)",
        options=[ft.dropdown.Option(e) for e in estado_plataformas],
        width=240, label_style=ft.TextStyle(size=14)
    )
    dd_estado_logistica = ft.Dropdown(
        label="Estado logística (opcional)",
        options=[ft.dropdown.Option(e) for e in estado_logistica],
        width=255, label_style=ft.TextStyle(size=14)
    )
    dd_tipo_logistica = ft.Dropdown(
        label="Tipo logística (opcional)",
        options=[ft.dropdown.Option(e) for e in tipo_logistica],
        width=240, label_style=ft.TextStyle(size=14)
    )

    # ---------- TABLA DE VENTAS ----------
    tabla = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("Plataforma")),
            ft.DataColumn(ft.Text("Nombre")),
            ft.DataColumn(ft.Text("Apellido")),
            ft.DataColumn(ft.Text("Fecha")),
            ft.DataColumn(ft.Text("Estado plataformas")),
            ft.DataColumn(ft.Text("Estado logística")),
            ft.DataColumn(ft.Text("Tipo logística")),
        ],
        rows=[],
    )

    def _fmt(v):
        return v if v is not None else ""

    def poblar_tabla():
        tabla.rows.clear()
        for ven in sistema.obtener_ventas():
            tabla.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(_fmt(ven.id_venta))),
                        ft.DataCell(ft.Text(_fmt(ven.plataforma))),
                        ft.DataCell(ft.Text(_fmt(ven.nombre))),
                        ft.DataCell(ft.Text(_fmt(ven.apellido))),
                        ft.DataCell(ft.Text(_fmt(ven.fecha))),
                        ft.DataCell(ft.Text(_fmt(ven.estado_plataforma))),
                        ft.DataCell(ft.Text(_fmt(ven.estado_logistica))),
                        ft.DataCell(ft.Text(_fmt(ven.tipo_logistica))),
                    ]
                )
            )
        page.update()

    # ---------- ACCIONES ----------
    def limpiar_form():
        tf_id.value = ""
        dd_plataforma.value = ""
        tf_nombre.value = ""
        tf_apellido.value = ""
        tf_fecha.value = ""
        tf_fecha.error_text = None

        for dd in [dd_estado_plataforma, dd_estado_logistica, dd_tipo_logistica]:
            dd.value = ""
            dd.update()

        page.update()

    def guardar_click(e):
        try:
            venta = Venta(
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
            page.snack_bar = ft.SnackBar(ft.Text("✅ Venta agregada correctamente."))
            page.snack_bar.open = True
            limpiar_form()
            poblar_tabla()  # refrescar listado
        except Exception as ex:
            page.dialog = ft.AlertDialog(
                title=ft.Text("Error"),
                content=ft.Text(str(ex)),
                actions=[
                    ft.TextButton(
                        "OK",
                        on_click=lambda _:
                            (setattr(page.dialog, "open", False), page.update()),
                    )
                ],
            )
            page.dialog.open = True
            page.update()

    # ---------- BOTONES ----------
    btn_guardar = ft.ElevatedButton("Guardar", icon="save", on_click=guardar_click)
    btn_limpiar = ft.OutlinedButton("Limpiar", icon="cancel", on_click=lambda _: limpiar_form())

    # ---------- LAYOUT ----------
    formulario = ft.Column(
        [
            ft.Text("Registrar nueva venta", size=20, weight=ft.FontWeight.BOLD),
            ft.Row([tf_id, dd_plataforma, tf_nombre, tf_apellido, tf_fecha], wrap=True, spacing=10),
            ft.Row([dd_estado_plataforma, dd_estado_logistica, dd_tipo_logistica], wrap=True, spacing=10),
            ft.Row([btn_guardar, btn_limpiar], spacing=10),
        ],
        spacing=10,
    )

    page.add(
        formulario,
        ft.Divider(),
        ft.Text("Ventas cargadas", size=18, weight=ft.FontWeight.BOLD),
        tabla,
    )

    # Carga inicial desde JSON
    poblar_tabla()


ft.app(target=main)






# page.theme_mode = "light"  # o "dark"
# page.theme = ft.Theme(
#     input_border_radius=8,
#     input_border_color="grey",
# )