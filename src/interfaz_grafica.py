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
from cartas import Dificultad
import puntuacion
from imagenes_cartas import cargar_imagen_carta, cargar_imagen_dorso, ANCHO_CARTA, ALTO_CARTA

ANCHO_FILA = 7  # puramente visual: cuántas pilas entran por fila antes de saltar de línea
ANCHO_VENTANA = 900
ALTO_VENTANA = 700

COLOR_FONDO = "#0b6623"     # verde "paño de mesa"
COLOR_PILA = "#fdfaf5"
COLOR_TEXTO_PILA = "#222222"
COLOR_ACENTO = "#c62828"
COLOR_TEXTO_CLARO = "#ffe082"
COLOR_TEXTO_MUTED = "#bcd9c0"   # info secundaria (dificultad, mazo, pilas): visible pero discreta
COLOR_EXITO = "#aed581"
COLOR_ERROR = "#ff8a65"
FUENTE_CONTADOR = ("Arial", 12, "bold")
DIAMETRO_RELOJ = 62               # chico: no debe competir con el tablero
COLOR_RELOJ_FONDO = "#1a1a1a"     # cuerpo casi negro, como un cronómetro deportivo real
COLOR_RELOJ_ANILLO = "#e53935"    # anillo/botón rojo
COLOR_RELOJ_DIGITOS = "#4dff88"   # dígitos verde LED: alto contraste, se lee de un vistazo
ANCHO_MAZO = int(ANCHO_CARTA * 1.15)
ALTO_MAZO = int(ALTO_CARTA * 1.15)


def _maximizar_ventana(raiz: tk.Tk) -> None:
    """
    Arranca con la ventana maximizada, para que entre todo el tablero sin
    tener que estirarla a mano. "zoomed" anda en Windows y la mayoría de
    Linux; si el sistema no lo soporta (algunos entornos Linux/Mac), cae
    a agrandarla al tamaño de la pantalla como plan B.
    """
    try:
        raiz.state("zoomed")
    except tk.TclError:
        try:
            raiz.attributes("-zoomed", True)
        except tk.TclError:
            ancho = raiz.winfo_screenwidth()
            alto = raiz.winfo_screenheight()
            raiz.geometry(f"{ancho}x{alto}+0+0")


def elegir_dificultad(padre: tk.Tk) -> Dificultad:
    """
    Abre un diálogo modal (bloquea la ventana principal) para elegir la
    dificultad. Se usa al arrancar una partida, y de nuevo cada vez que
    empieza una partida nueva.
    """
    ventana = tk.Toplevel(padre)
    ventana.title("Elegí la dificultad")
    ventana.configure(bg=COLOR_FONDO)
    ventana.resizable(False, False)
    ventana.grab_set()  # modal: bloquea la ventana principal hasta que se cierra esta

    resultado = {"dificultad": None}

    tk.Label(
        ventana, text="¿Con qué dificultad querés jugar?",
        font=("Arial", 12, "bold"), bg=COLOR_FONDO, fg="white",
    ).pack(padx=24, pady=(18, 10))

    def elegir(dificultad: Dificultad) -> None:
        resultado["dificultad"] = dificultad
        ventana.destroy()

    marco_botones = tk.Frame(ventana, bg=COLOR_FONDO)
    marco_botones.pack(pady=(0, 18), padx=24)

    tk.Button(
        marco_botones, text="Fácil\n(sin 8 ni 9 — 40 cartas)",
        command=lambda: elegir(Dificultad.FACIL),
        bg=COLOR_ACENTO, fg="white", font=("Arial", 10, "bold"), justify="center",
    ).pack(side="left", padx=8)

    tk.Button(
        marco_botones, text="Difícil\n(con 8 y 9 — 48 cartas)",
        command=lambda: elegir(Dificultad.DIFICIL),
        bg=COLOR_ACENTO, fg="white", font=("Arial", 10, "bold"), justify="center",
    ).pack(side="left", padx=8)

    # si el jugador cierra la ventana con la X sin elegir, queda Difícil por defecto
    padre.wait_window(ventana)
    return resultado["dificultad"] or Dificultad.DIFICIL


