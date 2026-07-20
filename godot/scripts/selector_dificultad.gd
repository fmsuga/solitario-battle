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

## Posición Y (dentro de cada caja) donde las cartas quedan escondidas,
## tapadas por la tapa de la caja — y a dónde vuelven las 3 tarjetas
## nuevas que se instancien la próxima vez que se entra a esta pantalla.
const Y_ESCONDIDA := 210.0
## Cuánto asoma cada carta por encima de la tapa al abrirse: la primera
## apenas se asoma, la del medio bastante más, la de adelante es la que
## más sale — así se leen como una fila de cartas deslizándose hacia
## afuera, no como un abanico girado.
const Y_ASOMOS := [100.0, 55.0, 5.0]
const DEMORA_ENTRE_CARTAS := 0.09
const DURACION_ASOMO := 0.32
## Tiempo que se deja ver la animación completa antes de pasar de
## pantalla — lo pidió así: "que lo muestre un segundito".
const ESPERA_ANTES_DE_ENTRAR := 1.0

@onready var boton_facil: Button = $Centro/Columna/Tarjetas/Facil/Toque
@onready var boton_dificil: Button = $Centro/Columna/Tarjetas/Dificil/Toque
@onready var cartas_facil: Control = $Centro/Columna/Tarjetas/Facil/Cartas
@onready var cartas_dificil: Control = $Centro/Columna/Tarjetas/Dificil/Cartas
@onready var boton_volver: Button = $Centro/Columna/Volver


func _ready() -> void:
	boton_facil.pressed.connect(_al_elegir.bind(Carta.Dificultad.FACIL, cartas_facil))
	boton_dificil.pressed.connect(_al_elegir.bind(Carta.Dificultad.DIFICIL, cartas_dificil))
	boton_volver.pressed.connect(_al_tocar_volver)

	# Entrada suave en vez de aparecer de golpe, mismo criterio que los
	# overlays de pausa/fin/ajustes (ver tablero_visual.gd).
	modulate.a = 0.0
	create_tween().tween_property(self, "modulate:a", 1.0, 0.2)


func _al_elegir(dificultad: int, cartas: Control) -> void:
	# Se bloquean las dos cajas apenas se elige una: evita que un
	# segundo toque (accidental, mientras la animación todavía corre)
	# dispare otra selección o interrumpa la que ya está en curso.
	boton_facil.disabled = true
	boton_dificil.disabled = true

	_abrir_caja(cartas)

	await get_tree().create_timer(ESPERA_ANTES_DE_ENTRAR).timeout

	EstadoJuego.dificultad_seleccionada = dificultad
	get_tree().change_scene_to_packed(ESCENA_TABLERO)


## Anima las 3 cartas de esa caja saliendo hacia arriba, una atrás de la
## otra, con un empujoncito elástico al final (en vez de deslizarse y
## frenar seco) — como si la tapa se destrabara al abrirse.
func _abrir_caja(cartas: Control) -> void:
	for indice in range(cartas.get_child_count()):
		var carta := cartas.get_child(indice)
		var animacion := create_tween()
		animacion.tween_interval(indice * DEMORA_ENTRE_CARTAS)
		animacion.tween_property(carta, "position:y", Y_ASOMOS[indice], DURACION_ASOMO)\
			.set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)


func _al_tocar_volver() -> void:
	get_tree().change_scene_to_packed(ESCENA_MENU)
