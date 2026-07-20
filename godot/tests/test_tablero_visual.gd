extends GutTest

const ESCENA_TABLERO := preload("res://scenes/tablero.tscn")


func test_flujo_visual_reparte_valida_invalida_y_finaliza() -> void:
	var vista = ESCENA_TABLERO.instantiate()
	vista.juego = Juego.new(Carta.Dificultad.FACIL)
	add_child_autofree(vista)

	vista._al_tocar_mazo()
	assert_eq(vista.juego.tablero.cantidad_pilas(), 1)
	assert_eq(vista.mensaje_label.text, "")

	vista.juego.tablero = Tablero.new()
	vista.juego.tablero.agregar_carta_nueva(Carta.new(Carta.Palo.OROS, 1))
	vista.juego.tablero.agregar_carta_nueva(Carta.new(Carta.Palo.COPAS, 4))
	vista.juego.tablero.agregar_carta_nueva(Carta.new(Carta.Palo.ESPADAS, 7))
	vista._refrescar_tablero()
	vista._al_tocar_pila(1)
	vista._al_tocar_pila(1)
	assert_eq(vista.indice_seleccionado, -1)
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
	assert_string_contains(vista.mensaje_label.text, "Buena jugada")
	assert_eq(vista.juego.tablero.cantidad_pilas(), 2)
	while vista._animando_movimiento:
		await get_tree().process_frame

	vista.juego.tablero = Tablero.new()
	vista.juego.tablero.agregar_carta_nueva(Carta.new(Carta.Palo.OROS, 1))
	vista.juego.tablero.agregar_carta_nueva(Carta.new(Carta.Palo.COPAS, 4))
	vista.juego.tablero.agregar_carta_nueva(Carta.new(Carta.Palo.BASTOS, 1))
	vista._refrescar_tablero()
	vista._intentar_arrastre(1, 0)
	assert_eq(vista.juego.tablero.cantidad_pilas(), 2)
	while vista._animando_movimiento:
		await get_tree().process_frame

	vista.juego.mazo.cartas.clear()
	vista._refrescar_tablero()
	vista._al_tocar_mazo()
	assert_false(vista.juego.esta_terminada())
	assert_true(vista.boton_terminar_partida.visible)
	vista._al_tocar_finalizar()
	assert_true(vista.juego.esta_terminada())
	assert_true(vista.pantalla_fin.visible)
