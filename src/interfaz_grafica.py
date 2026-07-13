"""
interfaz_grafica.py
--------------------
Interfaz gráfica con Tkinter. Como juego.py, tablero.py, cartas.py y
reglas.py no saben nada de CÓMO se muestra el juego, este archivo es
lo único nuevo: reutiliza toda la lógica ya armada, solo cambia la
presentación e interacción (nada de esto toca la lógica del juego).

Interacción: hacés click en la pila que vos creas que es el lado
IZQUIERDO de una jugada válida (se compara automáticamente contra la
pila que está 2 lugares después, salteando la del medio). Si tenés
razón, se fusiona. Si no, te avisa y podés seguir mirando.
"""

import math
import tkinter as tk
from tkinter import messagebox

from juego import Juego
from cartas import Dificultad, CANTIDAD_CARTAS_EN_MAZO
import puntuacion
from imagenes_cartas import cargar_imagen_carta, cargar_imagen_dorso, ANCHO_CARTA, ALTO_CARTA

COLOR_FONDO = "#0b6623"     # verde "paño de mesa"
COLOR_PILA = "#fdfaf5"
COLOR_TEXTO_PILA = "#222222"
COLOR_ACENTO = "#c62828"
COLOR_ACENTO_HOVER = "#e53935"  # rojo más vivo, para el efecto hover del botón de acción
COLOR_TEXTO_CLARO = "#ffe082"
COLOR_TEXTO_MUTED = "#bcd9c0"   # info secundaria (dificultad, mazo, pilas): visible pero discreta
COLOR_EXITO = "#aed581"
COLOR_ERROR = "#ff8a65"
COLOR_BORDE_PILA = "#054d1a"  # marco fijo y sutil (no cambia con el mouse): le da presencia sin gimmicks
GROSOR_BORDE_PILA = 2
DIAMETRO_RELOJ = 62               # chico: no debe competir con el tablero
COLOR_RELOJ_FONDO = "#1a1a1a"     # cuerpo casi negro, como un cronómetro deportivo real
COLOR_RELOJ_ANILLO = "#e53935"    # anillo/botón rojo
COLOR_RELOJ_DIGITOS = "#4dff88"   # dígitos verde LED: alto contraste, se lee de un vistazo

# --- Tamaño de carta y layout del tablero ---
# El tamaño de carta ya NO es fijo: se recalcula en cada partida según el
# tamaño de PANTALLA disponible, para que las cartas se vean grandes en
# monitores grandes y sigan entrando enteras en pantallas chicas.
# ANCHO_CARTA/ALTO_CARTA (importados de imagenes_cartas) se usan solo como
# referencia de PROPORCIÓN (alto/ancho de una carta real), no como tamaño final.
RATIO_CARTA = ALTO_CARTA / ANCHO_CARTA

COLUMNAS_MIN_TABLERO = 6
COLUMNAS_MAX_TABLERO = 12
ANCHO_CARTA_MINIMO = 60     # por debajo de esto la carta deja de leerse bien
ANCHO_CARTA_MAXIMO = 200    # tope para que no queden gigantes en monitores enormes
GAP_CELDA = 8               # separación total que ya suman los padx/pady de cada .grid
PROPORCION_AREA_TRABAJO = 0.99  # la ventana de juego usa casi toda la pantalla (el menú es aparte, chico)

# Márgenes conservadores para no chocar con la barra de tareas / el marco
# de la ventana, que Tkinter no puede medir de antemano.
MARGEN_PANTALLA_ANCHO = 60
MARGEN_PANTALLA_ALTO = 90
MARGEN_INFERIOR_TABLERO = 20
MARGEN_VENTANA_AJUSTADA = 40  # aire extra alrededor del contenido medido


def _centrar_ventana(raiz: tk.Tk, ancho: int, alto: int) -> None:
    """Centra la ventana en la pantalla con el tamaño dado (nunca fullscreen)."""
    ancho_pantalla = raiz.winfo_screenwidth()
    alto_pantalla = raiz.winfo_screenheight()
    x = (ancho_pantalla - ancho) // 2
    y = (alto_pantalla - alto) // 2
    raiz.geometry(f"{ancho}x{alto}+{x}+{y}")


def _calcular_layout_tablero(ancho_disponible: int, alto_disponible: int) -> tuple[int, int, int]:
    """
    Busca, entre un rango razonable de columnas, la combinación de
    columnas + tamaño de carta más grande que entra SIN scroll en el
    espacio disponible.

    Siempre calcula para la cantidad MÁXIMA posible de celdas (las 48
    cartas del mazo completo + 1 celda más para el propio mazo), sin
    importar la dificultad elegida: así, si en la misma ventana se arranca
    una partida nueva con otra dificultad, el tamaño no cambia y todo
    sigue entrando.

    Devuelve (columnas, ancho_carta, alto_carta). Si ni el tamaño mínimo
    legible entra en el espacio disponible, igual devuelve la mejor
    combinación encontrada — quien llama decide si hace falta recurrir
    al modo con scroll.
    """
    celdas_totales = CANTIDAD_CARTAS_EN_MAZO + 1  # +1: la celda del mazo

    mejor_ancho_carta = 0
    mejor_columnas = COLUMNAS_MIN_TABLERO
    for columnas in range(COLUMNAS_MIN_TABLERO, COLUMNAS_MAX_TABLERO + 1):
        filas = math.ceil(celdas_totales / columnas)
        ancho_segun_ancho = ancho_disponible / columnas - GAP_CELDA
        ancho_segun_alto = (alto_disponible / filas - GAP_CELDA) / RATIO_CARTA
        ancho_carta = min(ancho_segun_ancho, ancho_segun_alto, ANCHO_CARTA_MAXIMO)
        if ancho_carta > mejor_ancho_carta:
            mejor_ancho_carta = ancho_carta
            mejor_columnas = columnas

    ancho_carta = max(int(mejor_ancho_carta), 1)
    alto_carta = int(ancho_carta * RATIO_CARTA)
    return mejor_columnas, ancho_carta, alto_carta


