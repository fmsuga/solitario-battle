class_name Configuracion
extends RefCounted

## Preferencias persistentes del jugador. Equivalente a configuracion.py
## de la versión de escritorio (por ahora: volumen). En vez de una
## carpeta al lado del .exe, usamos "user://" — la carpeta que Godot ya
## resuelve automáticamente según el sistema (AppData en Windows,
## almacenamiento privado de la app en Android) — así que, a diferencia
## de la versión de escritorio, acá no hace falta un recursos.gd propio
## para calcular la ruta.

const ARCHIVO_PERFIL := "user://perfil_jugador.json"
const VOLUMEN_PREDETERMINADO := 0.70


static func cargar_volumen() -> float:
	var volumen = _cargar_perfil().get("volumen", VOLUMEN_PREDETERMINADO)
	if typeof(volumen) != TYPE_FLOAT and typeof(volumen) != TYPE_INT:
		return VOLUMEN_PREDETERMINADO
	return clampf(float(volumen), 0.0, 1.0)


static func guardar_volumen(volumen: float) -> void:
	var perfil := _cargar_perfil()
	perfil["volumen"] = clampf(volumen, 0.0, 1.0)
	var archivo := FileAccess.open(ARCHIVO_PERFIL, FileAccess.WRITE)
	if archivo != null:
		archivo.store_string(JSON.stringify(perfil))


## Aplica el volumen guardado al bus Master. Se llama una sola vez al
## arrancar la app (ver EstadoJuego._ready), para que el volumen elegido
## la última vez siga vigente al reabrir el juego.
static func aplicar_volumen_guardado() -> void:
	aplicar_volumen(cargar_volumen())


## Sube/baja el volumen de TODOS los sonidos en tiempo real (los
## AudioStreamPlayer del proyecto usan el bus "Master" por defecto, así
## que no hace falta tocar cada uno por separado). 0.0 silencia del todo
## en vez de acercarse a -infinito decibeles.
static func aplicar_volumen(volumen: float) -> void:
	var indice_bus := AudioServer.get_bus_index("Master")
	var silencio := volumen <= 0.0
	AudioServer.set_bus_mute(indice_bus, silencio)
	if not silencio:
		AudioServer.set_bus_volume_db(indice_bus, linear_to_db(clampf(volumen, 0.001, 1.0)))


static func _cargar_perfil() -> Dictionary:
	if not FileAccess.file_exists(ARCHIVO_PERFIL):
		return {}
	var archivo := FileAccess.open(ARCHIVO_PERFIL, FileAccess.READ)
	if archivo == null:
		return {}
	var datos = JSON.parse_string(archivo.get_as_text())
	return datos if typeof(datos) == TYPE_DICTIONARY else {}
