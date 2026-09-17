# 1 ESO · T1 Números naturales y potencias: juegos eliminatorios

## Nueva versión de naturales

`juego_numeros_naturales_1eso_v3.ggb` conserva las ayudas y añade reloj rojo en
los últimos 10 segundos, cruces para ayudas gastadas y respuestas descartadas,
copas y cartel final con victoria por puntos, incluidos empates. Está documentado
en la [guía completa de la versión 3](README_naturales_v3.md). La versión 2 y los
otros juegos se conservan; su actualización queda para una petición posterior.
Los últimos ajustes de v3 incorporan **Siguiente ronda** durante toda la partida,
**Fin de partida** con confirmación y un contador más grande dentro de un círculo.

`juego_numeros_naturales_1eso_v2.ggb` añade tres comodines por equipo, puntos,
oportunidad de revivir, eliminación por tiempo agotado y pausa con pantalla
oculta. Se genera por separado con `generar_naturales_v2.py` y conserva los
archivos anteriores. Consulta las [reglas y pruebas de la versión 2](README_naturales_v2.md).

## Juegos originales

- `juego_numeros_naturales_1eso.ggb` (41 retos): valor posicional, aproximación, propiedades, cálculo mental, división, jerarquía de operaciones, problemas y números romanos.
- `juego_potencias_1eso.ggb` (44 retos): qué es una potencia, exponentes 0 y 1, cuadrados y cubos, potencias de 10, producto y cociente de potencias de la misma base, potencia de una potencia, potencias con el mismo exponente y errores con la suma y la resta. Solo se usan exponentes naturales, sin fracciones ni letras.
- `juego_operaciones_niveles_1eso.ggb` (45 retos, pensado para Refuerzo): operaciones combinadas con números naturales, en 3 niveles de 15 retos:
  - **Nivel 1:** cálculo mental (tablas, ×10, :10, sumar 99…) y dos operaciones sin paréntesis.
  - **Nivel 2:** paréntesis, operaciones del mismo nivel de izquierda a derecha, potencias y raíces sencillas.
  - **Nivel 3:** corchetes, llaves, potencias y raíces combinadas.

  El nivel se elige al empezar y se puede cambiar en cualquier momento con los botones de arriba. Con **Todos** se mezclan los 45 retos. Al responder aparece la resolución paso a paso.

## Cómo se juega

1. En la pantalla de inicio se elige el número de grupos (2 a 8) y el tiempo por reto (0 = sin límite). Después se pulsa **EMPEZAR**.
2. GeoGebra sortea un reto que no haya salido todavía y lo asigna al grupo que tiene el turno (resaltado en amarillo en el marcador).
3. El grupo puede hacer una de dos cosas:
   - **Responder:** se pulsa la opción que ha dicho. Si acierta, sigue en juego y suma un acierto. Si falla, queda eliminado. En los dos casos se marca la opción correcta y aparece una explicación corta.
   - **PASAPALABRA** (solo una vez por partida): no responde, no queda eliminado y el turno pasa al siguiente grupo con un reto nuevo.
4. **Siguiente reto ►** pasa al siguiente grupo que siga en juego. Si se pulsa sin responder, sirve para anular un reto.
5. Gana el último grupo que quede en juego. El marcador muestra también los aciertos de cada grupo, por si la clase termina antes.

## Cronómetro y uso sin internet

El cronómetro usa un deslizador oculto con animación nativa de GeoGebra. Se
reinicia al empezar, pasar palabra o sortear otro reto; se detiene al responder,
al volver a la pantalla inicial o al llegar a cero. Con tiempo 0 no se anima.
Al agotarse el tiempo aparece **¡TIEMPO!**: es un aviso para el profesor, sin
eliminación automática ni bloqueo de respuestas.

Se ha sustituido el temporizador JavaScript anterior, que se quedaba parado en
entornos donde `setInterval` no está disponible. Los archivos no necesitan
JavaScript global ni recursos de internet. La velocidad de la animación sigue
la [documentación de GeoGebra](https://geogebra.github.io/docs/manual/en/Animation/);
es un reloj aproximado para el aula, no un cronómetro de precisión.

Para Ubuntu de 64 bits, GeoGebra enlaza **Classic 5 Portable para Linux** en su
[manual de instalación](https://geogebra.github.io/docs/reference/en/GeoGebra_Installation/).
La [descarga procede de GeoGebra](https://download.geogebra.org/package/linux-port),
aunque la distribución Linux está marcada como **sin soporte**. Se descomprime
y se ejecuta `geogebra-portable` desde la carpeta extraída. Una vez descargado,
permite abrir estos `.ggb` locales sin internet.

La validación automática comprueba la estructura de los archivos y los guiones
del reloj, pero no sustituye la prueba dentro de GeoGebra. Antes de llevarlos al
aula: abrir cada juego con el wifi desconectado, elegir 5 segundos, comprobar la
cuenta atrás y su reinicio con **Siguiente reto** y **PASAPALABRA**, responder
antes de que acabe y comprobar también una partida con tiempo 0.

## Editar los retos

Los `.ggb` se generan con `generar_juegos.py`. Para cambiar o añadir retos, edita las listas `NATURALES`, `POTENCIAS` u `OPERACIONES` y ejecuta:

```bash
python3 generar_juegos.py
```

La letra de la opción correcta se reparte a partes iguales entre A, B, C y D. Si alguna opción es larga, ese reto muestra las opciones en una sola columna.

En `OPERACIONES` cada reto se escribe en texto sencillo, por ejemplo `oper("2+3*[10-(4+2)]", ["(2+3)*[10-(4+2)]", ...], tema)`:

- **Símbolos:** `*` multiplicar, `/` dividir, `^` potencia, `( ) [ ] { }` agrupar y `r(...)` raíz cuadrada.
- **Distractores:** se escriben como la expresión que haría un alumno al cometer el error típico, o directamente como número.
- **Comprobaciones:** el script calcula la solución y los pasos, y avisa si una resta da negativo, si una división o una raíz no es exacta, o si un distractor coincide con la solución.
