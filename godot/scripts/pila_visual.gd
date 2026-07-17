class_name PilaVisual
extends Button

## Fase 3: muestra la carta real (PNG) en vez del placeholder de color.
## El contador de cartas se dibuja como Label superpuesto sobre el sprite,
## igual que se decidió en el plan (reemplaza a _dibujar_contador de Python).

@onready var fondo: ColorRect = $Fondo
@onready var borde: ColorRect = $Borde
@onready var imagen_carta: TextureRect = $Borde/Imagen
@onready var cantidad_label: Label = $Cantidad

const COLOR_NORMAL := Color("163a30")
const COLOR_SELECCIONADA := Color("2c5849")
const COLOR_BORDE_NORMAL := Color("e5be72")
const COLOR_BORDE_SELECCIONADA := Color("d85b45")

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
	fondo.color = COLOR_SELECCIONADA if seleccionada else COLOR_NORMAL
	borde.color = COLOR_BORDE_SELECCIONADA if seleccionada else COLOR_BORDE_NORMAL
	tooltip_text = "Pila %d: %s" % [indice + 1, pila._to_string()]


func _textura_de_carta(carta: Carta) -> Texture2D:
	var prefijo: String = PREFIJO_ARCHIVO_POR_PALO[carta.palo]
	var ruta := "res://assets/cartas_img/%s_%d.png" % [prefijo, carta.valor]
	return load(ruta) as Texture2D
