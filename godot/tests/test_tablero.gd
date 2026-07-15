extends GutTest


func test_pila_tope_es_la_ultima_carta() -> void:
	var pila := Tablero.Pila.new(Carta.new(Carta.Palo.OROS, 5))
	assert_eq(pila.tope().valor, 5)
	assert_eq(pila.tope().palo, Carta.Palo.OROS)


func test_apilar_encima_conserva_ambas_cartas() -> void:
	var pila_1 := Tablero.Pila.new(Carta.new(Carta.Palo.OROS, 5))
	var pila_2 := Tablero.Pila.new(Carta.new(Carta.Palo.COPAS, 9))
	pila_1.apilar_encima(pila_2)
	assert_eq(pila_1.cantidad_cartas(), 2)
	assert_eq(pila_1.tope().valor, 9)


func test_tablero_agregar_carta_nueva_crea_pila() -> void:
	var tablero := Tablero.new()
	tablero.agregar_carta_nueva(Carta.new(Carta.Palo.OROS, 1))
	assert_eq(tablero.cantidad_pilas(), 1)
	tablero.agregar_carta_nueva(Carta.new(Carta.Palo.COPAS, 2))
	assert_eq(tablero.cantidad_pilas(), 2)


func test_fusionar_reduce_una_pila_y_conserva_las_cartas() -> void:
	var tablero := Tablero.new()
	tablero.agregar_carta_nueva(Carta.new(Carta.Palo.OROS, 7))
	tablero.agregar_carta_nueva(Carta.new(Carta.Palo.COPAS, 3))
	tablero.agregar_carta_nueva(Carta.new(Carta.Palo.OROS, 9))

	tablero.fusionar(0, 1)

	assert_eq(tablero.cantidad_pilas(), 2)
	assert_eq(tablero.pilas[0].cantidad_cartas(), 2)
	assert_eq(tablero.pilas[0].tope().valor, 3)
	assert_eq(tablero.pilas[1].tope().valor, 9)
