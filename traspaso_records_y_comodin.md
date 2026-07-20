# Traspaso completo — Análisis del juego, Comodín Táctico y Pantalla de Récords

Documento para el agente que continúa el trabajo de código. Contiene el
análisis estadístico completo generado (con datos exactos, no
aproximados), las decisiones de diseño ya cerradas, lo que se probó y se
**descartó explícitamente** (para no volver a proponerlo), y las
instrucciones de implementación de la Pantalla de Récords listas para
aplicar.

Todo el análisis se hizo en un laboratorio Python **fuera del repo del
juego** (motor de reglas reimplementado en Python puro, sin tocar Godot).
No están versionados en GitHub — si hace falta reproducir algo, hay que
reconstruir los scripts con la lógica descripta acá.

---

## 1. Estado del proyecto

- Repo: `fmsuga/solitario-battle`. Trabajar siempre contra un clon fresco
  de `main` (el usuario puede seguir tocando el proyecto en paralelo —
  re-clonar antes de cada sesión de trabajo, no asumir que este estado
  sigue vigente).
- **Último commit al momento de este traspaso:** `8d77b20` — "Nuevo
  sistema en selector de dificultad, mejores visuales en header y en
  terminar partida". Commits inmediatos anteriores, mismo lote de pulido
  estético (no tocan lógica ni la infraestructura de Récords): `1a6a3d2`
  "Ajustes visuales en card selector dificultad, en header de partida y
  en botón de terminarla", `25203ce` "mejoras estéticas en selector de
  dificultad".
- Ese lote de 3 commits tocó: `godot/scenes/selector_dificultad.tscn`,
  `godot/scenes/tablero.tscn`, `godot/scenes/pila_visual.tscn`,
  `godot/scripts/selector_dificultad.gd`, `godot/scripts/pila_visual.gd`,
  `godot/scripts/tablero_visual.gd` (+38/-13 líneas — solo visual/HUD,
  no afecta la función de guardado de récord ni la lógica de juego), y
  sumó 5 estilos nuevos a `godot/assets/estilos/`
  (`caja_dificultad_dificil.tres`, `caja_dificultad_facil.tres`,
  `chip_tiempo.tres`, `medallon_anillo.tres`, `panel_encabezado.tres`).
- **Confirmado, sigue vigente para lo que sigue de este documento:**
  `configuracion.gd`, `puntuacion.gd` y `menu_principal.gd` NO cambiaron
  en este lote — toda la sección 5 (Récords) sigue apuntando a los
  nombres de función correctos. En particular, el guardado de récord en
  pantalla de fin de partida sigue en
  `tablero_visual.gd::_al_tocar_guardar_record()` (línea 220 al momento
  de este traspaso), conectado al botón `$Margen/Columna/Finalizar`
  (`boton_finalizar`).
- Fase 5 (menús y flujo completo) casi cerrada: ya existen
  `ajustes_overlay.tscn/.gd`, `configuracion.gd` (Ajustes), menú de pausa
  y pantalla de fin de partida ya rediseñados con el design system de
  `godot/assets/estilos/*.tres`, y ahora también selector de dificultad y
  header pulidos.
- **Pendiente de Fase 5:** la Pantalla de Récords (instrucciones abajo,
  sección 5) y la Pantalla de "Mi progreso" (no cubierta en este
  documento, usa las mismas funciones de `puntuacion.gd` que Récords).
- Antes de tocar código: mostrar el diff propuesto y esperar OK explícito
  del usuario antes de aplicar.
- En `menu_principal.tscn` ya existen (sin cablear en `menu_principal.gd`)
  los nodos `$Centro/Columna/Menu/Tarjeta/Botones/Records` y
  `.../Progreso` — están en la escena, deshabilitados, esperando que se
  conecten. Sin cambios en este lote de commits.

---

## 2. Hallazgo técnico central (bajo qué supuesto se hizo todo el análisis)

**El momento de repartir una carta no afecta el conjunto de resultados
finales alcanzables.** Repartir solo agrega una pila nueva al final del
array de pilas; nunca modifica pilas ya existentes. Por lo tanto,
cualquier partida jugada intercalando "repartir → jugar → repartir →
jugar" tiene exactamente el mismo abanico de resultados finales posibles
que repartir el mazo completo de una vez y después aplicar la misma
secuencia de fusiones. Esto es lo que permite estudiar el juego como "una
mano fija de N cartas + una búsqueda del mejor orden de fusiones",
ignorando el timing del reparto.

