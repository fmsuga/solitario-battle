"""
main_grafico.py
----------------
Punto de entrada de la versión GRÁFICA (Tkinter). Queda en la raíz a
propósito; el código real está en src/.

Requiere:
- paquete de sistema python3-tk (Ubuntu/Debian: sudo apt install python3-tk)
- Pillow (pip install pillow --break-system-packages)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from interfaz_grafica import jugar_partida_grafica

if __name__ == "__main__":
    jugar_partida_grafica()
