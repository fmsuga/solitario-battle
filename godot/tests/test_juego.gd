extends GutTest


func _pilas_simuladas(cantidad: int) -> Array[Tablero.Pila]:
	var pilas: Array[Tablero.Pila] = []
	for _indice in range(cantidad):
		pilas.append(Tablero.Pila.new(Carta.new(Carta.Palo.OROS, 1)))
	return pilas


func test_juego_arranca_sin_pilas_y_con_48_cartas() -> void:
	var juego := Juego.new()
	assert_eq(juego.tablero.cantidad_pilas(), 0)
	assert_eq(juego.mazo.quedan_cartas(), 48)
	assert_false(juego.esta_terminada())


func test_repartir_carta_agrega_una_pila_y_saca_del_mazo() -> void:
	var juego := Juego.new()
	juego.repartir_carta()
	assert_eq(juego.tablero.cantidad_pilas(), 1)
	assert_eq(juego.mazo.quedan_cartas(), 47)


func test_finalizar_bloquea_repartir_y_jugadas() -> void:
	var juego := Juego.new()
	juego.repartir_carta()
	var pilas_antes := juego.tablero.cantidad_pilas()

	juego.finalizar()
	assert_true(juego.esta_terminada())
	juego.repartir_carta()
	assert_eq(juego.tablero.cantidad_pilas(), pilas_antes)
	assert_false(juego.intentar_jugada(0))


func test_calcular_puntaje_formula_con_bono_de_5_pilas() -> void:
	var juego := Juego.new()
	for _indice in range(5):
		juego.repartir_carta()
	var puntaje_esperado := roundi(((48 - juego.cantidad_pilas_finales()) * 10 + 1400) * 1.5)
	assert_eq(juego.calcular_puntaje(), puntaje_esperado)


func test_quedan_cartas_en_mano() -> void:
	var juego := Juego.new()
	assert_true(juego.quedan_cartas_en_mano())
	for _indice in range(48):
		juego.repartir_carta()
	assert_false(juego.quedan_cartas_en_mano())


func test_intentar_jugada_exitosa_suma_al_contador_de_movimientos() -> void:
	var juego := Juego.new()
	juego.tablero.agregar_carta_nueva(Carta.new(Carta.Palo.OROS, 7))
	juego.tablero.agregar_carta_nueva(Carta.new(Carta.Palo.COPAS, 3))
	juego.tablero.agregar_carta_nueva(Carta.new(Carta.Palo.OROS, 9))

	assert_eq(juego.cantidad_jugadas_realizadas, 0)
	assert_true(juego.intentar_jugada(0))
	assert_eq(juego.cantidad_jugadas_realizadas, 1)


func test_intentar_jugada_invalida_no_suma_al_contador() -> void:
	var juego := Juego.new()
	juego.tablero.agregar_carta_nueva(Carta.new(Carta.Palo.OROS, 7))
	juego.tablero.agregar_carta_nueva(Carta.new(Carta.Palo.COPAS, 3))
	juego.tablero.agregar_carta_nueva(Carta.new(Carta.Palo.ESPADAS, 9))

	assert_false(juego.intentar_jugada(0))
	assert_eq(juego.cantidad_jugadas_realizadas, 0)


func test_obtener_resumen_trae_todas_las_claves_esperadas() -> void:
	var juego := Juego.new()
	juego.repartir_carta()
	juego.finalizar()
	var resumen := juego.obtener_resumen()

	for clave in ["fecha", "duracion_segundos", "movimientos", "pilas_finales", "puntaje"]:
		assert_true(resumen.has(clave))
	assert_gte(resumen["duracion_segundos"], 0)
	assert_eq(resumen["movimientos"], 0)
	assert_eq(resumen["pilas_finales"], 1)


func test_finalizar_congela_la_duracion() -> void:
	var juego := Juego.new()
	juego.finalizar()
	var duracion_al_terminar := juego.duracion_segundos()
	OS.delay_msec(50)
	assert_eq(juego.duracion_segundos(), duracion_al_terminar)


func test_finalizar_es_idempotente_no_pisa_momento_fin() -> void:
	var juego := Juego.new()
	juego.finalizar()
	var primer_momento_fin = juego.momento_fin
	OS.delay_msec(20)
	juego.finalizar()
	assert_eq(juego.momento_fin, primer_momento_fin)


func test_juego_facil_arranca_con_40_cartas_y_calcula_puntaje_bien() -> void:
	var juego := Juego.new(Carta.Dificultad.FACIL)
	assert_eq(juego.mazo.quedan_cartas(), 40)
	assert_eq(juego.cantidad_cartas_inicial, 40)

	for _indice in range(5):
		juego.repartir_carta()
	assert_eq(juego.calcular_puntaje(), (40 - juego.cantidad_pilas_finales()) * 10 + 1400)


