class_name Puntuacion
extends RefCounted

## Persistencia local y consultas de puntajes.

static var archivo_historial := "user://historial.json"


static func interpretar_resultado(pilas_finales: int) -> String:
	if pilas_finales <= 2:
		return "🏆 IMPOSIBLE. Partida perfecta absoluta — de esas que se cuentan pocas veces en la vida."
	if pilas_finales <= 4:
		return "✨ Juego perfecto. Un resultado espectacular."
	if pilas_finales <= 7:
		return "🎯 Excelente. Muy buena lectura del tablero."
	if pilas_finales <= 10:
		return "👍 Bueno. Nada mal."
	return "😅 Bueno... confío en que te irá mejor la próxima vez."


static func formatear_duracion(segundos: int) -> String:
	var minutos := segundos / 60
	var segundos_restantes := segundos % 60
	return "%dm %ds" % [minutos, segundos_restantes] if minutos else "%ds" % segundos_restantes


static func guardar_puntaje(nombre_jugador: String, resumen: Dictionary) -> void:
	var historial := cargar_historial()
	var entrada := resumen.duplicate()
	entrada["id_partida"] = resumen.get("id_partida", str(ResourceUID.create_id()))
	entrada["version_esquema"] = 1
	entrada["origen"] = "local"
	entrada["jugador"] = nombre_jugador
	historial.append(entrada)
	_guardar_historial(historial)


static func cargar_historial() -> Array:
	if not FileAccess.file_exists(archivo_historial):
		return []

	var archivo := FileAccess.open(archivo_historial, FileAccess.READ)
	if archivo == null:
		return []
	var datos = JSON.parse_string(archivo.get_as_text())
	return datos if typeof(datos) == TYPE_ARRAY else []


static func mejor_puntaje() -> Variant:
	var historial := cargar_historial()
	if historial.is_empty():
		return null
	return ordenar_records(historial)[0]


static func es_nuevo_record(resumen: Dictionary) -> bool:
	var mejor = mejor_puntaje()
	return mejor == null or _va_antes(resumen, mejor)


static func ordenar_records(partidas: Array) -> Array:
	var ordenadas := partidas.duplicate()
	ordenadas.sort_custom(_va_antes)
	return ordenadas


static func indice_jugador(partidas: Array) -> int:
	var total := 0
	var mejores := ordenar_records(partidas)
	for indice in range(mini(5, mejores.size())):
		total += _puntaje(mejores[indice])
	return total


static func clasificar_resultado(pilas_finales: int) -> String:
	if pilas_finales <= 2:
		return "Perfecta"
	if pilas_finales <= 4:
		return "Excelente"
	if pilas_finales <= 7:
		return "Muy buena"
	if pilas_finales <= 10:
		return "Buena"
	return "En progreso"


static func partidas_de_dificultad(partidas: Array, dificultad: String) -> Array:
	var resultado: Array = []
	for partida in partidas:
		if partida.get("dificultad") == dificultad:
			resultado.append(partida)
	return resultado


static func analizar_progreso(partidas: Array, dificultad: String) -> Dictionary:
	var juegos := partidas_de_dificultad(partidas, dificultad)
	if juegos.is_empty():
		return {"partidas": 0, "dificultad": dificultad, "distribucion": {}}

	var pilas: Array[int] = []
	var puntajes: Array[int] = []
	var tiempos: Array[int] = []
	var movimientos_totales := 0
	for juego in juegos:
		pilas.append(int(juego["pilas_finales"]))
		puntajes.append(int(juego["puntaje"]))
		tiempos.append(int(juego["duracion_segundos"]))
		movimientos_totales += int(juego["movimientos"])

	var mejor_resultado = _mejor_resultado(juegos)
	var menor_pilas := int(mejor_resultado["pilas_finales"])
	var candidatas_tiempo: Array = []
	for juego in juegos:
		if int(juego["pilas_finales"]) == menor_pilas:
			candidatas_tiempo.append(juego)
	var mejor_tiempo = _menor_tiempo(candidatas_tiempo)

	var distribucion := {"2": 0, "3-4": 0, "5-7": 0, "8-10": 0, "11+": 0}
	for cantidad in pilas:
		var clave := "2" if cantidad <= 2 else "3-4" if cantidad <= 4 else "5-7" if cantidad <= 7 else "8-10" if cantidad <= 10 else "11+"
		distribucion[clave] += 1

	var tendencia: Variant = null
	if juegos.size() >= 20:
		tendencia = _promedio(pilas.slice(-20, -10)) - _promedio(pilas.slice(-10))

	var mejor_promedio_reciente: Variant = null
	if juegos.size() >= 10:
		for indice in range(juegos.size() - 9):
			var promedio := _promedio(pilas.slice(indice, indice + 10))
			if mejor_promedio_reciente == null or promedio < mejor_promedio_reciente:
				mejor_promedio_reciente = promedio

	return {
		"partidas": juegos.size(),
		"dificultad": dificultad,
		"tiempo_total": _suma(tiempos),
		"movimientos_totales": movimientos_totales,
		"promedio_pilas": _promedio(pilas),
		"mediana_pilas": _mediana(pilas),
		"puntaje_promedio": roundi(float(_suma(puntajes)) / puntajes.size()),
		"mejor_resultado": mejor_resultado,
		"mayor_puntaje": ordenar_records(juegos)[0],
		"mejor_tiempo": mejor_tiempo,
		"promedio_ultimas_diez": _promedio(pilas.slice(-10)),
		"mejor_promedio_reciente": mejor_promedio_reciente,
		"tendencia_pilas": tendencia,
		"distribucion": distribucion,
	}