class VentanaJuego:
    def __init__(self, raiz: tk.Tk):
        self.raiz = raiz
        self.raiz.title("Solitario Hunting")
        self.raiz.configure(bg=COLOR_FONDO)
        # OJO: acá todavía no se maximiza ni se fija ningún tamaño de
        # ventana. Eso se decide en _armar_widgets_fijos, una vez armado
        # el encabezado, cuando ya sabemos cuánto lugar le queda al
        # tablero y podemos elegir el modo (ventana fija vs. maximizada).

        self.juego = None       # todavía no se eligió dificultad
        self.dificultad = None
        self._imagenes_actuales = []  # referencias vivas, para que Tkinter no las borre de memoria
        self._id_reloj = None
        self._arrastre = None  # info de la pila que se está arrastrando ahora mismo (o None)

        self._armar_widgets_fijos()
        # El selector de dificultad va DENTRO del propio tablero (no una
        # ventana aparte flotando encima): más integrado, y de paso es el
        # mismo mecanismo que se usa para "limpiar" el tablero al rendirse
        # (ver _nueva_partida).
        self._mostrar_selector_dificultad(self._comenzar_partida)

    def _armar_widgets_fijos(self) -> None:
        # --- Área con scroll que envuelve TODO el contenido de la partida ---
        # El scroll solo se ACTIVA (barra + rueda del mouse) si más abajo
        # resulta que el tablero no entra entero en pantalla. Si entra, la
        # ventana queda con tamaño fijo y no hace falta scrollear nada.
        self.marco_juego = tk.Frame(self.raiz, bg=COLOR_FONDO)
        self.marco_juego.pack(fill="both", expand=True)

        self.canvas_principal = tk.Canvas(
            self.marco_juego, bg=COLOR_FONDO, highlightthickness=0
        )
        self._barra_scroll = tk.Scrollbar(
            self.marco_juego, orient="vertical", command=self.canvas_principal.yview
        )
        self.canvas_principal.configure(yscrollcommand=self._barra_scroll.set)
        self.canvas_principal.pack(side="left", fill="both", expand=True)

        self.marco_contenido = tk.Frame(self.canvas_principal, bg=COLOR_FONDO)
        self._id_ventana_canvas = self.canvas_principal.create_window(
            (0, 0), window=self.marco_contenido, anchor="nw"
        )

        self.marco_contenido.bind(
            "<Configure>",
            lambda evento: self.canvas_principal.configure(
                scrollregion=self.canvas_principal.bbox("all")
            ),
        )
        # el ancho del contenido sigue al ancho del canvas (si la ventana se agranda)
        self.canvas_principal.bind(
            "<Configure>",
            lambda evento: self.canvas_principal.itemconfig(
                self._id_ventana_canvas, width=evento.width
            ),
        )

        # --- A partir de acá, todo se cuelga de self.marco_contenido, no de self.raiz ---
        # El reloj: un cronómetro chico centrado arriba. Los movimientos van
        # debajo, en texto claro (ni protagonista ni invisible).
        marco_reloj = tk.Frame(self.marco_contenido, bg=COLOR_FONDO)
        marco_reloj.pack(pady=(16, 2))

        self.canvas_reloj = tk.Canvas(
            marco_reloj, width=DIAMETRO_RELOJ + 16, height=DIAMETRO_RELOJ + 22,
            bg=COLOR_FONDO, highlightthickness=0,
        )
        self.canvas_reloj.pack()
        self._dibujar_reloj_circular()

        self.etiqueta_movimientos = tk.Label(
            marco_reloj, text="0 movimientos", font=("Arial", 12),
            bg=COLOR_FONDO, fg=COLOR_TEXTO_CLARO,
        )
        self.etiqueta_movimientos.pack(pady=(4, 0))

        # Barra de controles: info de la partida a la izquierda, y el botón
        # de Rendirse/Terminar a la derecha. Antes este botón vivía flotando
        # con .place() sobre una esquina de toda la PANTALLA (lejos del
        # tablero en monitores grandes); ahora es una fila más, junto a la
        # info que describe, como el resto de los controles de la partida.
        barra_superior = tk.Frame(self.marco_contenido, bg=COLOR_FONDO)
        barra_superior.pack(fill="x", padx=24, pady=(4, 2))

        self.etiqueta_info = tk.Label(
            barra_superior, text="", font=("Arial", 9),
            bg=COLOR_FONDO, fg=COLOR_TEXTO_MUTED,
        )
        self.etiqueta_info.pack(side="left")

        self.boton_accion = tk.Button(
            barra_superior, text="Rendirse", command=self._on_accion_principal,
            bg=COLOR_ACENTO, fg="white", font=("Arial", 11, "bold"),
            relief="flat", bd=0, padx=18, pady=9, cursor="hand2",
            activebackground=COLOR_ACENTO_HOVER, activeforeground="white",
        )
        self.boton_accion.bind("<Enter>", lambda e: self.boton_accion.config(bg=COLOR_ACENTO_HOVER))
        self.boton_accion.bind("<Leave>", lambda e: self.boton_accion.config(bg=COLOR_ACENTO))
        self.boton_accion.pack(side="right")

        self.etiqueta_mensaje = tk.Label(
            self.marco_contenido,
            text="Elegí la dificultad para arrancar.",
            font=("Arial", 13, "bold"), bg=COLOR_FONDO, fg=COLOR_TEXTO_CLARO,
            wraplength=560, justify="center",
        )
        self.etiqueta_mensaje.pack(pady=(4, 12))

        self.marco_tablero = tk.Frame(self.marco_contenido, bg=COLOR_FONDO)
        self.marco_tablero.pack(padx=12, pady=6)

        # --- Con el encabezado ya armado, medimos cuánto ocupa, y con eso
        # calculamos cuánto lugar le queda al tablero. La ventana de juego
        # usa casi toda la pantalla (PROPORCION_AREA_TRABAJO), así las
        # cartas se ven grandes; el margen que queda es solo para no
        # chocar con la barra de tareas / el marco de la ventana. El menú
        # principal es aparte y se mantiene chico (ver MenuPrincipal).
        self.raiz.update_idletasks()
        alto_encabezado = self.marco_contenido.winfo_reqheight()

        ancho_pantalla = self.raiz.winfo_screenwidth()
        alto_pantalla = self.raiz.winfo_screenheight()
        ancho_area_trabajo = int(ancho_pantalla * PROPORCION_AREA_TRABAJO)
        alto_area_trabajo = int(alto_pantalla * PROPORCION_AREA_TRABAJO)

        ancho_disponible = ancho_area_trabajo - MARGEN_PANTALLA_ANCHO
        alto_disponible_tablero = (
            alto_area_trabajo - MARGEN_PANTALLA_ALTO - alto_encabezado - MARGEN_INFERIOR_TABLERO
        )

        columnas, ancho_carta, alto_carta = _calcular_layout_tablero(
            ancho_disponible, alto_disponible_tablero
        )
        self.columnas_tablero = columnas
        self.ancho_carta = max(ancho_carta, ANCHO_CARTA_MINIMO)
        self.alto_carta = int(self.ancho_carta * RATIO_CARTA)

        # El scroll queda SIEMPRE disponible como red de seguridad (antes
        # solo se activaba si el cálculo no daba abasto, y en ese caso la
        # ventana además se maximizaba). Así, pase lo que pase —pantalla
        # chica, fuente del sistema grande, lo que sea— el tablero entero
        # siempre se puede ver, sin necesidad de recurrir a fullscreen.
        self._barra_scroll.pack(side="right", fill="y")
        self.canvas_principal.bind_all("<MouseWheel>", self._on_rueda_mouse)
        self.canvas_principal.bind_all("<Button-4>", lambda e: self.canvas_principal.yview_scroll(-1, "units"))
        self.canvas_principal.bind_all("<Button-5>", lambda e: self.canvas_principal.yview_scroll(1, "units"))

        # El tamaño final se calcula de forma ANALÍTICA (columnas x filas x
        # tamaño de carta), sin necesidad de armar el tablero real: en este
        # punto todavía no se eligió dificultad, así que marco_tablero está
        # vacío (ahí va a ir el selector). Como ya sabemos cuántas
        # columnas/filas puede llegar a tener el tablero completo (ver
        # _calcular_layout_tablero), alcanza con la cuenta para fijar la
        # ventana en su tamaño definitivo — siempre topado al área de
        # trabajo (80% de pantalla), nunca más grande que eso.
        celdas_totales = CANTIDAD_CARTAS_EN_MAZO + 1
        filas_totales = math.ceil(celdas_totales / columnas)
        ancho_tablero = columnas * (self.ancho_carta + GAP_CELDA)
        alto_tablero = filas_totales * (self.alto_carta + GAP_CELDA)

        ancho_ventana = min(
            max(ancho_tablero, self.marco_contenido.winfo_reqwidth()) + MARGEN_VENTANA_AJUSTADA,
            ancho_area_trabajo,
        )
        alto_ventana = min(
            alto_encabezado + alto_tablero + MARGEN_VENTANA_AJUSTADA, alto_area_trabajo
        )
        _centrar_ventana(self.raiz, ancho_ventana, alto_ventana)
        self.raiz.resizable(True, True)  # el usuario puede agrandarla más si quiere; el scroll cubre el resto

    def _dibujar_reloj_circular(self) -> None:
        """
        Dibuja UNA vez el cronómetro; el texto adentro se actualiza aparte.
        Estilo cronómetro deportivo: cuerpo oscuro, anillo rojo, un botón
        arriba (como el de un cronómetro de mano) y marcas a los 4 puntos
        cardinales. Los dígitos van en verde tipo LED, que es lo que más
        contraste y "lectura rápida" da sobre un fondo oscuro.
        """
        cx = (DIAMETRO_RELOJ + 16) / 2
        cy = (DIAMETRO_RELOJ + 22) / 2 + 6
        radio = DIAMETRO_RELOJ / 2

        # botoncito arriba, como el de un cronómetro real
        self.canvas_reloj.create_rectangle(
            cx - 6, cy - radio - 9, cx + 6, cy - radio + 2,
            fill=COLOR_RELOJ_ANILLO, outline="",
        )
        # cuerpo del cronómetro
        self.canvas_reloj.create_oval(
            cx - radio, cy - radio, cx + radio, cy + radio,
            fill=COLOR_RELOJ_FONDO, outline=COLOR_RELOJ_ANILLO, width=4,
        )
        # 4 marcas cardinales, como un dial
        for angulo in (0, 90, 180, 270):
            rad = math.radians(angulo)
            x1, y1 = cx + math.sin(rad) * (radio - 10), cy - math.cos(rad) * (radio - 10)
            x2, y2 = cx + math.sin(rad) * (radio - 4), cy - math.cos(rad) * (radio - 4)
            self.canvas_reloj.create_line(x1, y1, x2, y2, fill=COLOR_RELOJ_ANILLO, width=2)

        self._id_texto_tiempo = self.canvas_reloj.create_text(
            cx, cy, text="00:00", font=("Courier New", 13, "bold"), fill=COLOR_RELOJ_DIGITOS,
        )

    def _actualizar_reloj_visual(self, movimientos: int, segundos: int) -> None:
        self.canvas_reloj.itemconfig(
            self._id_texto_tiempo, text=puntuacion.formatear_duracion(segundos)
        )
        plural = "movimiento" if movimientos == 1 else "movimientos"
        self.etiqueta_movimientos.config(text=f"{movimientos} {plural}")

    def _mostrar_mensaje(self, texto: str, tipo: str = "info") -> None:
        """Actualiza el mensaje post-jugada. Color según el tipo, sin animación."""
        colores = {"exito": COLOR_EXITO, "error": COLOR_ERROR, "info": COLOR_TEXTO_CLARO}
        self.etiqueta_mensaje.config(text=texto, fg=colores.get(tipo, COLOR_TEXTO_CLARO))

    def _on_rueda_mouse(self, evento) -> None:
        self.canvas_principal.yview_scroll(int(-1 * (evento.delta / 120)), "units")

    def _iniciar_reloj(self) -> None:
        """Arranca (o reinicia) el reloj que refresca movimientos y tiempo cada segundo."""
        if self._id_reloj is not None:
            self.raiz.after_cancel(self._id_reloj)
        self._actualizar_reloj()

    def _actualizar_reloj(self) -> None:
        if self.juego.esta_terminada():
            self._id_reloj = None
            return  # no se reprograma más: se frenó el reloj
        movimientos = self.juego.cantidad_jugadas_realizadas
        segundos = self.juego.duracion_segundos()
        self._actualizar_reloj_visual(movimientos, segundos)
        self._id_reloj = self.raiz.after(1000, self._actualizar_reloj)

    def _on_repartir(self) -> None:
        if self.juego.esta_terminada() or not self.juego.quedan_cartas_en_mano():
            return
        self.juego.repartir_carta()
        self._mostrar_mensaje("Carta repartida. ¿Ves alguna jugada?", "info")
        self._actualizar_pantalla()

    def _on_accion_principal(self) -> None:
        """
        Un solo botón con dos comportamientos, según el momento:
        - Si todavía quedan cartas en el mazo: es un "Rendirse" (pide
          confirmación, porque descarta la partida en curso).
        - Si ya no quedan cartas: es "Terminar partida" (cierre normal,
          sin confirmación, porque ya jugaste todo lo que había).
        """
        if self.juego.esta_terminada():
            return

        if self.juego.quedan_cartas_en_mano():
            confirmar = messagebox.askyesno(
                "Rendirse",
                "¿Seguro que querés abandonar esta partida y empezar una nueva?\n"
                "No se va a guardar ningún puntaje de esta partida.",
            )
            if confirmar:
                self._nueva_partida()
        else:
            self.juego.finalizar()
            self._terminar_partida()

    def _iniciar_arrastre(self, evento: tk.Event, indice: int) -> None:
        """Se dispara al apretar el botón del mouse sobre una pila: la "levanta"."""
        if self.juego.esta_terminada():
            return
        boton = self._botones_pilas[indice]
        self._arrastre = {
            "indice_origen": indice,
            "boton": boton,
            "x_inicial": boton.winfo_x(),
            "y_inicial": boton.winfo_y(),
            "x_mouse_inicial": evento.x_root,
            "y_mouse_inicial": evento.y_root,
        }
        boton.grid_forget()
        boton.place(x=self._arrastre["x_inicial"], y=self._arrastre["y_inicial"])
        boton.lift()  # que se vea por encima de las demás pilas mientras se arrastra

    def _arrastrando(self, evento: tk.Event) -> None:
        """Se dispara en cada movimiento del mouse mientras está apretado."""
        if self._arrastre is None:
            return
        dx = evento.x_root - self._arrastre["x_mouse_inicial"]
        dy = evento.y_root - self._arrastre["y_mouse_inicial"]
        self._arrastre["boton"].place(
            x=self._arrastre["x_inicial"] + dx,
            y=self._arrastre["y_inicial"] + dy,
        )

    def _soltar_arrastre(self, evento: tk.Event) -> None:
        """
        Se dispara al soltar el botón del mouse. La única jugada válida es
        soltar la pila arrastrada ENCIMA de la que está inmediatamente a su
        izquierda (así se simula "empujar" una pila sobre la anterior).
        Si no cayó ahí, no pasa nada: _actualizar_pantalla() la vuelve a
        su lugar original en la grilla.
        """
        if self._arrastre is None:
            return
        indice_origen = self._arrastre["indice_origen"]
        boton_arrastrado = self._arrastre["boton"]
        indice_destino = indice_origen - 1
        self._arrastre = None

        if indice_destino >= 0 and self._soltada_sobre_pila(boton_arrastrado, indice_destino):
            if self.juego.intentar_jugada(indice_destino):
                self._mostrar_mensaje("¡Jugada válida! Buen ojo. 👀", "exito")
            else:
                self._mostrar_mensaje("Ahí no hay ninguna coincidencia. Fijate de nuevo.", "error")
        self._actualizar_pantalla()

    def _soltada_sobre_pila(self, boton_arrastrado: tk.Widget, indice_objetivo: int) -> bool:
        """True si el CENTRO del botón arrastrado terminó dentro del área de la pila objetivo."""
        if indice_objetivo >= len(self._botones_pilas):
            return False
        objetivo = self._botones_pilas[indice_objetivo]

        centro_x = boton_arrastrado.winfo_x() + boton_arrastrado.winfo_width() / 2
        centro_y = boton_arrastrado.winfo_y() + boton_arrastrado.winfo_height() / 2

        ox, oy = objetivo.winfo_x(), objetivo.winfo_y()
        ancho, alto = objetivo.winfo_width(), objetivo.winfo_height()

        return ox <= centro_x <= ox + ancho and oy <= centro_y <= oy + alto

    def _actualizar_pantalla(self) -> None:
        for widget in self.marco_tablero.winfo_children():
            widget.destroy()
        self._imagenes_actuales = []  # se descartan las anteriores, se cargan las nuevas
        self._botones_pilas = []      # referencias vivas, necesarias para el arrastre

        columnas = self.columnas_tablero
        cartas_restantes = self.juego.mazo.quedan_cartas()

        # El mazo ocupa la celda 0: es una pila más de la grilla (mismo
        # tamaño, mismo estilo), no un elemento aparte. El contador de
        # cartas restantes va grabado en la propia imagen del dorso (ver
        # imagenes_cartas._dibujar_contador), no como texto del botón.
        self._imagen_dorso = cargar_imagen_dorso(self.ancho_carta, self.alto_carta, cantidad=cartas_restantes)
        self.boton_mazo = tk.Button(
            self.marco_tablero,
            image=self._imagen_dorso,
            bg=COLOR_PILA,
            cursor="hand2",
            relief="flat",
            bd=0,
            highlightthickness=GROSOR_BORDE_PILA,
            highlightbackground=COLOR_BORDE_PILA,
            highlightcolor=COLOR_BORDE_PILA,
            command=self._on_repartir,
        )
        self.boton_mazo.grid(row=0, column=0, padx=4, pady=4)

        pilas = self.juego.tablero.pilas
        for indice, pila in enumerate(pilas):
            posicion = indice + 1  # +1: la celda 0 ya la ocupa el mazo
            fila = posicion // columnas
            columna = posicion % columnas

            imagen = cargar_imagen_carta(pila.tope(), self.ancho_carta, self.alto_carta, cantidad=len(pila))
            self._imagenes_actuales.append(imagen)  # evita que se pierda la referencia

            boton = tk.Button(
                self.marco_tablero,
                image=imagen,
                bg=COLOR_PILA,
                cursor="hand2",  # manito: más amigable que la cruz de flechas de "fleur"
                relief="flat",
                bd=0,
                highlightthickness=GROSOR_BORDE_PILA,
                highlightbackground=COLOR_BORDE_PILA,
                highlightcolor=COLOR_BORDE_PILA,
            )
            boton.grid(row=fila, column=columna, padx=4, pady=4)
            boton.bind("<ButtonPress-1>", lambda e, i=indice: self._iniciar_arrastre(e, i))
            boton.bind("<B1-Motion>", self._arrastrando)
            boton.bind("<ButtonRelease-1>", self._soltar_arrastre)
            self._botones_pilas.append(boton)

        # Sin esto, al "levantar" una pila del grid (ver _iniciar_arrastre) su
        # columna se queda sin nada adentro y Tkinter la colapsa a ancho 0,
        # lo que corre a las demás pilas visualmente ANTES de soltar nada.
        # Fijando un tamaño mínimo por columna/fila, el hueco se mantiene
        # quieto mientras dura el arrastre. Se calcula sobre TODOS los
        # botones (mazo incluido), para que la celda del mazo no achique
        # su fila/columna cuando queda como la única celda ocupada de esa fila.
        todos_los_botones = [self.boton_mazo] + self._botones_pilas
        self.marco_tablero.update_idletasks()
        ancho_celda = max(b.winfo_reqwidth() for b in todos_los_botones) + 8
        alto_celda = max(b.winfo_reqheight() for b in todos_los_botones) + 8
        filas_totales = len(pilas) // columnas + 1
        for columna_config in range(columnas):
            self.marco_tablero.grid_columnconfigure(columna_config, minsize=ancho_celda)
        for fila_config in range(filas_totales):
            self.marco_tablero.grid_rowconfigure(fila_config, minsize=alto_celda)

        texto_dificultad = "Fácil" if self.dificultad == Dificultad.FACIL else "Difícil"
        self.etiqueta_info.config(
            text=f"{texto_dificultad} · {len(pilas)} pilas en mesa"
        )

        if cartas_restantes == 0 and not self.juego.esta_terminada():
            self.boton_mazo.config(state="disabled")
            self.boton_accion.config(text="Terminar partida")
            self._mostrar_mensaje(
                "Se acabaron las cartas. ¿Ves alguna jugada más? "
                "Si no encontrás ninguna, apretá 'Terminar partida'.",
                "info",
            )

    def _terminar_partida(self) -> None:
        self.boton_mazo.config(state="disabled")
        self.boton_accion.config(state="disabled")

        resumen = self.juego.obtener_resumen()
        interpretacion = puntuacion.interpretar_resultado(resumen["pilas_finales"])
        duracion_texto = puntuacion.formatear_duracion(resumen["duracion_segundos"])
        self._abrir_ventana_resumen(resumen, interpretacion, duracion_texto)

    def _abrir_ventana_resumen(self, resumen: dict, interpretacion: str, duracion_texto: str) -> None:
        """
        El resumen de la partida vive en su propia ventana modal, para que
        el tablero quede completamente tapado y el cierre de la partida
        tenga su propio espacio. Reusa el mismo lenguaje visual que ya
        está instalado en el resto del juego: tarjeta color hueso con
        borde dorado (mismo que el mazo/pilas al pasar el mouse), el
        puntaje como una placa oscura estilo cronómetro (mismo que el
        reloj y el contador de cartas), y botones con el mismo estilo
        plano + hover que "Rendirse".
        """
        ventana = tk.Toplevel(self.raiz)
        ventana.title("Partida terminada")
        ventana.configure(bg=COLOR_FONDO)
        ventana.resizable(False, False)
        ventana.transient(self.raiz)
        # si la cierran con la X, la salida segura es volver al menú
        ventana.protocol("WM_DELETE_WINDOW", lambda: self._cerrar_resumen_y(ventana, self._volver_al_menu))

        ancho, alto = 440, 560
        self.raiz.update_idletasks()
        x = self.raiz.winfo_rootx() + (self.raiz.winfo_width() - ancho) // 2
        y = self.raiz.winfo_rooty() + (self.raiz.winfo_height() - alto) // 2
        ventana.geometry(f"{ancho}x{alto}+{x}+{y}")

        tk.Label(
            ventana, text="🏁 Partida terminada", font=("Arial", 16, "bold"),
            bg=COLOR_FONDO, fg=COLOR_TEXTO_CLARO,
        ).pack(pady=(20, 14))

        # --- Tarjeta central: crema con borde dorado, mismo material que las cartas ---
        tarjeta = tk.Frame(
            ventana, bg=COLOR_PILA, highlightbackground=COLOR_TEXTO_CLARO,
            highlightthickness=3, padx=26, pady=22,
        )
        tarjeta.pack(padx=28, fill="both", expand=True)

        # --- Puntaje: placa oscura con dígitos LED, mismo lenguaje que el reloj ---
        marco_puntaje = tk.Frame(
            tarjeta, bg=COLOR_RELOJ_FONDO, highlightbackground=COLOR_RELOJ_ANILLO, highlightthickness=3,
        )
        marco_puntaje.pack(fill="x", pady=(0, 16))
        tk.Label(
            marco_puntaje, text="PUNTAJE", font=("Arial", 9, "bold"),
            bg=COLOR_RELOJ_FONDO, fg=COLOR_TEXTO_MUTED,
        ).pack(pady=(10, 0))
        tk.Label(
            marco_puntaje, text=str(resumen["puntaje"]), font=("Courier New", 32, "bold"),
            bg=COLOR_RELOJ_FONDO, fg=COLOR_RELOJ_DIGITOS,
        ).pack(pady=(0, 10))

        tk.Label(
            tarjeta, text=interpretacion, font=("Arial", 11, "bold"),
            bg=COLOR_PILA, fg=COLOR_TEXTO_PILA, wraplength=340, justify="center",
        ).pack(pady=(0, 6))

        tk.Label(
            tarjeta,
            text=(
                f"{resumen['pilas_finales']} pilas finales   ·   "
                f"{resumen['movimientos']} movimientos   ·   {duracion_texto}"
            ),
            font=("Arial", 9), bg=COLOR_PILA, fg="#6b6b6b",
        ).pack(pady=(0, 18))

        tk.Label(
            tarjeta, text="Nombre para guardar el puntaje", font=("Arial", 9, "bold"),
            bg=COLOR_PILA, fg=COLOR_TEXTO_PILA,
        ).pack()

        entrada_nombre = tk.Entry(
            tarjeta, font=("Arial", 11), justify="center", relief="flat",
            highlightbackground="#c9bfa0", highlightthickness=1,
        )
        entrada_nombre.pack(pady=(6, 18), ipady=5, fill="x")

        boton_guardar = tk.Button(
            tarjeta, text="Guardar puntaje", command=lambda: self._guardar(resumen, entrada_nombre),
            bg=COLOR_ACENTO, fg="white", font=("Arial", 11, "bold"),
            relief="flat", bd=0, pady=10, cursor="hand2",
            activebackground=COLOR_ACENTO_HOVER, activeforeground="white",
        )
        boton_guardar.bind("<Enter>", lambda e: boton_guardar.config(bg=COLOR_ACENTO_HOVER))
        boton_guardar.bind("<Leave>", lambda e: boton_guardar.config(bg=COLOR_ACENTO))
        boton_guardar.pack(fill="x", pady=(0, 8))

        marco_secundarios = tk.Frame(tarjeta, bg=COLOR_PILA)
        marco_secundarios.pack(fill="x")

        def _boton_secundario(padre: tk.Widget, texto: str, comando) -> tk.Button:
            boton = tk.Button(
                padre, text=texto, command=comando,
                bg=COLOR_PILA, fg=COLOR_TEXTO_PILA, font=("Arial", 10),
                relief="flat", bd=0, pady=9, cursor="hand2",
                highlightbackground="#c9bfa0", highlightthickness=1,
                activebackground="#e8e0cc",
            )
            boton.bind("<Enter>", lambda e: boton.config(bg="#e8e0cc"))
            boton.bind("<Leave>", lambda e: boton.config(bg=COLOR_PILA))
            return boton

        _boton_secundario(
            marco_secundarios, "Nueva partida",
            lambda: self._cerrar_resumen_y(ventana, self._nueva_partida),
        ).pack(side="left", expand=True, fill="x", padx=(0, 4))

        _boton_secundario(
            marco_secundarios, "Volver al menú",
            lambda: self._cerrar_resumen_y(ventana, self._volver_al_menu),
        ).pack(side="left", expand=True, fill="x", padx=(4, 0))

        ventana.grab_set()  # modal: bloquea el tablero de atrás hasta que se cierre

    def _cerrar_resumen_y(self, ventana: tk.Toplevel, accion) -> None:
        ventana.destroy()
        accion()

    def _guardar(self, resumen: dict, entrada_nombre: tk.Entry) -> None:
        nombre = entrada_nombre.get().strip()
        if not nombre:
            messagebox.showinfo("Falta el nombre", "Escribí un nombre antes de guardar.")
            return
        puntuacion.guardar_puntaje(nombre, resumen)
        messagebox.showinfo("Guardado", "Puntaje guardado en historial.json")

    def _mostrar_selector_dificultad(self, al_elegir) -> None:
        """
        Selector de dificultad embebido DENTRO del propio tablero, en vez
        de una ventana Toplevel flotando encima (quedaba desconectada del
        resto). Se usa tanto al arrancar el juego por primera vez como al
        empezar de nuevo después de rendirse: en los dos casos, lo primero
        que hace es limpiar marco_tablero (así el tablero viejo desaparece
        de verdad, no queda tapado por una ventana). Al elegir una opción,
        llama a al_elegir(dificultad) para armar la partida en su lugar.
        """
        for widget in self.marco_tablero.winfo_children():
            widget.destroy()

        marco_selector = tk.Frame(self.marco_tablero, bg=COLOR_FONDO)
        marco_selector.pack(pady=60, padx=40)

        tk.Label(
            marco_selector, text="¿Con qué dificultad querés jugar?",
            font=("Arial", 14, "bold"), bg=COLOR_FONDO, fg=COLOR_TEXTO_CLARO,
        ).pack(pady=(0, 20))

        marco_botones = tk.Frame(marco_selector, bg=COLOR_FONDO)
        marco_botones.pack()

        opciones = (
            ("Fácil\n(sin 8 ni 9 — 40 cartas)", Dificultad.FACIL),
            ("Difícil\n(con 8 y 9 — 48 cartas)", Dificultad.DIFICIL),
        )
        for texto, dificultad in opciones:
            tk.Button(
                marco_botones, text=texto, command=lambda d=dificultad: al_elegir(d),
                bg=COLOR_ACENTO, fg="white", font=("Arial", 11, "bold"), justify="center",
                relief="flat", bd=0, padx=18, pady=12, cursor="hand2",
                activebackground=COLOR_ACENTO_HOVER, activeforeground="white",
            ).pack(side="left", padx=10)

    def _comenzar_partida(self, dificultad: Dificultad) -> None:
        """Arma la partida elegida y la muestra en el tablero. La llama el selector de dificultad."""
        self.dificultad = dificultad
        self.juego = Juego(dificultad=dificultad)
        self._actualizar_pantalla()
        self._iniciar_reloj()
        self._mostrar_mensaje("Hacé click en el mazo para empezar.", "info")

    def _nueva_partida(self) -> None:
        """Abandona la partida actual (se haya guardado o no) y vuelve a pedir dificultad."""
        if self._id_reloj is not None:
            self.raiz.after_cancel(self._id_reloj)
            self._id_reloj = None
        self.boton_accion.config(text="Rendirse", state="normal")
        self._actualizar_reloj_visual(0, 0)
        self.etiqueta_info.config(text="")
        self._mostrar_mensaje("Elegí la dificultad para arrancar de nuevo.", "info")
        self._mostrar_selector_dificultad(self._comenzar_partida)

    def _volver_al_menu(self) -> None:
        """Descarta la partida actual (se haya guardado o no) y vuelve a la pantalla de menú."""
        if self._id_reloj is not None:
            self.raiz.after_cancel(self._id_reloj)
            self._id_reloj = None
        self.canvas_principal.unbind_all("<MouseWheel>")
        self.canvas_principal.unbind_all("<Button-4>")
        self.canvas_principal.unbind_all("<Button-5>")
        self.raiz.resizable(True, True)  # por si esta partida dejó la ventana en tamaño fijo
        self.marco_juego.destroy()  # ahora todo (barra, mazo, tablero) cuelga de acá
        MenuPrincipal(self.raiz)


