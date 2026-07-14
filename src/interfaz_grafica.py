"""Interfaz gráfica de Solitario Battle.

Este módulo sólo presenta la partida: no modifica reglas ni estado de las
clases de dominio. Incluye menú, tablero, arrastrar/soltar y pantallas de
resultado usando una única identidad visual.
"""

import math
import random
import tkinter as tk

try:
    from PIL import Image, ImageOps, ImageTk
except ImportError:
    Image = ImageOps = ImageTk = None

try:
    from pygame import mixer
except ImportError:  # Permite ejecutar la interfaz también fuera de Windows.
    mixer = None

from cartas import CANTIDAD_CARTAS_EN_MAZO, Dificultad
import configuracion
from imagenes_cartas import ALTO_CARTA, ANCHO_CARTA, cargar_imagen_carta, cargar_imagen_dorso
from juego import Juego
import puntuacion
import records_online
from recursos import ruta_base_recursos


# Paleta: paño de mesa profundo, carbón y tonos cálidos de las cartas.
COLOR_MESA = "#0B3D2E"
COLOR_MESA_OSCURO = "#062A20"
COLOR_PANEL = "#102C25"
COLOR_PANEL_ELEVADO = "#163A30"
COLOR_TARJETA = "#F8F3E8"
COLOR_TARJETA_HOVER = "#EEE5D3"
COLOR_TEXTO = "#F7F0DD"
COLOR_MUTED = "#B7CCBF"
COLOR_TEXTO_OSCURO = "#18332B"
COLOR_ACENTO = "#D85B45"
COLOR_ACENTO_HOVER = "#EE725A"
COLOR_BORDE = "#2C5849"
COLOR_DORADO = "#E5BE72"
COLOR_EXITO = "#B9E6A4"
COLOR_ERROR = "#FFAD91"
COLOR_SOMBRA_CLARA = "#C9D6D0"

FUENTE_TITULO = ("Segoe UI", 30, "bold")
FUENTE_SUBTITULO = ("Segoe UI", 11)
FUENTE_TEXTO = ("Segoe UI", 10)
FUENTE_BOTON = ("Segoe UI", 11, "bold")
FUENTE_ESTADISTICA = ("Consolas", 20, "bold")

RATIO_CARTA = ALTO_CARTA / ANCHO_CARTA
# El tablero se desplaza verticalmente, pero mantiene varias cartas visibles
# a la vez para que leer la mesa no exija recorrer demasiado la pantalla.
COLUMNAS_TABLERO = 10
ANCHO_CARTA_MINIMO = 100
ANCHO_CARTA_MAXIMO = 135
GAP_CELDA = 10
MARGEN_PANTALLA_X = 70
MARGEN_PANTALLA_Y = 100

CARPETA_SONIDOS = ruta_base_recursos() / "assets" / "sonidos"
SONIDO_REPARTIR = CARPETA_SONIDOS / "repartir.wav"
SONIDO_MOVIMIENTO_EXITOSO = CARPETA_SONIDOS / "movimiento_exitoso.wav"
RUTA_ORNAMENTO = ruta_base_recursos() / "assets" / "interfaz" / "ornamento_dorado.png"
RUTAS_PALOS_MENU = (
    ruta_base_recursos() / "assets" / "interfaz" / "palo_oros.png",
    ruta_base_recursos() / "assets" / "interfaz" / "palo_copas.png",
    ruta_base_recursos() / "assets" / "interfaz" / "palo_espadas.png",
    ruta_base_recursos() / "assets" / "interfaz" / "palo_bastos.png",
)


TEXTOS = {
    "es": {
        "choose_difficulty": "Elegí una dificultad", "moves": "MOVIMIENTOS", "time": "TIEMPO",
        "surrender": "Rendirse", "finish": "Finalizar", "options": "Opciones",
        "back_to_menu": "Volver al menú principal", "continue_game": "Continuar partida",
        "game_menu": "MENÚ DE PARTIDA", "difficulty_menu": "MENÚ DE DIFICULTAD",
        "choose_difficulty_title": "ELEGÍ LA DIFICULTAD", "difficulty_hint": "Las reglas son las mismas; cambia el tamaño del mazo.",
        "classic": "Clásico", "hard": "Difícil", "easy": "Fácil", "cards": "cartas",
        "valid_move": "¡Jugada válida! Buen ojo.", "invalid_move": "Ahí no hay ninguna coincidencia. Fijate de nuevo.",
        "deck_empty": "Se acabaron las cartas. Si no ves más jugadas, terminá la partida.",
        "new_game_hint": "Elegí la dificultad para arrancar de nuevo.", "game": "Partida",
        "piles_on_table": "pilas en mesa", "sound": "Sonido del juego", "volume": "VOLUMEN",
        "muted": "Silenciado", "language": "IDIOMA", "spanish": "Español", "english": "English",
        "save_options": "Guardar opciones", "settings": "Configuración", "save_settings": "Guardar configuración",
        "play": "Jugar", "records": "Récords", "quit": "Salir", "tagline": "Un juego de observación y estrategia",
        "abandon_game": "Abandonar partida", "abandon_confirm": "¿Seguro que querés abandonar esta partida?\nNo se guardará el puntaje actual.",
        "abandon": "Abandonar", "back_title": "Volver al menú", "back_confirm": "¿Querés volver al menú principal?\nLa partida actual no se guardará.",
        "cancel": "Cancelar", "understood": "Entendido", "finish_game": "TERMINAR PARTIDA  ·  VER RESULTADO",
        "game_finished": "PARTIDA TERMINADA", "your_result": "Tu mesa, tu resultado", "final_score": "PUNTAJE FINAL",
        "final_piles": "pilas finales", "name_to_save": "Nombre para guardar el puntaje", "save_score": "Guardar puntaje",
        "new_game": "Nueva partida", "main_menu": "Menú principal", "name_missing": "Falta el nombre",
        "restart_game": "Reiniciar partida", "restart_confirm": "¿Querés reiniciar la partida actual?\nVas a volver a elegir la dificultad.",
        "new_record": "¡NUEVO RÉCORD!",
        "resume_game": "Seguir jugando", "restart_from_menu": "Empezar de nuevo",
        "settings_from_menu": "Ajustes", "return_to_home": "Salir al inicio",
        "name_missing_message": "Escribí un nombre antes de guardar.", "score_saved": "Puntaje guardado",
        "score_published": "Puntaje guardado y publicado en el ranking mundial.",
    },
    "en": {
        "choose_difficulty": "Choose a difficulty", "moves": "MOVES", "time": "TIME",
        "surrender": "Surrender", "finish": "Finish", "options": "Options",
        "back_to_menu": "Back to main menu", "continue_game": "Continue game",
        "game_menu": "GAME MENU", "difficulty_menu": "DIFFICULTY MENU",
        "choose_difficulty_title": "CHOOSE A DIFFICULTY", "difficulty_hint": "The rules stay the same; only the deck size changes.",
        "classic": "Classic", "hard": "Hard", "easy": "Easy", "cards": "cards",
        "valid_move": "Valid move! Nice eye.", "invalid_move": "There is no match there. Try again.",
        "deck_empty": "There are no cards left. Finish when you cannot find any more moves.",
        "new_game_hint": "Choose a difficulty to start again.", "game": "Game",
        "piles_on_table": "piles on the table", "sound": "Game sound", "volume": "VOLUME",
        "muted": "Muted", "language": "LANGUAGE", "spanish": "Español", "english": "English",
        "save_options": "Save options", "settings": "Settings", "save_settings": "Save settings",
        "play": "Play", "records": "Records", "quit": "Quit", "tagline": "A game of observation and strategy",
        "abandon_game": "Leave game", "abandon_confirm": "Are you sure you want to leave this game?\nYour current score will not be saved.",
        "abandon": "Leave", "back_title": "Back to menu", "back_confirm": "Return to the main menu?\nYour current game will not be saved.",
        "cancel": "Cancel", "understood": "Got it", "finish_game": "FINISH GAME  ·  VIEW RESULTS",
        "game_finished": "GAME FINISHED", "your_result": "Your table, your result", "final_score": "FINAL SCORE",
        "final_piles": "final piles", "name_to_save": "Name to save the score", "save_score": "Save score",
        "new_game": "New game", "main_menu": "Main menu", "name_missing": "Name required",
        "restart_game": "Restart game", "restart_confirm": "Restart the current game?\nYou will choose the difficulty again.",
        "new_record": "NEW RECORD!",
        "resume_game": "Keep playing", "restart_from_menu": "Start over",
        "settings_from_menu": "Settings", "return_to_home": "Return home",
        "name_missing_message": "Enter a name before saving.", "score_saved": "Score saved",
        "score_published": "Score saved and published to the global ranking.",
    },
}


def t(clave: str) -> str:
    """Texto de interfaz en el idioma elegido, con español como respaldo."""
    return TEXTOS[configuracion.cargar_idioma()].get(clave, TEXTOS["es"].get(clave, clave))


