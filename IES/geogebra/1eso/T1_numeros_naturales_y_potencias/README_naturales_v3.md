# Numeros naturales: version 3

Abrir [juego_numeros_naturales_1eso_v3.ggb](juego_numeros_naturales_1eso_v3.ggb)
con GeoGebra Classic 5 Portable. Esta version parte de una copia de v2 y mantiene
41 preguntas, sin numeros romanos ni preguntas sobre propiedades. Incluye todos los scripts, iconos y el
cartel final dentro del archivo: no necesita internet durante la partida.

La version 2 y los otros juegos no se han modificado. Esta guia deja registrada
la referencia para una futura actualizacion de los demas GeoGebras, que **no se
realiza todavia**.

## Ultimos ajustes: 17 de septiembre

La misma v3 incorpora ahora **Siguiente ronda** siempre visible durante la
partida, **Fin de partida** para cerrar al sonar el timbre y un **reloj circular
mas grande**. V2 y los otros juegos siguen intactos.

Las cinco preguntas de conmutativa, asociativa, distributiva y elemento neutro
se sustituyen por operaciones breves, de dos o tres calculos, con soluciones
paso a paso. Se practican la jerarquia, los parentesis y corchetes y el orden de
izquierda a derecha entre operaciones de igual prioridad. **Sin potencias ni
raices**, porque aun no se han explicado. Se mantienen las 41 preguntas totales.

| Nuevas operaciones | Resultado |
| --- | --- |
| `6 + 3 * 4` | 18 |
| `24 : 3 * 2` | 16 |
| `18 - 6 + 2` | 14 |
| `3 * (8 - 5) + 4` | 13 |
| `24 : [2 * (5 - 2)]` | 4 |

En el juego la multiplicacion se representa con un punto. El generador comprueba
las soluciones, los pasos y que las tres respuestas incorrectas sean distintas.

## Novedades visuales

- **Reloj circular:** contador grande dentro de un circulo de 116 px, con los segundos indicados debajo. Las cifras se centran al pasar de una a dos o tres cifras. En modo sin limite, el circulo indica "Sin limite".
- **Ultimos 10 segundos:** las cifras aumentan aun mas de tamano y tanto el contador como el circulo pasan a rojo. No parpadea ni emite sonidos. Tambien se aplica a los intentos de revivir. Si el comodin eleva el tiempo restante por encima de 10 segundos, recupera el tamano y el color normales.
- **Comodines gastados:** una X roja los identifica tanto en los controles inferiores como en los iconos pequenos del marcador. Los controles grandes conservan el marco y tienen fondo rosado. En el reloj gastado, los segundos se sustituyen por "Usado".
- **Desactivados temporalmente:** siguen grises, sin X, cuando aun no se han consumido. Por ejemplo, el tiempo extra al jugar sin limite, o las ayudas de un equipo que esta descansando. No se confunde una ayuda bloqueada con una gastada.
- **Opciones descartadas:** conservan su contenido, pero tienen texto rojo oscuro, fondo rosado y una cruz al lado. Se aplica tanto al descarte por comodin como a la respuesta incorrecta elegida. No se pueden responder de nuevo.
- **Copas en el marcador:** todos los equipos empatados con la mayor puntuacion llevan una copa pequena. Durante la partida indican quienes van en cabeza; no aparecen mientras todos tienen cero puntos.
- **Cartel final:** sustituye al reto y muestra los ganadores y su puntuacion. Hay espacio para los ocho equipos en caso de empate. Cada ganador conserva tambien su copa junto al marcador.

La paleta es compartida entre los textos y los PNG: turquesa para controles y
turno, verde para aciertos, rojo oscuro sobre rosa claro para avisos y descartes,
y dorado para las copas y los resultados. El fondo general sigue siendo claro.
Las senales no dependen solo del color: tambien usan cruces, copas o un cambio
de tamano. No hay sacudidas, destellos ni sonidos.

## Configuracion y turnos

- Entre **2 y 8 equipos**; inicialmente 5.
- Tiempo normal entre **0 y 120 segundos**, en pasos de 5; inicialmente 30. **0 significa sin limite**.
- Tiempo extra entre **5 y 120 segundos**, en pasos de 5; inicialmente 20.
- Preguntas aleatorias sin repetir hasta agotar el banco. Entonces se vuelve a barajar el banco; agotarlo no termina la partida.
- **Un punto por acierto**, tambien al revivir. Dobles clics no suman puntos adicionales.
- Fallar o agotar el tiempo pone al equipo en **Descanso**, conserva su puntuacion y bloquea su respuesta.
- **Siguiente ronda** pasa al siguiente equipo activo, tanto antes como despues de responder. El turno actual se distingue en el marcador.

## Siguiente ronda y revision previa

