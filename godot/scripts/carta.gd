class_name Carta
extends RefCounted

## Datos puros de una carta española y de su mazo.
## Este archivo no conoce reglas de jugada ni interfaz.

enum Palo {
	OROS,
	COPAS,
	ESPADAS,
	BASTOS,
}

enum Dificultad {
	FACIL,
	DIFICIL,
}

const NOMBRES_VALOR := {
	1: "As",
	2: "2",
	3: "3",
	4: "4",
	5: "5",
	6: "6",
	7: "7",
	8: "8",
	9: "9",
	10: "10",
	11: "11",
	12: "12",
}

const NOMBRES_PALO := {
	Palo.OROS: "Oro",
	Palo.COPAS: "Copa",
	Palo.ESPADAS: "Espada",
	Palo.BASTOS: "Basto",
}

const CANTIDAD_CARTAS_EN_MAZO := 48

var palo: int
var valor: int


func _init(p_palo: int, p_valor: int) -> void:
	palo = p_palo
	valor = p_valor


func mismo_valor(otra: Carta) -> bool:
	return valor == otra.valor


func mismo_palo(otra: Carta) -> bool:
	return palo == otra.palo


func _to_string() -> String:
	return "%s de %s" % [NOMBRES_VALOR[valor], NOMBRES_PALO[palo]]


class Mazo extends RefCounted:
	var dificultad: int
	var cartas: Array[Carta] = []


	func _init(p_dificultad: int = Dificultad.DIFICIL) -> void:
		dificultad = p_dificultad
		cartas = _crear_mazo_completo()


	func _crear_mazo_completo() -> Array[Carta]:
		var valores_excluidos: Array[int] = []
		if dificultad == Dificultad.FACIL:
			valores_excluidos = [8, 9]

		var mazo: Array[Carta] = []
		for palo_actual in Palo.values():
			for valor_actual in range(1, 13):
				if valor_actual in valores_excluidos:
					continue
				mazo.append(Carta.new(palo_actual, valor_actual))
		return mazo


	func mezclar() -> void:
		cartas.shuffle()


	func repartir_una() -> Carta:
		return cartas.pop_back()


	func quedan_cartas() -> int:
		return cartas.size()