**Mecánica exacta simulada** (replicando `tablero.gd`/`reglas.gd`): dado
un array de pilas (representadas solo por su carta tope, que es lo único
relevante para jugadas futuras), una jugada en el índice `i` es válida si
`tope(pila[i])` coincide en **valor o palo** con `tope(pila[i+2])`
(salteando la del medio). Al ejecutarla, la pila del medio (`i+1`) se
absorbe en la de la izquierda (`i`) y se retira del array — el nuevo tope
de la pila izquierda pasa a ser el tope de lo que era la del medio. La
pila derecha (`i+2`) queda intacta, solo se corre un lugar.

Mazo: español de 48 cartas (Difícil, valores 1-12 x 4 palos) o 40
(Fácil, se excluyen 8 y 9).

---

## 3. Análisis estadístico completo

### 3.1 Orden de resolución de jugadas: "viejo primero" vs. "nuevo primero"

**Pregunta original del usuario:** ¿conviene resolver primero las
coincidencias más viejas (más a la izquierda) o las más nuevas (recién
formadas, más a la derecha)?

**Metodología:** cuatro estrategias de juego automatizado, jugadas hasta
que no queda ninguna jugada válida:
- `viejo_primero`: siempre resuelve la coincidencia disponible más a la
  izquierda.
- `nuevo_primero`: siempre resuelve la más a la derecha.
- `aleatorio`: elige al azar entre las jugadas válidas disponibles en
  cada paso (línea de base "sin criterio").
- `lookahead_1`: de las jugadas disponibles, elige la que deja más
  jugadas nuevas habilitadas inmediatamente después (heurística golosa a
  un paso, sin backtracking).

**A. Validación contra el óptimo matemático real** (solver exhaustivo con
memoización y poda — óptimo garantizado, no aproximado — en manos de 8,
10, 12, 14 y 16 cartas, 60 repeticiones por tamaño, n=300, 300/300
resueltas de forma exhaustiva):

| Estrategia | % de veces que iguala al óptimo real | Gap promedio sobre el óptimo (pilas de más) |
|---|---|---|
| **viejo primero** | **99.33%** | **0.017** |
| lookahead-1 | 99.33% | 0.017 |
| nuevo primero | 34.00% | 2.007 |

⭐ **Destacado / mostrable:** "jugar siempre la coincidencia más vieja
te deja a un promedio de 0.017 pilas del juego matemáticamente perfecto"
— dato fuerte, sorprendente y fácil de comunicar.

**B. Escala completa (mazo real de 48 y 40 cartas), 1500 mazos
simulados por dificultad, estadística descriptiva de pilas finales:**

DIFÍCIL (48 cartas):

| Estrategia | Media | Mediana | Desvío | Mín | Máx |
|---|---|---|---|---|---|
| viejo primero | 18.786 | 19.0 | 8.012 | 2 | 41 |
| lookahead-1 | 18.854 | 19.0 | 7.984 | 2 | 41 |
| aleatorio | 29.738 | 30.0 | 4.744 | 14 | 43 |
| nuevo primero | 34.299 | 34.0 | 3.087 | 24 | 43 |

FÁCIL (40 cartas):

| Estrategia | Media | Mediana | Desvío | Mín | Máx |
|---|---|---|---|---|---|
| viejo primero | 14.720 | 14.0 | 6.978 | 2 | 35 |
| lookahead-1 | 14.788 | 14.0 | 6.944 | 2 | 35 |
| aleatorio | 23.901 | 24.0 | 4.451 | 8 | 36 |
| nuevo primero | 28.260 | 28.0 | 2.817 | 18 | 37 |

**C. Comparación pareada** (mismo mazo/semilla para ambas estrategias,
n=1500, Difícil):

- Viejo-primero da **mejor o igual resultado en 99.8%** de los mazos
  (1497/1500 mejor, 3/1500 empate, **0/1500** casos donde nuevo-primero
  gana).
- Diferencia media: **15.51 pilas** a favor de viejo-primero. Mediana:
  15.0.

⭐ **Destacado / mostrable:** "nunca conviene jugar lo más nuevo primero
— en 1500 partidas comparadas, jugar lo más viejo primero nunca perdió".