**Siguiente ronda** esta visible durante todo el juego: pregunta activa,
respuesta cerrada, oferta o seleccion para revivir e intento de revivir. Permite
al profesor descartar la pregunta pendiente y avanzar sin sumar ni quitar puntos,
sin poner al equipo en Descanso y sin gastar pasapalabra. Reinicia el reloj del
nuevo reto, retira los descartes de la pregunta anterior y mantiene las ayudas
que ya se hayan consumido. Los aciertos ya registrados conservan su punto.

Si se pulsa cuando se esta ofreciendo o eligiendo una oportunidad de revivir,
se renuncia a ella en esa pregunta sin consumir una oportunidad no seleccionada.
Si el intento ya habia empezado, se abandona: el equipo no revive y la oportunidad
ya consumida no se devuelve. Se recupera el orden normal de turnos.

Para revisar la bateria antes de clase: elegir **tiempo 0**, empezar y pulsar
**Siguiente ronda** cuantas veces haga falta. Se pueden recorrer las 41 preguntas
sin contestar y sin repetir hasta agotar el banco. Con tiempo limitado, un plazo
que ya se haya agotado cuenta como fallo: el boton no deshace ese fallo.

Durante la pausa, las confirmaciones, la configuracion y el cartel final no se
muestran los botones de ronda o fin de partida. Asi se mantiene la pantalla
oculta al pausar y se evitan cambios de puntuacion tras terminar.

## Ganadores y final de partida

**Criterio aplicado en v3: gana la mayor puntuacion entre todos los equipos,
incluidos los que estan en Descanso. Todos los empatados comparten la victoria.**
Es un cambio respecto a v2, donde ganaba el ultimo equipo activo.

Hay dos formas de terminar:

- **Final por eliminacion:** cuando queda como maximo un equipo activo, avanzar con **Siguiente ronda** muestra el cartel. Una oferta de revivir no cierra por si sola la partida: el profesor puede conceder el intento o saltarlo expresamente.
- **Final por el timbre:** **Fin de partida**, bajo el marcador, permite terminar en cualquier momento, aunque queden varios equipos activos o haya un intento pendiente. Abre una confirmacion y detiene el reloj. **Finalizar** muestra los ganadores con los puntos actuales; **Continuar** vuelve exactamente a la pregunta, turno y tiempo anteriores.

Cerrar anticipadamente no concede puntos por respuestas pendientes ni cambia
el estado de los equipos o sus comodines. La victoria se calcula igual en los
dos casos; tampoco se consume una oportunidad de revivir aun no seleccionada.

Si todos terminan con cero puntos, se muestra el empate de todos a cero. Una
vez abierto el cartel, las respuestas y los comodines no alteran los resultados.
Se puede pausar o iniciar otra partida.

## Comodines

Cada equipo dispone de **un uso de cada tipo en toda la partida**:

| Icono | Comodin | Efecto |
| --- | --- | --- |
| Flecha de paso | Pasapalabra | Pasa al siguiente equipo con un reto nuevo, sin poner al anterior en Descanso. |
| Reloj | Tiempo extra | Suma los segundos configurados a lo que queda, sin reiniciar lo transcurrido ni cambiar la velocidad. |
| Lista tachada | Eliminar una incorrecta | Descarta exactamente una opcion incorrecta al azar, nunca la correcta. |

Los controles inferiores siguen siendo pequenos y recuadrados: 40 por 40 px
para paso y descarte, y 112 por 40 px para el reloj con su texto. En el marcador,
los iconos de ayudas son de 18 px y las copas de 24 px. El nombre aparece al
pasar el raton. En el reloj se puede pulsar el icono o los segundos.

El tiempo extra no se consume en el modo sin limite. Ningun comodin puede
utilizarse despues de cerrar la respuesta, durante la pausa o durante un intento
de revivir. Los gastados no se reponen al cambiar de pregunta.

## Oportunidad de revivir

Cada equipo tiene una oportunidad adicional de revivir, utilizable una sola vez
por partida. Cuando otro equipo falla o agota el tiempo:

1. Los equipos que ya estaban en Descanso y conservan su oportunidad pueden levantar la mano.
2. El profesor pulsa **+** junto a "Oportunidad de revivir" y elige el **+** del equipo al que concede el intento.
3. El elegido responde la **misma pregunta**, con un nuevo plazo igual al tiempo normal. La oportunidad se consume al seleccionarlo.
4. Si acierta, vuelve al juego, conserva sus puntos y suma uno. Los tres comodines iniciales quedan gastados, incluso si no los habia usado.
5. Si falla o agota el tiempo, sigue en Descanso y no recupera la oportunidad.

Se mantienen descartadas la respuesta incorrecta del primer equipo y la retirada
por comodin, si la hubo. Quedan al menos dos opciones al empezar el intento.
La respuesta correcta y la explicacion permanecen ocultas hasta terminar ese
intento o declinarlo con **Ver solucion**.

