"""Preferencias persistentes de la aplicación."""

import json

from recursos import ruta_base_datos_usuario


ARCHIVO_PERFIL = ruta_base_datos_usuario() / "perfil_jugador.json"
VOLUMEN_PREDETERMINADO = 0.70
IDIOMA_PREDETERMINADO = "es"


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


def cargar_idioma() -> str:
    """Devuelve el idioma de la interfaz, con español como opción segura."""
    idioma = _cargar_perfil().get("idioma", IDIOMA_PREDETERMINADO)
    return idioma if idioma in {"es", "en"} else IDIOMA_PREDETERMINADO


def guardar_idioma(idioma: str) -> None:
    """Guarda el idioma sin sobrescribir el resto de preferencias del perfil."""
    if idioma not in {"es", "en"}:
        raise ValueError("Idioma no soportado")
    perfil = _cargar_perfil()
    perfil["idioma"] = idioma
    ARCHIVO_PERFIL.write_text(json.dumps(perfil), encoding="utf-8")
