# Juegos de 1 ESO: version 3

Actualizacion del 18 de septiembre de 2026. Los tres juegos tienen las mismas
reglas y controles de Naturales v3, conservando los contenidos propios de cada
banco. Abrir los archivos terminados en **`_v3.ggb`** con GeoGebra Classic 5 Portable.

| Juego | Archivo | Preguntas |
| --- | --- | --- |
| Numeros naturales | [Naturales v3](juego_numeros_naturales_1eso_v3.ggb) | 41 |
| Potencias | [Potencias v3](juego_potencias_1eso_v3.ggb) | 44 |
| Operaciones por niveles | [Operaciones v3](juego_operaciones_niveles_1eso_v3.ggb) | 45, en 3 niveles de 15 |

Los originales sin sufijo y Naturales v2 se conservan intactos. Naturales v3 se
ha regenerado con el motor compartido, sin cambiar sus preguntas ni sus reglas.
Cada `.ggb` incluye scripts e imagenes: no depende de internet ni necesita
Python abierto para jugar.

## Funciones comunes

- Configuracion de **2 a 8 equipos**, tiempo por reto y tiempo extra. Valores iniciales: 5 equipos, 30 segundos por reto y 20 de comodin. Tiempo 0 permite revisar o jugar sin limite.
- **Un punto por acierto**, tambien al revivir. Se conservan los puntos de los equipos en Descanso.
- Un uso por equipo de **pasapalabra**, **tiempo extra** y **descarte de una incorrecta**. Los iconos gastados llevan una X, tanto en los controles inferiores como en el marcador.
- Una oportunidad de **revivir**, elegida por el profesor tras el fallo de otro equipo. Se usa la misma pregunta; no se revela la solucion hasta resolver o declinar el intento. Al revivir se retiran los tres comodines iniciales.
- **Reloj circular grande**, con cifras aun mayores y color rojo durante los ultimos 10 segundos. Agotar el tiempo pone al equipo en Descanso automaticamente.
- Respuestas descartadas con cruz y fondo rosado; aciertos en verde y aviso suave al fallar, sin sacudidas ni destellos.
- **Pausa** que oculta todo y congela el tiempo; solo queda el control para reanudar.
- **Siguiente ronda** disponible durante la partida para saltar preguntas sin gastar pasapalabra, incluso antes de responder.
- **Fin de partida** con confirmacion para terminar cuando suene el timbre; cancelar conserva la pregunta y el tiempo.
- Copas para quienes van en cabeza y cartel final para **todos los equipos con la mayor puntuacion**, incluidos empates y equipos en Descanso.
- Reinicio con confirmacion y todas las ayudas restauradas en la nueva partida.

La [guia detallada de Naturales v3](README_naturales_v3.md) explica los casos
especiales de rescate, salto de ronda, pausa, puntuacion y fin anticipado. Esas
reglas se aplican tambien a Potencias y Operaciones.

## Potencias

Se conservan las 44 preguntas originales: significado de una potencia,
exponentes 0 y 1, cuadrados y cubos, potencias de 10, problemas, producto y
cociente de potencias de igual base, potencia de una potencia, mismo exponente
y errores con sumas/restas. No hay selector de niveles.

La retirada de propiedades, potencias y raices solicitada para **Naturales** no
se aplica a este banco: aqui son precisamente el contenido que se practica.

## Operaciones y niveles

- **Nivel 1:** calculo mental, jerarquia y operaciones de igual prioridad de izquierda a derecha; sin potencias ni raices.
- **Nivel 2:** parentesis, operaciones de igual prioridad, potencias y raices sencillas.
- **Nivel 3:** corchetes, llaves y operaciones combinadas con potencias y raices.
- **Todos:** mezcla de las 45 preguntas.

Se empieza con **Nivel 1** seleccionado. Los botones superiores permiten elegir
el nivel antes de empezar o durante la partida. El seleccionado queda resaltado.
El cambio afecta a **la siguiente pregunta**, no sustituye la que se esta
resolviendo, no reinicia el reloj ni modifica puntos o comodines. El tema de la
pregunta indica su nivel actual; la cifra de pendientes corresponde al filtro
seleccionado para los siguientes sorteos.

