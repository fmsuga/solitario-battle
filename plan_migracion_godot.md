# Solitario Battle → Godot → Android

## Estado al 20/07/2026

La migración ya superó el prototipo: Godot 4.7 contiene lógica en GDScript, GUT, tablero táctil con cartas reales, selector de dificultad, HUD, pausa, pantalla final, historial local y récords online. Existe un APK exportado.

Validación actual: 51/51 pruebas de GUT pasan (131 aserciones). El proyecto también inicia y cierra correctamente en modo headless. Falta la validación manual en Android físico.

## Fases cerradas

- [x] Toolchain base Godot → Android: proyecto Mobile y APK existente.
- [x] Lógica de cartas, tablero, reglas, juego y puntuación en GDScript.
- [x] Pruebas unitarias GUT para lógica.
- [x] Tablero jugable con cartas reales y reparto.
- [x] Interacción táctil para jugadas.
- [x] Selector Fácil/Difícil, HUD, pausa, resumen, historial local y récords.
- [x] Orientación vertical y tema base responsive.
- [x] Récords: tabla, fallback local y envío no bloqueante a Supabase.

## Protocolo de continuidad (obligatorio)

Este archivo es la fuente única de verdad del progreso. Antes de iniciar una tarea, contrastar su estado con el código, tests y `git status`; no asumir que un documento histórico representa el árbol actual.

Al completar trabajo:

1. Actualizar este roadmap en la misma sesión: marcar tareas, eliminar las obsoletas y agregar descubrimientos en la etapa correspondiente.
2. Registrar al final un resumen breve, la próxima tarea recomendada y decisiones técnicas relevantes.
3. No depender del historial de conversación. Referenciar aquí los documentos, pruebas, archivos y criterios necesarios para retomar.
4. Antes de cambios significativos, mostrar el diff propuesto y esperar aprobación explícita del usuario.

## Etapa 1 — Estabilización (prioridad máxima)

Objetivo: una build reproducible y una suite confiable antes de cambiar reglas, puntuación o UI.

1. [x] Actualizar `test_tablero_visual.gd` al contrato vigente de `tablero_visual.gd`; no restaurar métodos eliminados solo para satisfacer el test.
2. [x] Ejecutar la suite completa: 46/46 verdes, 120 aserciones.
3. [ ] Probar en Android físico: reparto, jugada válida/inválida, pausa, reinicio, guardar récord y volver al menú. No hay dispositivo ADB conectado al 20/07/2026.
4. [x] Verificar export preset, SDK y firma de debug. Build reproducible validado el 20/07/2026 (APK debug firmado, 38.4 MB): desde `godot/`, ejecutar `& 'C:\\Users\\agus\\Desktop\\Godot_v4.7-stable_win64.exe\\Godot_v4.7-stable_win64_console.exe' --headless --path . --export-debug Solitario ..\\dist\\SolitarioBattle-debug.apk`. El preset usa `com.suga.solitariobattle`, arm64-v8a y la firma debug del SDK. Aviso no bloqueante: falta definir un icono propio de aplicación.
5. [ ] Evaluar actualizar GUT 9.6.1 a 9.7.1 solo si reaparecen incompatibilidades con Godot 4.7; la suite actual pasa completa.

Criterio de cierre: pruebas verdes y recorrido manual completo en un dispositivo Android.

## Etapa 2 — Sistema de resultados y puntuación

Objetivo: que el resultado sea justo, explicable y motivador.

### Diseño aprobado

La referencia es `viejo_primero`: en la simulación exhaustiva pequeña iguala al óptimo el 99,33% de las veces y queda a 0,017 pilas de media. No se ejecuta un solver exhaustivo en Android.

- **Oportunidad antigua bloqueada** (nombre de UI; internamente `bloqueo_de_prioridad`): se cuenta solo cuando, existiendo una jugada válida más antigua, el jugador hace una más nueva y esta altera/elimina las tres pilas de aquella oportunidad, con lo que deja de poder ejecutarse. No cuentan toques inválidos, simples demoras ni jugadas nuevas que dejan viva la anterior.
- **Eficiencia táctica**: `fusiones_jugador / fusiones_referencia × 100`, donde la referencia resuelve el mismo mazo completo mediante `viejo_primero`. Se muestra junto con las oportunidades bloqueadas y la diferencia de pilas; no se penaliza dos veces de forma directa por cada bloqueo.
- **Rareza**: usar la distribución acumulada versionada por dificultad de mazos jugados con la referencia. La UI comunica probabilidades del resultado real, por ejemplo: “La probabilidad de terminar con 3 pilas es 0,73% en Difícil”. Las cifras oficiales actuales: 2 pilas, Difícil 0,18% y Fácil 0,44%; ≤3, 0,91%/2,26%; ≤4, 2,29%/4,96%, n=20.000.
- **Puntaje v2**: `puntaje_rareza × (0,70 + 0,30 × eficiencia_normalizada)`. `puntaje_rareza` se deriva logarítmicamente de la probabilidad acumulada; la rareza ya normaliza la dificultad, por lo que sustituye el multiplicador fijo ×1,5. El tiempo y los movimientos solo desempatan.
- **Pantalla final**: 1) puntaje principal; 2) resultado y mensaje de rareza claro; 3) eficiencia, oportunidades bloqueadas y pilas de la referencia en un bloque integrado; 4) pilas, movimientos y duración; 5) logros personales nuevos (menos pilas, mayor puntaje y menor duración) si corresponden.
- **Historial/ranking**: `version_esquema` y `version_puntaje` separan v1 de v2. El ranking v2 mezcla dificultades por rareza normalizada; desempata por eficiencia, duración y movimientos. V1 permanece como historial, sin reinterpretarlo.

