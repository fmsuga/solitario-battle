from juego import Juego


def test_juego_arranca_sin_pilas_y_con_48_cartas():
    juego = Juego()
    assert juego.tablero.cantidad_pilas() == 0
    assert juego.mazo.quedan_cartas() == 48
    assert juego.esta_terminada() is False


def test_repartir_carta_agrega_una_pila_y_saca_del_mazo():
    juego = Juego()
    juego.repartir_carta()
    assert juego.tablero.cantidad_pilas() == 1
    assert juego.mazo.quedan_cartas() == 47


def test_finalizar_bloquea_repartir_y_jugadas():
    juego = Juego()
    juego.repartir_carta()
    pilas_antes = juego.tablero.cantidad_pilas()

    juego.finalizar()
    assert juego.esta_terminada() is True

    juego.repartir_carta()  # no debería hacer nada
    assert juego.tablero.cantidad_pilas() == pilas_antes

    resultado = juego.intentar_jugada(0)  # tampoco debería hacer nada
    assert resultado is False


def test_calcular_puntaje_formula_base_sin_bono():
    juego = Juego()
    # sin repartir nada, en teoría 0 pilas; pero la fórmula se basa en
    # CANTIDAD_CARTAS_EN_MAZO - pilas_finales, probamos con pilas simuladas
    for _ in range(5):
        juego.repartir_carta()
    pilas = juego.cantidad_pilas_finales()
    puntaje_esperado = round(((48 - pilas) * 10) * 1.5)
    assert juego.calcular_puntaje() == puntaje_esperado


def test_quedan_cartas_en_mano():
    juego = Juego()
    assert juego.quedan_cartas_en_mano() is True
    for _ in range(48):
        juego.repartir_carta()
    assert juego.quedan_cartas_en_mano() is False


def test_intentar_jugada_exitosa_suma_al_contador_de_movimientos():
    juego = Juego()
    # armo a mano una jugada válida: Oros7, Copas3, Oros9
    from cartas import Carta, Palo
    juego.tablero.agregar_carta_nueva(Carta(Palo.OROS, 7))
    juego.tablero.agregar_carta_nueva(Carta(Palo.COPAS, 3))
    juego.tablero.agregar_carta_nueva(Carta(Palo.OROS, 9))

    assert juego.cantidad_jugadas_realizadas == 0
    resultado = juego.intentar_jugada(0)
    assert resultado is True
    assert juego.cantidad_jugadas_realizadas == 1


def test_intentar_jugada_invalida_no_suma_al_contador():
    juego = Juego()
    from cartas import Carta, Palo
    juego.tablero.agregar_carta_nueva(Carta(Palo.OROS, 7))
    juego.tablero.agregar_carta_nueva(Carta(Palo.COPAS, 3))
    juego.tablero.agregar_carta_nueva(Carta(Palo.ESPADAS, 9))  # no coincide

    resultado = juego.intentar_jugada(0)
    assert resultado is False
    assert juego.cantidad_jugadas_realizadas == 0


def test_obtener_resumen_trae_todas_las_claves_esperadas():
    juego = Juego()
    juego.repartir_carta()
    juego.finalizar()
    resumen = juego.obtener_resumen()

    claves_esperadas = {"fecha", "duracion_segundos", "movimientos", "pilas_finales", "puntaje"}
    assert claves_esperadas.issubset(resumen.keys())
    assert resumen["duracion_segundos"] >= 0
    assert resumen["movimientos"] == 0
    assert resumen["pilas_finales"] == 1


def test_finalizar_congela_la_duracion():
    import time
    juego = Juego()
    juego.finalizar()
    duracion_al_terminar = juego.duracion_segundos()
    time.sleep(0.05)
    # como ya terminó, la duración no debería seguir creciendo
    assert juego.duracion_segundos() == duracion_al_terminar


def test_finalizar_es_idempotente_no_pisa_momento_fin():
    import time
    juego = Juego()
    juego.finalizar()
    primer_momento_fin = juego.momento_fin
    time.sleep(0.02)
    juego.finalizar()  # llamarlo de nuevo no debería cambiar el momento_fin ya fijado
    assert juego.momento_fin == primer_momento_fin


def test_juego_facil_arranca_con_40_cartas_y_calcula_puntaje_bien():
    from cartas import Dificultad
    juego = Juego(dificultad=Dificultad.FACIL)
    assert juego.mazo.quedan_cartas() == 40
    assert juego.cantidad_cartas_inicial == 40

    for _ in range(5):
        juego.repartir_carta()
    pilas = juego.cantidad_pilas_finales()
    assert juego.calcular_puntaje() == (40 - pilas) * 10


def test_puntaje_premia_mucho_mas_las_pocas_pilas_y_dificil():
    from cartas import Dificultad

    puntajes_dificil = []
    for pilas_finales in (2, 3, 4, 5):
        juego = Juego(dificultad=Dificultad.DIFICIL)
        juego.tablero.pilas = [object()] * pilas_finales
        puntajes_dificil.append(juego.calcular_puntaje())

    # Cada escalón representa un logro mucho mayor que el siguiente.
    assert puntajes_dificil[0] - puntajes_dificil[1] > 6000
    assert puntajes_dificil[1] - puntajes_dificil[2] > 3000
    assert puntajes_dificil[2] - puntajes_dificil[3] > 1500

    facil = Juego(dificultad=Dificultad.FACIL)
    facil.tablero.pilas = [object()] * 5
    dificil = Juego(dificultad=Dificultad.DIFICIL)
    dificil.tablero.pilas = [object()] * 5
    assert dificil.calcular_puntaje() > facil.calcular_puntaje()


def test_juego_dificil_es_el_default():
    from cartas import Dificultad
    juego = Juego()
    assert juego.dificultad == Dificultad.DIFICIL
    assert juego.mazo.quedan_cartas() == 48


def test_resumen_incluye_la_dificultad():
    from cartas import Dificultad
    juego = Juego(dificultad=Dificultad.FACIL)
    juego.finalizar()
    resumen = juego.obtener_resumen()
    assert resumen["dificultad"] == "facil"
