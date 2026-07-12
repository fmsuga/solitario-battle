"""
main.py
-------
Punto de entrada de la versión CONSOLA. Este archivo queda en la raíz
a propósito: es lo primero que se ejecuta, y de acá se busca el código
real dentro de src/.
"""

import sys
from pathlib import Path

# Agrega la carpeta src/ a los lugares donde Python busca módulos,
# para poder hacer "from interfaz_consola import ..." como si
# estuviéramos parados adentro de src/.
sys.path.insert(0, str(Path(__file__).parent / "src"))

from interfaz_consola import jugar

if __name__ == "__main__":
    jugar()
