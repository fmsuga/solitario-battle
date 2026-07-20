# Solitario Battle → Godot → Android

## Estado al 20/07/2026

La migración ya superó el prototipo: Godot 4.7 contiene lógica en GDScript, GUT, tablero táctil con cartas reales, selector de dificultad, HUD, pausa, pantalla final, historial local y récords online. Existe un APK exportado.

Validación actual: 45/46 pruebas de GUT pasan. La prueba visual `test_tablero_visual.gd` está desactualizada respecto de la UX actual y es el bloqueo inmediato de calidad. No introducir funcionalidad nueva hasta dejarla verde.

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

1. Actualizar `test_tablero_visual.gd` al contrato vigente de `tablero_visual.gd`; no restaurar métodos eliminados solo para satisfacer el test.
2. Ejecutar la suite completa y registrar 46/46 verdes.
3. Probar en Android físico: reparto, jugada válida/inválida, pausa, reinicio, guardar récord y volver al menú.
4. Verificar export preset, SDK y firma de debug; documentar el comando de build reproducible.

Criterio de cierre: pruebas verdes y recorrido manual completo en un dispositivo Android.

## Etapa 2 — Sistema de resultados y puntuación

Objetivo: que el resultado sea justo, explicable y motivador.

1. Usar `traspaso_records_y_comodin.md` como fuente estadística versionada. Referencias oficiales: 2 pilas con estrategia casi óptima: Difícil 0.18% (~1/570), Fácil 0.44% (~1/227), n=20.000 mazos por dificultad.
2. Diseñar una puntuación no lineal basada principalmente en pilas finales; acordar la curva antes de modificar `Juego.calcular_puntaje()`.
3. Diseñar una eficiencia estimada contra la referencia `viejo_primero` (gap de 0.017 pilas frente al óptimo en pruebas exhaustivas pequeñas). No ejecutar un solver exhaustivo en el cliente.
4. Sustituir el mensaje fijo de final por mensajes contextuales: rareza, desempeño personal y tono rotativo.
5. Extender el resumen persistido con versión de esquema para que rankings históricos continúen interpretándose correctamente.

Criterio de cierre: fórmula con tests de bordes, mensajes deterministas testeables y compatibilidad de historial verificada.

## Etapa 3 — Consistencia visual móvil

Objetivo: consolidar una identidad retro sobria, táctil y reutilizable.

1. Auditar las escenas `menu_principal`, `selector_dificultad`, `tablero`, `records` y `ajustes_overlay` contra un único contrato de botón.
2. Convertir el estilo de “Volver” en el estándar para acciones secundarias; rectangular, marfil/amarillo suave, borde y estado presionado claros.
3. Cambiar el selector para que lea como dos cajas de mazo, no como tarjetas redondeadas; eliminar hover que no aporte en móvil y alargar levemente la apertura.
4. Integrar `godot/assets/interfaz/cronometro.svg`; reemplazará el chip actual sin cambiar la fuente de tiempo ni el layout salvo necesidad comprobada.
5. Revisar legibilidad, áreas táctiles y pantallas 16:9 / 20:9 en dispositivo real.

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
- `godot/assets/interfaz/cronometro.svg` ya está disponible para la Etapa 3.
- La puntuación exacta, el trigger/arte del comodín y su efecto sobre score/récords siguen pendientes de aprobación.

## Cierre de sesión — 20/07/2026

Completado: roadmap reorganizado según el estado real; incorporado el protocolo de continuidad; leídas las estadísticas y registrado el diseño decidido del comodín; confirmado que el SVG del cronómetro existe.

Próxima tarea recomendada: actualizar `godot/tests/test_tablero_visual.gd` al contrato actual y recuperar 46/46 pruebas verdes. Después, integrar el cronómetro dentro de la Etapa 3.

Decisión técnica: los cambios de resultados no deben ejecutar un solver exhaustivo en Android; la referencia de eficiencia será una heurística o datos precalculados. El comodín es una acción de fusión forzada, no una carta del mazo.
