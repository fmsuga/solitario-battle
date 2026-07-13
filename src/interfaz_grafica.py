"""Interfaz gráfica de Solitario Battle.

Este módulo sólo presenta la partida: no modifica reglas ni estado de las
clases de dominio. Incluye menú, tablero, arrastrar/soltar y pantallas de
resultado usando una única identidad visual.
"""

import math
import tkinter as tk
from tkinter import messagebox

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
        self.canvas_principal.bind_all("<Button-4>", lambda _e: self.canvas_principal.yview_scroll(-1, "units"))
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
        barra = crear_tarjeta(self.marco_contenido, fondo=COLOR_PANEL, borde=COLOR_BORDE)
        barra.pack(fill="x", padx=24, pady=(20, 0))
        identidad = tk.Frame(barra, bg=COLOR_PANEL)
        identidad.pack(side="left", padx=18, pady=13)
        tk.Label(identidad, text="SOLITARIO BATTLE", font=("Segoe UI", 12, "bold"), bg=COLOR_PANEL, fg=COLOR_DORADO).pack(anchor="w")
        self.etiqueta_mensaje = tk.Label(
            barra, text="", font=("Segoe UI", 12, "bold"),
            bg=COLOR_PANEL, fg=COLOR_PANEL,
        )
        self.etiqueta_mensaje.place(relx=0.34, rely=0.5, anchor="center")
        self.etiqueta_info = tk.Label(identidad, text="Elegí una dificultad", font=("Segoe UI", 9), bg=COLOR_PANEL, fg=COLOR_MUTED)
        self.etiqueta_info.pack(anchor="w", pady=(2, 0))

        # El bloque de estadísticas vive en la columna central, independiente
        # de los controles laterales: el cronómetro queda realmente centrado.
        estadisticas = tk.Frame(barra, bg=COLOR_PANEL)
        estadisticas.place(relx=0.5, rely=0.5, anchor="center")
        self._crear_estadistica(estadisticas, "MOVIMIENTOS", "0", "movimientos")
        self._crear_estadistica(estadisticas, "TIEMPO", "00:00", "tiempo")

        acciones = tk.Frame(barra, bg=COLOR_PANEL)
        acciones.pack(side="right", padx=14, pady=10)
        self.boton_accion = crear_boton(acciones, "Rendirse", self._on_accion_principal, principal=True, fuente=("Segoe UI", 9, "bold"))
        self.boton_accion.pack(side="right")
        crear_boton(acciones, "Menú principal", self._confirmar_volver_menu, fuente=("Segoe UI", 9, "bold")).pack(side="right", padx=(0, 8))

    def _crear_estadistica(self, padre: tk.Widget, titulo: str, valor: str, atributo: str) -> None:
        tarjeta = tk.Frame(padre, bg=COLOR_PANEL_ELEVADO, padx=12, pady=5)
        tarjeta.pack(side="right", padx=(0, 9))
        tk.Label(tarjeta, text=titulo, font=("Segoe UI", 7, "bold"), bg=COLOR_PANEL_ELEVADO, fg=COLOR_MUTED).pack(anchor="e")
        etiqueta = tk.Label(tarjeta, text=valor, font=FUENTE_ESTADISTICA, bg=COLOR_PANEL_ELEVADO, fg=COLOR_TEXTO)
        etiqueta.pack(anchor="e")
        setattr(self, f"etiqueta_{atributo}", etiqueta)

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
        fondo = COLOR_PANEL
        texto_visible = "👍  Jugada válida, buen ojo." if tipo == "exito" else texto
        if self._id_ocultar_mensaje is not None:
            self.raiz.after_cancel(self._id_ocultar_mensaje)
            self._id_ocultar_mensaje = None
        self._version_mensaje += 1
        version = self._version_mensaje
        self._color_mensaje = color_final
        self._fondo_mensaje = fondo
        self.etiqueta_mensaje.config(
            text=texto_visible, fg=fondo, bg=fondo,
            font=("Segoe UI", 12, "bold"), padx=0, pady=0,
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
                    text="", fg=COLOR_PANEL, bg=COLOR_PANEL, font=("Segoe UI", 12, "bold"),
                    padx=0, pady=0, highlightthickness=0,
                )
                self._id_ocultar_mensaje = None

        desvanecer()

    def _on_rueda_mouse(self, evento: tk.Event) -> None:
        if getattr(evento, "delta", 0):
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
        if self.juego is None or self.juego.esta_terminada():
            return
        if self.juego.quedan_cartas_en_mano():
            if messagebox.askyesno("Rendirse", "¿Seguro que querés abandonar esta partida y empezar una nueva?\nNo se guardará su puntaje."):
                self._nueva_partida()
        else:
            self.juego.finalizar()
            self._terminar_partida()

    def _confirmar_volver_menu(self) -> None:
        """Permite abandonar la partida en curso sin ocultar la salida al menú."""
        if self.juego is None or self.juego.esta_terminada() or messagebox.askyesno(
            "Volver al menú", "¿Querés volver al menú principal?\nLa partida actual no se guardará."
        ):
            self._volver_al_menu()

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
                self._mostrar_mensaje("¡Jugada válida! Buen ojo.", "exito", duracion_ms=2300)
                self._actualizar_pantalla()
            else:
                self._mostrar_mensaje("Ahí no hay ninguna coincidencia. Fijate de nuevo.", "error", duracion_ms=2300)
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
        dificultad = "Fácil" if self.dificultad == Dificultad.FACIL else "Difícil"
        self.etiqueta_info.config(text=f"Partida {dificultad}  ·  {len(pilas)} pilas en mesa")
        if cartas_restantes == 0 and not self.juego.esta_terminada():
            self.boton_mazo.config(state="disabled")
            self.boton_accion.config(text="Terminar partida")
            self._mostrar_mensaje("Se acabaron las cartas. Si no ves más jugadas, terminá la partida.")

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
        self.boton_accion.config(state="disabled")
        resumen = self.juego.obtener_resumen()
        self._abrir_ventana_resumen(resumen, puntuacion.interpretar_resultado(resumen["pilas_finales"]), puntuacion.formatear_duracion(resumen["duracion_segundos"]))

    def _abrir_ventana_resumen(self, resumen: dict, interpretacion: str, duracion: str) -> None:
        ventana = tk.Toplevel(self.raiz)
        ventana.title("Partida terminada")
        ventana.configure(bg=COLOR_MESA_OSCURO)
        ventana.resizable(False, False)
        ventana.transient(self.raiz)
        ventana.protocol("WM_DELETE_WINDOW", lambda: self._cerrar_resumen_y(ventana, self._volver_al_menu))
        _centrar_ventana(ventana, 500, 610)

        tk.Label(ventana, text="PARTIDA TERMINADA", font=("Segoe UI", 11, "bold"), bg=COLOR_MESA_OSCURO, fg=COLOR_DORADO).pack(pady=(28, 4))
        tk.Label(ventana, text="Tu mesa, tu resultado", font=("Segoe UI", 22, "bold"), bg=COLOR_MESA_OSCURO, fg=COLOR_TEXTO).pack()
        tarjeta = crear_tarjeta(ventana, fondo=COLOR_TARJETA, borde=COLOR_DORADO)
        tarjeta.pack(fill="both", expand=True, padx=34, pady=22)
        tk.Label(tarjeta, text="PUNTAJE FINAL", font=("Segoe UI", 9, "bold"), bg=COLOR_TARJETA, fg="#60736B").pack(pady=(24, 0))
        tk.Label(tarjeta, text=str(resumen["puntaje"]), font=("Consolas", 38, "bold"), bg=COLOR_TARJETA, fg=COLOR_ACENTO).pack()
        tk.Label(tarjeta, text=interpretacion, font=("Segoe UI", 11, "bold"), bg=COLOR_TARJETA, fg=COLOR_TEXTO_OSCURO, wraplength=380, justify="center").pack(pady=(6, 12))
        tk.Label(tarjeta, text=f"{resumen['pilas_finales']} pilas finales   ·   {resumen['movimientos']} movimientos   ·   {duracion}", font=("Segoe UI", 9), bg=COLOR_TARJETA, fg="#60736B").pack()
        tk.Label(tarjeta, text="Nombre para guardar el puntaje", font=("Segoe UI", 9, "bold"), bg=COLOR_TARJETA, fg=COLOR_TEXTO_OSCURO).pack(pady=(22, 5))
        entrada = tk.Entry(tarjeta, justify="center", font=("Segoe UI", 11), relief="flat", highlightthickness=1, highlightbackground="#C9BFA6")
        entrada.pack(fill="x", padx=35, ipady=6, pady=(0, 12))
        crear_boton(tarjeta, "Guardar puntaje", lambda: self._guardar(ventana, resumen, entrada), principal=True).pack(fill="x", padx=35)
        fila = tk.Frame(tarjeta, bg=COLOR_TARJETA)
        fila.pack(fill="x", padx=35, pady=(8, 24))
        crear_boton(fila, "Nueva partida", lambda: self._cerrar_resumen_y(ventana, self._nueva_partida), principal=True, fuente=("Segoe UI", 9, "bold")).pack(side="left", expand=True, fill="x", padx=(0, 4))
        crear_boton(fila, "Menú principal", lambda: self._cerrar_resumen_y(ventana, self._volver_al_menu), fuente=("Segoe UI", 9, "bold")).pack(side="left", expand=True, fill="x", padx=(4, 0))
        ventana.grab_set()

    def _cerrar_resumen_y(self, ventana: tk.Toplevel, accion) -> None:
        ventana.destroy()
        accion()

    def _guardar(self, ventana: tk.Toplevel, resumen: dict, entrada_nombre: tk.Entry) -> None:
        nombre = entrada_nombre.get().strip()
        if not nombre:
            messagebox.showinfo("Falta el nombre", "Escribí un nombre antes de guardar.")
            return
        puntuacion.guardar_puntaje(nombre, resumen)
        error_sincronizacion = records_online.enviar_record(nombre, resumen)
        mensaje = "Puntaje guardado y publicado en el ranking mundial."
        if error_sincronizacion:
            mensaje = f"Puntaje guardado localmente. {error_sincronizacion}"
        messagebox.showinfo("Guardado", mensaje)
        # Una misma partida sólo se puede guardar una vez. Al cerrar el
        # resumen volvemos al menú, desde donde el récord ya está disponible.
        self._cerrar_resumen_y(ventana, self._volver_al_menu)

    def _mostrar_selector_dificultad(self, al_elegir) -> None:
        for widget in self.marco_tablero.winfo_children():
            widget.destroy()
        tarjeta = crear_tarjeta(self.marco_tablero, fondo=COLOR_PANEL, borde=COLOR_BORDE)
        tarjeta.pack(padx=20, pady=48)
        tk.Label(tarjeta, text="ELEGÍ LA DIFICULTAD", font=("Segoe UI", 9, "bold"), bg=COLOR_PANEL, fg=COLOR_DORADO).pack(pady=(25, 4))
        tk.Label(tarjeta, text="¿Qué desafío buscás hoy?", font=("Segoe UI", 19, "bold"), bg=COLOR_PANEL, fg=COLOR_TEXTO).pack()
        tk.Label(tarjeta, text="Las reglas son las mismas; cambia el tamaño del mazo.", font=FUENTE_TEXTO, bg=COLOR_PANEL, fg=COLOR_MUTED).pack(pady=(6, 22))
        opciones = tk.Frame(tarjeta, bg=COLOR_PANEL)
        opciones.pack(padx=30, pady=(0, 30))
        self._crear_opcion_dificultad(opciones, "Fácil", "40 cartas", "Sin 8 ni 9 · ideal para empezar", Dificultad.FACIL, al_elegir).pack(side="left", padx=(0, 10))
        self._crear_opcion_dificultad(opciones, "Difícil", "48 cartas", "Mazo completo · el desafío total", Dificultad.DIFICIL, al_elegir).pack(side="left", padx=(10, 0))

    def _crear_opcion_dificultad(self, padre, titulo, cantidad, detalle, dificultad, al_elegir):
        tarjeta = crear_tarjeta(padre, fondo=COLOR_TARJETA, borde=COLOR_DORADO)
        encabezado = tk.Frame(tarjeta, bg=COLOR_PANEL_ELEVADO)
        encabezado.pack(fill="x")
        tk.Label(encabezado, text=titulo.upper(), font=("Segoe UI", 17, "bold"), bg=COLOR_PANEL_ELEVADO, fg=COLOR_TEXTO).pack(padx=38, pady=(20, 2))
        tk.Label(encabezado, text=cantidad, font=("Segoe UI", 10, "bold"), bg=COLOR_PANEL_ELEVADO, fg=COLOR_DORADO).pack(pady=(0, 18))
        tk.Label(tarjeta, text=detalle, font=("Segoe UI", 10), bg=COLOR_TARJETA, fg="#60736B", justify="center", wraplength=230).pack(padx=24, pady=(22, 20))
        crear_boton(tarjeta, f"Jugar en {titulo}", lambda: al_elegir(dificultad), principal=True, fuente=("Segoe UI", 10, "bold")).pack(fill="x", padx=22, pady=(0, 22))
        self._hacer_tarjeta_clickeable(tarjeta, lambda: al_elegir(dificultad))
        return tarjeta

    @staticmethod
    def _hacer_tarjeta_clickeable(tarjeta: tk.Widget, comando) -> None:
        """Permite elegir la dificultad desde cualquier área no-botón de la card."""
        def enlazar(widget: tk.Widget) -> None:
            if not isinstance(widget, tk.Button):
                widget.configure(cursor="hand2")
                widget.bind("<Button-1>", lambda _evento: comando())
            for hijo in widget.winfo_children():
                enlazar(hijo)

        enlazar(tarjeta)

    def _comenzar_partida(self, dificultad: Dificultad) -> None:
        self.dificultad = dificultad
        self.juego = Juego(dificultad=dificultad)
        self.boton_accion.config(text="Rendirse", state="normal")
        self._actualizar_pantalla()
        self._iniciar_reloj()

    def _nueva_partida(self) -> None:
        if self._id_reloj is not None:
            self.raiz.after_cancel(self._id_reloj)
            self._id_reloj = None
        self.juego = None
        self._cache_imagenes.clear()
        self.boton_accion.config(text="Rendirse", state="normal")
        self.etiqueta_info.config(text="Elegí una dificultad")
        self._actualizar_reloj_visual(0, 0)
        self._mostrar_mensaje("Elegí la dificultad para arrancar de nuevo.")
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