**Conclusión operativa:** la regla "resolvé siempre la coincidencia más
vieja disponible" es, en la práctica, indistinguible de jugar perfecto.
No hace falta ninguna heurística más sofisticada (el lookahead-1 no
mejora nada relevante sobre la regla simple).

---

### 3.2 Probabilidad del "juego ideal"

**Pregunta del usuario:** ¿qué tan seguido se logra el resultado ideal
(todo fusionado en una pila + una carta suelta = 2 pilas finales), y qué
tan seguido se llega a 3 o 4 pilas, jugando casi-óptimo?

**Metodología:** 20.000 mazos simulados por dificultad, jugados con
`viejo_primero` (casi-óptimo, ver 3.1).

| Resultado final | Difícil (48 cartas) | Fácil (40 cartas) |
|---|---|---|
| **2 pilas (ideal)** | **0.18%** (~1 cada 570 partidas) | **0.44%** (~1 cada 227) |
| ≤3 pilas | 0.91% | 2.26% |
| ≤4 pilas | 2.29% | 4.96% |

⭐ **Destacado / mostrable en la UI:** estos porcentajes son excelentes
candidatos para mostrarle al jugador contexto real de qué tan
extraordinario fue su resultado ("solo el 0.18% de las partidas, incluso
jugadas casi perfectas, terminan así"). Útil en pantalla de fin de
partida o en "Mi progreso".

**Nota de consistencia:** en una corrida de control distinta (3000
mazos, parte del estudio de comodines, sección 3.4) salió 0.27% para
2 pilas — misma magnitud, diferencia atribuible al tamaño de muestra
menor. Usar el dato de 20.000 mazos (0.18%) como cifra de referencia
oficial por tener más muestra.

---

### 3.3 Suerte vs. habilidad — descomposición de varianza (ANOVA de dos vías)

**Pregunta del usuario:** ¿cuánto del resultado depende del mazo que te
tocó (suerte) y cuánto de tu criterio de juego (habilidad)?

**Metodología:** ANOVA de dos vías. Filas = mazos (n=3000 por
dificultad), columnas = nivel de habilidad (mismo mazo evaluado con
distintas estrategias). Se descompone la varianza total del resultado
(pilas finales) en: varianza entre mazos (suerte), varianza entre niveles
de habilidad (habilidad), y residual (interacción — algunos mazos
premian más la habilidad que otros).

**A. Rango de habilidad humano realista** (de "sin criterio, elige al
azar" a "casi perfecto" — el rango en el que se mueve un jugador real;
**esta es la cifra de referencia recomendada**, no la de 3B):

| | Difícil | Fácil |
|---|---|---|
| Suerte (mazo) | **45.6%** | **48.4%** |
| Habilidad (criterio de orden) | **40.7%** | **37.8%** |
| Residual / interacción | 13.7% | 13.8% |

⭐ **Destacado / mostrable:** "el resultado de una partida es
aproximadamente mitad suerte, mitad habilidad (44-48% suerte, 38-41%
habilidad)". Bueno para justificar por qué el puntaje crudo no alcanza
como única métrica de mérito (ver 3.5, métrica de eficiencia).

**B. Rango completo (incluye "nuevo primero" como anti-habilidad
extrema) — dato secundario, NO usar como cifra principal** porque casi
ningún jugador humano juega deliberadamente al revés:

| | Difícil | Fácil |
|---|---|---|
| Suerte | 28.3% | 29.8% |
| Habilidad | 56.7% | 54.8% |
| Residual | 15.0% | 15.4% |

Se incluye solo por completitud metodológica — el dato bueno para
comunicar y para diseño es el de 3.3-A.

---

### 3.4 Estudio de variantes de Comodín

Todo lo de esta sección alimentó la decisión final (sección 4). Se deja
documentado completo, incluyendo lo descartado, para que quede registro
de por qué no se sigue por esas líneas.

**A. Comodín repartido en el mazo, en posición aleatoria — DESCARTADO
en general a favor del Comodín Táctico (sección 4). Detalle:**

Cantidad de comodines agregados al mazo, jugado con `viejo_primero`
adaptado (un comodín en el tope matchea con cualquier cosa), 3000 mazos
por punto, Difícil:

| Comodines | Pilas finales (media) | P(ideal ≤2 pilas) | P(≤4 pilas) |
|---|---|---|---|
| 0 (control) | 18.79 | 0.27% | 2.60% |
| 1 | 11.28 | 4.83% | 17.93% |
| 2 | 8.64 | 8.63% | 28.70% |
| 3 | 7.18 | 12.97% | 37.57% |
| 4 | 6.13 | 16.43% | 45.70% |

**B. Variantes de "un solo uso" para el comodín de mazo:**

| Variante | Pilas finales (media) | P(ideal) |
|---|---|---|
| Persistente (infinito, tabla A con 1 comodín) | 11.28 | 4.83% |
| **Un uso, queda MUERTO en el tablero tras usarse** | **20.70** ⚠️ | **0.00%** |
| Un uso, se AUTOELIMINA del tablero al usarse | 18.04 | 0.33% |

⚠️ **DESCARTADO — hallazgo importante:** la variante "un uso, queda
muerto" es **peor que no tener comodín en absoluto** (20.70 vs. 18.79 de
control). Una vez gastado, esa carta no vuelve a matchear con nada (ni
valor ni palo) — es peor que una carta común, que al menos tiene
probabilidad de coincidir por azar, y además ocupa una pila extra en el
mazo (49 cartas en vez de 48). **No reimplementar esta variante.**

