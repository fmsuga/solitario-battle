class_name MazoVisual
extends Button

## Muestra el mazo boca abajo: la imagen de dorso.png con la cantidad de
## cartas que quedan por repartir superpuesta, igual que cargar_imagen_dorso()
## + _dibujar_contador en la versión de escritorio (imagenes_cartas.py).
## Tocar el mazo reparte la siguiente carta (tablero_visual.gd escucha
## la señal "pressed" heredada de Button, igual que antes).

@onready var cantidad_label: Label = $Cantidad


func mostrar_cantidad(cartas_restantes: int) -> void:
	if cartas_restantes == 0:
		cantidad_label.text = "Vacío"
	else:
		cantidad_label.text = "x%d" % cartas_restantes
