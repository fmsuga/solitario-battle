# Solitario de las 50 cartas (nombre pendiente 😄)

## Generar un .exe para compartir (Windows)

Esto empaqueta el juego en un único archivo `.exe` que corre en cualquier
Windows sin necesitar Python instalado. **Tenés que correr esto en una
máquina Windows** (PyInstaller no genera un `.exe` de Windows corriendo
desde Linux o Mac — arma un ejecutable para el sistema en el que corre).

1. Instalá las dependencias necesarias:
   ```
   python -m pip install pillow pyinstaller
   ```

2. Parado en la carpeta `solitario_50` (donde está `main_grafico.py`), corré:
   ```
   pyinstaller --onefile --windowed --name SolitarioDeLasCincuentaCartas --paths src --add-data "assets/cartas_img;assets/cartas_img" main_grafico.py
   ```
   (En Windows el separador de `--add-data` es `;`. En Mac/Linux sería `:`)

3. El ejecutable queda en `dist/SolitarioDeLasCincuentaCartas.exe`. Ese
   único archivo es el que le pasás a tus amigos — no necesitan nada
   más instalado.

4. El historial de puntajes (`historial.json`) se crea al lado del
   `.exe` la primera vez que alguien guarda un puntaje, así que cada
   persona arranca con su propio historial vacío.

**Notas:**
- `--windowed` evita que se abra una consola negra atrás de la ventana del juego.
- Podés cambiar `--name` por el nombre que quieras para el archivo final.
- Si querés regenerar el `.exe` después de algún cambio de código, borrá
  antes las carpetas `build/` y `dist/` y el archivo `.spec` que se
  generan, y volvé a correr el comando del paso 2.

## Subir el proyecto a GitHub

Esto te resuelve dos cosas: tener control de versiones (nunca más una
mezcla de archivos viejos/nuevos como nos pasó una vez) y compilar el
`.exe` automáticamente en la nube, sin correr `pyinstaller` a mano.

**1. Creá el repositorio en GitHub** (en github.com, botón "New repository").
No marques "Initialize with README" (ya tenés uno).

**2. Desde tu carpeta `solitario_50`, en la terminal:**
```
git init
git add .
git commit -m "Primera versión del proyecto"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/TU_REPO.git
git push -u origin main
```

**3. El `.exe` se compila solo.** En cuanto hagas ese primer `push`, se
dispara el workflow de `.github/workflows/build.yml` en los servidores
de GitHub (usando una máquina Windows en la nube). Para bajarlo:
- Entrá a la pestaña **Actions** de tu repo en GitHub.
- Abrí la ejecución más reciente (el nombre del commit).
- Al final de la página vas a ver un archivo adjunto llamado
  `SolitarioDeLasCincuentaCartas` — ese es tu `.exe`, comprimido en zip.

**De ahí en adelante**, cada vez que quieras agregar una mejora:
```
git add .
git commit -m "Descripción de lo que cambiaste"
git push
```
y en un par de minutos tenés un `.exe` nuevo esperándote en Actions,
sin que ni vos ni yo tengamos que compilarlo a mano.

**Para nuestras próximas sesiones**: si me pasás la URL de un archivo
puntual de tu repo (botón "Raw" en GitHub), puedo leerlo directo sin
que me lo subas — nos ahorra tiempo cuando quiero ver el estado actual
de algo puntual antes de tocarlo.

## Cómo jugar

Hay dos formas de jugar, y las dos usan exactamente la misma lógica
(`cartas.py`, `tablero.py`, `reglas.py`, `juego.py`) — esa es la ventaja
de haberlas separado bien desde el principio.

**Versión gráfica (recomendada):**
```
python3 main_grafico.py
```
Requiere el paquete de sistema `python3-tk` (en Ubuntu/Debian:
`sudo apt install python3-tk`) y la librería Pillow para mostrar las
imágenes de las cartas (`pip install pillow --break-system-packages`).
Se abre una ventana con las cartas reales de la baraja; apretás
"Repartir carta" para sacar la siguiente, y hacés click en la pila que
creas que es el lado izquierdo de una jugada válida.

**Versión por consola:**
```
python3 main.py
```
Igual mecánica, pero tipeando el número de la pila en vez de clickear.

## Estructura del proyecto

```
cartas.py             -> Carta, Palo, Mazo (los datos base)
tablero.py             -> Pila, Tablero (el estado de la mesa)
reglas.py               -> lógica pura: valida si UNA jugada propuesta es correcta
juego.py                 -> orquesta Mazo + Tablero + reglas
interfaz_consola.py       -> versión por consola
interfaz_grafica.py        -> versión gráfica (Tkinter)
imagenes_cartas.py           -> carga las imágenes de assets/cartas_img/ para la interfaz gráfica
recursos.py                    -> resuelve rutas (imágenes, historial) tanto normal como empaquetado en .exe
puntuacion.py                    -> historial en JSON + interpretación del resultado
main.py                            -> arranca la versión consola
main_grafico.py                     -> arranca la versión gráfica

assets/cartas_img/  -> las 48 imágenes de cartas + el dorso, recortadas de tu baraja
```

La idea de separarlo así: cada archivo tiene UNA sola responsabilidad.
Si mañana cambiás cómo se ve el juego (por ejemplo, a una interfaz web),
solo tocás `interfaz_consola.py` (o lo reemplazás por otro archivo).
El resto no se entera del cambio. Eso es lo que te va a evitar reescribir
todo de cero en el futuro.

## Orden sugerido para ir completando los TODO

1. **`cartas.py`**: primero esto. Es lo más chico y te sirve para practicar
   clases básicas, listas y `for`.
2. **`tablero.py`**: depende de `cartas.py`. Practicás manejo de listas
   dentro de una clase.
3. **`reglas.py`**: acá va la parte más "pensada" del juego. Te recomiendo
   armar unas pruebas simples (aunque sea con `print`) antes de conectarlo
   con `juego.py`.
4. **`juego.py`**: junta todo. Practicás cómo una clase puede "usar" a otras
   clases sin mezclarse con ellas.
5. **`interfaz_consola.py`** y **`main.py`**: recién acá lo hacés jugable.
6. **`puntuacion.py`**: dejalo para el final, cuando el juego ya funcione.

## Reglas ya confirmadas (importante para cuando programes)

- **La fila es solo visual.** El juego lógicamente trabaja sobre UNA sola
  secuencia continua de pilas (`tablero.pilas`, una lista plana). El
  "ancho de hombros" (`ANCHO_FILA` en `interfaz_consola.py`, por defecto 8)
  únicamente corta esa secuencia en filas a la hora de imprimir en pantalla.
  Las reglas (`reglas.py`) nunca deberían enterarse de en qué fila está cada
  pila — si en algún momento sentís que necesitás esa información ahí,
  probablemente sea una señal de que conviene repensar ese pedacito.
- **Efecto cadena confirmado:** cada vez que se fusionan dos pilas, hay que
  volver a comparar las nuevas últimas 3 pilas de la secuencia, y así en
  bucle, hasta que no haya más coincidencias. Por eso `reglas.py` tiene
  `procesar_fusiones`, que hace ese bucle completo (no una sola fusión).
- **Fin del juego confirmado:** termina cuando no quedan cartas en la mano
  (mazo vacío). Como las fusiones en cadena se resuelven apenas se
  despliega cada carta, no hace falta un chequeo extra al final.

## Cuando te trabes

Contame en qué archivo estás, qué intentaste, y qué error te tira (si tira
alguno) o qué resultado esperabas vs. qué obtuviste. Con eso te ayudo mucho
más rápido que si me pasás solo "no me funciona".
