extends Control

## Capa de interacción de la Fase 2. No altera las reglas ni el estado puro.

const ESCENA_PILA := preload("res://scenes/pila_visual.tscn")

@onready var grilla_pilas: GridContainer = $Margen/Columna/TableroScroll/Pilas
@onready var boton_mazo: Button = $Margen/Columna/Mazo
@onready var estado_label: Label = $Margen/Columna/Estado
@onready var mensaje_label: Label = $Margen/Columna/Mensaje

var juego := Juego.new()
var indice_seleccionado := -1


func _ready() -> void:
	boton_mazo.pressed.connect(_al_tocar_mazo)
	_refrescar_tablero()


func _al_tocar_mazo() -> void:
	if juego.esta_terminada():
		return
	if not juego.quedan_cartas_en_mano():
		_verificar_fin_de_partida()
		return

	juego.repartir_carta()
	indice_seleccionado = -1
	mensaje_label.text = "Carta repartida."
	_refrescar_tablero()
	_verificar_fin_de_partida()


func _al_tocar_pila(indice: int) -> void:
	if juego.esta_terminada():
		return

	if indice_seleccionado == -1:
		indice_seleccionado = indice
		mensaje_label.text = "Pila %d seleccionada para mover. Tocá la pila donde va a apilarse (la de su izquierda)." % (indice + 1)
		_refrescar_tablero()
		return

	var indice_pila_a_mover := indice_seleccionado
	var indice_destino := indice
	indice_seleccionado = -1

	if indice_pila_a_mover != indice_destino + 1:
		mensaje_label.text = "Para mover esa pila, tocá la que está inmediatamente a su izquierda."
		_refrescar_tablero()
		return

	if juego.intentar_jugada(indice_destino):
		mensaje_label.text = "Jugada válida. Las pilas se fusionaron."
	else:
		mensaje_label.text = "Ahí no hay coincidencia."
	_refrescar_tablero()
	_verificar_fin_de_partida()


func _refrescar_tablero() -> void:
	for hijo in grilla_pilas.get_children():
		hijo.queue_free()

	for indice in range(juego.tablero.cantidad_pilas()):
		var visual := ESCENA_PILA.instantiate() as PilaVisual
		grilla_pilas.add_child(visual)
		visual.mostrar_pila(juego.tablero.pilas[indice], indice, indice == indice_seleccionado)
		visual.pressed.connect(_al_tocar_pila.bind(indice))

	var cartas_restantes := juego.mazo.quedan_cartas()
	estado_label.text = "Pilas: %d | Cartas en mazo: %d" % [juego.tablero.cantidad_pilas(), cartas_restantes]
	boton_mazo.disabled = juego.esta_terminada() or cartas_restantes == 0
	boton_mazo.text = "Mazo vacío" if cartas_restantes == 0 else "Repartir carta (%d)" % cartas_restantes


func _verificar_fin_de_partida() -> void:
	if juego.quedan_cartas_en_mano():
		return
	if not Reglas.buscar_jugadas_posibles(juego.tablero).is_empty():
		mensaje_label.text = "No quedan cartas. Todavía hay jugadas posibles."
		return

	juego.finalizar()
	var resumen := juego.obtener_resumen()
	mensaje_label.text = "Partida terminada - Puntaje: %d | Pilas: %d | Movimientos: %d" % [
		resumen["puntaje"], resumen["pilas_finales"], resumen["movimientos"],
	]
	_refrescar_tablero()
