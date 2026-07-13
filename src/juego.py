"""
juego.py
--------
La clase Juego conoce el Mazo y el Tablero, y expone acciones que el
JUGADOR pide: repartir la siguiente carta, o intentar una jugada en una
posición que el jugador eligió. La clase no decide sola cuándo fusionar:
eso lo dispara siempre el jugador (ver interfaz_consola.py).
"""

from datetime import datetime

from cartas import Mazo, Dificultad
from tablero import Tablero
import reglas


class Juego:
    def __init__(self, dificultad: Dificultad = Dificultad.DIFICIL):
        self.dificultad = dificultad
        self.mazo = Mazo(dificultad=dificultad)
        self.mazo.mezclar()
        self.tablero = Tablero()
        self.terminada = False

        # Cuántas cartas había al arrancar (40 en Fácil, 48 en Difícil).
        # Se usa para calcular el puntaje sin depender de un número fijo.
        self.cantidad_cartas_inicial = self.mazo.quedan_cartas()

        # Datos para las estadísticas (no afectan la lógica del juego en sí)
        self.momento_inicio = datetime.now()
        self.momento_fin = None
        self.cantidad_jugadas_realizadas = 0

    def repartir_carta(self) -> None:
        """
        Despliega la siguiente carta del mazo y la pone en una pila nueva.
        No hace nada si la partida ya terminó o si no quedan cartas
        (evita romper si la interfaz llama esto por error).
        """
        if self.terminada or not self.quedan_cartas_en_mano():
            return
        carta = self.mazo.repartir_una()
        self.tablero.agregar_carta_nueva(carta)

    def intentar_jugada(self, indice_izquierda: int) -> bool:
        """
        El jugador propone una jugada dando la posición (base 0) de la
        pila de la izquierda del par. Devuelve True si era válida y se
        ejecutó, False si no. Si la partida ya terminó, no hace nada.
        """
        if self.terminada:
            return False
        resultado = reglas.ejecutar_jugada(self.tablero, indice_izquierda)
        if resultado:
            self.cantidad_jugadas_realizadas += 1
        return resultado

    def quedan_cartas_en_mano(self) -> bool:
        return self.mazo.quedan_cartas() > 0

    def finalizar(self) -> None:
        """
        El jugador decide que ya no encuentra más jugadas: cierra la
        partida. A partir de acá, repartir_carta() e intentar_jugada()
        dejan de hacer efecto.
        """
        if not self.terminada:
            self.momento_fin = datetime.now()
        self.terminada = True

    def esta_terminada(self) -> bool:
        return self.terminada

    def cantidad_pilas_finales(self) -> int:
        """Cuántas pilas quedaron sobre la mesa (2 es el mínimo posible: partida perfecta)."""
        return self.tablero.cantidad_pilas()

    def calcular_puntaje(self) -> int:
        """
        Puntaje con recompensa exponencial por cerrar el tablero.

        Las fusiones dan una base pequeña, pero la dificultad real está en
        llegar a muy pocas pilas. Por eso 2, 3, 4 y 5 pilas obtienen bonos
        claramente distantes. En Difícil el resultado final recibe además
        un multiplicador, para que sus récords reflejen el mazo completo.
        """
        pilas_finales = self.cantidad_pilas_finales()
        puntos_por_fusiones = (self.cantidad_cartas_inicial - pilas_finales) * 10
        bono_por_pilas = {
            2: 10000,
            3: 5500,
            4: 2800,
            5: 1400,
            6: 700,
            7: 350,
            8: 180,
        }
        bono = bono_por_pilas.get(pilas_finales, 0)
        multiplicador = 1.5 if self.dificultad == Dificultad.DIFICIL else 1.0
        return round((puntos_por_fusiones + bono) * multiplicador)

    def duracion_segundos(self) -> int:
        """Cuánto duró (o lleva durando, si todavía no terminó) la partida."""
        fin = self.momento_fin or datetime.now()
        return int((fin - self.momento_inicio).total_seconds())

    def obtener_resumen(self) -> dict:
        """
        Junta todas las estadísticas de la partida en un solo lugar.
        Se usa tanto para mostrar el resultado como para guardarlo en el
        historial (puntuacion.py). Si mañana agregás una métrica nueva,
        se agrega ACÁ, y no hay que tocar la firma de guardar_puntaje.
        """
        return {
            "fecha": self.momento_inicio.strftime("%Y-%m-%d %H:%M"),
            "dificultad": self.dificultad.value,
            "duracion_segundos": self.duracion_segundos(),
            "movimientos": self.cantidad_jugadas_realizadas,
            "pilas_finales": self.cantidad_pilas_finales(),
            "puntaje": self.calcular_puntaje(),
        }
