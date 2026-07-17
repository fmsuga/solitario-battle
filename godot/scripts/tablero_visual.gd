extends Control

## Capa de interacción. No altera las reglas ni el estado puro.
## Terminar la partida es SIEMPRE decisión del jugador: el motor no
## fuerza el fin solo porque detecte que no quedan jugadas, porque
## encontrar la coincidencia es la habilidad del juego (ver reglas.gd).
## Lo único que habilita el botón "Terminar partida" es que se acabe
## el mazo; a partir de ahí, la decisión de cortar es del jugador.

const ESCENA_PILA := preload("res://scenes/pila_visual.tscn")
const ESCENA_MENU := preload("res://scenes/menu_principal.tscn")
const TAMANIO_CASILLERO := Vector2(170, 261) # igual al custom_minimum_size de PilaVisual

@onready var grilla_pilas: GridContainer = $Margen/Columna/TableroScroll/Centro/Pilas
@onready var boton_mazo: MazoVisual = $Margen/Columna/Mazo
@onready var boton_finalizar: Button = $Margen/Columna/Finalizar
@onready var estado_label: Label = $Margen/Columna/InfoFila/Estado
@onready var tiempo_label: Label = $Margen/Columna/InfoFila/Tiempo
@onready var mensaje_label: Label = $Margen/Columna/Mensaje

@onready var boton_menu_hamburguesa: Button = $BotonMenu
@onready var menu_pausa: Control = $MenuPausa
@onready var boton_continuar: Button = $MenuPausa/Centro/Tarjeta/Columna/Continuar
@onready var boton_reiniciar: Button = $MenuPausa/Centro/Tarjeta/Columna/Reiniciar
@onready var boton_volver_menu_pausa: Button = $MenuPausa/Centro/Tarjeta/Columna/VolverMenu

@onready var pantalla_fin: Control = $PantallaFin
@onready var interpretacion_label: Label = $PantallaFin/Centro/Tarjeta/Columna/Interpretacion
@onready var estadisticas_label: Label = $PantallaFin/Centro/Tarjeta/Columna/Estadisticas
@onready var campo_nombre: LineEdit = $PantallaFin/Centro/Tarjeta/Columna/Nombre
@onready var boton_guardar_record: Button = $PantallaFin/Centro/Tarjeta/Columna/GuardarRecord
@onready var mensaje_guardado_label: Label = $PantallaFin/Centro/Tarjeta/Columna/MensajeGuardado
@onready var boton_jugar_de_nuevo: Button = $PantallaFin/Centro/Tarjeta/Columna/Botones/JugarDeNuevo
@onready var boton_volver_menu_fin: Button = $PantallaFin/Centro/Tarjeta/Columna/Botones/VolverMenu

@onready var sonido_repartir: AudioStreamPlayer = $SonidoRepartir
@onready var sonido_movimiento: AudioStreamPlayer = $SonidoMovimiento
@onready var temporizador_ui: Timer = $TemporizadorUI
@onready var temporizador_mensaje: Timer = $TemporizadorMensaje

var juego := Juego.new(EstadoJuego.dificultad_seleccionada)
var indice_seleccionado := -1
var resumen_final: Dictionary = {}


func _ready() -> void:
	boton_mazo.pressed.connect(_al_tocar_mazo)
	boton_finalizar.pressed.connect(_al_tocar_finalizar)

	boton_menu_hamburguesa.pressed.connect(_al_tocar_hamburguesa)
	boton_continuar.pressed.connect(_al_tocar_continuar)
	boton_reiniciar.pressed.connect(_al_tocar_reiniciar)
	boton_volver_menu_pausa.pressed.connect(_al_tocar_volver_menu)

	boton_guardar_record.pressed.connect(_al_tocar_guardar_record)
	boton_jugar_de_nuevo.pressed.connect(_al_tocar_reiniciar)
	boton_volver_menu_fin.pressed.connect(_al_tocar_volver_menu)

	temporizador_ui.timeout.connect(_actualizar_tiempo)

	_refrescar_tablero()


func _al_tocar_mazo() -> void:
	if juego.esta_terminada():
		return
	if not juego.quedan_cartas_en_mano():
		return

	juego.repartir_carta()
	sonido_repartir.play()
	indice_seleccionado = -1
	_refrescar_tablero()


func _al_tocar_pila(indice: int) -> void:
	if juego.esta_terminada():
		return

	if indice_seleccionado == -1:
		indice_seleccionado = indice
		_refrescar_tablero()
		return

	var indice_pila_a_mover := indice_seleccionado
	var indice_destino := indice
	indice_seleccionado = -1

	if indice_pila_a_mover != indice_destino + 1:
		# No es una jugada válida para intentar (no son adyacentes):
		# no regañamos, tratamos el toque como una nueva selección.
		indice_seleccionado = indice
		_refrescar_tablero()
		return

	if juego.intentar_jugada(indice_destino):
		sonido_movimiento.play()
		_mostrar_mensaje_temporal("¡Buena jugada!")
	else:
		_mostrar_mensaje_temporal("Ahí no hay coincidencia.")
	_refrescar_tablero()


