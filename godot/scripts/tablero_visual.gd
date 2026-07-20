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
const ESTILO_PELIGRO_PRESIONADO := preload("res://assets/estilos/boton_peligro_presionado.tres")
const ESTILO_SECUNDARIO := preload("res://assets/estilos/boton_secundario.tres")
const ESTILO_SECUNDARIO_HOVER := preload("res://assets/estilos/boton_secundario_hover.tres")
const ESTILO_SECUNDARIO_PRESIONADO := preload("res://assets/estilos/boton_secundario_presionado.tres")

@onready var grilla_pilas: GridContainer = $Margen/Columna/TableroScroll/Centro/Pilas
@onready var boton_mazo: MazoVisual = $Margen/Columna/MazoYTiempo/Mazo
@onready var boton_terminar_partida: Button = $Margen/Columna/MazoYTiempo/TerminarPartida
@onready var estado_label: Label = $Margen/Columna/EncabezadoPanel/Encabezado/TituloYEstado/Estado
@onready var tiempo_principal_label: Label = $Margen/Columna/EncabezadoPanel/Encabezado/Reloj/Pantalla/TiempoPrincipal
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
@onready var analisis_tactico_label: Label = $PantallaFin/Centro/Tarjeta/Fila/ZonaDetalle/AnalisisTactico
@onready var logros_label: Label = $PantallaFin/Centro/Tarjeta/Fila/ZonaDetalle/Logros
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
var _animando_movimiento := false
var _accion_finalizar_visible := false
var _animacion_fusion: Tween = null
var _animacion_accion_final: Tween = null

## Acciones destructivas (Reiniciar / Volver al menú desde pausa) piden un
## segundo toque para ejecutarse, en vez de actuar directo. Guardamos acá
## cuál botón está "armado" (esperando confirmación) para poder desarmarlo
## si se toca otro botón, se cierra el menú, o pasa el tiempo de espera.
var _boton_armado: Button = null
var _texto_original_por_boton: Dictionary = {}


func _ready() -> void:
	boton_mazo.pressed.connect(_al_tocar_mazo)
	boton_terminar_partida.pressed.connect(_al_tocar_finalizar)

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
	_actualizar_tiempo()


func _al_tocar_mazo() -> void:
	if juego.esta_terminada() or _animando_movimiento:
		return
	if not juego.quedan_cartas_en_mano():
		return

	juego.repartir_carta()
	sonido_repartir.play()
	indice_seleccionado = -1
	_refrescar_tablero()


func _al_tocar_pila(indice: int) -> void:
	if juego.esta_terminada() or _animando_movimiento:
		return

	if indice_seleccionado == -1:
		indice_seleccionado = indice
		_refrescar_tablero()
		return
	if indice_seleccionado == indice:
		indice_seleccionado = -1
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
		_confirmar_fusion(indice_destino)
	else:
		_mostrar_mensaje_temporal("Ahí no hay coincidencia.")
		_refrescar_tablero()


func _al_tocar_finalizar() -> void:
	if juego.esta_terminada() or juego.quedan_cartas_en_mano() or _animando_movimiento:
		return
	juego.finalizar()
	_actualizar_tiempo()
	resumen_final = juego.obtener_resumen()
	_mostrar_pantalla_fin()
	_refrescar_tablero()


func _al_soltar_arrastre(indice_origen: int, posicion_global: Vector2) -> void:
	var indice_destino := _indice_pila_en_posicion(posicion_global)
	if indice_destino != -1:
		_intentar_arrastre(indice_origen, indice_destino)


func _intentar_arrastre(indice_origen: int, indice_destino: int) -> void:
	if _animando_movimiento:
		return
	indice_seleccionado = -1
	if indice_origen == indice_destino or indice_origen != indice_destino + 1:
		_refrescar_tablero()
		return
	if juego.intentar_jugada(indice_destino):
		_confirmar_fusion(indice_destino)
	else:
		_mostrar_mensaje_temporal("Ahí no hay coincidencia.")
		_refrescar_tablero()


func _indice_pila_en_posicion(posicion_global: Vector2) -> int:
	for visual in grilla_pilas.get_children():
		if visual is PilaVisual and visual.get_global_rect().has_point(posicion_global):
			return visual.indice_pila
	return -1


func _confirmar_fusion(indice_destino: int) -> void:
	_animando_movimiento = true
	sonido_movimiento.play()
	_mostrar_mensaje_temporal("¡Buena jugada!")
	_animar_fusion(indice_destino)


func _animar_fusion(indice_destino: int) -> void:
	var destino := _visual_de_indice(indice_destino)
	var absorbida := _visual_de_indice(indice_destino + 1)
	if destino == null or absorbida == null:
		_refrescar_tablero()
		_animando_movimiento = false
		return

	var escala_destino := destino.scale
	# La fusión se confirma con el mismo lenguaje de la selección: un
	# acercamiento breve y elástico. La pila que desaparece sólo se apaga;
	# no se la desplaza hacia la otra, porque eso sugería una interacción
	# distinta a la de combinar dos pilas adyacentes.
	var impulso := create_tween().set_parallel(true)
	_animacion_fusion = impulso
	impulso.tween_property(destino, "scale", escala_destino * 1.09, 0.12)\
		.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	impulso.tween_property(absorbida, "scale", absorbida.scale * 0.96, 0.12)\
		.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
	impulso.tween_property(absorbida, "modulate:a", 0.0, 0.12)
	await impulso.finished
	if _animacion_fusion != impulso:
		return
	if not is_instance_valid(destino) or not is_instance_valid(absorbida):
		_animacion_fusion = null
		_animando_movimiento = false
		return

	var rebote := create_tween()
	_animacion_fusion = rebote
	rebote.tween_property(destino, "scale", escala_destino, 0.22)\
		.set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	await rebote.finished
	if _animacion_fusion != rebote:
		return
	_animacion_fusion = null
	_refrescar_tablero()
	_animando_movimiento = false


