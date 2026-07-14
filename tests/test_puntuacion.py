import os
from pathlib import Path

import puntuacion


def test_formatear_duracion_menos_de_un_minuto():
    assert puntuacion.formatear_duracion(45) == "45s"


def test_formatear_duracion_con_minutos():
    assert puntuacion.formatear_duracion(222) == "3m 42s"


def test_interpretar_resultado_extremos():
    assert "IMPOSIBLE" in puntuacion.interpretar_resultado(2)
    assert "próxima vez" in puntuacion.interpretar_resultado(30)


def test_es_nuevo_record_compara_con_el_mejor_historial(tmp_path, monkeypatch):
    archivo = tmp_path / "historial.json"
    archivo.write_text('[{"puntaje": 300, "duracion_segundos": 100, "movimientos": 20, "fecha": "2026-01-01"}]', encoding="utf-8")
    monkeypatch.setattr(puntuacion, "ARCHIVO_HISTORIAL", archivo)

    assert puntuacion.es_nuevo_record({"puntaje": 320, "duracion_segundos": 120, "movimientos": 21, "fecha": "2026-01-02"})
    assert not puntuacion.es_nuevo_record({"puntaje": 280, "duracion_segundos": 90, "movimientos": 18, "fecha": "2026-01-02"})


def test_guardar_y_cargar_historial(tmp_path, monkeypatch):
    # uso un archivo temporal para no ensuciar el historial.json real
    archivo_temporal = tmp_path / "historial_test.json"
    monkeypatch.setattr(puntuacion, "ARCHIVO_HISTORIAL", archivo_temporal)

    resumen = {
        "fecha": "2026-07-10 10:00",
        "duracion_segundos": 120,
        "movimientos": 5,
        "pilas_finales": 10,
        "puntaje": 380,
    }
    puntuacion.guardar_puntaje("Tester", resumen)

    historial = puntuacion.cargar_historial()
    assert len(historial) == 1
    assert historial[0]["jugador"] == "Tester"
    assert historial[0]["puntaje"] == 380

    mejor = puntuacion.mejor_puntaje()
    assert mejor["jugador"] == "Tester"


def test_ranking_prioriza_puntaje_y_desempata_por_tiempo_y_movimientos():
    partidas = [
        {"puntaje": 2000, "duracion_segundos": 90, "movimientos": 8, "fecha": "2026-01-03"},
        {"puntaje": 2000, "duracion_segundos": 70, "movimientos": 9, "fecha": "2026-01-02"},
        {"puntaje": 2000, "duracion_segundos": 70, "movimientos": 7, "fecha": "2026-01-01"},
        {"puntaje": 1900, "duracion_segundos": 10, "movimientos": 1, "fecha": "2026-01-01"},
    ]

    ordenadas = puntuacion.ordenar_records(partidas)

    assert ordenadas[0]["movimientos"] == 7
    assert ordenadas[1]["movimientos"] == 9
    assert ordenadas[-1]["puntaje"] == 1900
    assert puntuacion.indice_jugador(partidas) == 7900


def test_analizar_progreso_separa_dificultades_y_prioriza_menos_pilas():
    partidas = [
        {"dificultad": "facil", "pilas_finales": 5, "puntaje": 800, "duracion_segundos": 100, "movimientos": 35, "fecha": "2026-01-01"},
        {"dificultad": "facil", "pilas_finales": 3, "puntaje": 600, "duracion_segundos": 120, "movimientos": 37, "fecha": "2026-01-02"},
        {"dificultad": "dificil", "pilas_finales": 2, "puntaje": 15000, "duracion_segundos": 200, "movimientos": 46, "fecha": "2026-01-03"},
    ]

    datos = puntuacion.analizar_progreso(partidas, "facil")

    assert datos["partidas"] == 2
    assert datos["mejor_resultado"]["pilas_finales"] == 3
    assert datos["mejor_tiempo"]["pilas_finales"] == 3
    assert datos["distribucion"] == {"2": 0, "3-4": 1, "5-7": 1, "8-10": 0, "11+": 0}


def test_progreso_calcula_tendencia_solo_con_veinte_partidas():
    partidas = [
        {"dificultad": "facil", "pilas_finales": 10 if i < 10 else 6, "puntaje": i, "duracion_segundos": 60, "movimientos": 1, "fecha": f"2026-01-{i + 1:02d}"}
        for i in range(20)
    ]

    datos = puntuacion.analizar_progreso(partidas, "facil")

    assert datos["tendencia_pilas"] == 4.0
    assert datos["mejor_promedio_reciente"] == 6.0


def test_clasificacion_y_mensaje_de_comparacion():
    anterior = [{"dificultad": "facil", "pilas_finales": 5, "puntaje": 400, "duracion_segundos": 90, "movimientos": 35, "fecha": "2026-01-01"}]
    resumen = {"dificultad": "facil", "pilas_finales": 4, "puntaje": 500, "duracion_segundos": 100, "movimientos": 36}

    assert puntuacion.clasificar_resultado(4) == "Excelente"
    assert puntuacion.mensaje_comparacion(resumen, anterior) == "Nuevo mejor resultado personal."
