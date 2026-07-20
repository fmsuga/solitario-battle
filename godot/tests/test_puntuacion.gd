extends GutTest

const ARCHIVO_TEMPORAL := "user://historial_test_gut.json"


func before_each() -> void:
	Puntuacion.archivo_historial = ARCHIVO_TEMPORAL
	_borrar_historial_temporal()


func after_each() -> void:
	_borrar_historial_temporal()
	Puntuacion.archivo_historial = "user://historial.json"


func test_formatear_duracion_menos_de_un_minuto() -> void:
	assert_eq(Puntuacion.formatear_duracion(45), "45s")


func test_formatear_duracion_con_minutos() -> void:
	assert_eq(Puntuacion.formatear_duracion(222), "3m 42s")


func test_interpretar_resultado_extremos() -> void:
	assert_string_contains(Puntuacion.interpretar_resultado(2), "IMPOSIBLE")
	assert_string_contains(Puntuacion.interpretar_resultado(30), "próxima vez")


func test_es_nuevo_record_compara_con_el_mejor_historial() -> void:
	_escribir_historial_temporal([{
		"puntaje": 300, "duracion_segundos": 100, "movimientos": 20, "fecha": "2026-01-01",
	}])
	assert_true(Puntuacion.es_nuevo_record({
		"puntaje": 320, "duracion_segundos": 120, "movimientos": 21, "fecha": "2026-01-02",
	}))
	assert_false(Puntuacion.es_nuevo_record({
		"puntaje": 280, "duracion_segundos": 90, "movimientos": 18, "fecha": "2026-01-02",
	}))


func test_guardar_y_cargar_historial() -> void:
	var resumen := {
		"fecha": "2026-07-10 10:00", "duracion_segundos": 120,
		"movimientos": 5, "pilas_finales": 10, "puntaje": 380,
	}
	Puntuacion.guardar_puntaje("Tester", resumen)

	var historial := Puntuacion.cargar_historial()
	assert_eq(historial.size(), 1)
	assert_eq(historial[0]["jugador"], "Tester")
	assert_eq(int(historial[0]["puntaje"]), 380)
	assert_true(str(historial[0]["id_partida"]).length() > 0)
	assert_eq(int(historial[0]["version_esquema"]), 1)
	assert_eq(historial[0]["origen"], "local")
	assert_eq(Puntuacion.mejor_puntaje()["jugador"], "Tester")


func test_ranking_prioriza_puntaje_y_desempata_por_tiempo_y_movimientos() -> void:
	var partidas := [
		{"puntaje": 2000, "duracion_segundos": 90, "movimientos": 8, "fecha": "2026-01-03"},
		{"puntaje": 2000, "duracion_segundos": 70, "movimientos": 9, "fecha": "2026-01-02"},
		{"puntaje": 2000, "duracion_segundos": 70, "movimientos": 7, "fecha": "2026-01-01"},
		{"puntaje": 1900, "duracion_segundos": 10, "movimientos": 1, "fecha": "2026-01-01"},
	]
	var ordenadas := Puntuacion.ordenar_records(partidas)
	assert_eq(ordenadas[0]["movimientos"], 7)
	assert_eq(ordenadas[1]["movimientos"], 9)
	assert_eq(ordenadas[-1]["puntaje"], 1900)
	assert_eq(Puntuacion.indice_jugador(partidas), 7900)


func test_analizar_progreso_separa_dificultades_y_prioriza_menos_pilas() -> void:
	var partidas := [
		{"dificultad": "facil", "pilas_finales": 5, "puntaje": 800, "duracion_segundos": 100, "movimientos": 35, "fecha": "2026-01-01"},
		{"dificultad": "facil", "pilas_finales": 3, "puntaje": 600, "duracion_segundos": 120, "movimientos": 37, "fecha": "2026-01-02"},
		{"dificultad": "dificil", "pilas_finales": 2, "puntaje": 15000, "duracion_segundos": 200, "movimientos": 46, "fecha": "2026-01-03"},
	]
	var datos := Puntuacion.analizar_progreso(partidas, "facil")
	assert_eq(datos["partidas"], 2)
	assert_eq(datos["mejor_resultado"]["pilas_finales"], 3)
	assert_eq(datos["mejor_tiempo"]["pilas_finales"], 3)
	assert_eq(datos["distribucion"], {"2": 0, "3-4": 1, "5-7": 1, "8-10": 0, "11+": 0})


func test_progreso_calcula_tendencia_solo_con_veinte_partidas() -> void:
	var partidas: Array = []
	for indice in range(20):
		partidas.append({
			"dificultad": "facil", "pilas_finales": 10 if indice < 10 else 6,
			"puntaje": indice, "duracion_segundos": 60, "movimientos": 1,
			"fecha": "2026-01-%02d" % (indice + 1),
		})
	var datos := Puntuacion.analizar_progreso(partidas, "facil")
	assert_eq(datos["tendencia_pilas"], 4.0)
	assert_eq(datos["mejor_promedio_reciente"], 6.0)


func test_clasificacion_y_mensaje_de_comparacion() -> void:
	var anterior := [{
		"dificultad": "facil", "pilas_finales": 5, "puntaje": 400,
		"duracion_segundos": 90, "movimientos": 35, "fecha": "2026-01-01",
	}]
	var resumen := {
		"dificultad": "facil", "pilas_finales": 4, "puntaje": 500,
		"duracion_segundos": 100, "movimientos": 36,
	}
	assert_eq(Puntuacion.clasificar_resultado(4), "Excelente")
	assert_eq(Puntuacion.mensaje_comparacion(resumen, anterior), "Nuevo mejor resultado personal.")


func test_mensaje_comparacion_usa_promedio_reciente_con_diez_partidas() -> void:
	var anteriores: Array = []
	for indice in range(10):
		anteriores.append({
			"dificultad": "facil", "pilas_finales": 5 if indice == 0 else 6,
			"puntaje": 400, "duracion_segundos": 90, "movimientos": 35,
			"fecha": "2026-01-%02d" % (indice + 1),
		})
	var resumen := {
		"dificultad": "facil", "pilas_finales": 8, "puntaje": 300,
		"duracion_segundos": 100, "movimientos": 36,
	}
	assert_eq(
		Puntuacion.mensaje_comparacion(resumen, anteriores),
		"Tu promedio reciente es de 5.9 pilas."
	)


func test_mensaje_rareza_usa_probabilidades_documentadas_exactas() -> void:
	assert_string_contains(Puntuacion.mensaje_rareza({"dificultad": "dificil", "pilas_finales": 2}), "0.18%")
	# La probabilidad exacta de 3 se obtiene de P(≤3) - P(≤2).
	assert_string_contains(Puntuacion.mensaje_rareza({"dificultad": "dificil", "pilas_finales": 3}), "0.73%")


func test_logros_nuevos_detecta_pilas_puntaje_y_duracion() -> void:
	var anteriores := [{"pilas_finales": 5, "puntaje": 100, "duracion_segundos": 90}]
	var logros := Puntuacion.logros_nuevos({"pilas_finales": 4, "puntaje": 110, "duracion_segundos": 80}, anteriores)
	assert_eq(logros.size(), 3)


func _escribir_historial_temporal(datos: Array) -> void:
	var archivo := FileAccess.open(ARCHIVO_TEMPORAL, FileAccess.WRITE)
	archivo.store_string(JSON.stringify(datos))


func _borrar_historial_temporal() -> void:
	if FileAccess.file_exists(ARCHIVO_TEMPORAL):
		DirAccess.remove_absolute(ProjectSettings.globalize_path(ARCHIVO_TEMPORAL))
