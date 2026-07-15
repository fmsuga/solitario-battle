# Solitario Battle → Godot → Android (Play Store)
### Plan de proyecto

## Resumen ejecutivo

Hoy el juego es una app de escritorio en Python/Tkinter, con la lógica del juego (`cartas.py`, `tablero.py`, `reglas.py`, `juego.py`, `puntuacion.py`) ya desacoplada de la interfaz. Eso es la mitad difícil del trabajo, ya hecha.

El objetivo es migrar a **Godot 4**, reescribiendo la lógica en GDScript y construyendo una interfaz táctil nueva, para exportar un **AAB firmado** que cumpla los requisitos de Google Play (target API 36) y publicarlo.

Se trabaja en **8 fases**, cada una con un resultado concreto y verificable antes de avanzar a la siguiente. Nunca se avanza de fase sin haber cerrado la anterior — la idea es ir construyendo sobre una base que ya sabemos que funciona, no acumular deuda técnica invisible.

---

## Fase 0 — Entorno y validación del toolchain

**Objetivo:** probar que "Godot → APK en un dispositivo real" funciona ANTES de tocar una sola línea del juego. Esto aísla los problemas de infraestructura (que son los que mataron el plan con Kivy) de los problemas de código.

Tareas:
1. Instalar Godot 4 (versión estable más reciente).
2. Configurar Android SDK/NDK y las plantillas de exportación de Godot (Editor Settings → Export → Android).
3. Crear un proyecto vacío con un solo botón que diga "Hola".
4. Generar un export preset de Android, firmar con un keystore de debug, e instalar el APK en un celular real o emulador.

**Criterio de "hecho":** ver el botón "Hola" andando en un Android real. Si esto no funciona, no seguimos — se soluciona acá, no más adelante con el proyecto completo encima.

---

## Fase 1 — Portar la lógica pura (sin gráficos)

**Objetivo:** trasladar las reglas del juego a GDScript, sin ninguna interfaz todavía.

Tareas:
1. Traducir `cartas.py` → `Carta`, `Palo`, `Mazo` como clases GDScript (`class_name`).
2. Traducir `tablero.py` → `Pila`, `Tablero`.
3. Traducir `reglas.py` → funciones de validación de jugada.
4. Traducir `juego.py` → clase `Juego` (estado, puntaje, cronómetro).
5. Traducir `puntuacion.py` → guardado de historial (en Godot esto se hace con `FileAccess` sobre `user://historial.json`, reemplaza a `recursos.py`).
6. Escribir tests equivalentes a los que ya tenés (`test_cartas.py`, `test_reglas.py`, `test_tablero.py`, `test_juego.py`, `test_puntuacion.py`) usando el framework **GUT** (Godot Unit Test). Tus tests actuales en Python son literalmente la especificación a cumplir.

**Criterio de "hecho":** todos los tests de GUT pasan en verde, replicando el comportamiento de los tests de Python. Cero UI todavía.

---

## Fase 2 — Tablero jugable mínimo (sin arte)

**Objetivo:** ver el juego funcionando en pantalla, con formas simples (rectángulos de color + texto), sin imágenes de cartas todavía.

Tareas:
1. Escena principal con grilla de "pilas" representadas como `ColorRect` + `Label`.
2. Botón de mazo que reparte una carta nueva.
3. Interacción simple (sin drag todavía): tocar pila A, tocar pila B, intentar jugada.
4. Mostrar mensajes de jugada válida/inválida.

**Criterio de "hecho":** se puede jugar una partida completa de punta a punta, tocando con el dedo en el emulador/celular, aunque se vea feo.

---

## Fase 3 — Arte real

**Objetivo:** reemplazar los placeholders por las imágenes reales de cartas.

Tareas:
1. Importar `cartas_img/` como recursos de Godot (PNG nativo, sin necesidad de Pillow).
2. Reemplazar el contador "x N" dibujado a mano en Python (`_dibujar_contador` en `imagenes_cartas.py`) por un `Label` superpuesto sobre el sprite — mucho más simple en Godot que redibujar el PNG en cada actualización.
3. Ajustar tamaños de sprite según resolución de pantalla.

**Criterio de "hecho":** el tablero se ve con las cartas reales y el contador de cada pila, con la misma información que tenía la versión de escritorio.

---

## Fase 4 — Interacción táctil real (drag & drop)

**Objetivo:** reemplazar el "tocar A, tocar B" de la Fase 2 por arrastrar-y-soltar con el dedo, tal como funcionaba con mouse en Tkinter.

Tareas:
1. Implementar arrastre con `_gui_input` / `InputEventScreenTouch` sobre los nodos de pila.
2. Detectar sobre qué pila se soltó (equivalente a `_soltada_sobre_pila` de `interfaz_grafica.py`).
3. Mantener la regla: solo se compara contra la pila que está exactamente a la izquierda (misma lógica de `_soltar_arrastre`).

**Criterio de "hecho":** arrastrar una pila sobre su vecina izquierda dispara la jugada, igual que en la versión de escritorio.

---

## Fase 5 — Menús y flujo completo

**Objetivo:** todo lo que rodea a la partida: selector de dificultad, resumen final, guardado de puntaje.

Tareas:
1. Pantalla de selección Fácil/Difícil (equivalente a `_mostrar_selector_dificultad`).
2. HUD con cronómetro y contador de movimientos.
3. Pantalla de resumen final con puntaje e interpretación del resultado (`puntuacion.interpretar_resultado`).
4. Guardado de nombre + puntaje en el historial local.
5. Pantalla de récords (top 10).

