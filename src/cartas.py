"""
cartas.py
---------
Todo lo relacionado a los DATOS del mazo: qué es una carta, qué es el mazo.
Este módulo no sabe nada de "reglas de juego" ni de "cómo se muestra en pantalla".
Solo modela objetos.
"""

from enum import Enum
import random


class Palo(Enum):
    OROS = "Oro"
    COPAS = "Copa"
    ESPADAS = "Espada"
    BASTOS = "Basto"


NOMBRES_VALOR = {
    1: "As",
    2: "2",
    3: "3",
    4: "4",
    5: "5",
    6: "6",
    7: "7",
    8: "8",
    9: "9",
    10: "10",
    11: "11",
    12: "12",
}

class Dificultad(Enum):
    FACIL = "facil"       # 40 cartas: sin 8 ni 9 de ningún palo (mazo tradicional)
    DIFICIL = "dificil"   # 48 cartas: con 8 y 9 incluidos


# 4 palos x 12 valores = 48 cartas (el mazo de 50 sin los 2 comodines)
CANTIDAD_CARTAS_EN_MAZO = len(Palo) * 12


class Carta:
    """
    Representa una carta española.
    valor: 1 a 12 (12 valores x 4 palos = 48 cartas -> el mazo de 50 sin comodines).
    """

    def __init__(self, palo: Palo, valor: int):
        self.palo = palo
        self.valor = valor

    def mismo_valor(self, otra: "Carta") -> bool:
        return self.valor == otra.valor

    def mismo_palo(self, otra: "Carta") -> bool:
        return self.palo == otra.palo

    def __repr__(self):
        return f"{NOMBRES_VALOR[self.valor]} de {self.palo.value}"


class Mazo:
    """
    Representa el mazo completo: una lista de Cartas.
    Responsabilidades: crearse completo (según la dificultad), mezclarse,
    repartir una carta.
    """

    def __init__(self, dificultad: Dificultad = Dificultad.DIFICIL):
        self.dificultad = dificultad
        self.cartas = self._crear_mazo_completo()

    def _crear_mazo_completo(self) -> list[Carta]:
        valores_excluidos = {8, 9} if self.dificultad == Dificultad.FACIL else set()
        cartas = []
        for palo in Palo:
            for valor in range(1, 13):
                if valor in valores_excluidos:
                    continue
                cartas.append(Carta(palo, valor))
        return cartas

    def mezclar(self) -> None:
        random.shuffle(self.cartas)

    def repartir_una(self) -> Carta:
        """Saca (y devuelve) la carta de arriba del mazo."""
        return self.cartas.pop()

    def quedan_cartas(self) -> int:
        return len(self.cartas)
