import json

import configuracion


def test_guardar_volumen_preserva_los_datos_del_perfil(tmp_path, monkeypatch):
    archivo = tmp_path / "perfil.json"
    archivo.write_text(json.dumps({"device_id": "abc-123"}), encoding="utf-8")
    monkeypatch.setattr(configuracion, "ARCHIVO_PERFIL", archivo)

    configuracion.guardar_volumen(0.35)

    assert configuracion.cargar_volumen() == 0.35
    assert json.loads(archivo.read_text(encoding="utf-8"))["device_id"] == "abc-123"


def test_volumen_se_limita_entre_cero_y_uno(tmp_path, monkeypatch):
    monkeypatch.setattr(configuracion, "ARCHIVO_PERFIL", tmp_path / "perfil.json")

    configuracion.guardar_volumen(2)

    assert configuracion.cargar_volumen() == 1.0


def test_guardar_idioma_preserva_las_preferencias_existentes(tmp_path, monkeypatch):
    archivo = tmp_path / "perfil.json"
    archivo.write_text(json.dumps({"volumen": 0.35}), encoding="utf-8")
    monkeypatch.setattr(configuracion, "ARCHIVO_PERFIL", archivo)

    configuracion.guardar_idioma("en")

    assert configuracion.cargar_idioma() == "en"
    assert json.loads(archivo.read_text(encoding="utf-8"))["volumen"] == 0.35
