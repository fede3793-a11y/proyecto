import json
from datetime import date, datetime


estado_plataformas = [
                    "Anulado",
                    "En Proceso",
                    "Completado",
                    "Cancelado",
                    "Reclamo",
                    "Concretado"
                ]

estado_logistica = [
                    "Listo para despachar",
                    "En camino",
                    "Esperando mercadería",
                    "Entregado",
                    "En retorno",
                    "Devuelto",
                    "Siniestro"
                ]

tipo_logistica =   [
                    "Andreani",
                    "Retiro en sucursal",
                    "Correo Argentino",
                    "Logística propia"
                ]

plataforma = [
                "Mercado Libre",
                "Tienda Nube",
                "Tienda BNA+"
            ]


def cargar_datos(archivo="base_ventas.json"):
    try:
        with open(archivo, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {"ventas": []}

def guardar_datos(base, archivo="base_ventas.json"):
    with open(archivo, "w", encoding="utf-8") as file:
        json.dump(base, file, ensure_ascii=False, indent=4)




DATE_FMT = "%Y-%m-%d"       #formato de fecha utilizado en las ventas

def _validar_fecha(s):
    try:
        datetime.strptime(s, DATE_FMT)      
        return s
    except ValueError:
        raise ValueError("La fecha debe tener formato YYYY-MM-DD.")

_PLAT_SET = set(estado_plataformas)     #conjuntos para validación rápida
_LOGI_SET = set(estado_logistica)
_TIPO_SET = set(tipo_logistica)
_PTF_SET = set(plataforma)

class Venta:
    def __init__(self, id_venta, plataforma, nombre, apellido, fecha, estado_plataforma=None, estado_logistica=None, tipo_logistica=None):
        # Datos obligatorios
        if not str(id_venta).strip():
            raise ValueError("El ID es obligatorio.")
        if not str(plataforma).strip():
            raise ValueError("La plataforma es obligatoria.")
        if not str(nombre).strip():
            raise ValueError("El nombre es obligatorio.")
        if not str(apellido).strip():
            raise ValueError("El apellido es obligatorio.")

        self.id_venta = str(id_venta).strip()
        self.plataforma = str(plataforma).strip()
        self.nombre = str(nombre).strip()
        self.apellido = str(apellido).strip()
        self.fecha = _validar_fecha(str(fecha).strip())

        #Datos opcionales con validación
        if estado_plataforma and estado_plataforma not in _PLAT_SET:    #si se proporciona y está en el conjunto válido
            raise ValueError("Estado de plataforma inválido.")
        if estado_logistica and estado_logistica not in _LOGI_SET:
            raise ValueError("Estado de logística inválido.")
        if tipo_logistica and tipo_logistica not in _TIPO_SET:
            raise ValueError("Tipo de logística inválido.")

        self.estado_plataforma = estado_plataforma or None  #si no se proporciona, se establece como None
        self.estado_logistica = estado_logistica or None
        self.tipo_logistica = tipo_logistica or None


    def actualizar_estado_plataforma(self, nuevo_estado):
        if not nuevo_estado:
            self.estado_plataforma = None
            return
        if nuevo_estado not in estado_plataformas:
            raise ValueError("Estado de plataforma inválido.")
        self.estado_plataforma = nuevo_estado

    def actualizar_estado_logistica(self, nuevo_estado):
        if not nuevo_estado:
            self.estado_logistica = None
            return
        if nuevo_estado not in estado_logistica:
            raise ValueError("Estado de logística inválido.")
        self.estado_logistica = nuevo_estado

    def actualizar_tipo_logistica(self, nuevo_tipo):
        if not nuevo_tipo:
            self.tipo_logistica = None
            return
        if nuevo_tipo not in tipo_logistica:
            raise ValueError("Tipo de logística inválido.")
        self.tipo_logistica = nuevo_tipo

    # --- Modificar datos cliente ---
    def modificar_datos_cliente(self, nuevo_nombre=None, nuevo_apellido=None, nueva_fecha=None, nueva_plataforma=None):
        if nuevo_nombre is not None:
            self.nombre = str(nuevo_nombre).strip()
        if nuevo_apellido is not None:
            self.apellido = str(nuevo_apellido).strip()
        if nueva_fecha is not None:
            self.fecha = _validar_fecha(str(nueva_fecha).strip())
        if nueva_plataforma is not None:
            self.plataforma = str(nueva_plataforma).strip()

    # --- Conversión a dict ---
    def to_dict(self):
        d = {
            "id_venta": self.id_venta,
            "plataforma": self.plataforma,
            "nombre": self.nombre,
            "apellido": self.apellido,
            "fecha": self.fecha,
            "estado_plataforma": self.estado_plataforma,
            "estado_logistica": self.estado_logistica,
            "tipo_logistica": self.tipo_logistica,
        }
        return {k: v for k, v in d.items() if v is not None}



class SistemaVentas:
    def __init__(self):
        self.base_datos = cargar_datos()   #carga la base de datos desde el archivo JSON
        self.ventas = [Venta(**v) for v in self.base_datos.get("ventas", [])]  #lista de objetos Venta

    def agregar_venta(self, venta):
        if any(v.id_venta == venta.id_venta for v in self.ventas):
            raise ValueError("Ya existe una venta con ese ID.")
        self.ventas.append(venta)
        self._guardar()

    def _guardar(self):
        datos = {"ventas": [v.to_dict() for v in self.ventas]}
        guardar_datos(datos)

    def obtener_ventas(self):
        return self.ventas
    def buscar_venta_por_id(self, id_venta):
        for venta in self.ventas:
            if venta.id_venta == id_venta:
                return venta
        return None

