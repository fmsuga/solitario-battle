extends Node

## Autoload (registrar en Project Settings → Autoload, con el nombre
## "EstadoJuego"). Puentea datos entre escenas que un simple
## change_scene_to_packed no puede pasar por parámetro, como la
## dificultad elegida en el selector antes de instanciar el tablero.

var dificultad_seleccionada: int = Carta.Dificultad.FACIL

## Último resumen guardado desde la pantalla de fin de partida (con
## "jugador" agregado), para que records_visual.gd pueda resaltar esa
## fila si aparece en la tabla. Vacío si todavía no se guardó nada en
## esta sesión.
var ultimo_registro_guardado: Dictionary = {}


func _ready() -> void:
	# Se hace acá (un único punto de entrada, corre antes que cualquier
	# escena) para que el volumen elegido la última vez siga vigente
	# al reabrir la app, sin tener que repetir esta llamada en cada
	# escena que reproduce sonido.
	Configuracion.aplicar_volumen_guardado()
