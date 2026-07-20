extends Control

## Capa de interacción. No altera las reglas ni el estado puro.
## Terminar la partida es SIEMPRE decisión del jugador: el motor no
## fuerza el fin solo porque detecte que no quedan jugadas, porque
## encontrar la coincidencia es la habilidad del juego (ver reglas.gd).
## Lo único que habilita el botón "Terminar partida" es que se acabe
## el mazo; a partir de ahí, la decisión de cortar es del jugador.

const ESCENA_PILA := preload("res://scenes/pila_visual.tscn")
# load() en vez de preload(): ver el comentario en selector_dificultad.gd
# (mismo motivo — esta escena también vuelve al menú principal, que
# preload-ea el selector que a su vez preload-eaba el tablero: ciclo).
var ESCENA_MENU := load("res://scenes/menu_principal.tscn")
const TAMANIO_CASILLERO := Vector2(170, 261) # igual al custom_minimum_size de PilaVisual

const ESTILO_PELIGRO := preload("res://assets/estilos/boton_peligro.tres")
const ESTILO_PELIGRO_HOVER := preload("res://assets/estilos/boton_peligro_hover.tres")
const ESTILO_SECUNDARIO := preload("res://assets/estilos/boton_secundario.tres")
const ESTILO_SECUNDARIO_HOVER := preload("res://assets/estilos/boton_secundario_hover.tres")

@onready var grilla_pilas: GridContainer = $Margen/Columna/TableroScroll/Centro/Pilas
@onready var boton_mazo: MazoVisual = $Margen/Columna/Mazo
@onready var boton_finalizar: Button = $Margen/Columna/Finalizar
@onready var estado_label: Label = $Margen/Columna/EncabezadoPanel/Encabezado/TituloYEstado/Estado
@onready var tiempo_label: Label = $Margen/Columna/EncabezadoPanel/Encabezado/ChipTiempo/Fila/Tiempo
@onready var mensaje_label: Label = $Margen/Columna/Mensaje

@onready var boton_menu_hamburguesa: Button = $Margen/Columna/EncabezadoPanel/Encabezado/BotonMenu
@onready var menu_pausa: Control = $MenuPausa
@onready var tarjeta_pausa: Control = $MenuPausa/Centro/Tarjeta
@onready var boton_continuar: Button = $MenuPausa/Centro/Tarjeta/Columna/Continuar
@onready var boton_reiniciar: Button = $MenuPausa/Centro/Tarjeta/Columna/Reiniciar
@onready var boton_ajustes: Button = $MenuPausa/Centro/Tarjeta/Columna/Ajustes
@onready var ajustes: Control = $AjustesOverlay
@onready var boton_volver_menu_pausa: Button = $MenuPausa/Centro/Tarjeta/Columna/VolverMenu
@onready var aviso_confirmacion: Label = $MenuPausa/Centro/Tarjeta/Columna/AvisoConfirmacion

@onready var pantalla_fin: Control = $PantallaFin
@onready var tarjeta_fin: Control = $PantallaFin/Centro/Tarjeta
@onready var interpretacion_label: Label = $PantallaFin/Centro/Tarjeta/Fila/ZonaMedallon/Interpretacion
@onready var valor_puntaje: Label = $PantallaFin/Centro/Tarjeta/Fila/ZonaMedallon/Medallon/Columna/Valor
@onready var valor_pilas: Label = $PantallaFin/Centro/Tarjeta/Fila/ZonaDetalle/Estadisticas/ValorPilas
@onready var valor_movimientos: Label = $PantallaFin/Centro/Tarjeta/Fila/ZonaDetalle/Estadisticas/ValorMovimientos
@onready var valor_duracion: Label = $PantallaFin/Centro/Tarjeta/Fila/ZonaDetalle/Estadisticas/ValorDuracion
@onready var campo_nombre: LineEdit = $PantallaFin/Centro/Tarjeta/Fila/ZonaDetalle/Nombre
@onready var boton_guardar_record: Button = $PantallaFin/Centro/Tarjeta/Fila/ZonaDetalle/GuardarRecord
@onready var mensaje_guardado_label: Label = $PantallaFin/Centro/Tarjeta/Fila/ZonaDetalle/MensajeGuardado
@onready var boton_jugar_de_nuevo: Button = $PantallaFin/Centro/Tarjeta/Fila/ZonaDetalle/Botones/JugarDeNuevo
@onready var boton_volver_menu_fin: Button = $PantallaFin/Centro/Tarjeta/Fila/ZonaDetalle/Botones/VolverMenu