func _al_tocar_finalizar() -> void:
	if juego.esta_terminada() or juego.quedan_cartas_en_mano():
		return
	juego.finalizar()
	resumen_final = juego.obtener_resumen()
	_mostrar_pantalla_fin()
	_refrescar_tablero()


func _al_tocar_hamburguesa() -> void:
	menu_pausa.visible = true


func _al_tocar_continuar() -> void:
	menu_pausa.visible = false


func _al_tocar_reiniciar() -> void:
	get_tree().reload_current_scene()


func _al_tocar_volver_menu() -> void:
	get_tree().change_scene_to_packed(ESCENA_MENU)


func _al_tocar_guardar_record() -> void:
	var nombre := campo_nombre.text.strip_edges()
	if nombre.is_empty():
		nombre = "Jugador"
	Puntuacion.guardar_puntaje(nombre, resumen_final)
	mensaje_guardado_label.visible = true
	boton_guardar_record.disabled = true
	campo_nombre.editable = false


func _mostrar_pantalla_fin() -> void:
	interpretacion_label.text = Puntuacion.interpretar_resultado(resumen_final["pilas_finales"])
	estadisticas_label.text = "Puntaje: %d\nPilas finales: %d\nMovimientos: %d\nDuración: %s" % [
		resumen_final["puntaje"],
		resumen_final["pilas_finales"],
		resumen_final["movimientos"],
		Puntuacion.formatear_duracion(resumen_final["duracion_segundos"]),
	]
	mensaje_guardado_label.visible = false
	boton_guardar_record.disabled = false
	campo_nombre.editable = true
	campo_nombre.text = ""
	pantalla_fin.visible = true


func _mostrar_mensaje_temporal(texto: String) -> void:
	mensaje_label.text = texto
	temporizador_mensaje.stop()
	temporizador_mensaje.start()
	if not temporizador_mensaje.timeout.is_connected(_ocultar_mensaje):
		temporizador_mensaje.timeout.connect(_ocultar_mensaje)


func _ocultar_mensaje() -> void:
	mensaje_label.text = ""


func _actualizar_tiempo() -> void:
	if juego.esta_terminada():
		temporizador_ui.stop()
		return
	tiempo_label.text = Puntuacion.formatear_duracion(juego.duracion_segundos())


func _refrescar_tablero() -> void:
	for hijo in grilla_pilas.get_children():
		hijo.queue_free()

	for casillero in _orden_visual(juego.tablero.cantidad_pilas(), grilla_pilas.columns):
		if casillero == -1:
			var vacio := Control.new()
			vacio.custom_minimum_size = TAMANIO_CASILLERO
			grilla_pilas.add_child(vacio)
			continue
		var indice: int = casillero
		var visual := ESCENA_PILA.instantiate() as PilaVisual
		grilla_pilas.add_child(visual)
		visual.mostrar_pila(juego.tablero.pilas[indice], indice, indice == indice_seleccionado)
		visual.pressed.connect(_al_tocar_pila.bind(indice))

	var cartas_restantes := juego.mazo.quedan_cartas()
	estado_label.text = "Pilas: %d | Cartas en mazo: %d" % [juego.tablero.cantidad_pilas(), cartas_restantes]
	boton_mazo.disabled = juego.esta_terminada() or cartas_restantes == 0
	boton_mazo.mostrar_cantidad(cartas_restantes)
	boton_finalizar.visible = cartas_restantes == 0 and not juego.esta_terminada()


func _orden_visual(cantidad: int, columnas: int) -> Array:
	## Arma el orden de aparición "en víbora": la fila 0 se llena de
	## izquierda a derecha, la fila 1 de derecha a izquierda, la 2 de
	## nuevo izquierda a derecha, y así — para que la última pila de
	## cada fila quede pegada a la primera de la fila siguiente, tal
	## como se juega en la mesa real.
	##
	## Mientras una fila impar (derecha a izquierda) está incompleta,
	## esta función antepone casilleros vacíos (-1) del lado izquierdo,
	## para que las cartas ya repartidas queden ancladas del lado
	## derecho y no se corran cuando se reparte una carta nueva.
	var casilleros: Array = []
	var fila := 0
	var inicio := 0
	while inicio < cantidad:
		var fin: int = min(inicio + columnas, cantidad)
		var segmento: Array = range(inicio, fin)
		if fila % 2 == 1:
			segmento.reverse()
			var huecos := columnas - (fin - inicio)
			for _i in range(huecos):
				casilleros.append(-1)
		casilleros.append_array(segmento)
		inicio = fin
		fila += 1
	return casilleros
