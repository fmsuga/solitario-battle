extends GutTest


func _tablero_de_prueba() -> Tablero:
	var tablero := Tablero.new()
	tablero.agregar_carta_nueva(Carta.new(Carta.Palo.OROS, 7))
	tablero.agregar_carta_nueva(Carta.new(Carta.Palo.COPAS, 3))
	tablero.agregar_carta_nueva(Carta.new(Carta.Palo.OROS, 9))
	return tablero


func test_hay_coincidencia_por_valor() -> void:
	assert_true(Reglas.hay_coincidencia(
		Carta.new(Carta.Palo.OROS, 7), Carta.new(Carta.Palo.COPAS, 7)
	))


func test_hay_coincidencia_por_palo() -> void:
	assert_true(Reglas.hay_coincidencia(
		Carta.new(Carta.Palo.OROS, 7), Carta.new(Carta.Palo.OROS, 9)
	))


func test_no_hay_coincidencia() -> void:
	assert_false(Reglas.hay_coincidencia(
		Carta.new(Carta.Palo.OROS, 7), Carta.new(Carta.Palo.COPAS, 9)
	))


func test_es_jugada_valida_detecta_coincidencia() -> void:
	assert_true(Reglas.es_jugada_valida(_tablero_de_prueba(), 0))


func test_es_jugada_valida_fuera_de_rango() -> void:
	var tablero := _tablero_de_prueba()
	assert_false(Reglas.es_jugada_valida(tablero, 1))
	assert_false(Reglas.es_jugada_valida(tablero, -1))


func test_ejecutar_jugada_fusiona_si_es_valida() -> void:
	var tablero := _tablero_de_prueba()
	var resultado := Reglas.ejecutar_jugada(tablero, 0)
	assert_true(resultado)
	assert_eq(tablero.cantidad_pilas(), 2)


func test_ejecutar_jugada_no_hace_nada_si_es_invalida() -> void:
	var tablero := _tablero_de_prueba()
	var resultado := Reglas.ejecutar_jugada(tablero, 1)
	assert_false(resultado)
	assert_eq(tablero.cantidad_pilas(), 3)


func test_buscar_jugadas_posibles() -> void:
	assert_eq(Reglas.buscar_jugadas_posibles(_tablero_de_prueba()), [0])
