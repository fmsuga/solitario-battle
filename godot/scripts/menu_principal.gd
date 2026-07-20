extends Control

## Menú principal. Equivalente a MenuPrincipal en interfaz_grafica.py.
## Mi progreso / Récords quedan visibles pero deshabilitados: son
## pantallas propias que se arman en pasos posteriores. Ajustes ya está
## conectado (ver AjustesOverlay).

const ESCENA_SELECTOR_DIFICULTAD := preload("res://scenes/selector_dificultad.tscn")
const ESCENA_RECORDS := preload("res://scenes/records.tscn")

@onready var boton_jugar: Button = $Centro/Columna/Menu/Tarjeta/Botones/Jugar
@onready var boton_records: Button = $Centro/Columna/Menu/Tarjeta/Botones/Records
@onready var boton_salir: Button = $Centro/Columna/Menu/Tarjeta/Botones/Salir
@onready var boton_configuracion: Button = $Centro/Columna/Menu/Tarjeta/Botones/Configuracion
@onready var ajustes: Control = $AjustesOverlay


func _ready() -> void:
	boton_jugar.pressed.connect(_al_tocar_jugar)
	boton_records.pressed.connect(_al_tocar_records)
	boton_records.disabled = false
	boton_salir.pressed.connect(_al_tocar_salir)
	boton_configuracion.pressed.connect(ajustes.mostrar)


func _al_tocar_jugar() -> void:
	get_tree().change_scene_to_packed(ESCENA_SELECTOR_DIFICULTAD)


func _al_tocar_records() -> void:
	get_tree().change_scene_to_packed(ESCENA_RECORDS)


func _al_tocar_salir() -> void:
	get_tree().quit()