static func mensaje_comparacion(resumen: Dictionary, partidas_anteriores: Array) -> String:
	var juegos := partidas_de_dificultad(partidas_anteriores, resumen["dificultad"])
	if juegos.is_empty():
		return "Tu primera partida en esta dificultad. Ya tenés una referencia para superar."

	var mejor_anterior = _mejor_resultado(juegos)
	var pilas := int(resumen["pilas_finales"])
	var mejor_pilas := int(mejor_anterior["pilas_finales"])
	if pilas < mejor_pilas:
		return "Nuevo mejor resultado personal."
	if pilas == mejor_pilas:
		if _va_antes(resumen, ordenar_records(juegos)[0]):
			return "Igualaste tu mejor resultado y lograste tu mayor puntaje."
		return "Igualaste tu mejor resultado personal."
	if pilas == mejor_pilas + 1:
		return "A una pila de tu mejor resultado personal."
	if juegos.size() >= 10:
		var promedio := _promedio(_pilas_finales(juegos.slice(-10)))
		var diferencia := snappedf(promedio - pilas, 0.1)
		if diferencia > 0:
			return "%.1f pilas mejor que tu promedio reciente." % diferencia
		if diferencia < 0:
			return "Tu promedio reciente es de %.1f pilas." % promedio
	return "Tu mejor resultado personal es de %d pilas." % mejor_pilas


static func _guardar_historial(historial: Array) -> void:
	var archivo := FileAccess.open(archivo_historial, FileAccess.WRITE)
	if archivo != null:
		archivo.store_string(JSON.stringify(historial, "\t"))


static func _va_antes(a: Dictionary, b: Dictionary) -> bool:
	if _puntaje(a) != _puntaje(b):
		return _puntaje(a) > _puntaje(b)
	if int(a.get("duracion_segundos", 0)) != int(b.get("duracion_segundos", 0)):
		return int(a.get("duracion_segundos", 0)) < int(b.get("duracion_segundos", 0))
	if int(a.get("movimientos", 0)) != int(b.get("movimientos", 0)):
		return int(a.get("movimientos", 0)) < int(b.get("movimientos", 0))
	return str(a.get("fecha", a.get("played_at", ""))) < str(b.get("fecha", b.get("played_at", "")))


static func _puntaje(partida: Dictionary) -> int:
	return int(partida.get("puntaje", partida.get("score", 0)))


static func _mejor_resultado(juegos: Array):
	var mejor = juegos[0]
	for juego in juegos.slice(1):
		if int(juego["pilas_finales"]) < int(mejor["pilas_finales"]):
			mejor = juego
		elif int(juego["pilas_finales"]) == int(mejor["pilas_finales"]) and _va_antes(juego, mejor):
			mejor = juego
	return mejor


static func _menor_tiempo(juegos: Array):
	var mejor = juegos[0]
	for juego in juegos.slice(1):
		if int(juego["duracion_segundos"]) < int(mejor["duracion_segundos"]):
			mejor = juego
	return mejor


static func _promedio(valores: Array) -> float:
	return snappedf(float(_suma(valores)) / valores.size(), 0.1)


static func _pilas_finales(juegos: Array) -> Array[int]:
	var pilas: Array[int] = []
	for juego in juegos:
		pilas.append(int(juego["pilas_finales"]))
	return pilas


static func _suma(valores: Array) -> int:
	var total := 0
	for valor in valores:
		total += int(valor)
	return total


static func _mediana(valores: Array[int]) -> float:
	var ordenados := valores.duplicate()
	ordenados.sort()
	var medio := ordenados.size() / 2
	return ordenados[medio] if ordenados.size() % 2 else (ordenados[medio - 1] + ordenados[medio]) / 2.0