Cada nivel recorre sus 15 preguntas sin repetir. Al agotarlo, se repone solo ese
nivel; los demas conservan sus preguntas pendientes. Cambiar de nivel y volver
no repone las preguntas ya vistas. Con Todos, se usan las pendientes de todos
los niveles y se repone el banco completo cuando ya no quede ninguna.

Un cambio de nivel durante una oportunidad de revivir **no cambia la pregunta
fallada ni sus opciones descartadas**. El siguiente turno normal ya usa el nuevo
nivel. Los selectores tambien desaparecen al pausar, confirmar el cierre/reinicio
o mostrar los resultados. Al reiniciar se conserva la seleccion, pero se
restablecen las preguntas pendientes, puntos y comodines.

Se mantienen las resoluciones paso a paso del juego original. En los dos juegos
nuevos la expresion esta algo mas arriba para dejar sitio a exponentes y raices
sin invadir la primera respuesta.

## Regenerar desde Python

Desde la raiz del repositorio, validar y generar **solo Potencias y Operaciones**:

```bash
python3 IES/geogebra/1eso/T1_numeros_naturales_y_potencias/generar_juegos_v3.py --dry-run
python3 IES/geogebra/1eso/T1_numeros_naturales_y_potencias/generar_juegos_v3.py
```

Para uno solo, anadir `--juego potencias` o `--juego operaciones`.
Para regenerar tambien Naturales tras un cambio en las reglas comunes:

```bash
python3 IES/geogebra/1eso/T1_numeros_naturales_y_potencias/generar_naturales_v3.py
```

- `generar_juegos_v3.py`: seleccion de banco, titulo, niveles y destinos de los dos juegos nuevos.
- `generar_naturales_v3.py`: constructor compartido de interfaz, recursos, banco y ZIP; mantiene el nombre por compatibilidad con Naturales.
- `naturales_v3.js`: motor e interfaz compartidos, incluido el filtro opcional de niveles. Los nombres internos `NaturalesGame` y `NV3` se mantienen, pero las reglas son las mismas en los tres archivos.
- `generar_juegos.py`: origen de `POTENCIAS` y `OPERACIONES`. Se importa sin ejecutar su generador ni modificar sus archivos.

Solo se utiliza la biblioteca estandar. No hay dependencias nuevas ni descargas.
No hace falta ejecutar el generador anterior para actualizar los archivos v3.

## Comprobaciones

```bash
python3 IES/geogebra/1eso/T1_numeros_naturales_y_potencias/test_naturales_v3.py
python3 IES/geogebra/1eso/T1_numeros_naturales_y_potencias/test_juegos_v3.py
```

Para ejecutar JavaScript con Node.js, si esta disponible como herramienta de
desarrollo; no es una dependencia del juego:

```bash
python3 IES/geogebra/1eso/T1_numeros_naturales_y_potencias/test_juegos_v3.py --javascript potencias | node
python3 IES/geogebra/1eso/T1_numeros_naturales_y_potencias/test_juegos_v3.py --javascript operaciones | node
```

Verificado durante esta actualizacion:

- `py_compile`, `--dry-run`, 16 pruebas Python de Naturales y 6 de los nuevos archivos.
- 57 pruebas JavaScript con Naturales, 57 con Potencias y 68 con Operaciones, tambien en Rhino 1.8.1 del Portable, a partir de los scripts extraidos de los `.ggb` generados.
- Bancos completos, respuestas y resoluciones conservadas; filtros de nivel, agotamiento de preguntas, rescates, pausa, cierres y reinicios.
- Recursos incrustados, botones de nivel sin solaparse con reloj/reinicio, ZIP reproducibles y originales conservados.
- Todas las formulas de los dos bancos nuevos se han procesado con el renderizador LaTeX del Portable y caben en el espacio reservado para expresion, respuestas y explicacion. La mayor altura de expresion fue 56 px en Potencias y 49 px en Operaciones; hay 65 px hasta la primera respuesta.

Estas pruebas no sustituyen la ventana real de GeoGebra. Queda probar los dos
archivos en pantalla completa, con wifi apagado y con 2 y 8 equipos, ademas de
los niveles 1/2/3/Todos en el portatil y la pizarra. El [TODO](../../TODO.md)
distingue esa comprobacion visual de las pruebas automaticas.