func _visual_de_indice(indice: int) -> PilaVisual:
	for visual in grilla_pilas.get_children():
		if visual is PilaVisual and visual.indice_pila == indice:
			return visual
	return null


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
	boton.add_theme_stylebox_override("pressed", ESTILO_PELIGRO_PRESIONADO)
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
	_boton_armado.add_theme_stylebox_override("pressed", ESTILO_SECUNDARIO_PRESIONADO)
	_boton_armado = null


func _al_vencer_confirmacion() -> void:
	_desarmar_confirmacion()


func _al_tocar_guardar_record() -> void:
	var nombre := campo_nombre.text.strip_edges()
	if nombre.is_empty():
		nombre = "Jugador"
	Puntuacion.guardar_puntaje(nombre, resumen_final)

	EstadoJuego.ultimo_registro_guardado = resumen_final.duplicate()
	EstadoJuego.ultimo_registro_guardado["jugador"] = nombre
	# Fuego y olvido: si falla (sin conexión, Supabase caído) no rompe
	# nada, el guardado local de arriba ya es la fuente de verdad.
	RecordsOnline.enviar_record(nombre, resumen_final)

	mensaje_guardado_label.visible = true
	boton_guardar_record.disabled = true
	campo_nombre.editable = false


func _mostrar_pantalla_fin() -> void:
	interpretacion_label.text = Puntuacion.mensaje_rareza(resumen_final)
	valor_puntaje.text = str(resumen_final["puntaje"])
	valor_pilas.text = str(resumen_final["pilas_finales"])
	valor_movimientos.text = str(resumen_final["movimientos"])
	valor_duracion.text = Puntuacion.formatear_duracion(resumen_final["duracion_segundos"])
	analisis_tactico_label.text = Puntuacion.mensaje_analisis_tactico(resumen_final)
	var logros := Puntuacion.logros_nuevos(resumen_final, Puntuacion.cargar_historial())
	logros_label.text = "\n".join(logros)
	logros_label.visible = not logros.is_empty()
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
	var tiempo := juego.duracion_segundos_precisa()
	var segundos_totales := int(tiempo)
	tiempo_principal_label.text = "%02d:%02d:%02d" % [segundos_totales / 3600, (segundos_totales / 60) % 60, segundos_totales % 60]
	if juego.esta_terminada():
		temporizador_ui.stop()


func _refrescar_tablero() -> void:
	if _animacion_fusion != null:
		_animacion_fusion.kill()
		_animacion_fusion = null
		_animando_movimiento = false
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
		visual.tocada.connect(_al_tocar_pila)
		visual.arrastre_soltado.connect(_al_soltar_arrastre)

	var cartas_restantes := juego.mazo.quedan_cartas()
	estado_label.text = "Pilas: %d  ·  Mazo: %d  ·  Mov.: %d" % [juego.tablero.cantidad_pilas(), cartas_restantes, juego.cantidad_jugadas_realizadas]
	boton_mazo.disabled = juego.esta_terminada()
	boton_mazo.mostrar_cantidad(cartas_restantes)
	var mostrar_finalizar := cartas_restantes == 0 and not juego.esta_terminada()
	if mostrar_finalizar and not _accion_finalizar_visible:
		_mostrar_accion_finalizar()
	elif not mostrar_finalizar:
		boton_mazo.visible = true
		boton_mazo.scale = Vector2.ONE
		boton_terminar_partida.visible = false
		boton_terminar_partida.scale = Vector2.ONE
	_accion_finalizar_visible = mostrar_finalizar


func _mostrar_accion_finalizar() -> void:
	# El mazo se cierra sobre su eje horizontal y revela la acción en el
	# mismo lugar. No hay cambio de color ni efecto de hover: sólo la
	# transición espacial entre ambas acciones.
	if _animacion_accion_final != null:
		_animacion_accion_final.kill()
	boton_mazo.pivot_offset = boton_mazo.size / 2.0
	boton_terminar_partida.pivot_offset = boton_terminar_partida.size / 2.0
	boton_terminar_partida.visible = true
	boton_terminar_partida.modulate.a = 1.0
	boton_terminar_partida.scale = Vector2(0.01, 1.0)
	var transicion := create_tween()
	_animacion_accion_final = transicion
	transicion.tween_property(boton_mazo, "scale:x", 0.01, 0.16)\
		.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
	transicion.tween_callback(func() -> void: boton_mazo.visible = false)
	transicion.tween_property(boton_terminar_partida, "scale:x", 1.0, 0.22)\
		.set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)


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