### Trabajo

1. [ ] Generar y versionar fuera del cliente una distribución acumulada completa por dificultad (simulación reproducible, estrategia y tamaño de muestra incluidos). No inventar probabilidades para resultados no medidos.
2. [x] Conservar el orden inicial del mazo y ejecutar la referencia `viejo_primero` en memoria al finalizar; cubierto con prueba determinista.
3. [x] Registrar oportunidades antiguas bloqueadas mediante identidad de pilas y añadir eficiencia, pilas de referencia y diferencia al resumen. Se prueban tanto el bloqueo real como una jugada nueva que no altera la oportunidad antigua.
4. [ ] Crear la curva de rareza v2 y reemplazar `Juego.calcular_puntaje()` solo cuando exista la distribución completa; cubrir bordes, monotonía y comparabilidad entre dificultades.
5. [x] Integrar en la pantalla final el mensaje de rareza documentada, el bloque táctico (bloqueos, referencia y eficiencia) y los logros personales de menos pilas, mayor puntaje y menor duración. Para resultados sin probabilidad documentada se declara explícitamente que falta la tabla completa.
6. [ ] Versionar persistencia local, Supabase y ranking; conservar registros v1 como históricos y habilitar progreso con eficiencia, rareza y bloqueos.

Criterio de cierre: referencia y bloqueos con pruebas deterministas; distribución reproducible; fórmula con tests de bordes; mensajes de rareza comprobables; y compatibilidad de historial verificada.

## Etapa 3 — Consistencia visual móvil

Objetivo: consolidar una identidad retro sobria, táctil y reutilizable.

1. [x] Auditar las escenas `menu_principal`, `selector_dificultad`, `tablero`, `records` y `ajustes_overlay`. Hallazgo: estilos compartidos con radio 14, estados `pressed` iguales a `hover`, y estilos propios en menú/tabs de récords.
2. [x] Convertir el estilo de “Volver” en el estándar para acciones secundarias: rectangular, marfil/amarillo suave, borde oscuro y estado presionado claro.
3. [x] Crear recursos de estado presionado para botones primario, secundario y peligro; no reutilizar hover. Migrar menú principal y pestañas de récords al contrato compartido mediante el tema y estilos reutilizables.
4. [x] Cambiar el selector para que lea como dos cajas de mazo, no como tarjetas redondeadas; cajas más estrechas y altas, materiales marfil/marrón, borde inferior profundo y apertura a 1.25 s. Las cartas empiezan invisibles y solo se muestran tras tocar una caja.
5. [x] Integrar el cronómetro al encabezado como display digital oscuro con dígitos rojos y formato `HH:MM:SS`; eliminado el SVG y el reloj separado. El mazo queda centrado en la zona inferior y el encabezado conserva pilas, mazo y movimientos.
6. [x] Unificar contadores de pilas y mazo: insignia oscura rectangular redondeada, solapada parcialmente fuera de la esquina inferior derecha; sin franja que tape el arte ni número de pila.
7. [ ] Revisar legibilidad, áreas táctiles y pantallas 16:9 / 20:9 en dispositivo real.
8. [x] Corregir regresiones de interacción y pulido: el menú de pausa vuelve a mostrar "Volver al menú" con confirmación, tocar una carta seleccionada la deselecciona, las cartas muestran solo su PNG y la selección se expresa mediante elevación sutil. El selector no revela cartas al entrar, no usa fade global y prolonga la apertura de mazo más una pausa de apreciación.
9. [x] Eliminar el estado crema residual del selector: los botones de las cajas conservan su estilo transparente también al deshabilitarse durante la apertura. Añadir arrastre táctil de pila a pila, con la misma validación de fusión que el doble toque. La carta seleccionada se eleva 20 px y escala a 1.06 sin clipping. Al agotarse el mazo, se revela una acción independiente de terminar en la misma zona, sin bloquear las jugadas restantes.
10. [x] Recuperar la consistencia escena–script del tablero: `MazoYTiempo` contiene `Mazo` y `TerminarPartida`; la animación de fusión cancela de forma segura ante una reconstrucción de grilla y bloquea nuevas interacciones hasta terminar.
11. [x] Pulido posterior a la estabilización: la fusión confirma con un zoom elástico, la acción de terminar se revela mediante un giro horizontal sin hover, Ajustes nace oculto y las tres cartas animadas de ambos selectores usan la misma geometría visible.

Criterio de cierre: mismas jerarquías visuales y feedback de presión en todos los botones, sin regresiones de layout.

