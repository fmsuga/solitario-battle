"""Punto de entrada de Solitario Battle."""

import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent / "src"))

from interfaz_grafica import jugar_partida_grafica


if __name__ == "__main__":
    jugar_partida_grafica()