func test_puntaje_premia_mucho_mas_las_pocas_pilas_y_dificil() -> void:
	var puntajes_dificil: Array[int] = []
	for pilas_finales in [2, 3, 4, 5]:
		var juego := Juego.new(Carta.Dificultad.DIFICIL)
		juego.tablero.pilas = _pilas_simuladas(pilas_finales)
		puntajes_dificil.append(juego.calcular_puntaje())

	assert_gt(puntajes_dificil[0] - puntajes_dificil[1], 6000)
	assert_gt(puntajes_dificil[1] - puntajes_dificil[2], 3000)
	assert_gt(puntajes_dificil[2] - puntajes_dificil[3], 1500)

	var facil := Juego.new(Carta.Dificultad.FACIL)
	facil.tablero.pilas = _pilas_simuladas(5)
	var dificil := Juego.new(Carta.Dificultad.DIFICIL)
	dificil.tablero.pilas = _pilas_simuladas(5)
	assert_gt(dificil.calcular_puntaje(), facil.calcular_puntaje())


func test_calcular_puntaje_aplica_toda_la_tabla_de_bonos() -> void:
	var bonos_esperados := {
		2: 10000,
		3: 5500,
		4: 2800,
		5: 1400,
		6: 700,
		7: 350,
		8: 180,
	}
	for pilas_finales_variant in bonos_esperados:
		var pilas_finales: int = pilas_finales_variant
		var juego := Juego.new(Carta.Dificultad.FACIL)
		juego.tablero.pilas = _pilas_simuladas(pilas_finales)
		var bono: int = bonos_esperados[pilas_finales]
		var esperado: int = (40 - pilas_finales) * 10 + bono
		assert_eq(juego.calcular_puntaje(), esperado)


func test_juego_dificil_es_el_default() -> void:
	var juego := Juego.new()
	assert_eq(juego.dificultad, Carta.Dificultad.DIFICIL)
	assert_eq(juego.mazo.quedan_cartas(), 48)


func test_resumen_incluye_la_dificultad() -> void:
	var juego := Juego.new(Carta.Dificultad.FACIL)
	juego.finalizar()
	assert_eq(juego.obtener_resumen()["dificultad"], "facil")


func test_jugada_nueva_que_bloquea_una_antigua_se_registra() -> void:
	var juego := Juego.new()
	# La jugada 0 (oros) es antigua. La 2 también es válida, pero al
	# resolverla cambia el tope de la tercera pila y bloquea la primera.
	for carta in [
		Carta.new(Carta.Palo.OROS, 1), Carta.new(Carta.Palo.COPAS, 2),
		Carta.new(Carta.Palo.OROS, 3), Carta.new(Carta.Palo.BASTOS, 4),
		Carta.new(Carta.Palo.OROS, 5),
	]:
		juego.tablero.agregar_carta_nueva(carta)

	assert_true(juego.intentar_jugada(2))
	assert_eq(juego.oportunidades_antiguas_bloqueadas, 1)
	assert_eq(juego.decisiones_con_bloqueo, 1)


func test_jugada_nueva_que_no_altera_la_antigua_no_es_bloqueo() -> void:
	var juego := Juego.new()
	for carta in [
		Carta.new(Carta.Palo.OROS, 1), Carta.new(Carta.Palo.COPAS, 2),
		Carta.new(Carta.Palo.OROS, 3), Carta.new(Carta.Palo.BASTOS, 4),
		Carta.new(Carta.Palo.COPAS, 5), Carta.new(Carta.Palo.BASTOS, 6),
	]:
		juego.tablero.agregar_carta_nueva(carta)

	# 0 es válida por oros; 3 es válida por bastos y no toca sus pilas.
	assert_true(juego.intentar_jugada(3))
	assert_eq(juego.oportunidades_antiguas_bloqueadas, 0)


func test_referencia_viejo_primero_y_eficiencia_usan_la_misma_mano() -> void:
	var juego := Juego.new()
	# El último elemento se reparte primero: Oros 1, Copas 2, Oros 3.
	juego.cartas_iniciales = [
		Carta.new(Carta.Palo.OROS, 3), Carta.new(Carta.Palo.COPAS, 2), Carta.new(Carta.Palo.OROS, 1),
	]
	juego.cantidad_cartas_inicial = 3
	for carta in [
		Carta.new(Carta.Palo.OROS, 1), Carta.new(Carta.Palo.COPAS, 2), Carta.new(Carta.Palo.OROS, 3),
	]:
		juego.tablero.agregar_carta_nueva(carta)

	assert_eq(juego.pilas_referencia_viejo_primero(), 2)
	assert_true(juego.intentar_jugada(0))
	assert_eq(juego.eficiencia_tactica(), 100.0)
