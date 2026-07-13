from interfaz_grafica import _posicion_en_viborita


def test_la_grilla_alterna_el_sentido_de_cada_fila():
    assert _posicion_en_viborita(0, 10) == (0, 0)
    assert _posicion_en_viborita(9, 10) == (0, 9)
    assert _posicion_en_viborita(10, 10) == (1, 9)
    assert _posicion_en_viborita(19, 10) == (1, 0)
    assert _posicion_en_viborita(20, 10) == (2, 0)