## Etapa 4 — Comodín táctico

Objetivo: añadir una decisión estratégica sin alterar las reglas ni introducir una carta persistente.

1. Acordar arte y trigger de UI; no hay diseño de carta todavía.
2. Añadir en `Juego` un único uso por partida y una operación que fuerce una fusión estructural (`i` con `i+2`), reutilizando la fusión actual y sin crear una carta comodín.
3. Decidir antes de codificar si afecta el puntaje o solo se registra en el resumen. Si se persiste, versionar el esquema y evaluar el cambio de Supabase.
4. Cubrir uso válido, consumo único, rechazo fuera de rango y ausencia de rastros en el tablero mediante pruebas.

Decisiones cerradas: puede usarse en cualquier momento; no esperar a que el tablero esté bloqueado; un comodín de mazo persistente, uno que queda muerto y variantes de múltiples usos están fuera de alcance.

## Etapa 5 — Release y publicación

1. Definir paquete definitivo, versionado y keystore de release (fuera de Git).
2. Generar AAB firmado y validarlo mediante testing interno de Play.
3. Completar ficha, política de privacidad, Data safety, icono, feature graphic y capturas.
4. Ejecutar testing cerrado y luego producción conforme a los requisitos vigentes de Play Console.

## Trabajo paralelo seguro

| Frente | Alcance independiente | Dependencia |
| --- | --- | --- |
| Calidad | Actualizar prueba visual y smoke tests de escenas | Ninguna |
| UI | Inventario de estilos y propuesta de botón/selector | No modificar nodos ni scripts de tablero sin coordinación |
| Resultados | Especificación de curva, rareza y mensajes | Usar `traspaso_records_y_comodin.md` |
| Android | Checklist de export/debug/release | Acceso a SDK, dispositivo y credenciales |
| Assets | Preparar arte del comodín, iconos y capturas | Trigger de comodín aprobado |

Cada frente debe trabajar en archivos distintos y entregar pruebas o capturas de verificación. Integrar primero calidad, luego modelo de resultados y finalmente UI, para evitar adaptar la presentación a contratos que sigan cambiando.

## Decisiones y referencias vigentes

- `traspaso_records_y_comodin.md` contiene la metodología y resultados completos; es referencia de diseño, no sustituto de este roadmap para el estado actual.
- El cronómetro usa un display digital nativo del tema; no depende de un SVG.
- La curva v2 requiere una distribución completa versionada antes de sustituir el puntaje actual; no se extrapolarán probabilidades ausentes.
- El comodín conserva pendientes su trigger/arte y efecto sobre score/récords.

## Cierre de sesión — 20/07/2026

Completado: roadmap reorganizado según el estado real; incorporado el protocolo de continuidad; leídas las estadísticas y registrado el diseño decidido del comodín; actualizada la prueba visual al flujo vigente; suite GUT en 51/51 verde (131 aserciones); smoke headless correcto; integrado el cronómetro digital al encabezado y retirado el SVG; auditada y corregida la inconsistencia de botones; refinados los contadores; selector convertido en cajas de mazo sin animación previa al toque; corregido el enlace de la insignia de `PilaVisual`; restaurado el retorno al menú desde pausa; pulida la selección y deselección de cartas; eliminado el estilo marfil residual del selector; incorporado arrastre táctil; restaurada la acción separada de terminar en la zona del mazo; recuperada la coherencia entre escena, script y transición de fusión; sustituida la absorción de fusión por zoom elástico; corregido el autoapertura de Ajustes; igualada la geometría de las cartas animadas de dificultad; y animada la revelación de terminar partida sin hover. Iniciado el análisis pospartida: referencia `viejo_primero`, eficiencia, oportunidades antiguas bloqueadas, mensajes de rareza con datos oficiales y logros personales. Se restauró `reglas.gd`, que estaba eliminado del árbol de trabajo. No generar APKs automáticamente salvo pedido expreso.

Próxima tarea recomendada: generar la distribución completa y reproducible de resultados de referencia para cerrar la curva de rareza v2; después versionar persistencia y ranking. La validación manual en Android sigue pendiente, incluida la legibilidad del nuevo bloque de análisis final.

Decisión técnica: los cambios de resultados no deben ejecutar un solver exhaustivo en Android; la referencia de eficiencia será una heurística o datos precalculados. El comodín es una acción de fusión forzada, no una carta del mazo. La prueba visual debe validar el contrato de UX vigente, no mensajes ni métodos retirados. El HUD usa tiempo preciso solo para display; el historial conserva duración entera. Los botones usan estilos reutilizables con estado presionado hundido, no el estilo hover. El mazo se ancla al centro de la zona inferior; el reloj es un display digital dentro del encabezado. Las cartas del selector nacen con `visible = false` y sus controles de toque permanecen transparentes en todos sus estados. El arrastre interpreta origen/destino como la misma jugada que el doble toque; no arrastra una representación visual de la carta. La escena es dueña de los nodos de UI y `tablero_visual.gd` solo los enlaza; una fusión bloquea la interacción hasta que su tween termina o se cancela de forma controlada.
