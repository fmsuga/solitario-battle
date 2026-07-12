"""
imagenes_cartas.py
-------------------
Mapea cada carta a su imagen (recortada de una foto del mazo completo,
en cartas_img/) y la carga con el tamaño que necesite la interfaz.

Requiere Pillow, porque Tkinter solo (sin Pillow) no puede redimensionar
imágenes a un tamaño arbitrario:
    pip install pillow --break-system-packages
"""

from pathlib import Path

from cartas import Carta
from recursos import ruta_base_recursos

try:
    from PIL import Image, ImageTk
    PILLOW_DISPONIBLE = True
except ImportError:
    PILLOW_DISPONIBLE = False

CARPETA_IMAGENES = ruta_base_recursos() / "assets" / "cartas_img"

ANCHO_CARTA = 92
ALTO_CARTA = 145


def ruta_imagen(carta: Carta) -> Path:
    """Arma el nombre de archivo esperado para una carta, ej: 'oros_7.png'."""
    nombre_palo = carta.palo.name.lower()  # Palo.OROS -> "oros"
    return CARPETA_IMAGENES / f"{nombre_palo}_{carta.valor}.png"


def cargar_imagen_carta(carta: Carta, ancho: int = ANCHO_CARTA, alto: int = ALTO_CARTA):
    """
    Carga y redimensiona la imagen de una carta.
    Devuelve un ImageTk.PhotoImage listo para usar como `image=` en un
    widget de Tkinter (ojo: hay que guardar una referencia a lo que
    devuelve esta función mientras el widget esté en pantalla, o Python
    se la borra de memoria y el botón queda en blanco).
    """
    if not PILLOW_DISPONIBLE:
        raise RuntimeError(
            "Falta Pillow para mostrar las imágenes de las cartas. "
            "Instalalo con: pip install pillow --break-system-packages"
        )
    imagen = Image.open(ruta_imagen(carta)).resize((ancho, alto))
    return ImageTk.PhotoImage(imagen)


def cargar_imagen_dorso(ancho: int = ANCHO_CARTA, alto: int = ALTO_CARTA):
    """Igual que cargar_imagen_carta, pero para el dorso (el mazo boca abajo)."""
    if not PILLOW_DISPONIBLE:
        raise RuntimeError(
            "Falta Pillow para mostrar las imágenes de las cartas. "
            "Instalalo con: pip install pillow --break-system-packages"
        )
    imagen = Image.open(CARPETA_IMAGENES / "dorso.png").resize((ancho, alto))
    return ImageTk.PhotoImage(imagen)
