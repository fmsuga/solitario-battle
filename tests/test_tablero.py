from cartas import Carta, Palo
from tablero import Pila, Tablero


def test_pila_tope_es_la_ultima_carta():
    pila = Pila(Carta(Palo.OROS, 5))
    assert pila.tope().valor == 5
    assert pila.tope().palo == Palo.OROS


def test_apilar_encima_conserva_ambas_cartas():
    pila_1 = Pila(Carta(Palo.OROS, 5))
    pila_2 = Pila(Carta(Palo.COPAS, 9))
    pila_1.apilar_encima(pila_2)
    assert len(pila_1) == 2
    assert pila_1.tope().valor == 9  # la de pila_2 quedó arriba


def test_tablero_agregar_carta_nueva_crea_pila():
    tablero = Tablero()
    tablero.agregar_carta_nueva(Carta(Palo.OROS, 1))
    assert tablero.cantidad_pilas() == 1
    tablero.agregar_carta_nueva(Carta(Palo.COPAS, 2))
    assert tablero.cantidad_pilas() == 2


def test_fusionar_reduce_una_pila_y_conserva_las_cartas():
    tablero = Tablero()
    tablero.agregar_carta_nueva(Carta(Palo.OROS, 7))
    tablero.agregar_carta_nueva(Carta(Palo.COPAS, 3))
    tablero.agregar_carta_nueva(Carta(Palo.OROS, 9))

    tablero.fusionar(0, 1)  # la pila del medio (Copas 3) se apila sobre la pila 0

    assert tablero.cantidad_pilas() == 2
    assert len(tablero.pilas[0]) == 2       # Oros7 + Copas3
    assert tablero.pilas[0].tope().valor == 3
    assert tablero.pilas[1].tope().valor == 9
