extends Node

## Autoload (registrar en Project Settings → Autoload, con el nombre
## "EstadoJuego"). Puentea datos entre escenas que un simple
## change_scene_to_packed no puede pasar por parámetro, como la
## dificultad elegida en el selector antes de instanciar el tablero.

var dificultad_seleccionada: int = Carta.Dificultad.FACIL
