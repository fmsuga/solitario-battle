extends Control

## Menú principal. Equivalente a MenuPrincipal en interfaz_grafica.py.
## Por ahora "Jugar" salta directo al tablero (Fácil por defecto), porque
## el selector de dificultad todavía no existe (próxima tarea de Fase 5).
## Mi progreso / Récords / Configuración quedan visibles pero deshabilitados:
## son pantallas propias que se arman en pasos posteriores.

const ESCENA_SELECTOR_DIFICULTAD := preload("res://scenes/selector_dificultad.tscn")

@onready var boton_jugar: Button = $Centro/Columna/Menu/Tarjeta/Botones/Jugar
@onready var boton_salir: Button = $Centro/Columna/Menu/Tarjeta/Botones/Salir


func _ready() -> void:
	boton_jugar.pressed.connect(_al_tocar_jugar)
	boton_salir.pressed.connect(_al_tocar_salir)


func _al_tocar_jugar() -> void:
	get_tree().change_scene_to_packed(ESCENA_SELECTOR_DIFICULTAD)


func _al_tocar_salir() -> void:
	get_tree().quit()
