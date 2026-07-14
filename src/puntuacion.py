"""
puntuacion.py
-------------
Guarda el historial de partidas jugadas en un archivo JSON (una lista de
diccionarios). No hace falta base de datos para esto.
"""

import json

from recursos import ruta_base_datos_usuario

ARCHIVO_HISTORIAL = ruta_base_datos_usuario() / "historial.json"


def clave_orden_record(partida: dict) -> tuple:
    """Orden único de rankings: puntaje, tiempo, movimientos y fecha."""
    return (
        -int(partida.get("puntaje", partida.get("score", 0))),
        int(partida.get("duracion_segundos", 0)),
        int(partida.get("movimientos", 0)),
        partida.get("fecha", partida.get("played_at", "")),
    )


def ordenar_records(partidas: list[dict]) -> list[dict]:
    return sorted(partidas, key=clave_orden_record)


def indice_jugador(partidas: list[dict]) -> int:
    """Rating local basado en las cinco mejores partidas, no en partidas flojas."""
    mejores = ordenar_records(partidas)[:5]
    return sum(int(partida.get("puntaje", partida.get("score", 0))) for partida in mejores)


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
    return ordenar_records(historial)[0]


def es_nuevo_record(resumen: dict) -> bool:
    """Indica si el resultado supera el mejor récord local anterior."""
    mejor = mejor_puntaje()
    return mejor is None or clave_orden_record(resumen) < clave_orden_record(mejor)
