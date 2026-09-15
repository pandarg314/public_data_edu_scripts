# 1 ESO · T1 Números naturales y potencias: juegos eliminatorios

- `juego_numeros_naturales_1eso.ggb` (41 retos): valor posicional, aproximación, propiedades, cálculo mental, división, jerarquía de operaciones, problemas y números romanos.
- `juego_potencias_1eso.ggb` (44 retos): qué es una potencia, exponentes 0 y 1, cuadrados y cubos, potencias de 10, producto y cociente de potencias de la misma base, potencia de una potencia, potencias con el mismo exponente y errores con la suma y la resta. Solo se usan exponentes naturales, sin fracciones ni letras.

## Cómo se juega

1. En la pantalla de inicio se elige el número de grupos (2 a 8) y el tiempo por reto (0 = sin límite). Después se pulsa **EMPEZAR**.
2. GeoGebra sortea un reto que no haya salido todavía y lo asigna al grupo que tiene el turno (resaltado en amarillo en el marcador).
3. El grupo puede hacer una de dos cosas:
   - **Responder:** se pulsa la opción que ha dicho. Si acierta, sigue en juego y suma un acierto. Si falla, queda eliminado. En los dos casos se marca la opción correcta y aparece una explicación corta.
   - **PASAPALABRA** (solo una vez por partida): no responde, no queda eliminado y el turno pasa al siguiente grupo con un reto nuevo.
4. **Siguiente reto ►** pasa al siguiente grupo que siga en juego. Si se pulsa sin responder, sirve para anular un reto.
5. Gana el último grupo que quede en juego. El marcador muestra también los aciertos de cada grupo, por si la clase termina antes.

## Editar los retos

Los `.ggb` se generan con `generar_juegos.py`. Para cambiar o añadir retos, edita las listas `NATURALES` o `POTENCIAS` y ejecuta:

```bash
python3 generar_juegos.py
```

La letra de la opción correcta se reparte a partes iguales entre A, B, C y D. Si alguna opción es larga, ese reto muestra las opciones en una sola columna.