Solo se concede un intento por fallo de un turno normal. El equipo que acaba
de fallar no aprovecha su propio fallo, y un intento fallido no abre otra cadena.
El siguiente turno normal se cuenta desde el equipo que habia fallado, no desde
el que intento revivir. Si quedan de nuevo varios equipos activos, se continua.

## Pausa, reinicio y funcionamiento local

La pausa oculta todo: pregunta, opciones, circulo del reloj, puntos, comodines,
botones del profesor, copas y cartel.
Solo queda el control para reanudar. El tiempo se congela y se recupera el mismo
estado al volver, tambien durante un intento de revivir.

La flecha circular abre la confirmacion de nueva partida y detiene el reloj.
**Continuar** conserva lo anterior; **Reiniciar** vuelve a la configuracion y la
siguiente partida comienza con cero puntos y todas las ayudas disponibles.

El contador utiliza la animacion nativa de GeoGebra y un deslizador oculto, no
temporizadores del navegador. Es un reloj aproximado para clase. Al volver a
abrir el archivo se comienza en la configuracion: **no se guardan partidas entre
sesiones**. No hace falta tener Python abierto ni conectado durante el juego.

La [guia de Ubuntu](../../USO_UBUNTU_24.md) conserva las instrucciones de Portable
y el atajo de pantalla completa que ya funciona en el portatil.

## Fuentes y regeneracion

Desde la raiz del proyecto:

```bash
python3 IES/geogebra/1eso/T1_numeros_naturales_y_potencias/generar_naturales_v3.py --dry-run
python3 IES/geogebra/1eso/T1_numeros_naturales_y_potencias/generar_naturales_v3.py
```

El generador escribe **solo el archivo v3** y usa exclusivamente la biblioteca
estandar de Python. No hay nuevas dependencias ni descargas.

- `generar_naturales_v3.py`: banco `RETOS_V3`, pantalla, PNG, paleta `PALETA` y empaquetado reproducible.
- `naturales_v3.js`: reglas e interfaz, en JavaScript ES5 para GeoGebra Classic 5 / Rhino.
- `generar_juegos.py`: banco original `NATURALES` y comprobador `oper`, importados sin ejecutar su generador. La copia v3 sustituye los dos retos de romanos por calculo mental y reparto de libros, igual que v2, y los cinco de propiedades por `RETOS_JERARQUIA_V3`.
- `recursos_naturales_v2/LICENSE-Lucide.txt`: licencia reutilizada de los iconos Lucide/Feather, incluida tambien en el `.ggb` v3.
- `test_naturales_v3.py` y `test_naturales_v3.js`: pruebas de archivo, reglas e integracion con una API simulada.

El centrado del contador usa [SetCoords](https://geogebra.github.io/docs/manual/en/commands/SetCoords/)
con textos de posicion absoluta, cuyas coordenadas se expresan en pixeles.

Python permite editar y regenerar el archivo; no es una conexion en directo con
la partida. Para usar el juego en clase basta con el `.ggb` y GeoGebra instalado.

## Verificacion

```bash
python3 -m py_compile IES/geogebra/1eso/T1_numeros_naturales_y_potencias/generar_naturales_v3.py IES/geogebra/1eso/T1_numeros_naturales_y_potencias/test_naturales_v3.py
python3 IES/geogebra/1eso/T1_numeros_naturales_y_potencias/test_naturales_v3.py
```

Las pruebas JavaScript pueden ejecutarse con Node.js, solo como herramienta de
desarrollo, o con Rhino. No es una dependencia para generar o jugar:

```bash
python3 IES/geogebra/1eso/T1_numeros_naturales_y_potencias/test_naturales_v3.py --javascript | node
```

Se comprueban 16 casos de Python y 56 de JavaScript: banco sin propiedades,
potencias ni raices, nuevas soluciones y pasos de calculo, reloj,
comodines, respuestas, turnos, rescates, pausa, reinicio, empates, cartel, PNG,
contraste, capas, posiciones, generacion reproducible y conservacion de v2 y de
los juegos originales, salto manual, fin anticipado, cancelacion y visibilidad
de los nuevos controles. Las 56 pruebas JavaScript han pasado tambien con Rhino
1.8.1 del Portable y el codigo extraido del `.ggb` generado. La API simulada no
equivale a dibujar la ventana real.

Pendiente de comprobar en Portable y pizarra: apariencia de esta version con
2 y 8 equipos, reloj circular, cruces, nuevos botones y cartel final, tambien con wifi apagado.
El [TODO](../../TODO.md) separa lo verificado automaticamente de esa comprobacion.

## Siguiente fase

Cuando se solicite, aplicar esta version a los demas GeoGebras mediante nuevas
copias, conservando sus bancos y particularidades, como los niveles de operaciones.
No ejecutar ahora `generar_juegos.py` ni sustituir los otros `.ggb`. Antes de
extenderla, confirmar en el aula esta interfaz y el criterio de victoria por puntos.