**C. Comodín de mazo con "N usos" (dial ajustable), 2000 mazos por
punto, Difícil:**

| Usos | Pilas finales (media) | P(ideal) | P(≤4 pilas) |
|---|---|---|---|
| 1 | 18.28 | 0.35% | 2.75% |
| 2 | 16.99 | 0.60% | 4.15% |
| 3 | 15.91 | 0.70% | 5.40% |
| 4 | 14.95 | 1.10% | 6.40% |
| 5 | 14.12 | 1.55% | 8.10% |
| 8 | 12.60 | 3.20% | 11.85% |
| ∞ (persistente) | 11.38 | 5.00% | 18.15% |

Dial funcional y probado, pero **queda descartado como línea principal**
a favor del Comodín Táctico — se documenta por si en el futuro se quiere
un comodín de mazo pasivo como variante de dificultad adicional (no
decidido, no pedido).

**D. Comodín Táctico (jugador elige cuándo y dónde usarlo) — GANADOR,
ver sección 4 para el diseño final:**

*D.1 — Mejor uso posible, en cualquier momento de la partida* (n=300
mazos Difícil; se simula la partida completa jugada con `viejo_primero`,
y en cada paso se prueba forzar una fusión extra en cada posición
posible del tablero en ese momento, tomando el mejor resultado hallado
en cualquier combinación de momento+posición):

- Mejora media: **8.18 pilas** (el lever más fuerte de todos los
  probados — más que el comodín de mazo persistente).
- Mejora mediana: 8.0.
- Mejora máxima observada: 19 pilas.
- **0% de los mazos sin ninguna mejora** (ayuda siempre, en el 100% de
  los casos probados).

*D.2 — ¿Cuándo conviene usarlo?* (n=200 mazos, se registra en qué % de
la partida ya jugada está el mejor momento de uso):

- Media: 23.7% de la partida transcurrida.
- **Mediana: 0.0%** (el mejor momento, la mitad de las veces, es
  literalmente lo antes posible).
- 71% de los casos: el mejor momento cae en el **primer tercio** de la
  partida.
- 23% de los casos: cae en el último tercio.

⭐ **Destacado / mostrable — refuta una intuición común:** "guardar el
comodín para el final" suele ser subóptimo. Forzar una fusión temprano
le da más tiempo al resto del tablero para armar una cadena larga a
partir de eso. Esto es un buen dato para comunicar en el juego (tooltip,
tutorial) y también un diferenciador de habilidad real entre jugadores.

*D.3 — Variante restringida "solo usable cuando el tablero está trabado
(sin mazo, sin jugadas posibles)"* — **evaluada y DESCARTADA por decisión
explícita del usuario** (ver sección 4, el usuario pidió expresamente
mantenerlo usable en cualquier momento):

- Mejora media: 6.35 pilas (22% menos que la versión sin restricción).
- Mejora mediana: 6.0.
- 100% de los mazos se benefician igual.
- Se documenta el número por si en algún momento se reconsidera, pero
  **la decisión vigente es la versión sin restricción de momento** (D.1).

