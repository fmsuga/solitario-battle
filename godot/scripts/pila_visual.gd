class_name PilaVisual
extends Button

signal tocada(indice: int)
signal arrastre_soltado(indice_origen: int, posicion_global: Vector2)

## Muestra la carta real (PNG) con el contador de cartas superpuesto.
##
## La pila "armada" (la que se tocó primero, esperando el segundo toque
## para intentar la jugada) se marca con un anillo grueso + un halo de
## color detrás + un pequeño "pop" de escala al seleccionarse — antes
## era apenas un cambio sutil de color, casi imperceptible.

@onready var imagen_carta: TextureRect = $Imagen
@onready var cantidad_label: Label = $Insignia/Cantidad

const ELEVACION_SELECCIONADA := 20.0
const ESCALA_SELECCIONADA := Vector2(1.06, 1.06)
const UMBRAL_ARRASTRE := 18.0

## Mapea el enum Palo al prefijo de archivo usado en assets/cartas_img/
## (oros_1.png, copas_12.png, etc.) Si el día de mañana se agregan cartas
## comodín u otro mazo, este es el único lugar que hay que tocar.
const PREFIJO_ARCHIVO_POR_PALO := {
	Carta.Palo.OROS: "oros",
	Carta.Palo.COPAS: "copas",
	Carta.Palo.ESPADAS: "espadas",
	Carta.Palo.BASTOS: "bastos",
}

var indice_pila := -1
var _posicion_inicial_toque := Vector2.ZERO
var _arrastrando := false


func _ready() -> void:
	gui_input.connect(_al_evento_gui)


func mostrar_pila(pila: Tablero.Pila, indice: int, seleccionada: bool) -> void:
	indice_pila = indice
	imagen_carta.texture = _textura_de_carta(pila.tope())
	cantidad_label.text = str(pila.cantidad_cartas())
	tooltip_text = "Pila %d: %s" % [indice + 1, pila._to_string()]

	if seleccionada:
		_animar_seleccion()


## _refrescar_tablero() destruye y vuelve a crear las PilaVisual en cada
## jugada, así que esta instancia siempre es nueva cuando llega acá con
## seleccionada=true — no hace falta comparar contra un estado anterior,
## el "pop" se dispara una sola vez, justo cuando aparece marcada.
func _animar_seleccion() -> void:
	position.y -= ELEVACION_SELECCIONADA
	pivot_offset = Vector2(custom_minimum_size.x / 2.0, custom_minimum_size.y)
	scale = Vector2(0.98, 0.98)
	z_index = 1
	var animacion := create_tween()
	animacion.tween_property(self, "scale", ESCALA_SELECCIONADA, 0.16)\
		.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)


func _al_evento_gui(evento: InputEvent) -> void:
	if disabled:
		return
	if evento is InputEventScreenTouch:
		if evento.pressed:
			_iniciar_interaccion(evento.position)
		else:
			_terminar_interaccion(evento.position)
		accept_event()
	elif evento is InputEventScreenDrag:
		_actualizar_arrastre(evento.position)
		accept_event()
	elif evento is InputEventMouseButton and evento.button_index == MOUSE_BUTTON_LEFT:
		if evento.pressed:
			_iniciar_interaccion(evento.position)
		else:
			_terminar_interaccion(evento.position)
		accept_event()
	elif evento is InputEventMouseMotion and evento.button_mask & MOUSE_BUTTON_MASK_LEFT:
		_actualizar_arrastre(evento.position)
		accept_event()


func _iniciar_interaccion(posicion: Vector2) -> void:
	_posicion_inicial_toque = posicion
	_arrastrando = false


func _actualizar_arrastre(posicion: Vector2) -> void:
	if posicion.distance_to(_posicion_inicial_toque) >= UMBRAL_ARRASTRE:
		_arrastrando = true


func _terminar_interaccion(posicion: Vector2) -> void:
	if _arrastrando:
		arrastre_soltado.emit(indice_pila, get_global_transform() * posicion)
	else:
		tocada.emit(indice_pila)
	_arrastrando = false


func _textura_de_carta(carta: Carta) -> Texture2D:
	var prefijo: String = PREFIJO_ARCHIVO_POR_PALO[carta.palo]
	var ruta := "res://assets/cartas_img/%s_%d.png" % [prefijo, carta.valor]
	return load(ruta) as Texture2D