class MenuPrincipal:
    def __init__(self, raiz: tk.Tk):
        self.raiz = raiz
        raiz.title("Solitario Battle")
        raiz.configure(bg=COLOR_MESA_OSCURO)
        raiz.resizable(True, True)
        _centrar_ventana(raiz, 760, 680)
        self.marco = tk.Frame(raiz, bg=COLOR_MESA_OSCURO)
        self.marco.pack(fill="both", expand=True)
        self._crear_vista()

    def _crear_vista(self) -> None:
        tk.Label(self.marco, text="♠  ♥  ♦  ♣", font=("Segoe UI Symbol", 18, "bold"), bg=COLOR_MESA_OSCURO, fg=COLOR_DORADO).pack(pady=(68, 10))
        tk.Label(self.marco, text="SOLITARIO\nBATTLE", font=("Segoe UI", 34, "bold"), bg=COLOR_MESA_OSCURO, fg=COLOR_TEXTO, justify="center").pack()
        tk.Label(self.marco, text="Un juego de observación y estrategia", font=FUENTE_SUBTITULO, bg=COLOR_MESA_OSCURO, fg=COLOR_MUTED).pack(pady=(12, 34))
        tarjeta = crear_tarjeta(self.marco, fondo=COLOR_PANEL, borde=COLOR_BORDE)
        tarjeta.pack(padx=20)
        crear_boton(tarjeta, "Jugar", self._on_jugar, principal=True, ancho=28, fuente=("Segoe UI", 14, "bold")).pack(padx=32, pady=(30, 10), fill="x")
        crear_boton(tarjeta, "Récords", self._on_records, ancho=28).pack(padx=32, pady=5, fill="x")
        crear_boton(tarjeta, "Configuración", self._on_configuracion, ancho=28).pack(padx=32, pady=5, fill="x")
        crear_boton(tarjeta, "Salir", self.raiz.destroy, ancho=28).pack(padx=32, pady=(5, 30), fill="x")

    def _on_jugar(self) -> None:
        self.marco.destroy()
        VentanaJuego(self.raiz)

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
        ventana.title("Configuración")
        ventana.configure(bg=COLOR_MESA_OSCURO)
        ventana.resizable(False, False)
        ventana.transient(self.raiz)
        _centrar_ventana(ventana, 460, 330)

        tk.Label(ventana, text="CONFIGURACIÓN", font=("Segoe UI", 10, "bold"), bg=COLOR_MESA_OSCURO, fg=COLOR_DORADO).pack(pady=(30, 5))
        tk.Label(ventana, text="Sonido del juego", font=("Segoe UI", 22, "bold"), bg=COLOR_MESA_OSCURO, fg=COLOR_TEXTO).pack()
        tarjeta = crear_tarjeta(ventana, fondo=COLOR_TARJETA, borde=COLOR_DORADO)
        tarjeta.pack(fill="both", expand=True, padx=36, pady=(20, 30))

        tk.Label(tarjeta, text="VOLUMEN", font=("Segoe UI", 9, "bold"), bg=COLOR_TARJETA, fg=COLOR_TEXTO_OSCURO).pack(pady=(24, 4))
        volumen = tk.IntVar(value=round(configuracion.cargar_volumen() * 100))
        etiqueta_valor = tk.Label(tarjeta, font=("Segoe UI", 15, "bold"), bg=COLOR_TARJETA, fg=COLOR_ACENTO)
        etiqueta_valor.pack()

        def actualizar_valor(_valor=None) -> None:
            actual = volumen.get()
            etiqueta_valor.config(text="Silenciado" if actual == 0 else f"{actual}%")

        barra = tk.Scale(
            tarjeta, from_=0, to=100, orient="horizontal", variable=volumen,
            command=actualizar_valor, showvalue=False, length=280, resolution=1,
            bg=COLOR_TARJETA, fg=COLOR_TEXTO_OSCURO, troughcolor="#D9CFBC",
            activebackground=COLOR_ACENTO, highlightthickness=0,
        )
        barra.pack(pady=(4, 16))
        actualizar_valor()

        def guardar() -> None:
            configuracion.guardar_volumen(volumen.get() / 100)
            ventana.destroy()

        crear_boton(tarjeta, "Guardar configuración", guardar, principal=True, fuente=("Segoe UI", 10, "bold")).pack(fill="x", padx=34, pady=(0, 24))


def jugar_partida_grafica() -> None:
    raiz = tk.Tk()
    MenuPrincipal(raiz)
    raiz.mainloop()
