"""
puntuacion.py
-------------
Guarda el historial de partidas jugadas en un archivo JSON (una lista de
diccionarios). No hace falta base de datos para esto.
"""

import json
from pathlib import Path

ARCHIVO_HISTORIAL = Path("historial.json")


def interpretar_resultado(pilas_finales: int) -> str:
    """
    Traduce la cantidad de pilas finales a una frase. Basado en la escala
    que armaste: 2 pilas es el mínimo posible (partida perfecta absoluta),
    y de ahí para arriba se va poniendo cada vez menos glorioso.
    """
    if pilas_finales <= 2:
        return "🏆 IMPOSIBLE. Partida perfecta absoluta — de esas que se cuentan pocas veces en la vida."
    elif pilas_finales <= 4:
        return "✨ Juego perfecto. Un resultado espectacular."
    elif pilas_finales <= 7:
        return "🎯 Excelente. Muy buena lectura del tablero."
    elif pilas_finales <= 10:
        return "👍 Bueno. Nada mal."
    else:
        return "😅 Bueno... confío en que te irá mejor la próxima vez."


def formatear_duracion(segundos: int) -> str:
    """Convierte una cantidad de segundos a un texto tipo '3m 42s'."""
    minutos, segundos_restantes = divmod(segundos, 60)
    if minutos:
        return f"{minutos}m {segundos_restantes}s"
    return f"{segundos_restantes}s"


def guardar_puntaje(nombre_jugador: str, resumen: dict) -> None:
    """
    Agrega una partida al historial y lo guarda en disco.
    `resumen` es el dict que devuelve Juego.obtener_resumen(): trae
    fecha, duracion_segundos, movimientos, pilas_finales y puntaje.
    """
    historial = cargar_historial()
    entrada = {"jugador": nombre_jugador, **resumen}
    historial.append(entrada)
    with open(ARCHIVO_HISTORIAL, "w", encoding="utf-8") as archivo:
        json.dump(historial, archivo, indent=2, ensure_ascii=False)


def cargar_historial() -> list[dict]:
    """Devuelve la lista de partidas jugadas hasta ahora (o vacía si no hay)."""
    if ARCHIVO_HISTORIAL.exists():
        with open(ARCHIVO_HISTORIAL, "r", encoding="utf-8") as archivo:
            return json.load(archivo)
    return []


def mejor_puntaje() -> dict | None:
    """Devuelve la partida con mayor puntaje (mejor resultado), si hay alguna."""
    historial = cargar_historial()
    if not historial:
        return None
    return max(historial, key=lambda partida: partida["puntaje"])