class MenuPrincipal:
    """
    Pantalla inicial. Se muestra primero, en la misma ventana (raiz) que
    después usa VentanaJuego: al apretar "Jugar" simplemente se destruye
    este marco y se arma el del juego encima.
    """

    def __init__(self, raiz: tk.Tk):
        self.raiz = raiz
        self.raiz.title("Solitario Hunting")
        self.raiz.configure(bg=COLOR_FONDO)
        self.raiz.resizable(True, True)  # por si la partida anterior dejó la ventana en tamaño fijo
        _centrar_ventana(self.raiz, 520, 620)

        self.marco = tk.Frame(raiz, bg=COLOR_FONDO, padx=50, pady=50)
        self.marco.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            self.marco, text="Solitario Hunting",
            font=("Arial", 20, "bold"), bg=COLOR_FONDO, fg=COLOR_TEXTO_CLARO,
        ).pack(pady=(0, 30))

        tk.Button(
            self.marco, text="Jugar", command=self._on_jugar,
            bg=COLOR_ACENTO, fg="white", font=("Arial", 13, "bold"), width=20,
        ).pack(pady=6)

        tk.Button(
            self.marco, text="Récords", command=self._on_records,
            bg=COLOR_PILA, fg=COLOR_TEXTO_PILA, font=("Arial", 13), width=20,
        ).pack(pady=6)

        # Todavía no hay tutorial armado: el botón queda visible pero
        # deshabilitado, como referencia de que la opción va a existir.
        tk.Button(
            self.marco, text="Tutorial", state="disabled",
            bg=COLOR_PILA, fg=COLOR_TEXTO_PILA, font=("Arial", 13), width=20,
        ).pack(pady=6)

        tk.Button(
            self.marco, text="Configuración", command=self._on_configuracion,
            bg=COLOR_PILA, fg=COLOR_TEXTO_PILA, font=("Arial", 13), width=20,
        ).pack(pady=6)

        tk.Button(
            self.marco, text="Salir", command=self.raiz.destroy,
            bg=COLOR_PILA, fg=COLOR_TEXTO_PILA, font=("Arial", 13), width=20,
        ).pack(pady=6)

    def _on_jugar(self) -> None:
        self.marco.destroy()
        VentanaJuego(self.raiz)

    def _on_records(self) -> None:
        """Abre una ventana aparte con el top 10 de mejores puntajes guardados."""
        ventana = tk.Toplevel(self.raiz)
        ventana.title("Récords")
        ventana.configure(bg=COLOR_FONDO)
        ventana.geometry("680x480")
        ventana.resizable(False, False)

        tk.Label(
            ventana, text="🏆 Mejores puntajes", font=("Arial", 18, "bold"),
            bg=COLOR_FONDO, fg=COLOR_TEXTO_CLARO,
        ).pack(pady=(18, 4))

        historial = puntuacion.cargar_historial()

        if not historial:
            tk.Label(
                ventana,
                text="Todavía no hay partidas guardadas.\n¡Jugá una y quedará tu marca acá!",
                font=("Arial", 11), bg=COLOR_FONDO, fg=COLOR_TEXTO_MUTED, justify="center",
            ).pack(pady=60)
        else:
            mejores = sorted(historial, key=lambda partida: partida["puntaje"], reverse=True)[:10]
            self._dibujar_tabla_records(ventana, mejores)

        boton_cerrar = tk.Button(
            ventana, text="Cerrar", command=ventana.destroy,
            bg=COLOR_ACENTO, fg="white", font=("Arial", 10, "bold"),
            relief="flat", bd=0, padx=20, pady=8, cursor="hand2",
            activebackground=COLOR_ACENTO_HOVER, activeforeground="white",
        )
        boton_cerrar.bind("<Enter>", lambda e: boton_cerrar.config(bg=COLOR_ACENTO_HOVER))
        boton_cerrar.bind("<Leave>", lambda e: boton_cerrar.config(bg=COLOR_ACENTO))
        boton_cerrar.pack(pady=(10, 18))

    def _dibujar_tabla_records(self, ventana: tk.Toplevel, mejores: list[dict]) -> None:
        """
        Tabla de verdad (Frame + Label por celda) en vez del Text monoespaciado
        de antes: zebra striping en el mismo tono crema de las cartas, medallas
        para el podio y la fila #1 resaltada en dorado — la misma paleta que
        ya se usa en el resto del juego (paño verde, dorado, cartas color hueso).
        """
        columnas = (
            ("#", 3), ("Jugador", 13), ("Dificultad", 10),
            ("Puntaje", 8), ("Pilas", 6), ("Mov.", 6), ("Fecha", 12),
        )
        medallas = {1: "🥇", 2: "🥈", 3: "🥉"}
        color_fila_par = COLOR_PILA       # crema, igual que el dorso/frente de las cartas
        color_fila_impar = "#f0ead9"      # crema apenas más oscuro, para el efecto zebra
        color_fila_primer_puesto = "#fff2b8"  # resalta el mejor puntaje de todos

        marco_tabla = tk.Frame(ventana, bg=COLOR_FONDO)
        marco_tabla.pack(padx=20, pady=(8, 4), fill="both", expand=True)

        fila_encabezado = tk.Frame(marco_tabla, bg=COLOR_FONDO)
        fila_encabezado.pack(fill="x", pady=(0, 4))
        for texto, ancho in columnas:
            tk.Label(
                fila_encabezado, text=texto, width=ancho, font=("Arial", 10, "bold"),
                bg=COLOR_FONDO, fg=COLOR_TEXTO_CLARO, anchor="w",
            ).pack(side="left", padx=2)

        for posicion, partida in enumerate(mejores, start=1):
            if posicion == 1:
                color_fila = color_fila_primer_puesto
            elif posicion % 2 == 0:
                color_fila = color_fila_par
            else:
                color_fila = color_fila_impar

            fila = tk.Frame(marco_tabla, bg=color_fila)
            fila.pack(fill="x")

            valores = (
                medallas.get(posicion, str(posicion)),
                partida["jugador"][:12],
                partida.get("dificultad", "-"),
                str(partida["puntaje"]),
                str(partida["pilas_finales"]),
                str(partida["movimientos"]),
                partida.get("fecha", "-"),
            )
            for (_, ancho), valor in zip(columnas, valores):
                tk.Label(
                    fila, text=valor, width=ancho, font=("Arial", 10),
                    bg=color_fila, fg=COLOR_TEXTO_PILA, anchor="w",
                ).pack(side="left", padx=2, pady=5)

    def _on_configuracion(self) -> None:
        messagebox.showinfo(
            "Configuración",
            "Todavía no hay opciones configurables. Próximamente.",
        )


def jugar_partida_grafica() -> None:
    raiz = tk.Tk()
    MenuPrincipal(raiz)
    raiz.mainloop()
