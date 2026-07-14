"""
puntuacion.py
-------------
Guarda el historial de partidas jugadas en un archivo JSON (una lista de
diccionarios). No hace falta base de datos para esto.
"""

import json
import statistics
import uuid

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
    registrar_partida_local({"jugador": nombre_jugador, **resumen})


def registrar_partida_local(resumen: dict) -> dict:
    """Persiste una partida finalizada sin depender de un ranking remoto."""
    historial = cargar_historial()
    entrada = {
        "id_partida": resumen.get("id_partida", str(uuid.uuid4())),
        "version_esquema": 1,
        "origen": "local",
        **resumen,
    }
    historial.append(entrada)
    with open(ARCHIVO_HISTORIAL, "w", encoding="utf-8") as archivo:
        json.dump(historial, archivo, indent=2, ensure_ascii=False)
    return entrada


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


def clasificar_resultado(pilas_finales: int) -> str:
    """Clasificación breve, basada sólo en el resultado objetivo."""
    if pilas_finales <= 2:
        return "Perfecta"
    if pilas_finales <= 4:
        return "Excelente"
    if pilas_finales <= 7:
        return "Muy buena"
    if pilas_finales <= 10:
        return "Buena"
    return "En progreso"


def partidas_de_dificultad(partidas: list[dict], dificultad: str) -> list[dict]:
    """Filtra sin mezclar resultados de mazos de distinto tamaño."""
    return [partida for partida in partidas if partida.get("dificultad") == dificultad]


def clave_mejor_resultado(partida: dict) -> tuple:
    """Prioriza cerrar la mesa; los demás datos sólo desempatan."""
    return (
        int(partida.get("pilas_finales", 99)),
        -int(partida.get("puntaje", 0)),
        int(partida.get("duracion_segundos", 0)),
        int(partida.get("movimientos", 0)),
        partida.get("fecha", ""),
    )


def _promedio(valores: list[int]) -> float | None:
    return round(sum(valores) / len(valores), 1) if valores else None


def analizar_progreso(partidas: list[dict], dificultad: str) -> dict:
    """Calcula el progreso local de una dificultad sin depender de la UI."""
    juegos = partidas_de_dificultad(partidas, dificultad)
    if not juegos:
        return {"partidas": 0, "dificultad": dificultad, "distribucion": {}}

    pilas = [int(juego["pilas_finales"]) for juego in juegos]
    puntajes = [int(juego["puntaje"]) for juego in juegos]
    tiempos = [int(juego["duracion_segundos"]) for juego in juegos]
    mejor_resultado = min(juegos, key=clave_mejor_resultado)
    menor_pilas = int(mejor_resultado["pilas_finales"])
    candidatas_tiempo = [juego for juego in juegos if int(juego["pilas_finales"]) == menor_pilas]
    mejor_tiempo = min(candidatas_tiempo, key=lambda juego: int(juego["duracion_segundos"]))
    ultimas_diez = juegos[-10:]
    distribucion = {"2": 0, "3-4": 0, "5-7": 0, "8-10": 0, "11+": 0}
    for cantidad in pilas:
        clave = "2" if cantidad <= 2 else "3-4" if cantidad <= 4 else "5-7" if cantidad <= 7 else "8-10" if cantidad <= 10 else "11+"
        distribucion[clave] += 1

    tendencia = None
    if len(juegos) >= 20:
        recientes = _promedio([int(juego["pilas_finales"]) for juego in juegos[-10:]])
        anteriores = _promedio([int(juego["pilas_finales"]) for juego in juegos[-20:-10]])
        tendencia = round(anteriores - recientes, 1)

    mejor_promedio_reciente = None
    if len(juegos) >= 10:
        promedios = [_promedio([int(juego["pilas_finales"]) for juego in juegos[indice:indice + 10]]) for indice in range(len(juegos) - 9)]
        mejor_promedio_reciente = min(promedios)

    return {
        "partidas": len(juegos), "dificultad": dificultad,
        "tiempo_total": sum(tiempos), "movimientos_totales": sum(int(juego["movimientos"]) for juego in juegos),
        "promedio_pilas": _promedio(pilas), "mediana_pilas": statistics.median(pilas),
        "puntaje_promedio": round(sum(puntajes) / len(puntajes)),
        "mejor_resultado": mejor_resultado, "mayor_puntaje": min(juegos, key=clave_orden_record),
        "mejor_tiempo": mejor_tiempo,
        "promedio_ultimas_diez": _promedio([int(juego["pilas_finales"]) for juego in ultimas_diez]),
        "mejor_promedio_reciente": mejor_promedio_reciente, "tendencia_pilas": tendencia,
        "distribucion": distribucion,
    }


def mensaje_comparacion(resumen: dict, partidas_anteriores: list[dict]) -> str:
    """Devuelve una sola comparación clara para el cierre de partida."""
    juegos = partidas_de_dificultad(partidas_anteriores, resumen["dificultad"])
    if not juegos:
        return "Tu primera partida en esta dificultad. Ya tenés una referencia para superar."
    mejor_anterior = min(juegos, key=clave_mejor_resultado)
    pilas, mejor_pilas = int(resumen["pilas_finales"]), int(mejor_anterior["pilas_finales"])
    if pilas < mejor_pilas:
        return "Nuevo mejor resultado personal."
    if pilas == mejor_pilas:
        mejor_puntaje_anterior = min(juegos, key=clave_orden_record)
        if clave_orden_record(resumen) < clave_orden_record(mejor_puntaje_anterior):
            return "Igualaste tu mejor resultado y lograste tu mayor puntaje."
        return "Igualaste tu mejor resultado personal."
    if pilas == mejor_pilas + 1:
        return "A una pila de tu mejor resultado personal."
    if len(juegos) >= 10:
        promedio = _promedio([int(juego["pilas_finales"]) for juego in juegos[-10:]])
        diferencia = round(promedio - pilas, 1)
        if diferencia > 0:
            return f"{diferencia:.1f} pilas mejor que tu promedio reciente."
        if diferencia < 0:
            return f"Tu promedio reciente es de {promedio:.1f} pilas."
    return f"Tu mejor resultado personal es de {mejor_pilas} pilas."