---

### 3.5 Implicancia para el diseño de puntaje/Récords (no implementado — línea futura)

Dado 3.3 (el resultado es ~45% suerte), el puntaje crudo (pilas finales,
o el `calcular_puntaje()` actual) premia mayormente el mazo que te tocó,
no el mérito del jugador. Una métrica de **"eficiencia"** —resultado real
del jugador comparado contra el óptimo estimado para su mazo específico—
mediría mérito real, filtrando el componente de suerte. **No está
implementada ni diseñada en detalle**: el solver que calcula el óptimo
es Python/offline y no es directamente portable a Godot en tiempo real
para mazos de 40-48 cartas (el espacio de estados es demasiado grande
para garantizar exhaustividad rápido — sí se resuelve rápido y exacto
hasta ~16-20 cartas). Queda pendiente de diseño: cómo aproximar un
"óptimo estimado" utilizable en el cliente sin correr un solver pesado
(candidatos no explorados todavía: tabla precalculada de percentiles,
heurística `viejo_primero` como proxy de referencia dado que se probó
0.017 de gap promedio contra el óptimo real).

---

## 4. Comodín Táctico — diseño final decidido

**Decisión del usuario:** se implementa el Comodín Táctico, **usable en
cualquier momento de la partida** (no restringido a cuando el tablero
está trabado — esa variante se evaluó, sección 3.4-D.3, y se descartó
explícitamente).

### Cómo funciona mecánicamente (aclarado para evitar ambigüedad de
implementación)

- **No es una carta que se inserta en el mazo ni una carta que se
  vuelve comodín para siempre.** Es una acción/recurso que el jugador
  gasta. El jugador elige una jugada de las que el tablero permite
  estructuralmente (salteando una pila, exactamente la misma mecánica de
  siempre: posición `i` compara contra `i+2`) y el comodín hace que esa
  jugada se ejecute **aunque las cartas no coincidan realmente en valor
  ni palo**.
- Al activarse, se ejecuta como cualquier fusión normal: la pila del
  medio (`i+1`) se absorbe en la de la izquierda (`i`) y se retira del
  tablero, igual que una jugada válida común (ver `tablero.gd::fusionar`
  / `reglas.gd::ejecutar_jugada`, no hace falta un camino de código
  nuevo para la fusión en sí — solo para saltear la validación).
- **No deja rastro:** después de usarlo no queda ninguna "carta comodín"
  visible en el tablero. El nuevo tope de la pila resultante es la carta
  real que ya estaba en la pila del medio. No hace falta ningún
  mecanismo de "asumir palo y número" — nunca fue un objeto físico en el
  tablero, así que no hay identidad que resolver.
- **Un solo uso por partida** (así se simuló en todos los estudios de la
  sección 3.4-D; no se probó ni se decidió una variante con más de un
  uso — si se quiere permitir más de uno, hay que simularlo antes de
  implementarlo, no está validado).
- Usable en cualquier momento de la partida, sin restricción de estado
  del tablero (decisión final, ver arriba).

### Pendiente de decidir/implementar (no cerrado en el diseño)

1. **Arte de la carta comodín:** no existe hoy en
   `godot/assets/cartas_img/` (o su ruta equivalente) — hay que diseñarla
   o conseguirla antes de poder mostrarla en la UI.
2. **Trigger de UI:** cómo y dónde se activa durante la partida (botón
   dedicado en el HUD, gesto, etc.) — no especificado.
3. **Impacto en puntaje/récord:** ¿usar el comodín resta puntos, es
   neutro, o simplemente se registra como dato adicional en la partida
   guardada (`usó_comodín: true/false`)? No decidido. Si se decide
   registrarlo, es un campo natural a sumar al resumen de
   `juego.gd::obtener_resumen()` y, eventualmente, a la tabla de
   Supabase (requiere alterar el esquema, ver sección 5.1).
4. Implementación en `reglas.gd`/`juego.gd`: falta escribir la función
   equivalente a `intentar_jugada` pero que salte la validación de
   coincidencia (ej. `forzar_jugada(indice_izquierda)`), consumible una
   sola vez por partida (flag booleano en el estado de `Juego`).

---

## 5. Pantalla de Récords — diseño cerrado, instrucciones de implementación

### 5.1 Decisiones de diseño (cerradas)

