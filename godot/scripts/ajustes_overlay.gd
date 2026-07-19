extends Control

## Overlay de Ajustes. Se instancia como HIJO tanto del menú principal
## como del tablero (ver menu_principal.tscn / tablero.tscn) — no es una
## escena a la que se navega con change_scene_to_packed. Eso es a
## propósito: si se abre desde una partida en curso, el objeto Juego que
## vive en memoria en tablero_visual.gd no se destruye. Al cerrar
## Ajustes, quien la abrió simplemente vuelve a quedar visible, tal como
## estaba.

signal cerrado

@onready var control_deslizante: HSlider = $Centro/Tarjeta/Columna/ControlDeslizante
@onready var etiqueta_porcentaje: Label = $Centro/Tarjeta/Columna/FilaVolumen/Porcentaje
@onready var boton_probar: Button = $Centro/Tarjeta/Columna/Probar
@onready var boton_cerrar: Button = $Centro/Tarjeta/Columna/Cerrar
@onready var boton_fondo: Button = $Fondo
@onready var sonido_prueba: AudioStreamPlayer = $SonidoPrueba
@onready var tarjeta: Control = $Centro/Tarjeta


func _ready() -> void:
	boton_fondo.pressed.connect(_cerrar)
	boton_cerrar.pressed.connect(_cerrar)
	boton_probar.pressed.connect(_al_tocar_probar)
	control_deslizante.value_changed.connect(_al_cambiar_volumen)


## Quien la contiene llama a esto en vez de simplemente poner
## visible = true, para que el control siempre arranque mostrando el
## volumen realmente guardado (por si se cambió desde otra instancia de
## este mismo overlay) y con la animación de entrada.
func mostrar() -> void:
	var volumen_actual := Configuracion.cargar_volumen()
	control_deslizante.set_value_no_signal(volumen_actual)
	_actualizar_porcentaje(volumen_actual)

	visible = true
	modulate.a = 0.0
	tarjeta.scale = Vector2(0.9, 0.9)
	await get_tree().process_frame  # aseguramos que 'tarjeta' ya tiene su tamaño final
	tarjeta.pivot_offset = tarjeta.size / 2
	var animacion := create_tween().set_parallel(true)
	animacion.tween_property(self, "modulate:a", 1.0, 0.16)
	animacion.tween_property(tarjeta, "scale", Vector2.ONE, 0.22)\
		.set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)


func _al_cambiar_volumen(valor: float) -> void:
	# Se aplica y se guarda apenas se mueve el control: en una pantalla
	# de ajustes de una sola opción no hace falta un botón "Guardar"
	# aparte, y el jugador escucha el resultado al toque.
	Configuracion.aplicar_volumen(valor)
	Configuracion.guardar_volumen(valor)
	_actualizar_porcentaje(valor)


func _al_tocar_probar() -> void:
	sonido_prueba.play()


func _actualizar_porcentaje(valor: float) -> void:
	etiqueta_porcentaje.text = "%d%%" % roundi(valor * 100)


func _cerrar() -> void:
	visible = false
	cerrado.emit()
