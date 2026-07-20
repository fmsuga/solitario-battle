extends Node

## Autoload (registrar en Project Settings → Autoload, nombre
## "RecordsOnline"). Puerto de src/records_online.py (versión Python) a
## GDScript. A diferencia de la versión Python, HTTPRequest es asíncrono
## en Godot, así que las tres funciones públicas son `await`-ables.
##
## No usa una clave secreta: la publishable key está pensada para vivir
## en el cliente, la seguridad la maneja Row Level Security en la base
## (ver supabase_schema.sql en la raíz del repo).

const SUPABASE_URL := "https://tqjpybhwkyrkgrapoxcr.supabase.co"
const SUPABASE_KEY := "sb_publishable_-Y5Qf1qNZ7ix4_H3opfvzA_v_uuUTXs"
const TABLA_RECORDS := "leaderboard_entries"
const CAMPOS_SELECT := "player_name,difficulty,score,piles_finales,moves,duration_seconds,played_at"


## Publica una partida. Devuelve "" si se publicó bien, o un mensaje de
## error legible para mostrar en la UI (nunca lanza ni bloquea al fallar).
func enviar_record(nombre: String, resumen: Dictionary) -> String:
	var datos := {
		"device_id": Configuracion.obtener_device_id(),
		"player_name": nombre.substr(0, 24),
		"difficulty": resumen.get("dificultad", ""),
		"score": resumen.get("puntaje", 0),
		"piles_finales": resumen.get("pilas_finales", 0),
		"moves": resumen.get("movimientos", 0),
		"duration_seconds": resumen.get("duracion_segundos", 0),
		"played_at": resumen.get("fecha", ""),
	}
	var resultado: Dictionary = await _solicitud(HTTPClient.METHOD_POST, TABLA_RECORDS, datos)
	return "" if resultado["ok"] else resultado["mensaje"]


func obtener_records_globales(limite: int = 50) -> Dictionary:
	var consulta := "select=%s&order=score.desc,duration_seconds.asc,moves.asc&limit=%d" % [CAMPOS_SELECT, limite]
	var resultado: Dictionary = await _solicitud(HTTPClient.METHOD_GET, "%s?%s" % [TABLA_RECORDS, consulta], null)
	if not resultado["ok"]:
		return {"records": [], "error": resultado["mensaje"]}
	return {"records": _normalizar_lista(resultado["datos"]), "error": ""}


func obtener_records_personales(limite: int = 50) -> Dictionary:
	var device_id := Configuracion.obtener_device_id()
	var consulta := "select=%s&device_id=eq.%s&order=score.desc,duration_seconds.asc,moves.asc&limit=%d" % [
		CAMPOS_SELECT, device_id, limite,
	]
	var resultado: Dictionary = await _solicitud(HTTPClient.METHOD_GET, "%s?%s" % [TABLA_RECORDS, consulta], null)
	if not resultado["ok"]:
		return {"records": [], "error": resultado["mensaje"]}
	return {"records": _normalizar_lista(resultado["datos"]), "error": ""}


## Crea un HTTPRequest hijo temporal, espera la respuesta y se limpia
## solo. `datos == null` para GET; un Dictionary para POST (se manda
## como JSON en el cuerpo).
func _solicitud(metodo: HTTPClient.Method, ruta: String, datos) -> Dictionary:
	var peticion := HTTPRequest.new()
	peticion.timeout = 4.0
	add_child(peticion)

	var encabezados := PackedStringArray([
		"apikey: %s" % SUPABASE_KEY,
		"Content-Type: application/json",
	])
	if metodo == HTTPClient.METHOD_POST:
		encabezados.append("Prefer: return=minimal")

	var cuerpo := JSON.stringify(datos) if datos != null else ""
	var error := peticion.request("%s/rest/v1/%s" % [SUPABASE_URL, ruta], encabezados, metodo, cuerpo)
	if error != OK:
		peticion.queue_free()
		return {"ok": false, "mensaje": "Sin conexión: se mostrarán tus récords locales.", "datos": []}

	var respuesta: Array = await peticion.request_completed
	peticion.queue_free()

	var resultado_conexion: int = respuesta[0]
	var codigo_http: int = respuesta[1]
	var cuerpo_bytes: PackedByteArray = respuesta[3]

	if resultado_conexion != HTTPRequest.RESULT_SUCCESS:
		return {"ok": false, "mensaje": "Sin conexión: se mostrarán tus récords locales.", "datos": []}
	if codigo_http < 200 or codigo_http >= 300:
		return {"ok": false, "mensaje": "No se pudieron actualizar los récords mundiales.", "datos": []}

	var texto := cuerpo_bytes.get_string_from_utf8()
	var analizado = JSON.parse_string(texto) if texto != "" else []
	return {"ok": true, "mensaje": "", "datos": analizado if typeof(analizado) == TYPE_ARRAY else []}


## Traduce los nombres de columna en inglés de Supabase al español que
## usa la UI (mismo criterio que _normalizar_record en records_online.py).
func _normalizar_lista(registros: Array) -> Array:
	var normalizados := []
	for registro in registros:
		normalizados.append({
			"jugador": registro.get("player_name", "-"),
			"dificultad": registro.get("difficulty", "-"),
			"puntaje": registro.get("score", 0),
			"pilas_finales": registro.get("piles_finales", 0),
			"movimientos": registro.get("moves", 0),
			"duracion_segundos": registro.get("duration_seconds", 0),
			"fecha": registro.get("played_at", ""),
		})
	return normalizados
