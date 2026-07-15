class_name Tablero
extends RefCounted

## Estado de la mesa: pilas de cartas ordenadas de izquierda a derecha.
## No contiene reglas para validar jugadas.


class Pila extends RefCounted:
	var cartas: Array[Carta] = []


	func _init(carta_inicial: Carta) -> void:
		cartas = [carta_inicial]


	func tope() -> Carta:
		return cartas.back()


	func apilar_encima(otra_pila: Pila) -> void:
		cartas.append_array(otra_pila.cartas)


	func cantidad_cartas() -> int:
		return cartas.size()


	func _to_string() -> String:
		if cantidad_cartas() > 1:
			return "%s (+%d debajo)" % [tope()._to_string(), cantidad_cartas() - 1]
		return tope()._to_string()


var pilas: Array[Pila] = []


func agregar_carta_nueva(carta: Carta) -> void:
	pilas.append(Pila.new(carta))


func cantidad_pilas() -> int:
	return pilas.size()


func fusionar(indice_pila_1: int, indice_pila_2: int) -> void:
	pilas[indice_pila_1].apilar_encima(pilas[indice_pila_2])
	pilas.remove_at(indice_pila_2)