- **Una sola tabla, mezclada (no separada por pestaña de dificultad).**
  Válido porque `juego.gd::calcular_puntaje()` ya aplica un multiplicador
  **1.5x en Difícil vs. Fácil** (ver línea 78 de `juego.gd`,
  `var multiplicador := 1.5 if dificultad == Carta.Dificultad.DIFICIL
  else 1.0`), así que los puntajes ya son comparables entre dificultades
  sin trabajo adicional. No hay que tocar la fórmula de puntaje para
  esto.
- **Columnas de cada fila:** `#, Jugador, Puntaje, Dificultad (chip
  visual), Pilas finales, Movimientos, Duración, Fecha`.
- **Dos pestañas: 🌍 Mundial / 📱 Mis récords.** Mundial = todos los
  jugadores vía Supabase. Mis récords = filtrado por `device_id` propio
  (ambos usan la misma tabla remota, distinto filtro).
- **Fallback automático a local:** si la consulta a Supabase falla (sin
  conexión, error HTTP, timeout), la pantalla debe caer automáticamente a
  mostrar el historial local (`Puntuacion.cargar_historial()` +
  `Puntuacion.ordenar_records()`), con un aviso visible tipo *"Sin
  conexión — mostrando récords locales"*.
- **Al guardar un récord** (el botón que ya existe hoy en la pantalla de
  fin de partida, en `tablero_visual.gd`): se sigue guardando local como
  hoy (no tocar esa parte), y **además** se debe intentar publicar a
  Supabase en paralelo — si el envío falla, no debe romper ni bloquear
  nada (el guardado local ya garantiza persistencia).
- **Resaltar visualmente la fila del jugador** si el resultado que
  acaba de guardar aparece en el top visible de la tabla (usar el estilo
  de borde dorado ya definido en `assets/estilos/panel_tarjeta.tres` o
  similar, para consistencia visual).

### 5.2 Infraestructura ya existente para reutilizar (NO reinventar)

**`supabase_schema.sql`** (raíz del repo — ya escrito, ya pensado para
vivir expuesto en el cliente con Row Level Security, sin secretos):

```sql
create table if not exists public.leaderboard_entries (
    id uuid primary key default gen_random_uuid(),
    device_id uuid not null,
    player_name varchar(24) not null check (char_length(trim(player_name)) between 1 and 24),
    difficulty varchar(10) not null check (difficulty in ('facil', 'dificil')),
    score integer not null check (score >= 0),
    piles_finales smallint not null check (piles_finales between 1 and 48),
    moves smallint not null check (moves >= 0),
    duration_seconds integer not null check (duration_seconds >= 0),
    played_at timestamptz not null default now(),
    created_at timestamptz not null default now()
);
-- índices para orden global y personal ya creados
-- RLS: SELECT público (anon+authenticated), INSERT público con checks
-- básicos, sin UPDATE/DELETE desde el cliente.
```

**`src/records_online.py`** (versión Python vieja — **de referencia
exclusiva para portar a GDScript, no ejecutar**): implementa
`obtener_id_dispositivo`, `enviar_record`, `obtener_records_globales`,
`obtener_records_personales`, todo vía REST directo (sin SDK) contra:

- `SUPABASE_URL = "https://tqjpybhwkyrkgrapoxcr.supabase.co"`
- `SUPABASE_PUBLISHABLE_KEY = "sb_publishable_-Y5Qf1qNZ7ix4_H3opfvzA_v_uuUTXs"`
  (clave pública, diseñada para vivir en el cliente — no es un secreto
  a proteger).
- Tabla: `leaderboard_entries`.
- Header requerido en cada request: `apikey: <PUBLISHABLE_KEY>`,
  `Content-Type: application/json`. En POST además `Prefer:
  return=minimal`.
- GET con querystring PostgREST: `select=...&order=score.desc,
  duration_seconds.asc,moves.asc&limit=N` (mundial), agregando
  `device_id=eq.<uuid>` para personal.
- La función `_normalizar_record` traduce nombres de columna en inglés
  (`player_name`, `difficulty`, `score`, `piles_finales`, `moves`,
  `duration_seconds`, `played_at`) al español que usa la UI (`jugador`,
  `dificultad`, `puntaje`, `pilas_finales`, `movimientos`,
  `duracion_segundos`, `fecha`) — replicar esta traducción en GDScript.

