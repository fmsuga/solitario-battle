"""
interfaz_consola.py
--------------------
Acá vive toda la interacción con el jugador: mostrar el tablero (con
números, para que puedas señalar una pila), repartir cartas, y
preguntarle si detecta una jugada. Esta es la ÚNICA capa que sabe de
print() e input(); si mañana hacés una versión gráfica, es el único
archivo (junto con main.py) que reemplazarías.
"""

from juego import Juego
import puntuacion

# Solo visual ("el ancho de hombros de una persona"). No afecta las reglas:
# juego.tablero.pilas sigue siendo una única secuencia continua, y una
# jugada puede compararse "cruzando" el borde de una fila sin problema.
ANCHO_FILA = 8


class PartidaAbandonada(Exception):
    """Se levanta cuando el jugador decide rendirse en medio de la partida."""
    pass


def mostrar_tablero(juego: Juego) -> None:
    """
    Muestra las pilas numeradas empezando en 1 (para que sea natural
    decir "la pila 3"), agrupadas de a ANCHO_FILA por fila.
    """
    pilas = juego.tablero.pilas
    for inicio in range(0, len(pilas), ANCHO_FILA):
        fila = pilas[inicio:inicio + ANCHO_FILA]
        textos = []
        for offset, pila in enumerate(fila):
            numero = inicio + offset + 1
            textos.append(f"{numero}:[{pila.tope()} x{len(pila)}]")
        print("  ".join(textos))
    print(f"-> Total de pilas en mesa: {len(pilas)}")


def pedir_jugada(juego: Juego) -> bool:
    """
    Le pregunta al jugador si ve una jugada. Si dice que sí, le pide la
    posición (tal como se ve en pantalla, empezando en 1) de la pila de
    la IZQUIERDA del par, e intenta ejecutarla.

    Si el jugador tipea "r", se levanta PartidaAbandonada (se rinde y
    corta la partida ahí mismo, sin llegar a repartir más cartas).

    Devuelve True si el jugador quiere seguir intentando jugadas ahora
    mismo (esto permite encadenar varias jugadas seguidas antes de
    repartir la próxima carta, tal como en la vida real).
    """
    respuesta = input("¿Ves alguna jugada? (s/n, o 'r' para rendirte): ").strip().lower()
    if respuesta == "r":
        raise PartidaAbandonada()
    if respuesta != "s":
        return False

    texto = input(
        "Posición de la pila IZQUIERDA del par "
        "(se compara con la que está 2 lugares después, salteando la del medio): "
    ).strip()

    if not texto.isdigit():
        print("Eso no es un número válido.\n")
        return True

    indice_izquierda = int(texto) - 1  # en pantalla se cuenta desde 1
    if juego.intentar_jugada(indice_izquierda):
        print("¡Jugada válida! Se fusionaron las pilas.\n")
        mostrar_tablero(juego)
        print()
    else:
        print("Ahí no hay ninguna coincidencia. Fijate de nuevo.\n")

    return True


def jugar_partida():
    """
    Corre UNA partida completa por consola.
    Devuelve el puntaje final, o None si el jugador se rindió a mitad de partida.
    """
    juego = Juego()
    print("=== Nueva partida ===")
    print("Se van repartiendo cartas. Si ves que la pila de una posición")
    print("coincide en VALOR o PALO con la que está 2 lugares después")
    print("(salteando la del medio), avisá y te pido la posición.")
    print("En cualquier momento podés tipear 'r' para rendirte y arrancar de nuevo.\n")

    try:
        while juego.quedan_cartas_en_mano():
            juego.repartir_carta()
            print()
            mostrar_tablero(juego)
            print(f"Cartas restantes en el mazo: {juego.mazo.quedan_cartas()}")

            while pedir_jugada(juego):
                pass  # sigue preguntando mientras el jugador quiera intentar jugadas
    except PartidaAbandonada:
        print("\nTe rendiste. Esta partida no cuenta ni se guarda.")
        return None

    juego.finalizar()
    resumen = juego.obtener_resumen()
    print(f"\nSe acabó el mazo. Quedaron {resumen['pilas_finales']} pila(s) sobre la mesa.")
    print(f"Puntaje: {resumen['puntaje']} puntos.")
    print(f"Jugadas realizadas: {resumen['movimientos']}   |   Duración: {puntuacion.formatear_duracion(resumen['duracion_segundos'])}")
    print(puntuacion.interpretar_resultado(resumen['pilas_finales']))

    nombre = input(
        "\nNombre del jugador (Enter para NO guardar este resultado y descartarlo): "
    ).strip()
    if nombre:
        puntuacion.guardar_puntaje(nombre, resumen)
        print("Puntaje guardado en historial.json")
    else:
        print("Resultado descartado, no se guardó nada.")

    return resumen['puntaje']


def jugar() -> None:
    """Punto de entrada real: juega partidas en bucle hasta que digas que no."""
    seguir = True
    while seguir:
        resultado = jugar_partida()
        if resultado is None:
            continue  # se rindió: arranca una nueva directo, sin preguntar
        respuesta = input("\n¿Jugar otra partida? (s/n): ").strip().lower()
        seguir = respuesta == "s"
    print("\n¡Gracias por jugar!")
