class_name Reglas
extends RefCounted

## Validación y ejecución de jugadas sobre un Tablero.


static func hay_coincidencia(carta_1: Carta, carta_3: Carta) -> bool:
	return carta_1.mismo_valor(carta_3) or carta_1.mismo_palo(carta_3)


static func es_jugada_valida(tablero: Tablero, indice_izquierda: int) -> bool:
	var indice_derecha := indice_izquierda + 2
	if indice_izquierda < 0 or indice_derecha >= tablero.cantidad_pilas():
		return false

	var pila_izquierda := tablero.pilas[indice_izquierda]
	var pila_derecha := tablero.pilas[indice_derecha]
	return hay_coincidencia(pila_izquierda.tope(), pila_derecha.tope())


static func ejecutar_jugada(tablero: Tablero, indice_izquierda: int) -> bool:
	if not es_jugada_valida(tablero, indice_izquierda):
		return false

	var indice_medio := indice_izquierda + 1
	tablero.fusionar(indice_izquierda, indice_medio)
	return true


static func buscar_jugadas_posibles(tablero: Tablero) -> Array[int]:
	var jugadas: Array[int] = []
	for indice in range(maxi(0, tablero.cantidad_pilas() - 2)):
		if es_jugada_valida(tablero, indice):
			jugadas.append(indice)
	return jugadas
