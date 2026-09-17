# Numeros naturales: version 2

Abrir **`juego_numeros_naturales_1eso_v2.ggb`** con GeoGebra Classic 5 Portable.
El archivo incluye sus scripts e iconos y no necesita internet durante la
partida. Los juegos anteriores conservan su comportamiento.

Hay **41 preguntas**. En esta version se han sustituido los dos ejercicios de
numeros romanos por uno de calculo mental y otro de reparto de libros.

## Partida

En el inicio se eligen de 2 a 8 equipos, los segundos por reto y los segundos
del comodin de tiempo. El valor inicial del comodin es **20 segundos**. Tiempo
por reto **0** significa sin limite; el comodin de tiempo queda desactivado y
no se consume en ese modo.

Cada acierto suma **un punto**. Fallar o agotar el tiempo elimina al equipo.
Los puntos siguen visibles aunque el equipo quede eliminado. Tras cerrar la
respuesta, **Siguiente reto** pasa al siguiente equipo activo o muestra el fin
de partida si queda como maximo uno. Gana el ultimo equipo activo; el marcador
permite tambien comparar los puntos al terminar la clase.

En pantalla, los equipos que ya no estan activos aparecen como **Descanso**.
El mensaje de fallo dice que el grupo "pasa a descansar"; las reglas de
eliminacion y la oportunidad de revivir no cambian.

## Comodines

Cada equipo tiene un uso de cada comodin **en toda la partida**:

- **Flecha de paso:** pasapalabra, sin eliminacion, con otro reto para el siguiente equipo.
- **Reloj:** suma el tiempo configurado a lo que queda, sin reiniciar ni acelerar el reloj.
- **Lista tachada:** desactiva una opcion incorrecta de la pregunta actual.

Los iconos grises no estan disponibles. El marcador muestra las ayudas que
conserva cada equipo, incluida su oportunidad de revivir. Los dibujos son
pequenos y cada control inferior tiene su propio recuadro, incluso cuando esta
gastado. Pasapalabra y descarte ocupan 40 por 40 pixeles; el reloj ocupa 112 por
40 para incluir tambien los segundos configurados dentro del mismo marco.
Se puede pulsar tanto en el reloj como en sus segundos. El nombre del icono
aparece al pasar el raton.

## Revivir

Cuando un equipo falla o agota el tiempo, los que ya estaban eliminados y
conservan su oportunidad pueden levantar la mano. La solucion sigue oculta.

1. El profesor pulsa **+** junto a "Oportunidad de revivir".
2. Elige el **+** del equipo al que concede el intento.
3. Ese equipo responde **la misma pregunta** con un nuevo plazo igual al tiempo normal por reto.
4. Si acierta, revive, conserva sus puntos y suma uno. Si falla o agota el tiempo, sigue eliminado.

La opcion incorrecta del primer fallo y la descartada con el comodin, si lo
hubo, permanecen desactivadas. Por eso quedan al menos dos opciones al comenzar
el intento. Si el fallo fue por tiempo, no se descarta una respuesta adicional.

La oportunidad se consume al seleccionar al equipo. Solo hay un intento de
revivir por equipo y por partida, y un intento concedido por fallo de un turno
normal. El equipo que acaba de fallar no puede aprovechar su propio fallo.
Un intento de revivir fallido no abre una cadena de nuevos intentos.

Durante el intento no se pueden usar los tres comodines iniciales. Al revivir,
quedan gastados todos ellos, incluso si alguno estaba sin usar. El turno normal
continua despues del equipo que habia fallado; el revivido entra en ese orden.

Si el profesor no concede un intento, pulsa **Ver solucion**. Despues podra
pasar de reto. El juego espera esta decision antes de declarar un ganador,
incluso cuando solo queda un equipo activo.

## Pausa y senal de fallo

El icono de pausa oculta todo el contenido del juego y congela el reloj. Solo
queda el icono para reanudar. Tambien funciona durante un intento de revivir.
Al volver se conservan el turno, las opciones descartadas y el tiempo exacto
que llevaba el reloj nativo.

