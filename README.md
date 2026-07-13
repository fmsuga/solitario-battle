# Solitario Battle

Un solitario de mesa con mazo español, jugado por parejas: se reparte
una carta a la vez y hay que "cazar" coincidencias entre pilas separadas
por una de por medio.

## Reglas

- Las cartas se reparten de a una, formando una fila de pilas boca
  arriba (la primera carta de cada pila queda tapada por las que le
  siguen encima; solo se ve el tope).
- Una jugada consiste en elegir una pila y compararla contra la que
  está **dos lugares a la derecha**, salteando la del medio. Si
  coinciden en **valor** o en **palo**, es una jugada válida.
- Al ejecutarse una jugada válida, la pila del medio se apila entera
  encima de la pila de la izquierda, y desaparece de la fila (las pilas
  restantes se corren para ocupar su lugar).
- **Efecto cadena:** después de cada fusión hay que volver a revisar,
  porque el nuevo acomodo puede abrir una jugada que antes no estaba
  disponible. Se sigue así hasta que no quede ninguna coincidencia más.
- El juego termina cuando se acaba el mazo (no quedan cartas para
  repartir) y ya no hay más jugadas posibles.
- **Puntaje:** cuantas menos pilas queden al final, mejor el resultado.
  2 pilas es el mínimo posible (partida perfecta).

### Dificultad

- **Fácil**: mazo de 40 cartas (se sacan el 8 y el 9 de cada palo).
- **Difícil**: mazo completo de 48 cartas.

## Cómo jugar

```
python main.py
```

La aplicación se juega exclusivamente mediante la interfaz gráfica.

## Récords mundiales

Los récords se guardan localmente y se sincronizan con Supabase cuando hay
conexión. El ranking único ordena por puntaje; ante empate, gana quien tardó
menos tiempo y, si sigue empatado, quien hizo menos movimientos.

Antes de usar los récords globales por primera vez:

1. Abrí el proyecto en Supabase y entrá a **SQL Editor**.
2. Creá una consulta nueva, pegá el contenido de `supabase_schema.sql` y ejecutala.

La aplicación utiliza una publishable key —apta para clientes móviles y de
escritorio— y las políticas RLS del esquema restringen el acceso a lectura y
publicación de partidas. Para una versión competitiva publicada se recomienda
añadir Supabase Auth y una Edge Function que valide las partidas en el servidor.