def _centrar_ventana(raiz: tk.Tk, ancho: int, alto: int) -> None:
    """Centra una ventana sin superar el área física disponible."""
    ancho = min(ancho, raiz.winfo_screenwidth() - 20)
    alto = min(alto, raiz.winfo_screenheight() - 50)
    x = (raiz.winfo_screenwidth() - ancho) // 2
    y = max(0, (raiz.winfo_screenheight() - alto) // 2)
    raiz.geometry(f"{ancho}x{alto}+{x}+{y}")


def _calcular_layout_tablero(ancho_disponible: int) -> tuple[int, int, int]:
    """Devuelve diez columnas legibles; las filas restantes usan scroll."""
    ancho = (ancho_disponible - (COLUMNAS_TABLERO - 1) * GAP_CELDA) / COLUMNAS_TABLERO
    ancho = max(ANCHO_CARTA_MINIMO, min(int(ancho), ANCHO_CARTA_MAXIMO))
    return COLUMNAS_TABLERO, ancho, int(ancho * RATIO_CARTA)


def _posicion_en_viborita(posicion: int, columnas: int = COLUMNAS_TABLERO) -> tuple[int, int]:
    """Convierte una posición lineal a fila/columna alternando la dirección."""
    fila, columna = divmod(posicion, columnas)
    if fila % 2:
        columna = columnas - 1 - columna
    return fila, columna


def crear_boton(
    padre: tk.Widget, texto: str, comando, *, principal: bool = False,
    ancho: int | None = None, fuente=None,
) -> tk.Button:
    """Crea un botón coherente y añade hover sin repetir configuración."""
    if principal:
        normal, hover, fg = COLOR_ACENTO, COLOR_ACENTO_HOVER, "white"
    else:
        normal, hover, fg = COLOR_TARJETA, COLOR_TARJETA_HOVER, COLOR_TEXTO_OSCURO
    boton = tk.Button(
        padre, text=texto, command=comando, bg=normal, fg=fg,
        font=fuente or FUENTE_BOTON, relief="flat", bd=0, cursor="hand2",
        activebackground=hover, activeforeground=fg, padx=18, pady=11,
        highlightthickness=1, highlightbackground=COLOR_BORDE,
    )
    if ancho is not None:
        boton.configure(width=ancho)
    boton.bind("<Enter>", lambda _e: boton.configure(bg=hover) if str(boton["state"]) == "normal" else None)
    boton.bind("<Leave>", lambda _e: boton.configure(bg=normal) if str(boton["state"]) == "normal" else None)
    return boton


def crear_tarjeta(padre: tk.Widget, *, fondo: str = COLOR_PANEL_ELEVADO, borde: str = COLOR_BORDE) -> tk.Frame:
    return tk.Frame(padre, bg=fondo, highlightthickness=1, highlightbackground=borde)


def crear_ornamento(padre: tk.Widget, *, invertido: bool = False) -> tk.Canvas:
    """Carga el PNG ornamental y usa Canvas sólo mientras el asset no exista."""
    if Image is not None and RUTA_ORNAMENTO.is_file():
        with Image.open(RUTA_ORNAMENTO) as origen:
            imagen = origen.convert("RGBA")
        # El asset puede llegar como silueta negra; se conserva su alpha y
        # se aplica el dorado de la interfaz al vuelo, sin perder detalle.
        alfa = imagen.getchannel("A")
        dorado = Image.new("RGBA", imagen.size, COLOR_DORADO)
        dorado.putalpha(alfa)
        imagen = dorado
        imagen.thumbnail((82, 30), Image.Resampling.LANCZOS)
        # El archivo original quedó ubicado al lado opuesto: el izquierdo
        # se espeja y el derecho conserva la orientación del PNG.
        if not invertido:
            imagen = ImageOps.mirror(imagen)
        foto = ImageTk.PhotoImage(imagen)
        etiqueta = tk.Label(padre, image=foto, bg=COLOR_MESA_OSCURO, bd=0)
        etiqueta.imagen = foto  # Mantiene la referencia viva para Tkinter.
        return etiqueta

    # Respaldo temporal para que la pantalla siga siendo correcta si falta
    # el archivo, por ejemplo antes de que se agregue al repositorio.
    ancho, alto = 82, 30
    lienzo = tk.Canvas(padre, width=ancho, height=alto, bg=COLOR_MESA_OSCURO, highlightthickness=0)

    def x(valor: int) -> int:
        return ancho - valor if invertido else valor

    oro, luz, sombra = COLOR_DORADO, "#F7DFA0", "#A97828"
    # Tallo con doble curva y hojas finas: la silueta se mantiene pequeña,
    # pero deja de leerse como una línea decorativa común.
    lienzo.create_line(x(2), 16, x(19), 16, x(29), 20, x(39), 16, x(55), 16,
                       fill=sombra, width=2, smooth=True)
    lienzo.create_line(x(11), 16, x(25), 10, x(31), 5, x(38), 10, x(42), 16,
                       fill=oro, width=1, smooth=True)
    lienzo.create_line(x(21), 18, x(29), 25, x(37), 26, x(42), 17,
                       fill=oro, width=1, smooth=True)
    lienzo.create_polygon(x(28), 13, x(34), 3, x(40), 12, x(35), 16,
                          fill=oro, outline=luz)
    lienzo.create_polygon(x(31), 19, x(39), 27, x(45), 19, x(38), 17,
                          fill="#C7983F", outline=luz)
    # Remate de tres puntas que mira hacia el texto central.
    lienzo.create_polygon(x(43), 16, x(54), 7, x(64), 16, x(54), 25,
                          fill=oro, outline=luz)
    lienzo.create_polygon(x(54), 16, x(69), 11, x(79), 16, x(69), 21,
                          fill="#C7983F", outline=luz)
    lienzo.create_oval(x(50) - 3, 13, x(50) + 3, 19, fill=luz, outline=sombra)
    return lienzo


def crear_palos_menu(padre: tk.Widget) -> tk.Widget:
    """Muestra los cuatro palos del menú y admite PNGs transparentes grandes.

    Cada imagen se recorta por su canal alfa antes de ajustarse a una caja
    visual común, por lo que el archivo puede venir con márgenes desparejos.
    Mientras falten assets se conserva un respaldo tipográfico discreto.
    """
    fila = tk.Frame(padre, bg=COLOR_MESA_OSCURO)
    if Image is None or ImageTk is None or not all(ruta.is_file() for ruta in RUTAS_PALOS_MENU):
        tk.Label(fila, text="♠  ♥  ♦  ♣", font=("Segoe UI Symbol", 24, "bold"), bg=COLOR_MESA_OSCURO, fg=COLOR_DORADO).pack()
        return fila

    for ruta in RUTAS_PALOS_MENU:
        with Image.open(ruta) as origen:
            imagen = origen.convert("RGBA")
        limites = imagen.getchannel("A").getbbox()
        if limites:
            imagen = imagen.crop(limites)
        imagen.thumbnail((76, 76), Image.Resampling.LANCZOS)
        foto = ImageTk.PhotoImage(imagen)
        celda = tk.Frame(fila, width=100, height=72, bg=COLOR_MESA_OSCURO)
        celda.pack(side="left")
        celda.pack_propagate(False)
        etiqueta = tk.Label(celda, image=foto, bg=COLOR_MESA_OSCURO, bd=0)
        etiqueta.imagen = foto
        etiqueta.pack(expand=True)
    return fila


class VentanaJuego:
    def __init__(self, raiz: tk.Tk):
        self.raiz = raiz
        self.raiz.title("Solitario Battle")
        self.raiz.configure(bg=COLOR_MESA)
        self.juego: Juego | None = None
        self.dificultad: Dificultad | None = None
        self._imagenes_actuales = []
        self._cache_imagenes = {}
        self._id_reloj = None
        self._arrastre = None
        self._id_ocultar_mensaje = None
        self._version_mensaje = 0
        self.volumen = configuracion.cargar_volumen()
        self._audio_disponible = None
        self._sonidos = {}
        self._armar_widgets_fijos()
        self._maximizar_ventana()
        self._mostrar_selector_dificultad(self._comenzar_partida)

    def _maximizar_ventana(self) -> None:
        """Aprovecha la pantalla completa sin ocultar los controles del sistema."""
        try:
            self.raiz.state("zoomed")
        except tk.TclError:
            # En plataformas donde Tk no ofrece "zoomed", la ventana conserva
            # su tamaño calculado normalmente.
            pass

    def _armar_widgets_fijos(self) -> None:
        self.marco_juego = tk.Frame(self.raiz, bg=COLOR_MESA)
        self.marco_juego.pack(fill="both", expand=True)

        self.canvas_principal = tk.Canvas(self.marco_juego, bg=COLOR_MESA, highlightthickness=0)
        self._barra_scroll = tk.Scrollbar(self.marco_juego, orient="vertical", command=self.canvas_principal.yview)
        self.canvas_principal.configure(yscrollcommand=self._barra_scroll.set)
        self.canvas_principal.pack(side="left", fill="both", expand=True)
        self._barra_scroll.pack(side="right", fill="y")

        self.marco_contenido = tk.Frame(self.canvas_principal, bg=COLOR_MESA)
        self._id_ventana_canvas = self.canvas_principal.create_window((0, 0), window=self.marco_contenido, anchor="nw")
        self.marco_contenido.bind("<Configure>", self._actualizar_scrollregion)
        self.canvas_principal.bind("<Configure>", self._ajustar_ancho_contenido)
        self.canvas_principal.bind_all("<MouseWheel>", self._on_rueda_mouse)
        self.canvas_principal.bind_all("<Button-5>", lambda _e: self.canvas_principal.yview_scroll(1, "units"))

        self._crear_barra_superior()
        self.marco_tablero = tk.Frame(self.marco_contenido, bg=COLOR_MESA)
        self.marco_tablero.pack(padx=24, pady=(18, 28))

        # La altura no limita el tamaño: el tablero tiene scroll vertical para
        # que las cartas sigan siendo cómodas de leer en notebooks.
        self.raiz.update_idletasks()
        ancho_area = self.raiz.winfo_screenwidth() - MARGEN_PANTALLA_X
        alto_header = self.marco_contenido.winfo_reqheight()
        self.columnas_tablero, self.ancho_carta, self.alto_carta = _calcular_layout_tablero(ancho_area - 40)
        filas = math.ceil((CANTIDAD_CARTAS_EN_MAZO + 1) / self.columnas_tablero)
        ancho_tablero = self.columnas_tablero * self.ancho_carta + (self.columnas_tablero - 1) * GAP_CELDA
        alto_tablero = filas * self.alto_carta + (filas - 1) * GAP_CELDA
        _centrar_ventana(self.raiz, max(780, ancho_tablero + 70), min(alto_header + alto_tablero + 55, self.raiz.winfo_screenheight() - 50))
        self.raiz.minsize(720, 600)

    def _crear_barra_superior(self) -> None:
        self.barra_superior = crear_tarjeta(self.marco_contenido, fondo=COLOR_PANEL, borde=COLOR_BORDE)
        self.barra_superior.pack(fill="x", padx=24, pady=(20, 0))
        identidad = tk.Frame(self.barra_superior, bg=COLOR_PANEL)
        identidad.pack(side="left", padx=18, pady=13)
        tk.Label(identidad, text="SOLITARIO BATTLE", font=("Segoe UI", 12, "bold"), bg=COLOR_PANEL, fg=COLOR_DORADO).pack(anchor="w")
        self.etiqueta_info = tk.Label(identidad, text=t("choose_difficulty"), font=("Segoe UI", 9), bg=COLOR_PANEL, fg=COLOR_MUTED)
        self.etiqueta_info.pack(anchor="w", pady=(2, 0))

        # El bloque de estadísticas vive en la columna central, independiente
        # de los controles laterales: el cronómetro queda realmente centrado.
        self.estadisticas = tk.Frame(self.barra_superior, bg=COLOR_PANEL)
        self.estadisticas.place(relx=0.5, rely=0.5, anchor="center")
        self._crear_estadistica(self.estadisticas, t("moves"), "0", "movimientos")
        self._crear_estadistica(self.estadisticas, t("time"), "00:00", "tiempo")

        acciones = tk.Frame(self.barra_superior, bg=COLOR_PANEL)
        acciones.pack(side="right", padx=14, pady=10)
        self.boton_menu = crear_boton(acciones, "☰", self._abrir_menu_partida, ancho=3, fuente=("Segoe UI Symbol", 12, "bold"))
        self.boton_menu.pack(side="right")
        # Este contenedor se empaqueta antes del tablero para que los avisos
        # nunca queden por debajo de las cartas ni compitan con el header.
        self.marco_mensaje = tk.Frame(self.marco_contenido, bg=COLOR_MESA, height=58)
        self.etiqueta_mensaje = tk.Label(
            self.marco_mensaje, text="", font=("Segoe UI", 11, "bold"), justify="center",
            wraplength=900, bg=COLOR_PANEL_ELEVADO, fg=COLOR_PANEL_ELEVADO, padx=20, pady=7,
        )
        self.etiqueta_mensaje.pack(fill="x", padx=80, pady=8)

    def _establecer_contexto_header(self, en_partida: bool) -> None:
        """Mantiene la identidad del header sin mostrar controles sin sentido."""
        if en_partida:
            self.estadisticas.place(relx=0.5, rely=0.5, anchor="center")
            self.marco_mensaje.pack(fill="x", before=self.marco_tablero)
            self.marco_mensaje.pack_propagate(False)
        else:
            self.estadisticas.place_forget()
            self.marco_mensaje.pack_forget()

    def _crear_estadistica(self, padre: tk.Widget, titulo: str, valor: str, atributo: str) -> None:
        tarjeta = tk.Frame(padre, bg=COLOR_PANEL_ELEVADO, padx=12, pady=5)
        tarjeta.pack(side="right", padx=(0, 9))
        etiqueta_titulo = tk.Label(tarjeta, text=titulo, font=("Segoe UI", 7, "bold"), bg=COLOR_PANEL_ELEVADO, fg=COLOR_MUTED)
        etiqueta_titulo.pack(anchor="e")
        etiqueta = tk.Label(tarjeta, text=valor, font=FUENTE_ESTADISTICA, bg=COLOR_PANEL_ELEVADO, fg=COLOR_TEXTO)
        etiqueta.pack(anchor="e")
        setattr(self, f"etiqueta_{atributo}", etiqueta)
        setattr(self, f"etiqueta_titulo_{atributo}", etiqueta_titulo)

    def _actualizar_idioma_visual(self) -> None:
        self.etiqueta_titulo_movimientos.config(text=t("moves"))
        self.etiqueta_titulo_tiempo.config(text=t("time"))
        if self.juego is None:
            self._mostrar_selector_dificultad(self._comenzar_partida)
        else:
            self._actualizar_pantalla()

    def _actualizar_scrollregion(self, _evento=None) -> None:
        self.canvas_principal.configure(scrollregion=self.canvas_principal.bbox("all"))

    def _ajustar_ancho_contenido(self, evento: tk.Event) -> None:
        self.canvas_principal.itemconfigure(self._id_ventana_canvas, width=evento.width)

    def _actualizar_reloj_visual(self, movimientos: int, segundos: int) -> None:
        self.etiqueta_tiempo.config(text=puntuacion.formatear_duracion(segundos))
        self.etiqueta_movimientos.config(text=str(movimientos))

    def _mostrar_mensaje(self, texto: str, tipo: str = "info", duracion_ms: int | None = None) -> None:
        """Muestra un aviso con una entrada suave y opcionalmente lo oculta."""
        colores = {"exito": COLOR_EXITO, "error": COLOR_ERROR, "info": COLOR_MUTED}
        color_final = colores.get(tipo, COLOR_MUTED)
        fondo = COLOR_PANEL_ELEVADO
        texto_visible = texto
        if self._id_ocultar_mensaje is not None:
            self.raiz.after_cancel(self._id_ocultar_mensaje)
            self._id_ocultar_mensaje = None
        self._version_mensaje += 1
        version = self._version_mensaje
        self._color_mensaje = color_final
        self._fondo_mensaje = fondo
        self.etiqueta_mensaje.config(
            text=texto_visible, fg=fondo, bg=fondo,
            font=("Segoe UI", 11, "bold"), padx=20, pady=7,
            highlightthickness=0,
        )

        def animar(paso: int = 0) -> None:
            if version != self._version_mensaje:
                return
            progreso = paso / 5
            self.etiqueta_mensaje.config(fg=self._mezclar_colores(fondo, color_final, progreso))
            if paso < 5:
                self.raiz.after(28, lambda: animar(paso + 1))

        animar()
        if duracion_ms is not None:
            self._id_ocultar_mensaje = self.raiz.after(
                duracion_ms, lambda: self._ocultar_mensaje(version)
            )

    @staticmethod
    def _mezclar_colores(origen: str, destino: str, progreso: float) -> str:
        """Interpela dos colores hexadecimales para una animación simple."""
        origen_rgb = tuple(int(origen[indice:indice + 2], 16) for indice in (1, 3, 5))
        destino_rgb = tuple(int(destino[indice:indice + 2], 16) for indice in (1, 3, 5))
        mezcla = tuple(round(inicio + (fin - inicio) * progreso) for inicio, fin in zip(origen_rgb, destino_rgb))
        return "#" + "".join(f"{canal:02X}" for canal in mezcla)

    def _ocultar_mensaje(self, version: int) -> None:
        if version != self._version_mensaje:
            return

        def desvanecer(paso: int = 0) -> None:
            if version != self._version_mensaje:
                return
            progreso = paso / 5
            self.etiqueta_mensaje.config(fg=self._mezclar_colores(self._color_mensaje, self._fondo_mensaje, progreso))
            if paso < 5:
                self.raiz.after(28, lambda: desvanecer(paso + 1))
            else:
                self.etiqueta_mensaje.config(
                    text="", fg=COLOR_PANEL_ELEVADO, bg=COLOR_PANEL_ELEVADO, font=("Segoe UI", 11, "bold"),
                    padx=20, pady=7, highlightthickness=0,
                )
                self._id_ocultar_mensaje = None

        desvanecer()

    def _on_rueda_mouse(self, evento: tk.Event) -> None:
        # Durante la partida la rueda sólo avanza por la mesa; evita que un
        # gesto hacia arriba desplace accidentalmente todo el juego.
        if getattr(evento, "delta", 0) < 0:
            self.canvas_principal.yview_scroll(int(-evento.delta / 120), "units")

    def _iniciar_reloj(self) -> None:
        if self._id_reloj is not None:
            self.raiz.after_cancel(self._id_reloj)
        self._actualizar_reloj()

    def _actualizar_reloj(self) -> None:
        if self.juego is None or self.juego.esta_terminada():
            self._id_reloj = None
            return
        self._actualizar_reloj_visual(self.juego.cantidad_jugadas_realizadas, self.juego.duracion_segundos())
        self._id_reloj = self.raiz.after(1000, self._actualizar_reloj)

    def _on_repartir(self) -> None:
        if self.juego is None or self.juego.esta_terminada() or not self.juego.quedan_cartas_en_mano():
            return
        self.juego.repartir_carta()
        self._reproducir_sonido(SONIDO_REPARTIR)
        self._actualizar_pantalla()

    def _on_accion_principal(self) -> None:
        if self.juego is None or self.juego.esta_terminada() or self.juego.quedan_cartas_en_mano():
            return
        self.juego.finalizar()
        self._terminar_partida()

    def _confirmar_reinicio(self) -> None:
        if self.juego is None or self.juego.esta_terminada():
            self._nueva_partida()
            return
        self._mostrar_dialogo_confirmacion(
            t("restart_game"), t("restart_confirm"), self._nueva_partida, t("restart_game"),
        )

    def _confirmar_volver_menu(self) -> None:
        """Permite abandonar la partida en curso sin ocultar la salida al menú."""
        if self.juego is None or self.juego.esta_terminada():
            self._volver_al_menu()
            return
        self._mostrar_dialogo_confirmacion(
            t("back_title"), t("back_confirm"),
            self._volver_al_menu,
            t("back_to_menu"),
        )

    def _abrir_menu_partida(self) -> None:
        """Menú breve y consistente para la partida o el selector."""
        ventana = tk.Toplevel(self.raiz)
        en_partida = self.juego is not None
        ventana.title(t("game_menu") if en_partida else t("difficulty_menu"))
        ventana.configure(bg=COLOR_MESA_OSCURO)
        ventana.resizable(False, False)
        ventana.transient(self.raiz)
        _centrar_ventana(ventana, 360, 390 if en_partida else 310)
        panel = crear_tarjeta(ventana, fondo=COLOR_PANEL, borde=COLOR_DORADO)
        panel.pack(fill="both", expand=True, padx=20, pady=20)
        contenido = tk.Frame(panel, bg=COLOR_PANEL)
        contenido.pack(fill="both", expand=True, padx=30, pady=28)
        tk.Label(contenido, text=t("game_menu") if en_partida else t("difficulty_menu"), font=("Segoe UI", 11, "bold"), bg=COLOR_PANEL, fg=COLOR_DORADO).pack(pady=(0, 16))
        acciones_menu = tk.Frame(contenido, bg=COLOR_PANEL)
        acciones_menu.pack(fill="x", expand=True)

        def boton_menu(texto: str, comando) -> None:
            crear_boton(acciones_menu, texto, lambda: (ventana.destroy(), comando()), fuente=("Segoe UI", 10, "bold")).pack(fill="x", pady=5)

        if en_partida:
            crear_boton(acciones_menu, t("resume_game"), ventana.destroy, fuente=("Segoe UI", 10, "bold")).pack(fill="x", pady=5)
            boton_menu(t("restart_from_menu"), self._confirmar_reinicio)
            boton_menu(t("settings_from_menu"), self._on_configuracion)
            boton_menu(t("return_to_home"), self._confirmar_volver_menu)
        else:
            boton_menu(t("settings_from_menu"), self._on_configuracion)
            boton_menu(t("return_to_home"), self._confirmar_volver_menu)
        ventana.grab_set()

    # La interacción conserva exactamente el contrato original: se intenta la jugada desde la pila izquierda.
    def _iniciar_arrastre(self, evento: tk.Event, indice: int) -> None:
        if self.juego is None or self.juego.esta_terminada():
            return
        boton = self._botones_pilas[indice]
        x_inicial, y_inicial = boton.winfo_x(), boton.winfo_y()
        fantasma = tk.Label(
            self.marco_tablero, image=boton.imagen, bg=COLOR_MESA,
            bd=0, highlightthickness=2, highlightbackground=COLOR_DORADO,
        )
        fantasma.place(x=x_inicial, y=y_inicial)
        fantasma.lift()
        # La carta real se oculta durante el arrastre: así no parece que haya
        # dos cartas apiladas en el origen ni quedan restos visuales.
        boton.grid_remove()
        boton.configure(highlightbackground=COLOR_DORADO)
        self._arrastre = {
            "indice_origen": indice, "boton": boton, "fantasma": fantasma,
            "x_inicial": x_inicial, "y_inicial": y_inicial,
            "x_mouse_inicial": evento.x_root, "y_mouse_inicial": evento.y_root,
            "id_movimiento": None, "posicion_pendiente": None,
        }

    def _arrastrando(self, evento: tk.Event) -> None:
        if self._arrastre is None:
            return
        self._arrastre["posicion_pendiente"] = (evento.x_root, evento.y_root)
        if self._arrastre["id_movimiento"] is None:
            self._arrastre["id_movimiento"] = self.raiz.after(16, self._actualizar_fantasma_arrastre)

    def _actualizar_fantasma_arrastre(self) -> None:
        if self._arrastre is None:
            return
        self._arrastre["id_movimiento"] = None
        x_mouse, y_mouse = self._arrastre["posicion_pendiente"]
        self._colocar_fantasma(self._arrastre, x_mouse, y_mouse)

    @staticmethod
    def _colocar_fantasma(arrastre: dict, x_mouse: int, y_mouse: int) -> None:
        arrastre["fantasma"].place_configure(
            x=arrastre["x_inicial"] + x_mouse - arrastre["x_mouse_inicial"],
            y=arrastre["y_inicial"] + y_mouse - arrastre["y_mouse_inicial"],
        )

    def _soltar_arrastre(self, evento: tk.Event) -> None:
        if self._arrastre is None:
            return
        arrastre = self._arrastre
        if arrastre["id_movimiento"] is not None:
            self.raiz.after_cancel(arrastre["id_movimiento"])
        self._colocar_fantasma(arrastre, evento.x_root, evento.y_root)
        indice_origen = arrastre["indice_origen"]
        boton = arrastre["boton"]
        fantasma = arrastre["fantasma"]
        self._arrastre = None
        destino = indice_origen - 1
        soltada_en_destino = destino >= 0 and self._soltada_sobre_pila(fantasma, destino)
        fantasma.destroy()
        boton.configure(highlightbackground=COLOR_BORDE)
        if soltada_en_destino:
            if self.juego.intentar_jugada(destino):
                self._reproducir_sonido(SONIDO_MOVIMIENTO_EXITOSO)
                self._mostrar_mensaje(t("valid_move"), "exito", duracion_ms=2300)
                self._actualizar_pantalla()
            else:
                self._mostrar_mensaje(t("invalid_move"), "error", duracion_ms=2300)
                boton.grid()
        else:
            # grid() sin argumentos recupera exactamente la celda que tenía
            # antes de grid_remove(), sin reconstruir ni parpadear la mesa.
            boton.grid()

    def _soltada_sobre_pila(self, boton: tk.Widget, indice_objetivo: int) -> bool:
        if indice_objetivo >= len(self._botones_pilas):
            return False
        objetivo = self._botones_pilas[indice_objetivo]
        centro_x = boton.winfo_x() + boton.winfo_width() / 2
        centro_y = boton.winfo_y() + boton.winfo_height() / 2
        return objetivo.winfo_x() <= centro_x <= objetivo.winfo_x() + objetivo.winfo_width() and objetivo.winfo_y() <= centro_y <= objetivo.winfo_y() + objetivo.winfo_height()

    def _reproducir_sonido(self, ruta_sonido) -> None:
        """Reproduce un WAV propio de forma asíncrona, si está disponible."""
        if mixer is None or not ruta_sonido.is_file():
            return
        if self._audio_disponible is None:
            try:
                mixer.init()
                self._audio_disponible = True
            except Exception:
                self._audio_disponible = False
        if not self._audio_disponible:
            return
        try:
            sonido = self._sonidos.get(ruta_sonido)
            if sonido is None:
                sonido = mixer.Sound(str(ruta_sonido))
                self._sonidos[ruta_sonido] = sonido
            sonido.set_volume(self.volumen)
            sonido.play()
        except Exception:
            # Un archivo de sonido inválido no debe impedir jugar.
            return

    def _actualizar_pantalla(self) -> None:
        self.marco_tablero.pack_configure(anchor="center", padx=24)
        for widget in self.marco_tablero.winfo_children():
            widget.destroy()
        self._imagenes_actuales = []
        self._botones_pilas = []
        cartas_restantes = self.juego.mazo.quedan_cartas()
        self._imagen_dorso = self._obtener_imagen_dorso(cartas_restantes)
        self.boton_mazo = self._crear_boton_carta(self._imagen_dorso, self._on_repartir)
        self.boton_mazo.grid(row=0, column=0)

        pilas = self.juego.tablero.pilas
        for indice, pila in enumerate(pilas):
            posicion = indice + 1
            imagen = self._obtener_imagen_carta(pila.tope(), len(pila))
            self._imagenes_actuales.append(imagen)
            boton = self._crear_boton_carta(imagen)
            fila, columna = _posicion_en_viborita(posicion, self.columnas_tablero)
            boton.grid(row=fila, column=columna)
            boton.bind("<ButtonPress-1>", lambda e, i=indice: self._iniciar_arrastre(e, i))
            boton.bind("<B1-Motion>", self._arrastrando)
            boton.bind("<ButtonRelease-1>", self._soltar_arrastre)
            self._botones_pilas.append(boton)

        for columna in range(self.columnas_tablero):
            self.marco_tablero.grid_columnconfigure(columna, minsize=self.ancho_carta, pad=GAP_CELDA // 2)
        filas = math.ceil((len(pilas) + 1) / self.columnas_tablero)
        for fila in range(filas):
            self.marco_tablero.grid_rowconfigure(fila, minsize=self.alto_carta, pad=GAP_CELDA // 2)
        dificultad = t("easy") if self.dificultad == Dificultad.FACIL else t("hard")
        self.etiqueta_info.config(text=f"{t('game')} {dificultad}  ·  {len(pilas)} {t('piles_on_table')}")
        if cartas_restantes == 0 and not self.juego.esta_terminada():
            self.boton_mazo.config(state="disabled")
            boton_final = crear_boton(
                self.marco_tablero,
                t("finish_game"),
                self._on_accion_principal,
                principal=True,
                fuente=("Segoe UI", 14, "bold"),
            )
            boton_final.grid(
                row=filas, column=0, columnspan=self.columnas_tablero,
                pady=(26, 10), ipadx=26, ipady=5,
            )
            self._mostrar_mensaje(t("deck_empty"))

    def _crear_boton_carta(self, imagen, comando=None) -> tk.Button:
        boton = tk.Button(self.marco_tablero, image=imagen, command=comando, bg=COLOR_MESA, activebackground=COLOR_MESA, cursor="hand2", relief="flat", bd=0, highlightthickness=2, highlightbackground=COLOR_BORDE, highlightcolor=COLOR_DORADO)
        boton.imagen = imagen
        return boton

    def _obtener_imagen_dorso(self, cantidad: int):
        clave = ("dorso", cantidad, self.ancho_carta, self.alto_carta)
        if clave not in self._cache_imagenes:
            self._cache_imagenes[clave] = cargar_imagen_dorso(
                self.ancho_carta, self.alto_carta, cantidad=cantidad
            )
        return self._cache_imagenes[clave]

    def _obtener_imagen_carta(self, carta, cantidad: int):
        clave = ("carta", carta.palo.name, carta.valor, cantidad, self.ancho_carta, self.alto_carta)
        if clave not in self._cache_imagenes:
            self._cache_imagenes[clave] = cargar_imagen_carta(
                carta, self.ancho_carta, self.alto_carta, cantidad=cantidad
            )
        return self._cache_imagenes[clave]

    def _terminar_partida(self) -> None:
        self.boton_mazo.config(state="disabled")
        resumen = self.juego.obtener_resumen()
        historial_anterior = puntuacion.cargar_historial()
        comparacion = puntuacion.mensaje_comparacion(resumen, historial_anterior)
        puntuacion.registrar_partida_local(resumen)
        self._abrir_ventana_resumen(
            resumen, puntuacion.clasificar_resultado(resumen["pilas_finales"]),
            puntuacion.formatear_duracion(resumen["duracion_segundos"]), comparacion,
        )

    def _abrir_ventana_resumen(self, resumen: dict, interpretacion: str, duracion: str, comparacion: str) -> None:
        ventana = tk.Toplevel(self.raiz)
        ventana.title(t("game_finished").title())
        ventana.configure(bg=COLOR_MESA_OSCURO)
        ventana.resizable(False, False)
        ventana.transient(self.raiz)
        ventana.protocol("WM_DELETE_WINDOW", lambda: self._cerrar_resumen_y(ventana, self._volver_al_menu))
        nuevo_record = comparacion.startswith("Nuevo mejor")
        _centrar_ventana(ventana, 500, 570 if nuevo_record else 505)

        tk.Label(ventana, text=t("game_finished"), font=("Segoe UI", 11, "bold"), bg=COLOR_MESA_OSCURO, fg=COLOR_DORADO).pack(pady=(28, 4))
        tk.Label(ventana, text=t("your_result"), font=("Segoe UI", 22, "bold"), bg=COLOR_MESA_OSCURO, fg=COLOR_TEXTO).pack()
        if nuevo_record:
            tk.Label(ventana, text=t("new_record"), font=("Segoe UI", 11, "bold"), bg=COLOR_MESA_OSCURO, fg=COLOR_DORADO).pack(pady=(8, 0))
            confeti = tk.Canvas(ventana, width=420, height=62, bg=COLOR_MESA_OSCURO, highlightthickness=0)
            confeti.pack(pady=(0, 2))
            self._animar_confeti(confeti)
        tarjeta = crear_tarjeta(ventana, fondo=COLOR_TARJETA, borde=COLOR_DORADO)
        tarjeta.pack(fill="both", expand=True, padx=34, pady=22)
        tk.Label(tarjeta, text=t("final_score"), font=("Segoe UI", 9, "bold"), bg=COLOR_TARJETA, fg="#60736B").pack(pady=(24, 0))
        tk.Label(tarjeta, text=str(resumen["puntaje"]), font=("Consolas", 38, "bold"), bg=COLOR_TARJETA, fg=COLOR_ACENTO).pack()
        tk.Label(tarjeta, text=interpretacion, font=("Segoe UI", 13, "bold"), bg=COLOR_TARJETA, fg=COLOR_TEXTO_OSCURO, wraplength=380, justify="center").pack(pady=(6, 8))
        tk.Label(tarjeta, text=f"{resumen['pilas_finales']} {t('final_piles')}   ·   {resumen['movimientos']} {t('moves').lower()}   ·   {duracion}", font=("Segoe UI", 9), bg=COLOR_TARJETA, fg="#60736B").pack()
        tk.Label(tarjeta, text=comparacion, font=("Segoe UI", 10, "bold"), bg=COLOR_TARJETA, fg=COLOR_ACENTO, wraplength=360, justify="center").pack(padx=22, pady=(20, 12))
        fila = tk.Frame(tarjeta, bg=COLOR_TARJETA)
        fila.pack(fill="x", padx=35, pady=(8, 24))
        crear_boton(fila, t("new_game"), lambda: self._cerrar_resumen_y(ventana, self._nueva_partida), principal=True, fuente=("Segoe UI", 9, "bold")).pack(side="left", expand=True, fill="x", padx=(0, 4))
        crear_boton(fila, t("main_menu"), lambda: self._cerrar_resumen_y(ventana, self._volver_al_menu), fuente=("Segoe UI", 9, "bold")).pack(side="left", expand=True, fill="x", padx=(4, 0))
        ventana.grab_set()

    def _animar_confeti(self, lienzo: tk.Canvas) -> None:
        """Pequeña explosión de confeti para destacar un récord local nuevo."""
        generador = random.Random(50)
        particulas = []
        colores = (COLOR_DORADO, "#F5D889", COLOR_ACENTO, "#B9E6A4", "#A8D7F5")
        for _ in range(28):
            x, y = 210, 34
            item = lienzo.create_rectangle(x - 3, y - 2, x + 3, y + 2, fill=generador.choice(colores), outline="")
            particulas.append((item, generador.uniform(-4.8, 4.8), generador.uniform(-5.4, -1.8)))

        def animar(paso: int = 0) -> None:
            try:
                for indice, (item, velocidad_x, velocidad_y) in enumerate(particulas):
                    lienzo.move(item, velocidad_x, velocidad_y + paso * 0.16)
                    particulas[indice] = (item, velocidad_x, velocidad_y)
                if paso < 30:
                    lienzo.after(28, lambda: animar(paso + 1))
            except tk.TclError:
                # La ventana pudo cerrarse mientras la animación seguía activa.
                return

        animar()

    def _cerrar_resumen_y(self, ventana: tk.Toplevel, accion) -> None:
        ventana.destroy()
        accion()

    def _guardar(self, ventana: tk.Toplevel, resumen: dict, entrada_nombre: tk.Entry) -> None:
        nombre = entrada_nombre.get().strip()
        if not nombre:
            self._mostrar_dialogo_info(t("name_missing"), t("name_missing_message"))
            return
        puntuacion.guardar_puntaje(nombre, resumen)
        error_sincronizacion = records_online.enviar_record(nombre, resumen)
        mensaje = t("score_published")
        if error_sincronizacion:
            mensaje = f"Puntaje guardado localmente. {error_sincronizacion}"
        self._mostrar_dialogo_info(t("score_saved"), mensaje)
        # Una misma partida sólo se puede guardar una vez. Al cerrar el
        # resumen volvemos al menú, desde donde el récord ya está disponible.
        self._cerrar_resumen_y(ventana, self._volver_al_menu)

    def _mostrar_selector_dificultad(self, al_elegir) -> None:
        self._establecer_contexto_header(False)
        self.etiqueta_info.config(text=t("choose_difficulty"))
        self.marco_tablero.pack_configure(anchor="center", padx=24)
        for widget in self.marco_tablero.winfo_children():
            widget.destroy()
        tarjeta = crear_tarjeta(self.marco_tablero, fondo=COLOR_PANEL, borde=COLOR_BORDE)
        tarjeta.pack(padx=20, pady=48)
        tk.Label(tarjeta, text=t("choose_difficulty_title"), font=("Segoe UI", 16, "bold"), bg=COLOR_PANEL, fg=COLOR_DORADO).pack(pady=(25, 4))
        tk.Label(tarjeta, text=t("difficulty_hint"), font=("Segoe UI", 11), bg=COLOR_PANEL, fg=COLOR_MUTED).pack(pady=(6, 22))
        opciones = tk.Frame(tarjeta, bg=COLOR_PANEL)
        opciones.pack(padx=30, pady=(0, 30))
        self._crear_opcion_dificultad(opciones, t("classic"), f"40 {t('cards')}", Dificultad.FACIL, al_elegir).pack(side="left", padx=(0, 10))
        self._crear_opcion_dificultad(opciones, t("hard"), f"48 {t('cards')}", Dificultad.DIFICIL, al_elegir).pack(side="left", padx=(10, 0))

    def _crear_opcion_dificultad(self, padre, titulo, cantidad, dificultad, al_elegir):
        """Selector clásico: un panel único con relieve estilo Win98."""
        tarjeta = tk.Canvas(
            padre, width=238, height=128, bg=COLOR_PANEL,
            highlightthickness=0, cursor="hand2",
        )
        # Sombra exterior cuadrada abajo a la izquierda y un único panel
        # frontal: el relieve no necesita un segundo recuadro decorativo.
        tarjeta.create_rectangle(3, 11, 226, 123, fill="#71847B", outline="", tags="sombra")
        tarjeta.create_rectangle(10, 3, 233, 115, fill="#EEF1EC", outline="#5C7067", tags="frente")
        tarjeta.create_line(11, 4, 232, 4, fill="#FFFFFF", tags="frente")
        tarjeta.create_line(11, 4, 11, 114, fill="#FFFFFF", tags="frente")
        tarjeta.create_line(11, 114, 232, 114, fill="#9AA9A1", tags="frente")
        tarjeta.create_line(232, 4, 232, 114, fill="#9AA9A1", tags="frente")
        tarjeta.create_text(121, 50, text=titulo.upper(), font=("Segoe UI", 16, "bold"), fill=COLOR_TEXTO_OSCURO, tags="frente")
        tarjeta.create_text(121, 78, text=cantidad, font=("Segoe UI", 11), fill="#54675F", tags="frente")
        presionada = False

        def presionar(_evento) -> None:
            nonlocal presionada
            if not presionada:
                tarjeta.move("frente", -2, 3)
                presionada = True

        def soltar(_evento) -> None:
            nonlocal presionada
            if presionada:
                tarjeta.move("frente", 2, -3)
                presionada = False
                al_elegir(dificultad)

        def cancelar_presion(_evento) -> None:
            nonlocal presionada
            if presionada:
                tarjeta.move("frente", 2, -3)
                presionada = False

        tarjeta.bind("<ButtonPress-1>", presionar)
        tarjeta.bind("<ButtonRelease-1>", soltar)
        tarjeta.bind("<Leave>", cancelar_presion)
        return tarjeta

    def _comenzar_partida(self, dificultad: Dificultad) -> None:
        self.dificultad = dificultad
        self.juego = Juego(dificultad=dificultad)
        self._establecer_contexto_header(True)
        self._actualizar_pantalla()
        self._iniciar_reloj()

    def _nueva_partida(self) -> None:
        if self._id_reloj is not None:
            self.raiz.after_cancel(self._id_reloj)
            self._id_reloj = None
        self.juego = None
        self._cache_imagenes.clear()
        self.etiqueta_info.config(text=t("choose_difficulty"))
        self._actualizar_reloj_visual(0, 0)
        self._mostrar_selector_dificultad(self._comenzar_partida)

    def _volver_al_menu(self) -> None:
        if self._id_reloj is not None:
            self.raiz.after_cancel(self._id_reloj)
        self.canvas_principal.unbind_all("<MouseWheel>")
        self.canvas_principal.unbind_all("<Button-4>")
        self.canvas_principal.unbind_all("<Button-5>")
        self.marco_juego.destroy()
        try:
            self.raiz.state("normal")
        except tk.TclError:
            pass
        MenuPrincipal(self.raiz)

    def _mostrar_dialogo_confirmacion(self, titulo: str, texto: str, al_confirmar, texto_confirmar: str) -> None:
        ventana = self._crear_dialogo(titulo, texto)
        acciones = tk.Frame(ventana._tarjeta_dialogo, bg=COLOR_TARJETA)
        acciones.pack(fill="x", padx=32, pady=(4, 28))
        crear_boton(acciones, t("cancel"), ventana.destroy, fuente=("Segoe UI", 10, "bold")).pack(side="left", expand=True, fill="x", padx=(0, 5))
        crear_boton(
            acciones, texto_confirmar,
            lambda: (ventana.destroy(), al_confirmar()),
            principal=True, fuente=("Segoe UI", 10, "bold"),
        ).pack(side="left", expand=True, fill="x", padx=(5, 0))

    def _mostrar_dialogo_info(self, titulo: str, texto: str) -> None:
        ventana = self._crear_dialogo(titulo, texto)
        crear_boton(
            ventana._tarjeta_dialogo, t("understood"), ventana.destroy,
            principal=True, fuente=("Segoe UI", 10, "bold"),
        ).pack(fill="x", padx=32, pady=(4, 28))

    def _crear_dialogo(self, titulo: str, texto: str) -> tk.Toplevel:
        """Diálogo propio para no interrumpir la identidad visual de la mesa."""
        ventana = tk.Toplevel(self.raiz)
        ventana.title(titulo)
        ventana.configure(bg=COLOR_MESA_OSCURO)
        ventana.resizable(False, False)
        ventana.transient(self.raiz)
        _centrar_ventana(ventana, 430, 245)
        tarjeta = crear_tarjeta(ventana, fondo=COLOR_TARJETA, borde=COLOR_DORADO)
        tarjeta.pack(fill="both", expand=True, padx=24, pady=24)
        ventana._tarjeta_dialogo = tarjeta
        tk.Label(tarjeta, text=titulo.upper(), font=("Segoe UI", 10, "bold"), bg=COLOR_TARJETA, fg=COLOR_ACENTO).pack(pady=(28, 8))
        tk.Label(tarjeta, text=texto, font=("Segoe UI", 11), bg=COLOR_TARJETA, fg=COLOR_TEXTO_OSCURO, justify="center", wraplength=335).pack(padx=24, pady=(0, 18))
        ventana.grab_set()
        return ventana

    def _on_configuracion(self) -> None:
        """Acceso a ajustes durante la partida, como en un menú de pausa."""
        ventana = tk.Toplevel(self.raiz)
        ventana.title(t("options"))
        ventana.configure(bg=COLOR_MESA_OSCURO)
        ventana.resizable(False, False)
        ventana.transient(self.raiz)
        _centrar_ventana(ventana, 460, 430)
        tk.Label(ventana, text=t("options").upper(), font=("Segoe UI", 10, "bold"), bg=COLOR_MESA_OSCURO, fg=COLOR_DORADO).pack(pady=(24, 5))
        tk.Label(ventana, text=t("sound"), font=("Segoe UI", 22, "bold"), bg=COLOR_MESA_OSCURO, fg=COLOR_TEXTO).pack()
        tarjeta = crear_tarjeta(ventana, fondo=COLOR_TARJETA, borde=COLOR_DORADO)
        tarjeta.pack(fill="both", expand=True, padx=36, pady=(20, 30))
        tk.Label(tarjeta, text=t("volume"), font=("Segoe UI", 9, "bold"), bg=COLOR_TARJETA, fg=COLOR_TEXTO_OSCURO).pack(pady=(20, 4))
        volumen = tk.IntVar(value=round(configuracion.cargar_volumen() * 100))
        etiqueta_valor = tk.Label(tarjeta, font=("Segoe UI", 15, "bold"), bg=COLOR_TARJETA, fg=COLOR_ACENTO)
        etiqueta_valor.pack()

        def actualizar_valor(_valor=None) -> None:
            actual = volumen.get()
            etiqueta_valor.config(text=t("muted") if actual == 0 else f"{actual}%")

        barra = tk.Scale(tarjeta, from_=0, to=100, orient="horizontal", variable=volumen,
            command=actualizar_valor, showvalue=False, length=280, resolution=1,
            bg=COLOR_TARJETA, fg=COLOR_TEXTO_OSCURO, troughcolor="#D9CFBC",
            activebackground=COLOR_ACENTO, highlightthickness=0)
        barra.pack(pady=(4, 14))
        actualizar_valor()
        tk.Label(tarjeta, text=t("language"), font=("Segoe UI", 9, "bold"), bg=COLOR_TARJETA, fg=COLOR_TEXTO_OSCURO).pack(pady=(0, 4))
        idiomas = {t("spanish"): "es", t("english"): "en"}
        idioma = tk.StringVar(value=t("spanish") if configuracion.cargar_idioma() == "es" else t("english"))
        selector_idioma = tk.OptionMenu(tarjeta, idioma, *idiomas)
        selector_idioma.configure(font=("Segoe UI", 10), bg=COLOR_TARJETA, fg=COLOR_TEXTO_OSCURO, activebackground=COLOR_TARJETA_HOVER, relief="flat", highlightthickness=1, highlightbackground="#C9BFA6", width=18)
        selector_idioma["menu"].configure(font=("Segoe UI", 10))
        selector_idioma.pack(pady=(0, 14))
        crear_boton(
            tarjeta, t("save_options"),
            lambda: (configuracion.guardar_volumen(volumen.get() / 100), configuracion.guardar_idioma(idiomas[idioma.get()]), ventana.destroy(), self._actualizar_idioma_visual()),
            principal=True, fuente=("Segoe UI", 10, "bold"),
        ).pack(fill="x", padx=34, pady=(0, 24))


class MenuPrincipal:
    def __init__(self, raiz: tk.Tk):
        self.raiz = raiz
        raiz.title("Solitario Battle")
        raiz.configure(bg=COLOR_MESA_OSCURO)
        raiz.resizable(False, False)
        _centrar_ventana(raiz, 620, 640)
        self.marco = tk.Frame(raiz, bg=COLOR_MESA_OSCURO)
        self.marco.pack(fill="both", expand=True)
        self._crear_vista()

    def _crear_vista(self) -> None:
        contenido = tk.Frame(self.marco, bg=COLOR_MESA_OSCURO)
        contenido.place(relx=0.5, rely=0.5, anchor="center")
        crear_palos_menu(contenido).pack(pady=(0, 5))
        tk.Label(contenido, text="SOLITARIO\nBATTLE", font=("Segoe UI", 30, "bold"), bg=COLOR_MESA_OSCURO, fg=COLOR_TEXTO, justify="center").pack()
        lema = tk.Frame(contenido, bg=COLOR_MESA_OSCURO)
        lema.pack(pady=(8, 5))
        crear_ornamento(lema).pack(side="left", padx=(0, 8))
        tk.Label(
            lema, text=t("tagline"),
            font=("Georgia", 13, "bold italic"), bg=COLOR_MESA_OSCURO, fg=COLOR_DORADO,
        ).pack(side="left")
        crear_ornamento(lema, invertido=True).pack(side="left", padx=(8, 0))
        tk.Label(
            contenido, text="v1.1", font=("Segoe UI", 8),
            bg=COLOR_MESA_OSCURO, fg="#8CA79A",
        ).pack(pady=(0, 14))
        tarjeta = crear_tarjeta(contenido, fondo=COLOR_PANEL, borde=COLOR_BORDE)
        tarjeta.pack(padx=20)
        crear_boton(tarjeta, t("play"), self._on_jugar, principal=True, ancho=25, fuente=("Segoe UI", 12, "bold")).pack(padx=26, pady=(18, 5), fill="x")
        crear_boton(tarjeta, "Mi progreso", self._on_progreso, ancho=25, fuente=("Segoe UI", 10, "bold")).pack(padx=26, pady=3, fill="x")
        crear_boton(tarjeta, t("records"), self._on_records, ancho=25, fuente=("Segoe UI", 10, "bold")).pack(padx=26, pady=3, fill="x")
        crear_boton(tarjeta, t("settings"), self._on_configuracion, ancho=25, fuente=("Segoe UI", 10, "bold")).pack(padx=26, pady=3, fill="x")
        crear_boton(tarjeta, t("quit"), self.raiz.destroy, ancho=25, fuente=("Segoe UI", 10, "bold")).pack(padx=26, pady=(3, 18), fill="x")

    def _on_jugar(self) -> None:
        self.marco.destroy()
        VentanaJuego(self.raiz)

    def _on_progreso(self) -> None:
        ventana = tk.Toplevel(self.raiz)
        ventana.title("Mi progreso")
        ventana.configure(bg=COLOR_MESA_OSCURO)
        ventana.resizable(False, False)
        ventana.transient(self.raiz)
        _centrar_ventana(ventana, 760, 650)
        tk.Label(ventana, text="MI PROGRESO", font=("Segoe UI", 11, "bold"), bg=COLOR_MESA_OSCURO, fg=COLOR_DORADO).pack(pady=(24, 3))
        tk.Label(ventana, text="Tus resultados locales", font=("Segoe UI", 24, "bold"), bg=COLOR_MESA_OSCURO, fg=COLOR_TEXTO).pack()
        pestañas = tk.Frame(ventana, bg=COLOR_MESA_OSCURO)
        pestañas.pack(pady=(14, 0))
        contenido = tk.Frame(ventana, bg=COLOR_MESA_OSCURO)
        contenido.pack(fill="both", expand=True, padx=32)
        historial = puntuacion.cargar_historial()

        def mostrar(dificultad: str) -> None:
            for widget in contenido.winfo_children():
                widget.destroy()
            facil = dificultad == "facil"
            boton_facil.config(bg=COLOR_ACENTO if facil else COLOR_TARJETA, fg="white" if facil else COLOR_TEXTO_OSCURO)
            boton_dificil.config(bg=COLOR_ACENTO if not facil else COLOR_TARJETA, fg="white" if not facil else COLOR_TEXTO_OSCURO)
            datos = puntuacion.analizar_progreso(historial, dificultad)
            if not datos["partidas"]:
                tk.Label(contenido, text="Todavía no terminaste partidas en esta dificultad.", font=FUENTE_SUBTITULO, bg=COLOR_MESA_OSCURO, fg=COLOR_MUTED).pack(expand=True)
                return
            resumen = crear_tarjeta(contenido, fondo=COLOR_TARJETA, borde=COLOR_DORADO)
            resumen.pack(fill="x", pady=(14, 10))
            valores = (
                ("PARTIDAS", str(datos["partidas"])),
                ("TIEMPO TOTAL", puntuacion.formatear_duracion(datos["tiempo_total"])),
                ("PROMEDIO", f"{datos['promedio_pilas']:.1f} pilas"),
                ("MEDIANA", f"{datos['mediana_pilas']} pilas"),
            )
            for titulo, valor in valores:
                bloque = tk.Frame(resumen, bg=COLOR_TARJETA)
                bloque.pack(side="left", expand=True, fill="x", padx=6, pady=16)
                tk.Label(bloque, text=titulo, font=("Segoe UI", 8, "bold"), bg=COLOR_TARJETA, fg="#60736B").pack()
                tk.Label(bloque, text=valor, font=("Segoe UI", 13, "bold"), bg=COLOR_TARJETA, fg=COLOR_TEXTO_OSCURO).pack(pady=(3, 0))

            detalle = tk.Frame(contenido, bg=COLOR_MESA_OSCURO)
            detalle.pack(fill="both", expand=True)
            izquierda = crear_tarjeta(detalle, fondo=COLOR_TARJETA, borde=COLOR_BORDE)
            izquierda.pack(side="left", fill="both", expand=True, padx=(0, 6), pady=4)
            derecha = crear_tarjeta(detalle, fondo=COLOR_TARJETA, borde=COLOR_BORDE)
            derecha.pack(side="left", fill="both", expand=True, padx=(6, 0), pady=4)
            tk.Label(izquierda, text="RÉCORDS PERSONALES", font=("Segoe UI", 9, "bold"), bg=COLOR_TARJETA, fg=COLOR_ACENTO).pack(pady=(18, 10))
            mejor = datos["mejor_resultado"]
            mayor = datos["mayor_puntaje"]
            tiempo = datos["mejor_tiempo"]
            for texto in (
                f"Mejor resultado  ·  {mejor['pilas_finales']} pilas",
                f"Mayor puntaje  ·  {mayor['puntaje']}",
                f"Mejor tiempo significativo  ·  {puntuacion.formatear_duracion(tiempo['duracion_segundos'])}",
                f"Fecha del récord  ·  {mejor.get('fecha', '-')[:10]}",
                f"Puntaje promedio  ·  {datos['puntaje_promedio']}",
                f"Movimientos totales  ·  {datos['movimientos_totales']}",
            ):
                tk.Label(izquierda, text=texto, anchor="w", font=("Segoe UI", 10), bg=COLOR_TARJETA, fg=COLOR_TEXTO_OSCURO).pack(fill="x", padx=20, pady=5)
            tk.Label(derecha, text="RENDIMIENTO RECIENTE", font=("Segoe UI", 9, "bold"), bg=COLOR_TARJETA, fg=COLOR_ACENTO).pack(pady=(18, 10))
            reciente = f"Últimas {min(datos['partidas'], 10)} · {datos['promedio_ultimas_diez']:.1f} pilas de promedio"
            tk.Label(derecha, text=reciente, font=("Segoe UI", 10), bg=COLOR_TARJETA, fg=COLOR_TEXTO_OSCURO).pack(padx=20, pady=5)
            if datos["mejor_promedio_reciente"] is not None:
                tk.Label(derecha, text=f"Mejor bloque de 10 · {datos['mejor_promedio_reciente']:.1f} pilas", font=("Segoe UI", 10), bg=COLOR_TARJETA, fg=COLOR_TEXTO_OSCURO).pack(padx=20, pady=2)
            if datos["tendencia_pilas"] is None:
                tendencia = "La comparación aparece tras 20 partidas."
            elif datos["tendencia_pilas"] > 0:
                tendencia = f"Mejoraste {datos['tendencia_pilas']:.1f} pilas frente a las 10 anteriores."
            elif datos["tendencia_pilas"] < 0:
                tendencia = f"Las 10 anteriores fueron {-datos['tendencia_pilas']:.1f} pilas mejores."
            else:
                tendencia = "Mantenés el mismo promedio que las 10 anteriores."
            tk.Label(derecha, text=tendencia, wraplength=285, justify="left", font=("Segoe UI", 10), bg=COLOR_TARJETA, fg=COLOR_TEXTO_OSCURO).pack(padx=20, pady=5, anchor="w")
            tk.Label(derecha, text="DISTRIBUCIÓN", font=("Segoe UI", 9, "bold"), bg=COLOR_TARJETA, fg=COLOR_ACENTO).pack(pady=(12, 5))
            for rango, cantidad in datos["distribucion"].items():
                tk.Label(derecha, text=f"{rango:>4} pilas   {cantidad}", anchor="w", font=("Consolas", 10), bg=COLOR_TARJETA, fg=COLOR_TEXTO_OSCURO).pack(fill="x", padx=28, pady=1)

        boton_facil = crear_boton(pestañas, "Fácil", lambda: mostrar("facil"), principal=True, fuente=("Segoe UI", 9, "bold"))
        boton_facil.pack(side="left", padx=(0, 5))
        boton_dificil = crear_boton(pestañas, "Difícil", lambda: mostrar("dificil"), fuente=("Segoe UI", 9, "bold"))
        boton_dificil.pack(side="left", padx=(5, 0))
        mostrar("facil")
        crear_boton(ventana, "Cerrar", ventana.destroy, principal=True, fuente=("Segoe UI", 9, "bold")).pack(pady=(8, 22))

    def _on_records(self) -> None:
        ventana = tk.Toplevel(self.raiz)
        ventana.title("Récords")
        ventana.configure(bg=COLOR_MESA_OSCURO)
        ventana.resizable(False, False)
        ventana.transient(self.raiz)
        _centrar_ventana(ventana, 760, 560)
        tk.Label(ventana, text="SALÓN DE RÉCORDS", font=("Segoe UI", 11, "bold"), bg=COLOR_MESA_OSCURO, fg=COLOR_DORADO).pack(pady=(28, 3))
        tk.Label(ventana, text="Mejores partidas", font=("Segoe UI", 24, "bold"), bg=COLOR_MESA_OSCURO, fg=COLOR_TEXTO).pack()
        pestañas = tk.Frame(ventana, bg=COLOR_MESA_OSCURO)
        pestañas.pack(pady=(16, 0))
        contenido = tk.Frame(ventana, bg=COLOR_MESA_OSCURO)
        contenido.pack(fill="both", expand=True)

        def mostrar(tipo: str) -> None:
            for widget in contenido.winfo_children():
                widget.destroy()
            globales = tipo == "global"
            if globales:
                records, error = records_online.obtener_records_globales()
            else:
                records, error = records_online.obtener_records_personales()
                if error:
                    records = puntuacion.cargar_historial()
            records = puntuacion.ordenar_records(records)
            boton_mundial.config(bg=COLOR_ACENTO if globales else COLOR_TARJETA, fg="white" if globales else COLOR_TEXTO_OSCURO)
            boton_personal.config(bg=COLOR_ACENTO if not globales else COLOR_TARJETA, fg="white" if not globales else COLOR_TEXTO_OSCURO)
            if records:
                if not globales:
                    tk.Label(contenido, text=f"ÍNDICE BATTLE · {puntuacion.indice_jugador(records)}", font=("Segoe UI", 9, "bold"), bg=COLOR_MESA_OSCURO, fg=COLOR_DORADO).pack(pady=(10, 0))
                self._dibujar_tabla_records(contenido, records[:10])
            else:
                texto = error or ("Todavía no tenés récords personales." if not globales else "El ranking mundial todavía está vacío.")
                tk.Label(contenido, text=texto, font=FUENTE_SUBTITULO, bg=COLOR_MESA_OSCURO, fg=COLOR_MUTED, justify="center", wraplength=620).pack(expand=True)

        boton_mundial = crear_boton(pestañas, "Récords mundiales", lambda: mostrar("global"), principal=True, fuente=("Segoe UI", 9, "bold"))
        boton_mundial.pack(side="left", padx=(0, 5))
        boton_personal = crear_boton(pestañas, "Mis récords", lambda: mostrar("personal"), fuente=("Segoe UI", 9, "bold"))
        boton_personal.pack(side="left", padx=(5, 0))
        mostrar("global")
        crear_boton(ventana, "Cerrar", ventana.destroy, principal=True, fuente=("Segoe UI", 9, "bold")).pack(pady=(8, 24))

    def _dibujar_tabla_records(self, ventana: tk.Widget, mejores: list[dict]) -> None:
        tabla = crear_tarjeta(ventana, fondo=COLOR_TARJETA, borde=COLOR_DORADO)
        tabla.pack(fill="both", expand=True, padx=36, pady=(20, 10))
        columnas = (("#", 4), ("Jugador", 16), ("Dificultad", 11), ("Puntaje", 10), ("Pilas", 7), ("Mov.", 7), ("Fecha", 13))
        encabezado = tk.Frame(tabla, bg=COLOR_TEXTO_OSCURO)
        encabezado.pack(fill="x")
        for texto, ancho in columnas:
            tk.Label(encabezado, text=texto, width=ancho, anchor="w", font=("Segoe UI", 9, "bold"), bg=COLOR_TEXTO_OSCURO, fg=COLOR_TEXTO).pack(side="left", padx=2, pady=8)
        medallas = {1: "1º", 2: "2º", 3: "3º"}
        for posicion, partida in enumerate(mejores, start=1):
            fondo = "#F4E7C4" if posicion == 1 else (COLOR_TARJETA if posicion % 2 else "#EFE8D9")
            fila = tk.Frame(tabla, bg=fondo)
            fila.pack(fill="x")
            jugador = partida.get("jugador", partida.get("player_name", "-"))
            duracion = puntuacion.formatear_duracion(int(partida.get("duracion_segundos", 0)))
            fecha = partida.get("fecha", partida.get("played_at", "-"))
            valores = (medallas.get(posicion, str(posicion)), jugador[:15], partida.get("dificultad", partida.get("difficulty", "-")), str(partida["puntaje"] if "puntaje" in partida else partida["score"]), str(partida["pilas_finales"]), str(partida["movimientos"] if "movimientos" in partida else partida["moves"]), f"{duracion} · {fecha[:10]}")
            for (_, ancho), valor in zip(columnas, valores):
                tk.Label(fila, text=valor, width=ancho, anchor="w", font=("Segoe UI", 9), bg=fondo, fg=COLOR_TEXTO_OSCURO).pack(side="left", padx=2, pady=6)

    def _on_configuracion(self) -> None:
        ventana = tk.Toplevel(self.raiz)
        ventana.title(t("settings"))
        ventana.configure(bg=COLOR_MESA_OSCURO)
        ventana.resizable(False, False)
        ventana.transient(self.raiz)
        _centrar_ventana(ventana, 460, 430)

        tk.Label(ventana, text=t("settings").upper(), font=("Segoe UI", 10, "bold"), bg=COLOR_MESA_OSCURO, fg=COLOR_DORADO).pack(pady=(24, 5))
        tk.Label(ventana, text=t("sound"), font=("Segoe UI", 22, "bold"), bg=COLOR_MESA_OSCURO, fg=COLOR_TEXTO).pack()
        tarjeta = crear_tarjeta(ventana, fondo=COLOR_TARJETA, borde=COLOR_DORADO)
        tarjeta.pack(fill="both", expand=True, padx=36, pady=(20, 30))

        tk.Label(tarjeta, text=t("volume"), font=("Segoe UI", 9, "bold"), bg=COLOR_TARJETA, fg=COLOR_TEXTO_OSCURO).pack(pady=(20, 4))
        volumen = tk.IntVar(value=round(configuracion.cargar_volumen() * 100))
        etiqueta_valor = tk.Label(tarjeta, font=("Segoe UI", 15, "bold"), bg=COLOR_TARJETA, fg=COLOR_ACENTO)
        etiqueta_valor.pack()

        def actualizar_valor(_valor=None) -> None:
            actual = volumen.get()
            etiqueta_valor.config(text=t("muted") if actual == 0 else f"{actual}%")

        barra = tk.Scale(
            tarjeta, from_=0, to=100, orient="horizontal", variable=volumen,
            command=actualizar_valor, showvalue=False, length=280, resolution=1,
            bg=COLOR_TARJETA, fg=COLOR_TEXTO_OSCURO, troughcolor="#D9CFBC",
            activebackground=COLOR_ACENTO, highlightthickness=0,
        )
        barra.pack(pady=(4, 14))
        actualizar_valor()
        tk.Label(tarjeta, text=t("language"), font=("Segoe UI", 9, "bold"), bg=COLOR_TARJETA, fg=COLOR_TEXTO_OSCURO).pack(pady=(0, 4))
        idiomas = {t("spanish"): "es", t("english"): "en"}
        idioma = tk.StringVar(value=t("spanish") if configuracion.cargar_idioma() == "es" else t("english"))
        selector_idioma = tk.OptionMenu(tarjeta, idioma, *idiomas)
        selector_idioma.configure(font=("Segoe UI", 10), bg=COLOR_TARJETA, fg=COLOR_TEXTO_OSCURO, activebackground=COLOR_TARJETA_HOVER, relief="flat", highlightthickness=1, highlightbackground="#C9BFA6", width=18)
        selector_idioma["menu"].configure(font=("Segoe UI", 10))
        selector_idioma.pack(pady=(0, 14))

        def guardar() -> None:
            configuracion.guardar_volumen(volumen.get() / 100)
            configuracion.guardar_idioma(idiomas[idioma.get()])
            ventana.destroy()
            self.marco.destroy()
            self.marco = tk.Frame(self.raiz, bg=COLOR_MESA_OSCURO)
            self.marco.pack(fill="both", expand=True)
            self._crear_vista()

        crear_boton(tarjeta, t("save_settings"), guardar, principal=True, fuente=("Segoe UI", 10, "bold")).pack(fill="x", padx=34, pady=(0, 24))


def jugar_partida_grafica() -> None:
    raiz = tk.Tk()
    MenuPrincipal(raiz)
    raiz.mainloop()
