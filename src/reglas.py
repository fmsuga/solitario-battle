"""
reglas.py
---------
Acá vive el "cerebro" del juego: decide si una jugada que PROPONE el
jugador es válida o no. OJO: esto no fusiona solo, ni busca jugadas por
su cuenta. Encontrar la coincidencia es trabajo del jugador — esa es
justamente la habilidad del juego real (los jugadores expertos ven
coincidencias más atrás en el tablero; los principiantes solo miran las
últimas cartas y se pierden jugadas).
"""

from tablero import Tablero


def hay_coincidencia(carta_1, carta_3) -> bool:
    """Devuelve True si carta_1 y carta_3 coinciden en valor o en palo."""
    return carta_1.mismo_valor(carta_3) or carta_1.mismo_palo(carta_3)


def es_jugada_valida(tablero: Tablero, indice_izquierda: int) -> bool:
    """
    Una jugada se identifica por la posición de la pila de la IZQUIERDA
    del par (en base 0: la primera pila del tablero es la 0). Se compara
    esa pila contra la que está dos lugares después (salteando la del
    medio). Devuelve True si esa jugada es válida.
    """
    indice_derecha = indice_izquierda + 2
    if indice_izquierda < 0 or indice_derecha >= tablero.cantidad_pilas():
        return False
    pila_izquierda = tablero.pilas[indice_izquierda]
    pila_derecha = tablero.pilas[indice_derecha]
    return hay_coincidencia(pila_izquierda.tope(), pila_derecha.tope())


def ejecutar_jugada(tablero: Tablero, indice_izquierda: int) -> bool:
    """
    Si la jugada es válida, la ejecuta (fusiona la pila del medio sobre
    la de la izquierda) y devuelve True. Si no es válida, no hace nada
    y devuelve False.
    """
    if not es_jugada_valida(tablero, indice_izquierda):
        return False
    indice_medio = indice_izquierda + 1
    tablero.fusionar(indice_izquierda, indice_medio)
    return True


def buscar_jugadas_posibles(tablero: Tablero) -> list[int]:
    """
    Devuelve la lista de índices (izquierda) donde hay una jugada válida
    disponible ahora mismo. El juego normal NO usa esto para jugar solo;
    te lo dejo armado por si más adelante querés agregar un botón de
    "pista" (ayuda) para cuando estés practicando.
    """
    return [i for i in range(max(0, tablero.cantidad_pilas() - 2)) if es_jugada_valida(tablero, i)]
