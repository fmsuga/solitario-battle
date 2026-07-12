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
