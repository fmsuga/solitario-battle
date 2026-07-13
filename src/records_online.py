"""Persistencia de récords globales mediante la API REST de Supabase.

No usa una clave secreta ni SDK externo: la publishable key es apropiada para
clientes de escritorio y móviles. Las reglas de acceso viven en la base de
datos, no en esta aplicación.
"""

import json
import uuid
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from recursos import ruta_base_datos_usuario

SUPABASE_URL = "https://tqjpybhwkyrkgrapoxcr.supabase.co"
SUPABASE_PUBLISHABLE_KEY = "sb_publishable_-Y5Qf1qNZ7ix4_H3opfvzA_v_uuUTXs"
TABLA_RECORDS = "leaderboard_entries"
ARCHIVO_PERFIL = ruta_base_datos_usuario() / "perfil_jugador.json"


def obtener_id_dispositivo() -> str:
    """Identificador anónimo y estable para separar los récords personales."""
    if ARCHIVO_PERFIL.exists():
        try:
            return json.loads(ARCHIVO_PERFIL.read_text(encoding="utf-8"))["device_id"]
        except (json.JSONDecodeError, KeyError):
            pass
    perfil = {"device_id": str(uuid.uuid4())}
    ARCHIVO_PERFIL.write_text(json.dumps(perfil), encoding="utf-8")
    return perfil["device_id"]


def _solicitud(metodo: str, ruta: str, datos: dict | None = None) -> list[dict]:
    contenido = json.dumps(datos).encode("utf-8") if datos is not None else None
    encabezados = {
        "apikey": SUPABASE_PUBLISHABLE_KEY,
        "Content-Type": "application/json",
    }
    if metodo == "POST":
        encabezados["Prefer"] = "return=minimal"
    solicitud = Request(f"{SUPABASE_URL}/rest/v1/{ruta}", data=contenido, headers=encabezados, method=metodo)
    with urlopen(solicitud, timeout=4) as respuesta:
        cuerpo = respuesta.read().decode("utf-8")
        return json.loads(cuerpo) if cuerpo else []


def _mensaje_error(error: Exception) -> str:
    if isinstance(error, HTTPError):
        return f"Supabase respondió {error.code}. Ejecutá primero supabase_schema.sql."
    if isinstance(error, URLError):
        return "Sin conexión: se mostrarán tus récords locales."
    return "No se pudieron actualizar los récords mundiales."


def _normalizar_record(record: dict) -> dict:
    """Traduce los nombres de Supabase al formato usado por la interfaz.

    La tabla conserva nombres de columna en inglés, mientras el historial
    local y la UI usan español. Centralizar la conversión evita que un récord
    publicado correctamente falle al mostrarse por claves distintas.
    """
    return {
        "jugador": record.get("player_name", "-"),
        "dificultad": record.get("difficulty", "-"),
        "puntaje": record.get("score", 0),
        "pilas_finales": record.get("piles_finales", 0),
        "movimientos": record.get("moves", 0),
        "duracion_segundos": record.get("duration_seconds", 0),
        "fecha": record.get("played_at", ""),
    }


def enviar_record(nombre: str, resumen: dict) -> str | None:
    """Publica una partida y devuelve un mensaje sólo si no pudo sincronizarse."""
    datos = {
        "device_id": obtener_id_dispositivo(),
        "player_name": nombre[:24],
        "difficulty": resumen["dificultad"],
        "score": resumen["puntaje"],
        "piles_finales": resumen["pilas_finales"],
        "moves": resumen["movimientos"],
        "duration_seconds": resumen["duracion_segundos"],
        "played_at": resumen["fecha"],
    }
    try:
        _solicitud("POST", TABLA_RECORDS, datos)
        return None
    except (HTTPError, URLError, TimeoutError, ValueError) as error:
        return _mensaje_error(error)


def obtener_records_globales(limite: int = 50) -> tuple[list[dict], str | None]:
    consulta = urlencode({
        "select": "player_name,difficulty,score,piles_finales,moves,duration_seconds,played_at",
        "order": "score.desc,duration_seconds.asc,moves.asc",
        "limit": limite,
    })
    try:
        records = _solicitud("GET", f"{TABLA_RECORDS}?{consulta}")
        return [_normalizar_record(record) for record in records], None
    except (HTTPError, URLError, TimeoutError, ValueError) as error:
        return [], _mensaje_error(error)


def obtener_records_personales(limite: int = 50) -> tuple[list[dict], str | None]:
    consulta = urlencode({
        "select": "player_name,difficulty,score,piles_finales,moves,duration_seconds,played_at",
        "device_id": f"eq.{obtener_id_dispositivo()}",
        "order": "score.desc,duration_seconds.asc,moves.asc",
        "limit": limite,
    })
    try:
        records = _solicitud("GET", f"{TABLA_RECORDS}?{consulta}")
        return [_normalizar_record(record) for record in records], None
    except (HTTPError, URLError, TimeoutError, ValueError) as error:
        return [], _mensaje_error(error)
