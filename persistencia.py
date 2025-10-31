import json

def cargar_datos(archivo="base_ventas.json"):
    try:
        with open(archivo, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {"ventas": []}

def guardar_datos(base, archivo="base_ventas.json"):
    with open(archivo, "w", encoding="utf-8") as file:
        json.dump(base, file, ensure_ascii=False, indent=4)
