extends Control

## Menú principal. Equivalente a MenuPrincipal en interfaz_grafica.py.
## Por ahora "Jugar" salta directo al tablero (Fácil por defecto), porque
## el selector de dificultad todavía no existe (próxima tarea de Fase 5).
## Mi progreso / Récords / Configuración quedan visibles pero deshabilitados:
## son pantallas propias que se arman en pasos posteriores.

const ESCENA_TABLERO := preload("res://scenes/tablero.tscn")

@onready var boton_jugar: Button = $Centro/Columna/Tarjeta/Botones/Jugar
@onready var boton_salir: Button = $Centro/Columna/Tarjeta/Botones/Salir


func _ready() -> void:
	boton_jugar.pressed.connect(_al_tocar_jugar)
	boton_salir.pressed.connect(_al_tocar_salir)


func _al_tocar_jugar() -> void:
	get_tree().change_scene_to_packed(ESCENA_TABLERO)


func _al_tocar_salir() -> void:
	get_tree().quit()
