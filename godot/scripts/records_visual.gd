extends Control

## Pantalla de Récords. Dos pestañas (Mundial / Mis récords) contra
## Supabase vía RecordsOnline; si falla, cae automático al historial
## local (Puntuacion) con un aviso. Resalta la fila del jugador si el
## resultado que acaba de guardar aparece en lo que se muestra.
##
## Cada puesto se dibuja como una "tarjeta" (no una grilla de columnas):
## insignia circular de posición + nombre/puntaje grandes arriba +
## una línea secundaria con el resto del detalle. El Top 3 recibe una
## tarjeta más alta con color distintivo (oro/plata/bronce).

# load() en vez de preload(): ciclo circular menu → records → menu.
# Mismo patrón que tablero_visual.gd.
var ESCENA_MENU := load("res://scenes/menu_principal.tscn")

const COLOR_TEXTO_OSCURO := Color(0.055, 0.145, 0.118, 1.0)
const COLOR_TEXTO_CLARO  := Color(0.918, 0.902, 0.870, 1.0)
const COLOR_ACENTO       := Color(0.898, 0.745, 0.447, 1.0)
const COLOR_DETALLE      := Color(0.616, 0.702, 0.657, 0.85)
const COLOR_DETALLE_TOP  := Color(0.918, 0.902, 0.870, 0.75)

# Colores de medalla para los tres primeros puestos.
const COLOR_ORO    := Color(0.898, 0.745, 0.447, 1.0)
const COLOR_PLATA  := Color(0.788, 0.816, 0.843, 1.0)
const COLOR_BRONCE := Color(0.804, 0.549, 0.337, 1.0)

@onready var boton_volver:   Button        = $Margen/Columna/Encabezado/BotonVolver
@onready var boton_mundial:  Button        = $Margen/Columna/Tabs/BotonMundial
@onready var boton_personal: Button        = $Margen/Columna/Tabs/BotonPersonal
@onready var label_estado:   Label         = $Margen/Columna/PanelTabla/MargenInterior/Interior/Estado
@onready var lista:          VBoxContainer = $Margen/Columna/PanelTabla/MargenInterior/Interior/Scroll/Lista

var _fuente_texto: FontFile = preload("res://assets/fuentes/NotoSans-Variable.ttf")
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
	for hijo in lista.get_children():
		hijo.queue_free()


func _llenar_tabla(registros: Array) -> void:
	var ultimo: Dictionary = EstadoJuego.ultimo_registro_guardado
	var puesto := 1
	for registro in registros:
		var es_propio := _es_el_mismo_registro(registro, ultimo)
		lista.add_child(_crear_fila(puesto, registro, es_propio))
		puesto += 1


## Construye una tarjeta completa para un puesto del ranking: insignia +
## nombre/puntaje + línea de detalle secundaria.
func _crear_fila(puesto: int, registro: Dictionary, es_propio: bool) -> Control:
	var es_podio := puesto <= 3

	var tarjeta := PanelContainer.new()
	tarjeta.add_theme_stylebox_override("panel", _estilo_tarjeta(puesto, es_propio))

	var margen := MarginContainer.new()
	var margen_v := 18 if es_podio else 12
	var margen_h := 20 if es_podio else 18
	margen.add_theme_constant_override("margin_left",   margen_h)
	margen.add_theme_constant_override("margin_right",  margen_h)
	margen.add_theme_constant_override("margin_top",    margen_v)
	margen.add_theme_constant_override("margin_bottom", margen_v)
	tarjeta.add_child(margen)

	var fila := HBoxContainer.new()
	fila.add_theme_constant_override("separation", 18)
	margen.add_child(fila)

	fila.add_child(_crear_insignia(puesto))

	var columna_info := VBoxContainer.new()
	columna_info.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	columna_info.add_theme_constant_override("separation", 4)
	fila.add_child(columna_info)

	var nombre := Label.new()
	nombre.text = str(registro.get("jugador", "-"))
	nombre.clip_text = true
	nombre.add_theme_font_override("font", _fuente_texto)
	nombre.add_theme_font_size_override("font_size", 22 if es_podio else 17)
	nombre.add_theme_color_override("font_color", COLOR_ACENTO if es_propio else COLOR_TEXTO_CLARO)
	columna_info.add_child(nombre)

	if es_propio:
		var etiqueta_propia := Label.new()
		etiqueta_propia.text = "Tu partida"
		etiqueta_propia.add_theme_font_override("font", _fuente_texto)
		etiqueta_propia.add_theme_font_size_override("font_size", 12)
		etiqueta_propia.add_theme_color_override("font_color", COLOR_ACENTO)
		columna_info.add_child(etiqueta_propia)

	var detalle := Label.new()
	detalle.text = _texto_secundario(registro)
	detalle.clip_text = true
	detalle.add_theme_font_override("font", _fuente_texto)
	detalle.add_theme_font_size_override("font_size", 14 if es_podio else 13)
	detalle.add_theme_color_override("font_color", COLOR_DETALLE_TOP if es_podio else COLOR_DETALLE)
	columna_info.add_child(detalle)

	var puntaje := Label.new()
	puntaje.text = str(registro.get("puntaje", 0))
	puntaje.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	puntaje.add_theme_font_override("font", _fuente_texto)
	puntaje.add_theme_font_size_override("font_size", 30 if es_podio else 21)
	puntaje.add_theme_color_override("font_color", COLOR_ACENTO)
	fila.add_child(puntaje)

	return tarjeta


