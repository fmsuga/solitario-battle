class_name Juego
extends RefCounted

## Orquesta el mazo, el tablero, el estado y las estadísticas de una partida.

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


func _init(p_dificultad: int = Carta.Dificultad.DIFICIL) -> void:
	dificultad = p_dificultad
	mazo = Carta.Mazo.new(dificultad)
	mazo.mezclar()
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

	var resultado := Reglas.ejecutar_jugada(tablero, indice_izquierda)
	if resultado:
		cantidad_jugadas_realizadas += 1
	return resultado


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
	var fin: float = momento_fin if momento_fin != null else Time.get_unix_time_from_system()
	return int(fin - momento_inicio)


func obtener_resumen() -> Dictionary:
	var fecha := Time.get_datetime_dict_from_unix_time(momento_inicio)
	return {
		"fecha": "%04d-%02d-%02d %02d:%02d" % [
			fecha.year, fecha.month, fecha.day, fecha.hour, fecha.minute,
		],
		"dificultad": NOMBRES_DIFICULTAD[dificultad],
		"duracion_segundos": duracion_segundos(),
		"movimientos": cantidad_jugadas_realizadas,
		"pilas_finales": cantidad_pilas_finales(),
		"puntaje": calcular_puntaje(),
	}
