"""
recursos.py
------------
Módulo centralizado para resolver rutas de recursos (imágenes, etc.) y de
datos persistentes (historial.json), tanto ejecutando desde el código
fuente como ejecutando el .exe generado con PyInstaller (--onefile).

Por qué hace falta esto:
PyInstaller, en modo --onefile, descomprime en tiempo de ejecución todo lo
declarado en `datas` a una carpeta temporal (sys._MEIPASS), que desaparece
al cerrar el programa. Además, como el proyecto se compila con
`--paths src` (para poder importar "cartas", "juego", etc. tal cual se
hace en desarrollo), los módulos de src/ quedan sueltos en la raíz del
paquete: no existe una subcarpeta "src" dentro del bundle. Calcular una
ruta a partir de `Path(__file__).parent.parent` (como si siempre hubiera
un nivel "src/" de por medio) apunta entonces a un lugar equivocado
cuando se corre el .exe, aunque funcione perfecto en desarrollo.

Este módulo resuelve ambos casos en un único lugar, para que el resto del
código no tenga que preocuparse por si está "congelado" o no.
"""

import sys
from pathlib import Path


def ruta_base_recursos() -> Path:
    """
    Carpeta base para ubicar recursos empaquetados de solo lectura
    (por ahora, assets/).

    - Ejecutando el .exe: sys._MEIPASS, la carpeta temporal donde
      PyInstaller descomprime lo declarado en `datas`/`--add-data`.
    - Ejecutando desde el código fuente: la raíz del proyecto (un nivel
      arriba de src/, que es donde vive la carpeta assets/).
    """
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent.parent


def ruta_base_datos_usuario() -> Path:
    """
    Carpeta base para archivos que el programa necesita poder leer Y
    escribir (por ahora, historial.json). A diferencia de los recursos
    empaquetados, no puede ser una carpeta temporal: tiene que ser la
    misma en cada ejecución (para que el historial persista) y tiene que
    admitir escritura.

    - Ejecutando el .exe: la carpeta donde está el .exe (no la temporal
      de descompresión), así el historial queda al lado del ejecutable
      y sobrevive entre partidas.
    - Ejecutando desde el código fuente: la raíz del proyecto.
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent
