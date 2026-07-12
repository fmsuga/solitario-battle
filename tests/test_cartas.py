from cartas import Carta, Palo, Mazo, CANTIDAD_CARTAS_EN_MAZO


def test_mismo_valor():
    a = Carta(Palo.OROS, 7)
    b = Carta(Palo.COPAS, 7)
    c = Carta(Palo.OROS, 3)
    assert a.mismo_valor(b) is True
    assert a.mismo_valor(c) is False


def test_mismo_palo():
    a = Carta(Palo.OROS, 7)
    b = Carta(Palo.OROS, 3)
    c = Carta(Palo.COPAS, 7)
    assert a.mismo_palo(b) is True
    assert a.mismo_palo(c) is False


def test_repr_as_y_numeros():
    assert repr(Carta(Palo.OROS, 1)) == "As de Oro"
    assert repr(Carta(Palo.ESPADAS, 10)) == "10 de Espada"
    assert repr(Carta(Palo.BASTOS, 12)) == "12 de Basto"


def test_mazo_tiene_48_cartas_unicas():
    mazo = Mazo()
    assert mazo.quedan_cartas() == 48 == CANTIDAD_CARTAS_EN_MAZO
    combinaciones = {(c.palo, c.valor) for c in mazo.cartas}
    assert len(combinaciones) == 48  # ninguna carta repetida


def test_repartir_una_reduce_el_mazo():
    mazo = Mazo()
    total_inicial = mazo.quedan_cartas()
    carta = mazo.repartir_una()
    assert isinstance(carta, Carta)
    assert mazo.quedan_cartas() == total_inicial - 1


def test_mazo_dificil_tiene_48_cartas_con_8_y_9():
    from cartas import Dificultad
    mazo = Mazo(dificultad=Dificultad.DIFICIL)
    assert mazo.quedan_cartas() == 48
    valores = {c.valor for c in mazo.cartas}
    assert 8 in valores and 9 in valores


def test_mazo_facil_tiene_40_cartas_sin_8_ni_9():
    from cartas import Dificultad
    mazo = Mazo(dificultad=Dificultad.FACIL)
    assert mazo.quedan_cartas() == 40
    valores = {c.valor for c in mazo.cartas}
    assert 8 not in valores
    assert 9 not in valores
