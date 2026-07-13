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

try:
    from PIL import Image, ImageDraw, ImageFont, ImageTk
    PILLOW_DISPONIBLE = True
except ImportError:
    PILLOW_DISPONIBLE = False

CARPETA_IMAGENES = Path(__file__).parent.parent / "assets" / "cartas_img"

ANCHO_CARTA = 112
ALTO_CARTA = 176


def _dibujar_contador(imagen: "Image.Image", cantidad: int, ancho_carta: int) -> "Image.Image":
    """
    Graba, en la esquina inferior derecha de la imagen, una placa oscura
    con el número de cartas de la pila — mismo lenguaje visual que el
    cronómetro de la interfaz (fondo oscuro, dígitos verdes, aro dorado).

    Antes el contador vivía AFUERA de la imagen, como texto del botón de
    Tkinter (`compound="bottom"`): eso obligaba a reservarle una franja
    entera debajo de la carta, casi siempre mucho más grande que lo que
    hacía falta para mostrar un solo número. Grabándolo en la imagen, el
    botón vuelve a medir justo el tamaño de la carta.
    """
    imagen = imagen.convert("RGBA")
    dibujo = ImageDraw.Draw(imagen)
    texto = f"x{cantidad}"

    tamaño_fuente = max(11, int(ancho_carta * 0.16))
    try:
        fuente = ImageFont.truetype("arial.ttf", tamaño_fuente)
    except OSError:
        fuente = ImageFont.load_default()

    caja_texto = dibujo.textbbox((0, 0), texto, font=fuente)
    ancho_texto = caja_texto[2] - caja_texto[0]
    alto_texto = caja_texto[3] - caja_texto[1]

    relleno_x = max(4, int(ancho_carta * 0.05))
    relleno_y = max(3, int(ancho_carta * 0.03))
    ancho_placa = ancho_texto + relleno_x * 2
    alto_placa = alto_texto + relleno_y * 2
    margen = max(3, int(ancho_carta * 0.045))

    x2, y2 = imagen.width - margen, imagen.height - margen
    x1, y1 = x2 - ancho_placa, y2 - alto_placa
    radio = alto_placa / 2

    dibujo.rounded_rectangle(
        (x1, y1, x2, y2), radius=radio,
        fill=(26, 26, 26, 235), outline=(255, 224, 130, 255), width=max(1, int(ancho_carta * 0.012)),
    )
    dibujo.text(
        (x1 + relleno_x - caja_texto[0], y1 + relleno_y - caja_texto[1]),
        texto, font=fuente, fill=(77, 255, 136, 255),
    )
    return imagen


def ruta_imagen(carta: Carta) -> Path:
    """Arma el nombre de archivo esperado para una carta, ej: 'oros_7.png'."""
    nombre_palo = carta.palo.name.lower()  # Palo.OROS -> "oros"
    return CARPETA_IMAGENES / f"{nombre_palo}_{carta.valor}.png"


def cargar_imagen_carta(carta: Carta, ancho: int = ANCHO_CARTA, alto: int = ALTO_CARTA, cantidad: int | None = None):
    """
    Carga y redimensiona la imagen de una carta. Si se pasa `cantidad`,
    graba además la placa-contador en la esquina (ver `_dibujar_contador`).
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
    if cantidad is not None:
        imagen = _dibujar_contador(imagen, cantidad, ancho)
    return ImageTk.PhotoImage(imagen)


def cargar_imagen_dorso(ancho: int = ANCHO_CARTA, alto: int = ALTO_CARTA, cantidad: int | None = None):
    """Igual que cargar_imagen_carta, pero para el dorso (el mazo boca abajo)."""
    if not PILLOW_DISPONIBLE:
        raise RuntimeError(
            "Falta Pillow para mostrar las imágenes de las cartas. "
            "Instalalo con: pip install pillow --break-system-packages"
        )
    imagen = Image.open(CARPETA_IMAGENES / "dorso.png").resize((ancho, alto))
    if cantidad is not None:
        imagen = _dibujar_contador(imagen, cantidad, ancho)
    return ImageTk.PhotoImage(imagen)
