"""
tablero.py
----------
Modela el ESTADO de la mesa: las pilas de cartas que van quedando visibles.
Tampoco sabe nada de "reglas" (eso vive en reglas.py). Solo sabe organizar pilas.
"""

from cartas import Carta


class Pila:
    """
    Una pila de cartas boca arriba sobre la mesa.
    La carta "visible" (la de arriba) es siempre la última de la lista.
    """

    def __init__(self, carta_inicial: Carta):
        self.cartas = [carta_inicial]

    def tope(self) -> Carta:
        """Devuelve la carta que está arriba de todo (la visible)."""
        return self.cartas[-1]

    def apilar_encima(self, otra_pila: "Pila") -> None:
        """
        Pone TODAS las cartas de otra_pila encima de esta pila.
        (Esto es lo que pasa cuando la pila del medio se apila sobre la primera)
        """
        self.cartas.extend(otra_pila.cartas)

    def __len__(self):
        return len(self.cartas)

    def __repr__(self):
        if len(self.cartas) > 1:
            return f"{self.tope()!r} (+{len(self.cartas) - 1} debajo)"
        return repr(self.tope())


class Tablero:
    """
    Representa TODAS las pilas que hay actualmente sobre la mesa,
    en el orden en que fueron apareciendo (de izquierda a derecha).

    Esta lista es una SECUENCIA ÚNICA y continua: no sabe nada de "filas".
    Las filas son un detalle de cómo se muestra en pantalla (ver interfaz_consola.py).
    """

    def __init__(self):
        self.pilas: list[Pila] = []

    def agregar_carta_nueva(self, carta: Carta) -> None:
        """Se despliega una carta nueva del mazo: crea una pila nueva."""
        self.pilas.append(Pila(carta))

    def cantidad_pilas(self) -> int:
        return len(self.pilas)

    def fusionar(self, indice_pila_1: int, indice_pila_2: int) -> None:
        """
        Fusiona la pila del medio (indice_pila_2) encima de la pila_1,
        y elimina la pila_2 de la lista de pilas.
        """
        self.pilas[indice_pila_1].apilar_encima(self.pilas[indice_pila_2])
        del self.pilas[indice_pila_2]
