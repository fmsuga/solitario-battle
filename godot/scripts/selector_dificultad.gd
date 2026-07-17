extends Control

const ESCENA_TABLERO := preload("res://scenes/tablero.tscn")
const ESCENA_MENU := preload("res://scenes/menu_principal.tscn")

@onready var boton_facil: Button = $Centro/Columna/Tarjeta/Botones/Facil
@onready var boton_dificil: Button = $Centro/Columna/Tarjeta/Botones/Dificil
@onready var boton_volver: Button = $Centro/Columna/Volver


func _ready() -> void:
	boton_facil.pressed.connect(_al_elegir.bind(Carta.Dificultad.FACIL))
	boton_dificil.pressed.connect(_al_elegir.bind(Carta.Dificultad.DIFICIL))
	boton_volver.pressed.connect(_al_tocar_volver)


func _al_elegir(dificultad: int) -> void:
	EstadoJuego.dificultad_seleccionada = dificultad
	get_tree().change_scene_to_packed(ESCENA_TABLERO)


func _al_tocar_volver() -> void:
	get_tree().change_scene_to_packed(ESCENA_MENU)
