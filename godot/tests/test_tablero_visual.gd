extends GutTest

const ESCENA_TABLERO := preload("res://scenes/tablero.tscn")


func test_flujo_visual_reparte_valida_invalida_y_finaliza() -> void:
	var vista = ESCENA_TABLERO.instantiate()
	vista.juego = Juego.new(Carta.Dificultad.FACIL)
	add_child_autofree(vista)

	vista._al_tocar_mazo()
	assert_eq(vista.juego.tablero.cantidad_pilas(), 1)
	assert_string_contains(vista.mensaje_label.text, "Carta repartida")

	vista.juego.tablero = Tablero.new()
	vista.juego.tablero.agregar_carta_nueva(Carta.new(Carta.Palo.OROS, 1))
	vista.juego.tablero.agregar_carta_nueva(Carta.new(Carta.Palo.COPAS, 4))
	vista.juego.tablero.agregar_carta_nueva(Carta.new(Carta.Palo.ESPADAS, 7))
	vista._refrescar_tablero()
	vista._al_tocar_pila(1)
	vista._al_tocar_pila(0)
	assert_string_contains(vista.mensaje_label.text, "no hay coincidencia")
	assert_eq(vista.juego.tablero.cantidad_pilas(), 3)

	vista.juego.tablero = Tablero.new()
	vista.juego.tablero.agregar_carta_nueva(Carta.new(Carta.Palo.OROS, 1))
	vista.juego.tablero.agregar_carta_nueva(Carta.new(Carta.Palo.COPAS, 4))
	vista.juego.tablero.agregar_carta_nueva(Carta.new(Carta.Palo.BASTOS, 1))
	vista._refrescar_tablero()
	vista._al_tocar_pila(1)
	vista._al_tocar_pila(0)
	assert_string_contains(vista.mensaje_label.text, "Jugada válida")
	assert_eq(vista.juego.tablero.cantidad_pilas(), 2)

	vista.juego.mazo.cartas.clear()
	vista._verificar_fin_de_partida()
	assert_true(vista.juego.esta_terminada())
	assert_string_contains(vista.mensaje_label.text, "Partida terminada")