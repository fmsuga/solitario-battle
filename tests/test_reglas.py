from cartas import Carta, Palo
from tablero import Tablero
import reglas


def _tablero_de_prueba():
    """3 pilas: Oros7, Copas3, Oros9 -> la 1 y la 3 coinciden en PALO."""
    tablero = Tablero()
    tablero.agregar_carta_nueva(Carta(Palo.OROS, 7))
    tablero.agregar_carta_nueva(Carta(Palo.COPAS, 3))
    tablero.agregar_carta_nueva(Carta(Palo.OROS, 9))
    return tablero


def test_hay_coincidencia_por_valor():
    assert reglas.hay_coincidencia(Carta(Palo.OROS, 7), Carta(Palo.COPAS, 7)) is True


def test_hay_coincidencia_por_palo():
    assert reglas.hay_coincidencia(Carta(Palo.OROS, 7), Carta(Palo.OROS, 9)) is True


def test_no_hay_coincidencia():
    assert reglas.hay_coincidencia(Carta(Palo.OROS, 7), Carta(Palo.COPAS, 9)) is False


def test_es_jugada_valida_detecta_coincidencia():
    tablero = _tablero_de_prueba()
    assert reglas.es_jugada_valida(tablero, 0) is True


def test_es_jugada_valida_fuera_de_rango():
    tablero = _tablero_de_prueba()
    assert reglas.es_jugada_valida(tablero, 1) is False  # no hay pila 2 lugares después
    assert reglas.es_jugada_valida(tablero, -1) is False


def test_ejecutar_jugada_fusiona_si_es_valida():
    tablero = _tablero_de_prueba()
    resultado = reglas.ejecutar_jugada(tablero, 0)
    assert resultado is True
    assert tablero.cantidad_pilas() == 2


def test_ejecutar_jugada_no_hace_nada_si_es_invalida():
    tablero = _tablero_de_prueba()
    resultado = reglas.ejecutar_jugada(tablero, 1)
    assert resultado is False
    assert tablero.cantidad_pilas() == 3  # no cambió nada


def test_buscar_jugadas_posibles():
    tablero = _tablero_de_prueba()
    assert reglas.buscar_jugadas_posibles(tablero) == [0]
