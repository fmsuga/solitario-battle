"""Preferencias persistentes de la aplicación."""

import json

from recursos import ruta_base_datos_usuario


ARCHIVO_PERFIL = ruta_base_datos_usuario() / "perfil_jugador.json"
VOLUMEN_PREDETERMINADO = 0.70


def _cargar_perfil() -> dict:
    if not ARCHIVO_PERFIL.exists():
        return {}
    try:
        return json.loads(ARCHIVO_PERFIL.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def cargar_volumen() -> float:
    """Devuelve un volumen normalizado entre 0 (silencio) y 1."""
    try:
        return max(0.0, min(float(_cargar_perfil().get("volumen", VOLUMEN_PREDETERMINADO)), 1.0))
    except (TypeError, ValueError):
        return VOLUMEN_PREDETERMINADO


def guardar_volumen(volumen: float) -> None:
    """Guarda el volumen sin perder el identificador anónimo del perfil."""
    perfil = _cargar_perfil()
    perfil["volumen"] = max(0.0, min(float(volumen), 1.0))
    ARCHIVO_PERFIL.write_text(json.dumps(perfil), encoding="utf-8")
