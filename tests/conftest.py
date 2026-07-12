"""
conftest.py
-----------
Pytest lee este archivo automáticamente antes de correr los tests.
Acá solo agregamos src/ a los lugares donde Python busca módulos, para
poder escribir "from cartas import Carta" en los tests como si
estuviéramos parados adentro de src/.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
