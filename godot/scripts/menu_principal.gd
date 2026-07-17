@tool
extends Control

## Menú principal. Equivalente a MenuPrincipal en interfaz_grafica.py.
## Por ahora "Jugar" salta directo al tablero (Fácil por defecto), porque
## el selector de dificultad todavía no existe (próxima tarea de Fase 5).
## Mi progreso / Récords / Configuración quedan visibles pero deshabilitados:
## son pantallas propias que se arman en pasos posteriores.

const ESCENA_TABLERO := preload("res://scenes/tablero.tscn")

## Se edita desde el Inspector del nodo MenuPrincipal.
## Valores positivos separan las letras; usalo si el peso del título las junta.
@export_category("Tipografía")
@export_range(-8, 24, 1) var espaciado_letras_titulo := 2

## Tamaño real dentro del layout (no usar Scale en los TextureRect).
@export_category("Encabezado")
@export_range(64, 260, 1, "suffix:px") var tamano_palos := 400.0:
	set(valor):
		tamano_palos = valor
		if is_node_ready():
			_aplicar_tamano_palos()

@export_category("Encabezado")
@export_range(-100, 50, 1, "suffix:px") var margen_superior_encabezado := 0:
	set(valor):
		margen_superior_encabezado = valor
		if is_node_ready():
			_aplicar_margen_encabezado()

@onready var boton_jugar: Button = $Centro/Columna/Menu/Tarjeta/Botones/Jugar
@onready var boton_salir: Button = $Centro/Columna/Menu/Tarjeta/Botones/Salir
@onready var titulo: Label = $Centro/Columna/Encabezado/Titulo
@onready var palos: Array[TextureRect] = [
	$Centro/Columna/Encabezado/Palos/Oros,
	$Centro/Columna/Encabezado/Palos/Copas,
	$Centro/Columna/Encabezado/Palos/Espadas,
	$Centro/Columna/Encabezado/Palos/Bastos,
]

func _aplicar_margen_encabezado() -> void:
	var encabezado = $Centro/Columna/Encabezado
	if encabezado:
		encabezado.add_theme_constant_override("margin_top", margen_superior_encabezado)


func _ready() -> void:
	_aplicar_tamano_palos()
	_aplicar_espaciado_titulo()
	_aplicar_margen_encabezado()
	if Engine.is_editor_hint():
		return
	boton_jugar.pressed.connect(_al_tocar_jugar)
	boton_salir.pressed.connect(_al_tocar_salir)


func _aplicar_espaciado_titulo() -> void:
	# Duplicamos la variante para no modificar el recurso compartido en disco.
	var fuente := titulo.get_theme_font("font") as FontVariation
	if fuente == null:
		return
	var fuente_con_espaciado := fuente.duplicate() as FontVariation
	fuente_con_espaciado.spacing_glyph = espaciado_letras_titulo
	titulo.add_theme_font_override("font", fuente_con_espaciado)


func _aplicar_tamano_palos() -> void:
	for palo in palos:
		palo.custom_minimum_size = Vector2(tamano_palos, tamano_palos)


func _al_tocar_jugar() -> void:
	get_tree().change_scene_to_packed(ESCENA_TABLERO)


func _al_tocar_salir() -> void:
	get_tree().quit()
