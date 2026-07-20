class_name Juego
extends RefCounted

## Orquesta el mazo, el tablero, el estado y las estadísticas de una partida.

const REGLAS := preload("res://scripts/reglas.gd")

const BONOS_POR_PILAS := {
	2: 10000,
	3: 5500,
	4: 2800,
	5: 1400,
	6: 700,
	7: 350,
	8: 180,
}

const NOMBRES_DIFICULTAD := {
	Carta.Dificultad.FACIL: "facil",
	Carta.Dificultad.DIFICIL: "dificil",
}

var dificultad: int
var mazo: Carta.Mazo
var tablero: Tablero
var terminada := false
var cantidad_cartas_inicial: int
var momento_inicio: float
var momento_fin: Variant = null
var cantidad_jugadas_realizadas := 0
var cartas_iniciales: Array[Carta] = []
var oportunidades_antiguas_bloqueadas := 0
var decisiones_con_bloqueo := 0


func _init(p_dificultad: int = Carta.Dificultad.DIFICIL) -> void:
	dificultad = p_dificultad
	mazo = Carta.Mazo.new(dificultad)
	mazo.mezclar()
	# El orden se conserva para analizar la misma mano al terminar. Repartir
	# extrae desde el final, pero el momento de reparto no altera los
	# resultados alcanzables (ver traspaso_records_y_comodin.md, sección 2).
	cartas_iniciales = mazo.cartas.duplicate()
	tablero = Tablero.new()
	cantidad_cartas_inicial = mazo.quedan_cartas()
	momento_inicio = Time.get_unix_time_from_system()


func repartir_carta() -> void:
	if terminada or not quedan_cartas_en_mano():
		return
	tablero.agregar_carta_nueva(mazo.repartir_una())


func intentar_jugada(indice_izquierda: int) -> bool:
	if terminada:
		return false

	var oportunidades_anteriores := _capturar_oportunidades_antiguas(indice_izquierda)
	var resultado: bool = REGLAS.ejecutar_jugada(tablero, indice_izquierda)
	if resultado:
		cantidad_jugadas_realizadas += 1
		var bloqueos_en_jugada := 0
		for oportunidad in oportunidades_anteriores:
			if not _oportunidad_sigue_disponible(oportunidad):
				bloqueos_en_jugada += 1
		oportunidades_antiguas_bloqueadas += bloqueos_en_jugada
		if bloqueos_en_jugada > 0:
			decisiones_con_bloqueo += 1
	return resultado


## Guarda las ternas de pilas de las jugadas más antiguas. Se conservan
## referencias a Pila, no índices: tras una fusión los índices cambian,
## pero la identidad de cada pila que sobrevive no.
func _capturar_oportunidades_antiguas(indice_elegido: int) -> Array:
	var oportunidades: Array = []
	for indice in REGLAS.buscar_jugadas_posibles(tablero):
		if indice >= indice_elegido:
			break
		oportunidades.append([
			tablero.pilas[indice], tablero.pilas[indice + 1], tablero.pilas[indice + 2],
		])
	return oportunidades


func _oportunidad_sigue_disponible(oportunidad: Array) -> bool:
	var izquierda: Tablero.Pila = oportunidad[0]
	var medio: Tablero.Pila = oportunidad[1]
	var derecha: Tablero.Pila = oportunidad[2]
	var indice_izquierda := tablero.pilas.find(izquierda)
	if indice_izquierda < 0 or indice_izquierda + 2 >= tablero.pilas.size():
		return false
	if tablero.pilas[indice_izquierda + 1] != medio or tablero.pilas[indice_izquierda + 2] != derecha:
		return false
	return REGLAS.es_jugada_valida(tablero, indice_izquierda)


func quedan_cartas_en_mano() -> bool:
	return mazo.quedan_cartas() > 0


func finalizar() -> void:
	if not terminada:
		momento_fin = Time.get_unix_time_from_system()
	terminada = true


func esta_terminada() -> bool:
	return terminada


func cantidad_pilas_finales() -> int:
	return tablero.cantidad_pilas()


func calcular_puntaje() -> int:
	var pilas_finales := cantidad_pilas_finales()
	var puntos_por_fusiones := (cantidad_cartas_inicial - pilas_finales) * 10
	var bono: int = BONOS_POR_PILAS.get(pilas_finales, 0)
	var multiplicador := 1.5 if dificultad == Carta.Dificultad.DIFICIL else 1.0
	return roundi((puntos_por_fusiones + bono) * multiplicador)


func duracion_segundos() -> int:
	return int(duracion_segundos_precisa())


func duracion_segundos_precisa() -> float:
	var fin: float = momento_fin if momento_fin != null else Time.get_unix_time_from_system()
	return fin - momento_inicio


func pilas_referencia_viejo_primero() -> int:
	var referencia := Tablero.new()
	# Mazo.repartir_una() usa pop_back(), por eso el orden de juego es el
	# inverso del array mezclado conservado al inicio.
	for indice in range(cartas_iniciales.size() - 1, -1, -1):
		referencia.agregar_carta_nueva(cartas_iniciales[indice])
	while true:
		var jugadas: Array[int] = REGLAS.buscar_jugadas_posibles(referencia)
		if jugadas.is_empty():
			break
		REGLAS.ejecutar_jugada(referencia, jugadas[0])
	return referencia.cantidad_pilas()


func eficiencia_tactica() -> float:
	var fusiones_referencia := cantidad_cartas_inicial - pilas_referencia_viejo_primero()
	if fusiones_referencia <= 0:
		return 100.0
	var fusiones_jugador := cantidad_cartas_inicial - cantidad_pilas_finales()
	return snappedf(maxf(0.0, float(fusiones_jugador) / fusiones_referencia * 100.0), 0.1)


func obtener_resumen() -> Dictionary:
	var fecha := Time.get_datetime_dict_from_unix_time(int(momento_inicio))
	var referencia := pilas_referencia_viejo_primero()
	return {
		"fecha": "%04d-%02d-%02d %02d:%02d" % [
			fecha.year, fecha.month, fecha.day, fecha.hour, fecha.minute,
		],
		"dificultad": NOMBRES_DIFICULTAD[dificultad],
		"duracion_segundos": duracion_segundos(),
		"movimientos": cantidad_jugadas_realizadas,
		"pilas_finales": cantidad_pilas_finales(),
		"puntaje": calcular_puntaje(),
		"pilas_referencia": referencia,
		"diferencia_referencia": cantidad_pilas_finales() - referencia,
		"eficiencia_tactica": eficiencia_tactica(),
		"oportunidades_antiguas_bloqueadas": oportunidades_antiguas_bloqueadas,
		"decisiones_con_bloqueo": decisiones_con_bloqueo,
	}
