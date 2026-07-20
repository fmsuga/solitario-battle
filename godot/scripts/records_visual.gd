extends Control

## Pantalla de Récords. Dos pestañas (Mundial / Mis récords) contra
## Supabase vía RecordsOnline; si falla, cae automático al historial
## local (Puntuacion) con un aviso. Resalta la fila del jugador si el
## resultado que acaba de guardar aparece en lo que se muestra.

# load() en vez de preload(): ciclo circular menu → records → menu.
# Mismo patrón que tablero_visual.gd.
var ESCENA_MENU := load("res://scenes/menu_principal.tscn")

const COLUMNAS := 8
const COLOR_FILA_PROPIA  := Color(0.898, 0.745, 0.447, 1.0)
const COLOR_FILA_NORMAL  := Color(0.855, 0.820, 0.710, 1.0)
const COLOR_ENCABEZADO   := Color(0.898, 0.745, 0.447, 1.0)

@onready var boton_volver:   Button        = $Margen/Columna/Encabezado/BotonVolver
@onready var boton_mundial:  Button        = $Margen/Columna/Tabs/BotonMundial
@onready var boton_personal: Button        = $Margen/Columna/Tabs/BotonPersonal
@onready var label_estado:   Label         = $Margen/Columna/PanelTabla/MargenInterior/Interior/Estado
@onready var grilla:         GridContainer = $Margen/Columna/PanelTabla/MargenInterior/Interior/Scroll/Grilla

var _pestania_actual := "mundial"


func _ready() -> void:
	boton_volver.pressed.connect(_al_tocar_volver)
	boton_mundial.pressed.connect(func(): _cambiar_pestania("mundial"))
	boton_personal.pressed.connect(func(): _cambiar_pestania("personal"))
	_actualizar_estilos_tabs()
	_cargar_pestania_actual()


func _al_tocar_volver() -> void:
	get_tree().change_scene_to_packed(ESCENA_MENU)


func _cambiar_pestania(nombre: String) -> void:
	if nombre == _pestania_actual:
		return
	_pestania_actual = nombre
	_actualizar_estilos_tabs()
	_cargar_pestania_actual()


func _actualizar_estilos_tabs() -> void:
	# El tab activo resalta con borde dorado completo; el inactivo es sutil.
	var mundial_activo := _pestania_actual == "mundial"
	_estilo_tab(boton_mundial,  mundial_activo)
	_estilo_tab(boton_personal, not mundial_activo)


func _estilo_tab(boton: Button, activo: bool) -> void:
	var sb := StyleBoxFlat.new()
	sb.corner_radius_top_left    = 12
	sb.corner_radius_top_right   = 12
	sb.corner_radius_bottom_left = 0
	sb.corner_radius_bottom_right = 0
	if activo:
		sb.bg_color      = Color(0.898, 0.745, 0.447, 0.18)
		sb.border_width_top    = 2
		sb.border_width_left   = 2
		sb.border_width_right  = 2
		sb.border_width_bottom = 0
		sb.border_color  = Color(0.898, 0.745, 0.447, 0.9)
		boton.add_theme_color_override("font_color", Color(0.898, 0.745, 0.447, 1))
	else:
		sb.bg_color      = Color(1, 1, 1, 0.03)
		sb.border_width_top    = 1
		sb.border_width_left   = 1
		sb.border_width_right  = 1
		sb.border_width_bottom = 0
		sb.border_color  = Color(0.898, 0.745, 0.447, 0.25)
		boton.add_theme_color_override("font_color", Color(0.7, 0.65, 0.55, 1))
	boton.add_theme_stylebox_override("normal",  sb)
	boton.add_theme_stylebox_override("hover",   sb)
	boton.add_theme_stylebox_override("pressed", sb)


func _cargar_pestania_actual() -> void:
	var pestania_solicitada := _pestania_actual
	_limpiar_filas()
	_mostrar_estado("Cargando...")

	var resultado: Dictionary
	if pestania_solicitada == "mundial":
		resultado = await RecordsOnline.obtener_records_globales(10)
	else:
		resultado = await RecordsOnline.obtener_records_personales(10)

	# El usuario pudo cambiar de pestaña mientras esperábamos la
	# respuesta: esta respuesta ya está obsoleta.
	if pestania_solicitada != _pestania_actual:
		return

	var registros: Array = resultado["records"]
	var error: String    = resultado["error"]

	if error != "":
		_mostrar_estado(error)
		registros = _historial_local_filtrado()

	if registros.is_empty() and error == "":
		_mostrar_estado("Todavía no hay partidas registradas.")
		return

	if error == "":
		label_estado.visible = false

	_llenar_tabla(registros)


func _historial_local_filtrado() -> Array:
	var historial: Array = Puntuacion.cargar_historial()
	return Puntuacion.ordenar_records(historial).slice(0, 10)


func _mostrar_estado(texto: String) -> void:
	label_estado.text    = texto
	label_estado.visible = true


func _limpiar_filas() -> void:
	for hijo in grilla.get_children():
		if hijo.get_index() >= COLUMNAS:
			hijo.queue_free()


func _llenar_tabla(registros: Array) -> void:
	var ultimo: Dictionary = EstadoJuego.ultimo_registro_guardado
	var numero := 1
	for registro in registros:
		var es_propio := _es_el_mismo_registro(registro, ultimo)
		var color := COLOR_FILA_PROPIA if es_propio else COLOR_FILA_NORMAL
		var negrita := es_propio
		_agregar_celda(str(numero),                                                          color, negrita)
		_agregar_celda(str(registro.get("jugador", "-")),                                    color, negrita)
		_agregar_celda(str(registro.get("puntaje", 0)),                                      color, negrita)
		_agregar_celda(_etiqueta_dificultad(registro.get("dificultad", "")),                 color, negrita)
		_agregar_celda(str(registro.get("pilas_finales", 0)),                                color, negrita)
		_agregar_celda(str(registro.get("movimientos", 0)),                                  color, negrita)
		_agregar_celda(Puntuacion.formatear_duracion(registro.get("duracion_segundos", 0)),  color, negrita)
		_agregar_celda(_formatear_fecha(str(registro.get("fecha", ""))),                     color, negrita)
		numero += 1


func _agregar_celda(texto: String, color: Color, negrita: bool = false) -> void:
	var etiqueta := Label.new()
	etiqueta.text = texto
	etiqueta.add_theme_color_override("font_color", color)
	if negrita:
		etiqueta.add_theme_font_size_override("font_size", 17)
	grilla.add_child(etiqueta)


func _etiqueta_dificultad(valor: String) -> String:
	return "Difícil" if valor == "dificil" else "Fácil"


func _formatear_fecha(fecha_iso: String) -> String:
	return fecha_iso.substr(0, 10) if fecha_iso.length() >= 10 else fecha_iso


func _es_el_mismo_registro(registro: Dictionary, ultimo: Dictionary) -> bool:
	if ultimo.is_empty():
		return false
	return (
		registro.get("jugador", "") == ultimo.get("jugador", "")
		and int(registro.get("puntaje", -1)) == int(ultimo.get("puntaje", -2))
		and str(registro.get("fecha", "")) == str(ultimo.get("fecha", ""))
	)