@onready var sonido_repartir: AudioStreamPlayer = $SonidoRepartir
@onready var sonido_movimiento: AudioStreamPlayer = $SonidoMovimiento
@onready var temporizador_ui: Timer = $TemporizadorUI
@onready var temporizador_mensaje: Timer = $TemporizadorMensaje
@onready var temporizador_confirmacion: Timer = $TemporizadorConfirmacion

var juego := Juego.new(EstadoJuego.dificultad_seleccionada)
var indice_seleccionado := -1
var resumen_final: Dictionary = {}

## Acciones destructivas (Reiniciar / Volver al menú desde pausa) piden un
## segundo toque para ejecutarse, en vez de actuar directo. Guardamos acá
## cuál botón está "armado" (esperando confirmación) para poder desarmarlo
## si se toca otro botón, se cierra el menú, o pasa el tiempo de espera.
var _boton_armado: Button = null
var _texto_original_por_boton: Dictionary = {}


func _ready() -> void:
	boton_mazo.pressed.connect(_al_tocar_mazo)
	boton_finalizar.pressed.connect(_al_tocar_finalizar)

	boton_menu_hamburguesa.pressed.connect(_al_tocar_hamburguesa)
	boton_continuar.pressed.connect(_al_tocar_continuar)
	$MenuPausa/Fondo.pressed.connect(_al_tocar_continuar)
	boton_reiniciar.pressed.connect(_armar_o_confirmar.bind(boton_reiniciar, _al_tocar_reiniciar))
	boton_ajustes.pressed.connect(_al_tocar_ajustes)
	boton_volver_menu_pausa.pressed.connect(_armar_o_confirmar.bind(boton_volver_menu_pausa, _al_tocar_volver_menu))
	temporizador_confirmacion.timeout.connect(_al_vencer_confirmacion)

	boton_guardar_record.pressed.connect(_al_tocar_guardar_record)
	boton_jugar_de_nuevo.pressed.connect(_al_tocar_reiniciar)
	boton_volver_menu_fin.pressed.connect(_al_tocar_volver_menu)

	temporizador_ui.timeout.connect(_actualizar_tiempo)

	# La grilla arranca con SU ancho fijo (5 columnas de cartas), no con
	# el ancho que ocupen las pilas que haya en ese momento. Si no, cada
	# vez que se reparte una carta nueva, el GridContainer crece un
	# casillero y el HBoxContainer que lo centra ("Centro") lo vuelve a
	# recentrar en pantalla — dando la sensación de que la fila entera
	# "se desliza" hacia la izquierda con cada carta repartida, en vez
	# de que la primera carta quede clavada en el primer casillero desde
	# el arranque.
	var separacion: int = grilla_pilas.get_theme_constant("h_separation")
	grilla_pilas.custom_minimum_size.x = grilla_pilas.columns * TAMANIO_CASILLERO.x \
		+ (grilla_pilas.columns - 1) * separacion

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
	_desarmar_confirmacion()
	_mostrar_con_animacion(menu_pausa, tarjeta_pausa)


func _al_tocar_continuar() -> void:
	_desarmar_confirmacion()
	menu_pausa.visible = false


