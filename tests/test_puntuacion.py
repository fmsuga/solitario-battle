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