**`godot/scripts/puntuacion.gd`** — ya tiene todo lo necesario para la
parte local, no tocar para lo básico:
`guardar_puntaje`, `cargar_historial`, `ordenar_records`,
`mejor_puntaje`, `analizar_progreso`, `interpretar_resultado`,
`formatear_duracion`.

**`godot/scripts/configuracion.gd`** — ya usa `user://perfil_jugador.json`
(hoy solo guarda `volumen`). **No existe todavía `device_id` en Godot.**

### 5.3 Archivos a crear/modificar (lista exacta de trabajo)

1. **`godot/scripts/configuracion.gd`** — agregar función nueva,
   siguiendo el mismo patrón que `cargar_volumen`/`guardar_volumen`:
   ```gdscript
   static func obtener_device_id() -> String:
       var perfil := _cargar_perfil()
       if perfil.has("device_id"):
           return perfil["device_id"]
       var nuevo_id := _generar_uuid_v4()
       perfil["device_id"] = nuevo_id
       var archivo := FileAccess.open(ARCHIVO_PERFIL, FileAccess.WRITE)
       if archivo != null:
           archivo.store_string(JSON.stringify(perfil))
       return nuevo_id
   ```
   (Godot 4 no tiene generador de UUID nativo — hay que escribir
   `_generar_uuid_v4()` a mano, ej. con `randi()`/`randf()` armando los
   bytes con la versión/variant bits correctos, o usar una librería
   mínima. Revisar alternativas antes de escribir una implementación
   propia poco robusta.) Esto reutiliza `ARCHIVO_PERFIL` y `_cargar_perfil`
   que ya existen en el archivo — no crear un archivo nuevo de perfil.

2. **`godot/scripts/records_online.gd`** (nuevo) — puerto de
   `records_online.py` usando el nodo `HTTPRequest` de Godot. Debe
   exponer equivalentes de `enviar_record`, `obtener_records_globales`,
   `obtener_records_personales`, con la misma URL/key/tabla/columnas
   documentadas en 5.2. Como `HTTPRequest` en Godot es asíncrono (señal
   `request_completed`), la API en GDScript no puede tener la misma forma
   sincrónica que en Python — diseñar con señales o `await` sobre la
   señal de completado.

3. **`godot/scenes/records.tscn`** + **`godot/scripts/records_visual.gd`**
   (nuevos) — la pantalla en sí: dos pestañas (Mundial/Mis récords),
   tabla con las columnas de 5.1, fallback local si Supabase falla,
   resaltado de la fila propia. Reusar los estilos de
   `godot/assets/estilos/*.tres` (panel_tarjeta, botones, chip_estadistica)
   para consistencia visual con pausa/fin de partida ya rediseñados.

4. **`godot/scripts/menu_principal.gd`** — cablear el botón ya presente
   en la escena (`$Centro/Columna/Menu/Tarjeta/Botones/Records`, hoy sin
   conectar): agregar `@onready var boton_records: Button = ...`, en
   `_ready()` conectar `boton_records.pressed.connect(_al_tocar_records)`,
   y agregar la función que navega a `records.tscn` (mismo patrón que
   `_al_tocar_jugar` con `ESCENA_SELECTOR_DIFICULTAD`). Habilitar el
   botón (`disabled = false`) si está deshabilitado en la escena.

5. **`godot/scripts/tablero_visual.gd`** — en la función que maneja
   guardar el récord al terminar la partida (`_al_tocar_guardar_record`
   o equivalente): después del guardado local existente, sumar una
   llamada a `RecordsOnline.enviar_record(...)` en paralelo, sin esperar
   su resultado de forma bloqueante ni mostrar error si falla (el
   guardado local ya es la fuente de verdad si no hay conexión).

### 5.4 Fuera de alcance de esta tarea (no incluir)

- La métrica de "eficiencia" (sección 3.5) — no diseñada en detalle,
  requiere resolver primero cómo aproximar el óptimo en el cliente.
- Registrar el uso del Comodín Táctico en el récord — depende de
  decisiones pendientes de la sección 4 (arte, trigger de UI, impacto en
  puntaje), no implementar hasta que eso se cierre.
- Separar tablas por dificultad — decidido explícitamente que NO (sección
  5.1), no reabrir esta discusión salvo pedido expreso del usuario.
