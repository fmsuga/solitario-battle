class_name PilaVisual
extends Button

## Representación temporal de una pila: texto y color hasta incorporar arte.

@onready var fondo: ColorRect = $Fondo
@onready var borde: ColorRect = $Borde
@onready var carta_label: Label = $Carta
@onready var cantidad_label: Label = $Cantidad

const COLOR_NORMAL := Color("1f4063")
const COLOR_SELECCIONADA := Color("285a47")
const COLOR_BORDE_NORMAL := Color("d1b552")
const COLOR_BORDE_SELECCIONADA := Color("79dfb6")


func mostrar_pila(pila: Tablero.Pila, indice: int, seleccionada: bool) -> void:
	carta_label.text = pila.tope()._to_string()
	cantidad_label.text = "Pila %d  x%d" % [indice + 1, pila.cantidad_cartas()]
	fondo.color = COLOR_SELECCIONADA if seleccionada else COLOR_NORMAL
	borde.color = COLOR_BORDE_SELECCIONADA if seleccionada else COLOR_BORDE_NORMAL
	tooltip_text = "Pila %d: %s" % [indice + 1, pila._to_string()]