**Criterio de "hecho":** se puede abrir la app, elegir dificultad, jugar, terminar, guardar el puntaje, y verlo en la tabla de récords — sin pasar por el editor de Godot.

---

## Fase 6 — Pulido UX móvil

**Objetivo:** que se sienta como una app hecha para celular, no un puerto forzado.

Tareas:
1. Layout responsive (anchors/containers de Godot) para distintos tamaños de pantalla.
2. Tamaños táctiles cómodos (botones no tan chicos como para fallar el toque).
3. Manejo de rotación de pantalla (o forzar orientación fija, si se prefiere).
4. Ícono de la app y splash screen.

**Criterio de "hecho":** se prueba en al menos 2 dispositivos con tamaños de pantalla distintos y se ve/usa bien en ambos.

---

## Fase 7 — Build de release

**Objetivo:** generar el artefacto final que Google Play acepta.

Tareas:
1. Keystore de release (no el de debug de la Fase 0).
2. Export preset configurado con: `targetSdkVersion` 36, nombre de paquete definitivo (`com.tunombre.solitariobattle`), versionCode/versionName.
3. Generar el **AAB** (no APK suelto).
4. Probar el AAB (vía `bundletool` o subida a testing interno) en un dispositivo real.

**Criterio de "hecho":** un AAB firmado, instalable, con la versión final del juego.

---

## Fase 8 — Publicación en Play Store

**Objetivo:** que el juego esté disponible públicamente.

Tareas:
1. Cuenta de desarrollador en Play Console (USD 25, pago único).
2. Completar ficha: política de privacidad (URL pública), formulario de "Data safety", ícono 512×512, feature graphic 1024×500, capturas de pantalla.
3. Subir el AAB a **testing cerrado** (Google exige ~12 testers activos durante 14 días para cuentas nuevas antes de habilitar producción).
4. Pasar a producción.

**Criterio de "hecho":** la app aparece en Play Store bajo tu cuenta.

---

## Cómo trabajar esto con la IA, paso a paso

La idea es **no pedir "migrá todo el juego a Godot" en un solo mensaje**. Eso da un resultado grande, difícil de revisar, y difícil de debuggear si algo sale mal. En cambio, cada sesión de trabajo ataca **una tarea de una fase**, se verifica, y recién ahí se sigue.

Guardá este archivo y, al empezar cada sesión, usá el prompt de abajo como punto de partida (ajustando la fase/tarea puntual).

---

## 📋 Prompt maestro (copiar y pegar al arrancar una sesión de trabajo)

```
Estoy migrando un juego de cartas (Solitario Battle) de Python/Tkinter a
Godot 4, con el objetivo final de publicarlo en Google Play Store como AAB.

CONTEXTO DEL PROYECTO ORIGINAL:
El juego tiene la lógica separada de la interfaz:
- cartas.py: modela Carta, Palo, Mazo
- tablero.py: modela Pila, Tablero (estado de la mesa)
- reglas.py: valida y ejecuta jugadas (comparar pila izquierda contra la
  que está 2 lugares después, salteando la del medio, por valor o palo)
- juego.py: clase Juego que orquesta mazo + tablero + puntaje + cronómetro
- puntuacion.py: guarda historial de partidas en JSON
La interfaz gráfica original (Tkinter) NO se porta — se reconstruye desde
cero en Godot, pero la LÓGICA de estos módulos sí debe preservarse
exactamente (tengo tests en Python que documentan el comportamiento
esperado: test_cartas.py, test_reglas.py, test_tablero.py, test_juego.py,
test_puntuacion.py).

PLAN GENERAL (8 fases): 0) validar toolchain Godot→APK, 1) portar lógica
pura a GDScript con tests (GUT), 2) tablero jugable sin arte, 3) arte real,
4) drag & drop táctil, 5) menús y flujo completo, 6) pulido UX móvil,
7) build de release (AAB, API 36), 8) publicación en Play Console.

DÓNDE ESTAMOS HOY: Fase [NÚMERO] — [nombre de la fase]
TAREA PUNTUAL DE ESTA SESIÓN: [describir la tarea específica, chica]

CÓMO QUIERO TRABAJAR:
- Pasos pequeños y sólidos: no avances a la siguiente tarea sin que yo
  confirme que la actual funciona.
- Explicame las decisiones de diseño en GDScript cuando difieran de cómo
  estaba en Python (por qué, no solo qué).
- Al final de cada tarea, decime cómo verificar que funcionó (qué probar
  en el editor o en el dispositivo).
- Si una tarea depende de algo de una fase anterior que no cerramos, avisame
  en vez de asumir y seguir.

Adjunto el código Python original como referencia de la lógica a preservar.
```

---

### Notas para vos, no para la IA

- Fases 0 y 7 son las de mayor riesgo real (todo lo relacionado a build/toolchain). Si algo se traba, es ahí — y es exactamente donde Kivy nos hubiera dejado colgados.
- Fase 1 es la que más aprovecha que ya tenés tests: usalos como criterio objetivo de "está bien portado", no una opinión.
- No hace falta pasar por las 8 fases sin parar en una sola racha — el plan está pensado justamente para poder cortar en cualquier fase y retomar después sin perder el hilo.