class VentanaJuego:
    def __init__(self, raiz: tk.Tk):
        self.raiz = raiz
        self.raiz.title("Solitario de las 50 cartas")
        self.raiz.configure(bg=COLOR_FONDO)
        _maximizar_ventana(self.raiz)

        self.dificultad = elegir_dificultad(self.raiz)
        self.juego = Juego(dificultad=self.dificultad)
        self._imagenes_actuales = []  # referencias vivas, para que Tkinter no las borre de memoria
        self._id_reloj = None
        self._arrastre = None  # info de la pila que se está arrastrando ahora mismo (o None)

        self._armar_widgets_fijos()
        self._actualizar_pantalla()
        self._iniciar_reloj()

    def _armar_widgets_fijos(self) -> None:
        # --- Área con scroll que envuelve TODO el contenido de la partida ---
        # OJO CON EL ORDEN: esto se arma PRIMERO, y recién después se crean
        # el mazo y el botón Rendirse (más abajo). En Tkinter, entre widgets
        # hermanos de un mismo padre, el que se crea último queda dibujado
        # ENCIMA. La vez pasada quedó al revés y por eso el mazo y el botón
        # quedaban tapados por este marco, que ocupa toda la ventana.
        self.marco_juego = tk.Frame(self.raiz, bg=COLOR_FONDO)
        self.marco_juego.pack(fill="both", expand=True)

        self.canvas_principal = tk.Canvas(
            self.marco_juego, bg=COLOR_FONDO, highlightthickness=0
        )
        barra_scroll = tk.Scrollbar(
            self.marco_juego, orient="vertical", command=self.canvas_principal.yview
        )
        self.canvas_principal.configure(yscrollcommand=barra_scroll.set)
        self.canvas_principal.pack(side="left", fill="both", expand=True)
        barra_scroll.pack(side="right", fill="y")

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
        # rueda del mouse: Windows/Mac mandan <MouseWheel>, Linux manda <Button-4>/<Button-5>
        self.canvas_principal.bind_all("<MouseWheel>", self._on_rueda_mouse)
        self.canvas_principal.bind_all("<Button-4>", lambda e: self.canvas_principal.yview_scroll(-1, "units"))
        self.canvas_principal.bind_all("<Button-5>", lambda e: self.canvas_principal.yview_scroll(1, "units"))

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

        # Info secundaria (dificultad, pilas en mesa): útil pero no crítica
        # momento a momento, por eso queda chica y discreta.
        self.etiqueta_info = tk.Label(
            self.marco_contenido, text="", font=("Arial", 9),
            bg=COLOR_FONDO, fg=COLOR_TEXTO_MUTED,
        )
        self.etiqueta_info.pack(pady=(2, 8))

        self.etiqueta_mensaje = tk.Label(
            self.marco_contenido,
            text="Hacé click en el mazo para empezar.",
            font=("Arial", 13, "bold"), bg=COLOR_FONDO, fg=COLOR_TEXTO_CLARO,
            wraplength=560, justify="center",
        )
        self.etiqueta_mensaje.pack(pady=(4, 12))

        self.marco_tablero = tk.Frame(self.marco_contenido, bg=COLOR_FONDO)
        self.marco_tablero.pack(padx=12, pady=6)

        # --- Elementos flotantes: SIEMPRE al final, para que queden arriba ---
        # Rendirse, esquina superior derecha.
        self.boton_accion = tk.Button(
            self.raiz, text="Rendirse", command=self._on_accion_principal,
            bg=COLOR_ACENTO, fg="white", font=("Arial", 11, "bold"),
        )
        self.boton_accion.place(relx=1.0, x=-14, y=14, anchor="ne")

        # El mazo: abajo a la izquierda, con margen (no pegado al borde).
        self.marco_mazo = tk.Frame(self.raiz, bg=COLOR_FONDO)
        self.marco_mazo.place(relx=0.0, rely=1.0, x=70, y=-60, anchor="sw")

        self._imagen_dorso = cargar_imagen_dorso(ANCHO_MAZO, ALTO_MAZO)  # referencia viva
        self.boton_mazo = tk.Button(
            self.marco_mazo, image=self._imagen_dorso, command=self._on_repartir,
            bg=COLOR_PILA, cursor="hand2", relief="raised", bd=2,
        )
        self.boton_mazo.pack()

        self.etiqueta_mazo_cantidad = tk.Label(
            self.marco_mazo, text="", font=("Arial", 15, "bold"),
            bg=COLOR_FONDO, fg=COLOR_TEXTO_CLARO,
        )
        self.etiqueta_mazo_cantidad.pack(pady=(4, 0))

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

        pilas = self.juego.tablero.pilas
        for indice, pila in enumerate(pilas):
            fila = indice // ANCHO_FILA
            columna = indice % ANCHO_FILA

            imagen = cargar_imagen_carta(pila.tope())
            self._imagenes_actuales.append(imagen)  # evita que se pierda la referencia

            boton = tk.Button(
                self.marco_tablero,
                image=imagen,
                text=f"x{len(pila)}",
                compound="bottom",
                font=FUENTE_CONTADOR,
                bg=COLOR_PILA,
                cursor="hand2",  # manito: más amigable que la cruz de flechas de "fleur"
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
        # quieto mientras dura el arrastre.
        if self._botones_pilas:
            self.marco_tablero.update_idletasks()
            ancho_celda = max(b.winfo_reqwidth() for b in self._botones_pilas) + 8
            alto_celda = max(b.winfo_reqheight() for b in self._botones_pilas) + 8
            filas_totales = (len(pilas) - 1) // ANCHO_FILA + 1
            for columna_config in range(ANCHO_FILA):
                self.marco_tablero.grid_columnconfigure(columna_config, minsize=ancho_celda)
            for fila_config in range(filas_totales):
                self.marco_tablero.grid_rowconfigure(fila_config, minsize=alto_celda)

        cartas_restantes = self.juego.mazo.quedan_cartas()
        texto_dificultad = "Fácil" if self.dificultad == Dificultad.FACIL else "Difícil"
        self.etiqueta_mazo_cantidad.config(text=f"x{cartas_restantes}")
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
        El resumen de la partida ahora vive en su propia ventana modal, en
        vez de mezclado adentro del scroll junto con el tablero: así el
        tablero queda completamente tapado y el cierre de la partida tiene
        su propio espacio, sin competir visualmente con las cartas de atrás.
        """
        ventana = tk.Toplevel(self.raiz)
        ventana.title("Partida terminada")
        ventana.configure(bg=COLOR_FONDO)
        ventana.resizable(False, False)
        ventana.transient(self.raiz)
        # si la cierran con la X, la salida segura es volver al menú
        ventana.protocol("WM_DELETE_WINDOW", lambda: self._cerrar_resumen_y(ventana, self._volver_al_menu))

        ancho, alto = 480, 380
        self.raiz.update_idletasks()
        x = self.raiz.winfo_rootx() + (self.raiz.winfo_width() - ancho) // 2
        y = self.raiz.winfo_rooty() + (self.raiz.winfo_height() - alto) // 2
        ventana.geometry(f"{ancho}x{alto}+{x}+{y}")

        tk.Label(
            ventana,
            text=(
                f"Se acabó el mazo. Quedaron {resumen['pilas_finales']} pila(s). "
                f"Puntaje: {resumen['puntaje']}"
            ),
            font=("Arial", 13, "bold"), bg=COLOR_FONDO, fg="white",
            wraplength=430, justify="center",
        ).pack(pady=(22, 6), padx=20)

        tk.Label(
            ventana,
            text=f"Jugadas realizadas: {resumen['movimientos']}   |   Duración: {duracion_texto}",
            font=("Arial", 10), bg=COLOR_FONDO, fg=COLOR_TEXTO_CLARO,
        ).pack(pady=(0, 8))

        tk.Label(
            ventana, text=interpretacion, font=("Arial", 11),
            bg=COLOR_FONDO, fg=COLOR_TEXTO_CLARO, wraplength=420, justify="center",
        ).pack(pady=(0, 16), padx=20)

        tk.Label(
            ventana, text="Nombre para guardar el puntaje:",
            bg=COLOR_FONDO, fg="white",
        ).pack()

        entrada_nombre = tk.Entry(ventana)
        entrada_nombre.pack(pady=4)

        marco_botones_finales = tk.Frame(ventana, bg=COLOR_FONDO)
        marco_botones_finales.pack(pady=(14, 4))

        tk.Button(
            marco_botones_finales, text="Guardar puntaje",
            command=lambda: self._guardar(resumen, entrada_nombre),
            bg=COLOR_ACENTO, fg="white",
        ).pack(side="left", padx=6)

        tk.Button(
            marco_botones_finales, text="Nueva partida (sin guardar)",
            command=lambda: self._cerrar_resumen_y(ventana, self._nueva_partida),
            bg=COLOR_ACENTO, fg="white",
        ).pack(side="left", padx=6)

        tk.Button(
            ventana, text="Volver al menú principal",
            command=lambda: self._cerrar_resumen_y(ventana, self._volver_al_menu),
            bg=COLOR_ACENTO, fg="white",
        ).pack(pady=(6, 16))

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

    def _nueva_partida(self) -> None:
        """Descarta la partida actual (se guardó o no) y arranca una nueva desde cero."""
        self.dificultad = elegir_dificultad(self.raiz)
        self.juego = Juego(dificultad=self.dificultad)
        self.boton_mazo.config(state="normal")
        self.boton_accion.config(text="Rendirse", state="normal")
        self._actualizar_pantalla()
        self._iniciar_reloj()
        self._mostrar_mensaje("Nueva partida. Hacé click en el mazo para empezar.", "info")

    def _volver_al_menu(self) -> None:
        """Descarta la partida actual (se haya guardado o no) y vuelve a la pantalla de menú."""
        if self._id_reloj is not None:
            self.raiz.after_cancel(self._id_reloj)
            self._id_reloj = None
        self.canvas_principal.unbind_all("<MouseWheel>")
        self.canvas_principal.unbind_all("<Button-4>")
        self.canvas_principal.unbind_all("<Button-5>")
        self.boton_accion.destroy()  # vive afuera de marco_juego: hay que sacarlo a mano
        self.marco_mazo.destroy()   # ídem: el mazo también vive afuera de marco_juego
        self.marco_juego.destroy()
        MenuPrincipal(self.raiz)


class MenuPrincipal:
    """
    Pantalla inicial. Se muestra primero, en la misma ventana (raiz) que
    después usa VentanaJuego: al apretar "Jugar" simplemente se destruye
    este marco y se arma el del juego encima.
    """

    def __init__(self, raiz: tk.Tk):
        self.raiz = raiz
        self.raiz.title("Solitario de las 50 cartas")
        self.raiz.configure(bg=COLOR_FONDO)
        _maximizar_ventana(self.raiz)

        self.marco = tk.Frame(raiz, bg=COLOR_FONDO, padx=50, pady=50)
        self.marco.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            self.marco, text="Solitario de las 50 cartas",
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
        ventana.geometry("560x420")

        tk.Label(
            ventana, text="🏆 Mejores puntajes", font=("Arial", 14, "bold"),
            bg=COLOR_FONDO, fg=COLOR_TEXTO_CLARO,
        ).pack(pady=(14, 8))

        historial = puntuacion.cargar_historial()

        if not historial:
            tk.Label(
                ventana, text="Todavía no hay partidas guardadas.",
                font=("Arial", 11), bg=COLOR_FONDO, fg="white",
            ).pack(pady=30)
        else:
            mejores = sorted(historial, key=lambda partida: partida["puntaje"], reverse=True)[:10]

            marco_lista = tk.Frame(ventana, bg=COLOR_FONDO)
            marco_lista.pack(padx=16, pady=4, fill="both", expand=True)

            texto = tk.Text(
                marco_lista, font=("Courier New", 9), bg=COLOR_PILA, fg=COLOR_TEXTO_PILA,
                wrap="none", height=15,
            )
            texto.pack(side="left", fill="both", expand=True)

            scroll_texto = tk.Scrollbar(marco_lista, command=texto.yview)
            scroll_texto.pack(side="right", fill="y")
            texto.configure(yscrollcommand=scroll_texto.set)

            encabezado = f"{'#':<3}{'Jugador':<14}{'Dificultad':<10}{'Puntaje':<9}{'Pilas':<7}{'Mov.':<6}Fecha"
            texto.insert("end", encabezado + "\n")
            texto.insert("end", "-" * len(encabezado) + "\n")
            for posicion, partida in enumerate(mejores, start=1):
                dificultad = partida.get("dificultad", "-")
                fila = (
                    f"{posicion:<3}{partida['jugador'][:12]:<14}{dificultad:<10}"
                    f"{partida['puntaje']:<9}{partida['pilas_finales']:<7}"
                    f"{partida['movimientos']:<6}{partida['fecha']}"
                )
                texto.insert("end", fila + "\n")
            texto.config(state="disabled")

        tk.Button(
            ventana, text="Cerrar", command=ventana.destroy,
            bg=COLOR_ACENTO, fg="white", font=("Arial", 10, "bold"),
        ).pack(pady=10)

    def _on_configuracion(self) -> None:
        messagebox.showinfo(
            "Configuración",
            "Todavía no hay opciones configurables. Próximamente.",
        )


def jugar_partida_grafica() -> None:
    raiz = tk.Tk()
    MenuPrincipal(raiz)
    raiz.mainloop()