## Ajustes se abre ENCIMA del juego (no dentro de la tarjeta de pausa):
## se cierra la pausa y se muestra el overlay. Al cerrar Ajustes, el
## jugador vuelve directo a la partida, no de nuevo al menú de pausa —
## mismo patrón que "Configuración" en la mayoría de las apps móviles.
func _al_tocar_ajustes() -> void:
	_desarmar_confirmacion()
	menu_pausa.visible = false
	ajustes.mostrar()


func _al_tocar_reiniciar() -> void:
	get_tree().reload_current_scene()


func _al_tocar_volver_menu() -> void:
	get_tree().change_scene_to_packed(ESCENA_MENU)


## Primer toque: arma el botón (cambia a estilo de peligro y pide
## confirmar). Segundo toque sobre el MISMO botón, antes de que venza el
## temporizador: recién ahí ejecuta la acción. Evita perder una partida
## por un toque accidental, sin necesitar un cuadro de diálogo aparte.
func _armar_o_confirmar(boton: Button, accion: Callable) -> void:
	if _boton_armado == boton:
		_desarmar_confirmacion()
		accion.call()
		return

	_desarmar_confirmacion()
	_boton_armado = boton
	if not _texto_original_por_boton.has(boton):
		_texto_original_por_boton[boton] = boton.text

	boton.text = "¿Seguro? Tocá de nuevo"
	boton.add_theme_stylebox_override("normal", ESTILO_PELIGRO)
	boton.add_theme_stylebox_override("hover", ESTILO_PELIGRO_HOVER)
	boton.add_theme_stylebox_override("pressed", ESTILO_PELIGRO_HOVER)
	aviso_confirmacion.visible = true
	temporizador_confirmacion.start()


func _desarmar_confirmacion() -> void:
	temporizador_confirmacion.stop()
	aviso_confirmacion.visible = false
	if _boton_armado == null:
		return
	if _texto_original_por_boton.has(_boton_armado):
		_boton_armado.text = _texto_original_por_boton[_boton_armado]
	_boton_armado.add_theme_stylebox_override("normal", ESTILO_SECUNDARIO)
	_boton_armado.add_theme_stylebox_override("hover", ESTILO_SECUNDARIO_HOVER)
	_boton_armado.add_theme_stylebox_override("pressed", ESTILO_SECUNDARIO_HOVER)
	_boton_armado = null


func _al_vencer_confirmacion() -> void:
	_desarmar_confirmacion()


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
	valor_puntaje.text = str(resumen_final["puntaje"])
	valor_pilas.text = str(resumen_final["pilas_finales"])
	valor_movimientos.text = str(resumen_final["movimientos"])
	valor_duracion.text = Puntuacion.formatear_duracion(resumen_final["duracion_segundos"])
	mensaje_guardado_label.visible = false
	boton_guardar_record.disabled = false
	campo_nombre.editable = true
	campo_nombre.text = ""
	_mostrar_con_animacion(pantalla_fin, tarjeta_fin)


## Entrada suave para los paneles superpuestos (pausa / fin de partida):
## la tarjeta aparece con un ligero "pop" (escala 0.9 -> 1.0 con rebote)
## mientras el fondo oscuro se desvanece. Aparecer de golpe, sin
## transición, se siente brusco en una pantalla táctil; esta animación es
## corta (~0.2s) para no demorar al jugador.
func _mostrar_con_animacion(overlay: Control, tarjeta: Control) -> void:
	overlay.visible = true
	overlay.modulate.a = 0.0
	tarjeta.scale = Vector2(0.9, 0.9)
	await get_tree().process_frame  # esperamos un frame para que 'tarjeta' ya tenga su tamaño final
	tarjeta.pivot_offset = tarjeta.size / 2
	var animacion := create_tween().set_parallel(true)
	animacion.tween_property(overlay, "modulate:a", 1.0, 0.16)
	animacion.tween_property(tarjeta, "scale", Vector2.ONE, 0.22)\
		.set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)


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