## Insignia circular con el número de puesto. El Top 3 usa el color de
## medalla correspondiente; el resto, un círculo neutro sutil.
func _crear_insignia(puesto: int) -> Control:
	var tamano := 52 if puesto <= 3 else 40
	var contenedor := PanelContainer.new()
	contenedor.custom_minimum_size = Vector2(tamano, tamano)
	contenedor.size_flags_vertical = Control.SIZE_SHRINK_CENTER

	var sb := StyleBoxFlat.new()
	sb.corner_radius_top_left     = tamano / 2
	sb.corner_radius_top_right    = tamano / 2
	sb.corner_radius_bottom_left  = tamano / 2
	sb.corner_radius_bottom_right = tamano / 2

	var color_texto := COLOR_TEXTO_CLARO
	match puesto:
		1:
			sb.bg_color = COLOR_ORO
			color_texto = COLOR_TEXTO_OSCURO
		2:
			sb.bg_color = COLOR_PLATA
			color_texto = COLOR_TEXTO_OSCURO
		3:
			sb.bg_color = COLOR_BRONCE
			color_texto = COLOR_TEXTO_OSCURO
		_:
			sb.bg_color = Color(1, 1, 1, 0.06)
			sb.border_width_left   = 1
			sb.border_width_top    = 1
			sb.border_width_right  = 1
			sb.border_width_bottom = 1
			sb.border_color = Color(0.898, 0.745, 0.447, 0.3)
			color_texto = Color(0.898, 0.745, 0.447, 0.9)
	contenedor.add_theme_stylebox_override("panel", sb)

	var numero := Label.new()
	numero.text = str(puesto)
	numero.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	numero.vertical_alignment   = VERTICAL_ALIGNMENT_CENTER
	numero.add_theme_font_override("font", _fuente_texto)
	numero.add_theme_font_size_override("font_size", 22 if puesto <= 3 else 16)
	numero.add_theme_color_override("font_color", color_texto)
	contenedor.add_child(numero)

	return contenedor


## Fondo y borde de la tarjeta según el puesto y si es la partida propia.
func _estilo_tarjeta(puesto: int, es_propio: bool) -> StyleBoxFlat:
	var sb := StyleBoxFlat.new()
	sb.corner_radius_top_left     = 14
	sb.corner_radius_top_right    = 14
	sb.corner_radius_bottom_left  = 14
	sb.corner_radius_bottom_right = 14
	sb.border_width_left   = 2
	sb.border_width_top    = 2
	sb.border_width_right  = 2
	sb.border_width_bottom = 2

	match puesto:
		1:
			sb.bg_color     = Color(0.898, 0.745, 0.447, 0.16)
			sb.border_color = Color(0.898, 0.745, 0.447, 0.85)
			sb.shadow_color = Color(0.898, 0.745, 0.447, 0.15)
			sb.shadow_size  = 8
		2:
			sb.bg_color     = Color(0.788, 0.816, 0.843, 0.12)
			sb.border_color = Color(0.788, 0.816, 0.843, 0.7)
		3:
			sb.bg_color     = Color(0.804, 0.549, 0.337, 0.14)
			sb.border_color = Color(0.804, 0.549, 0.337, 0.7)
		_:
			sb.bg_color     = Color(1, 1, 1, 0.035)
			sb.border_color = Color(0.898, 0.745, 0.447, 0.14)

	if es_propio:
		sb.border_width_left   = 3
		sb.border_width_top    = 3
		sb.border_width_right  = 3
		sb.border_width_bottom = 3
		sb.border_color = COLOR_ACENTO

	return sb


func _texto_secundario(registro: Dictionary) -> String:
	var partes := PackedStringArray()
	partes.append(_etiqueta_dificultad(registro.get("dificultad", "")))
	partes.append("%d pilas" % int(registro.get("pilas_finales", 0)))
	partes.append("%d mov." % int(registro.get("movimientos", 0)))
	partes.append(Puntuacion.formatear_duracion(registro.get("duracion_segundos", 0)))
	partes.append(_formatear_fecha(str(registro.get("fecha", ""))))
	return "  ·  ".join(partes)


func _etiqueta_dificultad(valor: String) -> String:
	return "Difícil" if valor == "dificil" else "Fácil"


func _formatear_fecha(fecha_iso: String) -> String:
	# "2026-07-12T..." -> "12/07/2026"
	if fecha_iso.length() < 10:
		return fecha_iso
	var solo_fecha := fecha_iso.substr(0, 10)
	var partes := solo_fecha.split("-")
	if partes.size() != 3:
		return solo_fecha
	return "%s/%s/%s" % [partes[2], partes[1], partes[0]]


func _es_el_mismo_registro(registro: Dictionary, ultimo: Dictionary) -> bool:
	if ultimo.is_empty():
		return false
	return (
		registro.get("jugador", "") == ultimo.get("jugador", "")
		and int(registro.get("puntaje", -1)) == int(ultimo.get("puntaje", -2))
		and str(registro.get("fecha", "")) == str(ultimo.get("fecha", ""))
	)