Al fallar, la zona del mensaje toma un tono rosado suave. No hay sacudidas,
sonidos ni destellos. El aviso permanece hasta la siguiente accion de juego
y tambien desaparece de la vista al pausar.

La flecha circular abre una confirmacion para empezar otra partida. Mientras
se decide, el reloj se detiene; **Continuar** conserva la partida actual.

## Fuentes y Python

Desde la raiz del repositorio:

```bash
python3 IES/geogebra/1eso/T1_numeros_naturales_y_potencias/generar_naturales_v2.py --dry-run
python3 IES/geogebra/1eso/T1_numeros_naturales_y_potencias/generar_naturales_v2.py
```

Se escribe exclusivamente el `.ggb` de la version 2, con contenido reproducible:

- `generar_naturales_v2.py`: construccion de la pantalla, iconos PNG y empaquetado; solo biblioteca estandar de Python.
- `naturales_v2.js`: reglas, turnos, ayudas e interaccion, incorporados al `.ggb`. Usa JavaScript ES5 compatible con Rhino.
- `NATURALES`, en `generar_juegos.py`: banco original de preguntas, importado sin ejecutar ni modificar ese generador. `RETOS_V2`, en el nuevo script, filtra los romanos y anade sus dos sustitutos.
- `recursos_naturales_v2/LICENSE-Lucide.txt`: licencia de los iconos adaptados de Lucide/Feather, tambien incluida en el `.ggb`.

Python sigue siendo el punto de entrada para generar y cambiar el juego. No
hace falta mantener Python abierto durante la clase. Las reglas e iconos viajan
dentro del `.ggb`; no se necesita llevar los archivos fuente al aula.

El reloj usa un deslizador nativo de intervalo fijo; JavaScript escucha sus
actualizaciones mediante la [API de GeoGebra](https://geogebra.github.io/docs/reference/en/GeoGebra_Apps_API/).
No usa `setInterval`, `setTimeout`, servicios externos ni JavaScript del navegador.
Su velocidad sigue la [animacion nativa](https://geogebra.github.io/docs/manual/en/Animation/):
es un reloj aproximado para clase. Al abrir de nuevo el archivo se vuelve a
la configuracion inicial; esta version no guarda partidas para otro dia.

## Verificacion

Pruebas estructurales, recursos PNG y generacion reproducible:

```bash
python3 IES/geogebra/1eso/T1_numeros_naturales_y_potencias/test_naturales_v2.py
```

Pruebas de reglas e integracion con una API simulada, si se dispone de Node.js
(solo para desarrollo, no es una dependencia del juego):

```bash
python3 IES/geogebra/1eso/T1_numeros_naturales_y_potencias/test_naturales_v2.py --javascript | node
```

Durante el desarrollo se ejecutaron esas mismas 30 pruebas tambien en Rhino
1.8.1, incluido en el Portable del portatil. Se verificaron respuestas repetidas,
reloj, pausa, comodines, intentos de revivir, reinicio y agotamiento del banco.
La API simulada comprueba las llamadas y los objetos; no sustituye la carga y
el dibujo reales de GeoGebra. Las 8 pruebas de Python incluyen ahora la opacidad
de los iconos y la visibilidad del texto de los botones, tras detectar en las
primeras capturas que ambos faltaban. Tambien se comprueba el formato del color
de fondo segun el [comando SetBackgroundColor](https://geogebra.github.io/docs/manual/en/commands/SetBackgroundColor/).
Se comprueban tambien los marcos, la posicion de los segundos y los ejercicios
que sustituyen a los romanos.

Las capturas del usuario de las 23:06 confirman que se ven iconos, botones y
colores. **Pendiente de comprobacion visual en el portatil y la pizarra:** los
nuevos recuadros y los segundos dentro del reloj, probar 5 segundos con wifi
apagado y una partida con 8 equipos. En la sesion de desarrollo no se pudo abrir
la ventana de GeoGebra para inspeccionarla. El [TODO](../../TODO.md) mantiene
esa distincion.
