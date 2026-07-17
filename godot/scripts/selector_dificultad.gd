extends Control

const ESCENA_TABLERO := preload("res://scenes/tablero.tscn")
# load() en vez de preload(): esta escena vuelve al menú principal, que a
# su vez preload-ea esta misma escena (selector_dificultad) para llegar
# acá. Si las dos usaran preload(), Godot necesitaría terminar de cargar
# cada una para poder cargar la otra -> ciclo -> "Parse Error: Busy".
# load() se resuelve recién cuando se ejecuta la línea (al tocar
# "Volver"), momento en el que ambas escenas ya están completamente
# cargadas, así que el ciclo desaparece.
var ESCENA_MENU := load("res://scenes/menu_principal.tscn")

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
