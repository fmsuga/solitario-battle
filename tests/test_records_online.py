import records_online


def test_records_de_supabase_se_normalizan_para_la_interfaz(monkeypatch):
    respuesta_supabase = [{
        "player_name": "Ada",
        "difficulty": "dificil",
        "score": 1850,
        "piles_finales": 4,
        "moves": 31,
        "duration_seconds": 97,
        "played_at": "2026-07-13T12:00:00+00:00",
    }]
    monkeypatch.setattr(records_online, "_solicitud", lambda *_args: respuesta_supabase)

    records, error = records_online.obtener_records_globales()

    assert error is None
    assert records == [{
        "jugador": "Ada",
        "dificultad": "dificil",
        "puntaje": 1850,
        "pilas_finales": 4,
        "movimientos": 31,
        "duracion_segundos": 97,
        "fecha": "2026-07-13T12:00:00+00:00",
    }]


def test_records_personales_usa_el_id_del_dispositivo(monkeypatch):
    rutas = []
    monkeypatch.setattr(records_online, "obtener_id_dispositivo", lambda: "device-test")
    monkeypatch.setattr(records_online, "_solicitud", lambda _metodo, ruta: rutas.append(ruta) or [])

    records, error = records_online.obtener_records_personales()

    assert records == []
    assert error is None
    assert "device_id=eq.device-test" in rutas[0]
