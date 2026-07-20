class_name PilaVisual
extends Button

## Muestra la carta real (PNG) con el contador de cartas superpuesto.
##
## La pila "armada" (la que se tocó primero, esperando el segundo toque
## para intentar la jugada) se marca con un anillo grueso + un halo de
## color detrás + un pequeño "pop" de escala al seleccionarse — antes
## era apenas un cambio sutil de color, casi imperceptible.

@onready var halo: ColorRect = $Halo
@onready var borde: ColorRect = $Borde
@onready var imagen_carta: TextureRect = $Borde/Imagen
@onready var cantidad_label: Label = $Cantidad

const COLOR_BORDE_REPOSO := Color(0.898, 0.745, 0.447, 0.3)
const COLOR_BORDE_SELECCIONADA := Color(0.9333, 0.4471, 0.3529, 1)
const COLOR_HALO_SELECCIONADA := Color(0.8471, 0.3569, 0.2706, 0.4)
const COLOR_HALO_REPOSO := Color(0.8471, 0.3569, 0.2706, 0)
const COLOR_TEXTO_REPOSO := Color(0.96, 0.94, 0.84, 1)
const COLOR_TEXTO_SELECCIONADA := Color(0.9333, 0.4471, 0.3529, 1)

const CRECIMIENTO_HALO := 16.0

## Mapea el enum Palo al prefijo de archivo usado en assets/cartas_img/
## (oros_1.png, copas_12.png, etc.) Si el día de mañana se agregan cartas
## comodín u otro mazo, este es el único lugar que hay que tocar.
const PREFIJO_ARCHIVO_POR_PALO := {
	Carta.Palo.OROS: "oros",
	Carta.Palo.COPAS: "copas",
	Carta.Palo.ESPADAS: "espadas",
	Carta.Palo.BASTOS: "bastos",
}


func mostrar_pila(pila: Tablero.Pila, indice: int, seleccionada: bool) -> void:
	imagen_carta.texture = _textura_de_carta(pila.tope())
	cantidad_label.text = "Pila %d  x%d" % [indice + 1, pila.cantidad_cartas()]
	tooltip_text = "Pila %d: %s" % [indice + 1, pila._to_string()]

	borde.color = COLOR_BORDE_SELECCIONADA if seleccionada else COLOR_BORDE_REPOSO
	halo.color = COLOR_HALO_SELECCIONADA if seleccionada else COLOR_HALO_REPOSO
	cantidad_label.add_theme_color_override(
		"font_color", COLOR_TEXTO_SELECCIONADA if seleccionada else COLOR_TEXTO_REPOSO
	)

	var crecimiento := CRECIMIENTO_HALO if seleccionada else 0.0
	halo.offset_left = -crecimiento
	halo.offset_top = -crecimiento
	halo.offset_right = crecimiento
	halo.offset_bottom = crecimiento

	if seleccionada:
		_animar_seleccion()


## _refrescar_tablero() destruye y vuelve a crear las PilaVisual en cada
## jugada, así que esta instancia siempre es nueva cuando llega acá con
## seleccionada=true — no hace falta comparar contra un estado anterior,
## el "pop" se dispara una sola vez, justo cuando aparece marcada.
func _animar_seleccion() -> void:
	pivot_offset = custom_minimum_size / 2
	scale = Vector2(0.93, 0.93)
	var animacion := create_tween()
	animacion.tween_property(self, "scale", Vector2.ONE, 0.2)\
		.set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)


func _textura_de_carta(carta: Carta) -> Texture2D:
	var prefijo: String = PREFIJO_ARCHIVO_POR_PALO[carta.palo]
	var ruta := "res://assets/cartas_img/%s_%d.png" % [prefijo, carta.valor]
	return load(ruta) as Texture2D
