extends GutTest


func test_mismo_valor() -> void:
	var a := Carta.new(Carta.Palo.OROS, 7)
	var b := Carta.new(Carta.Palo.COPAS, 7)
	var c := Carta.new(Carta.Palo.OROS, 3)
	assert_true(a.mismo_valor(b))
	assert_false(a.mismo_valor(c))


func test_mismo_palo() -> void:
	var a := Carta.new(Carta.Palo.OROS, 7)
	var b := Carta.new(Carta.Palo.OROS, 3)
	var c := Carta.new(Carta.Palo.COPAS, 7)
	assert_true(a.mismo_palo(b))
	assert_false(a.mismo_palo(c))


func test_to_string_as_y_numeros() -> void:
	assert_eq(Carta.new(Carta.Palo.OROS, 1)._to_string(), "As de Oro")
	assert_eq(Carta.new(Carta.Palo.ESPADAS, 10)._to_string(), "10 de Espada")
	assert_eq(Carta.new(Carta.Palo.BASTOS, 12)._to_string(), "12 de Basto")


func test_mazo_tiene_48_cartas_unicas() -> void:
	var mazo := Carta.Mazo.new()
	assert_eq(mazo.quedan_cartas(), Carta.CANTIDAD_CARTAS_EN_MAZO)

	var combinaciones := {}
	for carta in mazo.cartas:
		combinaciones["%d:%d" % [carta.palo, carta.valor]] = true
	assert_eq(combinaciones.size(), Carta.CANTIDAD_CARTAS_EN_MAZO)


func test_repartir_una_reduce_el_mazo() -> void:
	var mazo := Carta.Mazo.new()
	var total_inicial := mazo.quedan_cartas()
	var carta := mazo.repartir_una()
	assert_is(carta, Carta)
	assert_eq(mazo.quedan_cartas(), total_inicial - 1)


func test_mazo_dificil_tiene_48_cartas_con_8_y_9() -> void:
	var mazo := Carta.Mazo.new(Carta.Dificultad.DIFICIL)
	assert_eq(mazo.quedan_cartas(), 48)

	var valores := {}
	for carta in mazo.cartas:
		valores[carta.valor] = true
	assert_true(valores.has(8))
	assert_true(valores.has(9))


func test_mazo_facil_tiene_40_cartas_sin_8_ni_9() -> void:
	var mazo := Carta.Mazo.new(Carta.Dificultad.FACIL)
	assert_eq(mazo.quedan_cartas(), 40)

	var valores := {}
	for carta in mazo.cartas:
		valores[carta.valor] = true
	assert_false(valores.has(8))
	assert_false(valores.has(9))
