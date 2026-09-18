# TODO: numeros naturales

## Zona segura para la pizarra, 18 de septiembre

- [x] Registrar la incidencia: el control nativo de animacion inferior izquierdo
  no se veia en la pizarra. La captura del portatil no confirma la causa.
- [x] Distinguir ese control de la pausa propia del juego, situada arriba a la
  derecha y encargada de ocultar la partida y congelar el reloj.
- [x] Crear [PROTOCOLO_PIZARRA.md](PROTOCOLO_PIZARRA.md) con margen inicial del
  5 % por lado, minimo 40 pixeles, diagnostico y comprobaciones de aula.
- [x] Enlazar el protocolo desde las instrucciones de esta carpeta y las guias.
- [ ] Confirmar si se recortan tambien el escritorio y otras aplicaciones;
  registrar modelo, conexion, resolucion, escala y modo de pantalla del aula.
- [ ] Incorporar la zona segura al diseno compartido de los tres juegos v3,
  incluyendo las posiciones dinamicas, sin recortar el lado contrario ni
  reducir la legibilidad; conservar las versiones anteriores.
- [ ] Regenerar y verificar Naturales, Potencias y Operaciones, sus distintos
  estados y resoluciones, segun el protocolo.
- [ ] Confirmar en la pizarra fisica que los cuatro bordes y todos los controles
  propios quedan visibles y accesibles.

Este registro solo modifica documentacion. Los `.ggb` mantienen su interfaz
actual; la causa del recorte y la adaptacion de margenes siguen pendientes.

## Potencias y operaciones: version 3, 18 de septiembre

- [x] Crear `juego_potencias_1eso_v3.ggb` con las 44 preguntas originales.
- [x] Crear `juego_operaciones_niveles_1eso_v3.ggb` con 45 preguntas, 15 por nivel, y selector de niveles/Todos.
- [x] Compartir las reglas e interfaz v3: ayudas, puntos, revivir, reloj circular, pausa, ronda manual y final con ganadores empatados.
- [x] Mantener las preguntas de cada juego: la exclusion de potencias, raices y propiedades se limita al banco de Naturales.
- [x] Conservar los `.ggb` originales y v2; comprobar tambien Naturales v3 al ampliar el motor compartido.
- [x] Probar niveles, agotamiento y cambio de banco, rescates, recursos y textos matematicos; documentar y generar los nuevos archivos.
- [ ] Comprobar visualmente los dos nuevos juegos en GeoGebra Portable y pizarra.

Documentado en la [guia conjunta](1eso/T1_numeros_naturales_y_potencias/README_juegos_v3.md).
Pruebas superadas: 22 Python y 182 JavaScript entre los tres bancos; tambien se
han ejecutado los scripts incrustados con Rhino del Portable. Se han comprobado
las dimensiones de todas las formulas de los dos bancos nuevos usando su
renderizador LaTeX, sin abrir la ventana interactiva de GeoGebra. Naturales v3
se regenera con el motor compartido; no cambia su banco ni su interfaz.

## Version 3: color y resultados

### Ultimos ajustes, 17 de septiembre

- [x] Sustituir las cinco preguntas de propiedades por cinco operaciones cortas de jerarquia, parentesis/corchetes y empates resueltos de izquierda a derecha, sin potencias ni raices. Conservar 41 preguntas y dejar intactos v2 y los demas juegos.
- [x] Mostrar siempre Siguiente ronda durante la partida: permite saltar sin responder, sin sumar puntos ni consumir pasapalabra.
- [x] Mantener ese control durante ofertas, seleccion e intentos de revivir; al saltar se abandona esa oportunidad, sin devolver las ayudas ya consumidas.
- [x] Agrandar el contador dentro de un circulo, conservando el aumento adicional y el rojo de los ultimos 10 segundos.
- [x] Anadir Fin de partida para terminar por el timbre, con confirmacion y ganadores por puntos, incluidos empates.
- [x] Actualizar guia, pruebas y `.ggb` v3; no modificar v2 ni otros juegos.

Controles ocultos durante pausa, confirmaciones, configuracion y resultados.
Comprobadas cancelacion del cierre, conservacion del tiempo, recorrido completo
de las 41 preguntas sin responder, fin desde un rescate, colores del circulo y
espacio bajo el marcador de 8 equipos. Las medidas de glifos de Java AWT del
Portable para 1, 10, 40 y 240 caben dentro del circulo; no es una prueba completa
de la ventana de GeoGebra. Sigue pendiente la comprobacion visual en el aula.

Peticion: partir de una copia de la version 2 que el usuario ya considera
correcta. No actualizar todavia los demas juegos; se pedira mas adelante.

- [x] Crear generador, reglas y archivo `.ggb` v3 separados, conservando v2.
- [x] Mostrar los ultimos 10 segundos mas grandes y en rojo, sin parpadeos.
- [x] Marcar con una X los comodines consumidos, tanto en controles como en marcador.
- [x] Distinguir un comodin gastado de otro temporalmente desactivado.
- [x] Destacar las opciones descartadas con cruz y color de contraste.
- [x] Mostrar copas para todos los equipos empatados en cabeza y un cartel final.
- [x] Documentar el criterio de ganadores, las caracteristicas completas y la regeneracion en un `.md` propio.
- [x] Probar reglas, nuevos estados visuales, recursos y conservacion de v2.
- [ ] Confirmar visualmente la nueva version en Portable y pizarra.

Criterio inicial para resolver los empates: maxima puntuacion entre todos los
equipos, incluidos los que descansan. Se mantiene el cierre por eliminacion al
avanzar con como maximo un equipo activo. Desde el ajuste del 17, el profesor
puede renunciar expresamente al rescate con Siguiente ronda o cerrar antes con
Fin de partida, aunque queden varios equipos activos.

Generado `juego_numeros_naturales_1eso_v3.ggb`. La
[guia completa de v3](1eso/T1_numeros_naturales_y_potencias/README_naturales_v3.md)
enlaza ahora con la adaptacion de Potencias y Operaciones realizada el 18 de septiembre.
Verificados `py_compile`, `--dry-run`, 16 pruebas Python y 57 JavaScript, estas
ultimas tambien con Rhino 1.8.1 del Portable y el JavaScript extraido del `.ggb`
generado. Comprobados los hashes de v2 y de los tres juegos originales, los
PNG incrustados y el contraste de los colores. La API simulada y las pruebas
de posiciones/capas no sustituyen la inspeccion de la ventana real de v3.

## Version 2

Peticion registrada el 16 de septiembre de 2026, antes de comenzar la nueva
implementacion. Trabajo dividido en fases para probar cada avance en clase.

Actualizacion: implementadas las fases 1 a 3 y generada la version 2. Pasan
30 pruebas de reglas e integracion con API simulada (tambien en Rhino 1.8.1
del Portable) y 8 pruebas de archivo, recursos y reproducibilidad. Las casillas
de implementacion no equivalen a una prueba visual en GeoGebra: esa parte de
la fase 4 sigue pendiente. Vease la [guia de la version 2](1eso/T1_numeros_naturales_y_potencias/README_naturales_v2.md).

## Correccion tras las primeras capturas

- [x] Revisar las capturas del 16 de septiembre a las 22:46 y 22:47: los textos del juego aparecian, pero faltaban iconos y las etiquetas de los botones.
- [x] Corregir la opacidad de las imagenes en el XML: se estaban exportando con `alpha="0"`.
- [x] Activar `show label="true"` en los botones para que aparezcan sus nombres.
- [x] Corregir los colores de fondo: `SetBackgroundColor` recibe ahora colores hexadecimales; sus componentes numericos usan 0..1, no 0..255.
- [x] Anadir pruebas que reproducen estos fallos antes de corregirlos.
- [x] Confirmar en las capturas de las 23:06 que aparecen los iconos, el texto de los botones y el tono suave de fallo del archivo corregido.

## Ajustes tras las capturas de las 23:06

- [x] Cambiar "Fuera" por "Descanso" en el marcador y sustituir el mensaje "eliminado" por "pasa a descansar".
- [x] Recuadrar por separado los tres controles de comodin, tambien cuando estan gastados.
- [x] Incluir el icono del reloj y los segundos en un mismo recuadro; ambos permiten activar la ayuda.
- [x] Sustituir los dos ejercicios de romanos por calculo mental y reparto de libros, manteniendo 41 preguntas y el banco anterior intacto.
- [x] Confirmar en Portable el aspecto de los nuevos marcos y el reloj con sus segundos dentro: el usuario considera correcta esta version.

## Alcance y estado

- [x] Registrar los requisitos y las fases en este documento.
- [x] Confirmar con el usuario que GeoGebra Portable abre en Ubuntu 24.04.
- [x] Confirmar con el usuario que funciona la pantalla completa.
- [x] Crear una nueva version basada exclusivamente en `juego_numeros_naturales_1eso.ggb`.
- [x] Mantener intactos el generador anterior y los tres juegos existentes; hashes SHA256 comprobados.
- [x] Conservar Python como fuente editable y reproducible del nuevo `.ggb`.
- [x] Incorporar todos los recursos para uso local sin internet; prueba interactiva en Portable pendiente.

Ubicacion prevista, siguiendo la organizacion actual del tema:

```text
IES/geogebra/1eso/T1_numeros_naturales_y_potencias/
    generar_naturales_v2.py
    naturales_v2.js
    juego_numeros_naturales_1eso_v2.ggb
```

La conexion con Python se entiende inicialmente como poder editar el banco,
las reglas y la interfaz en el script y regenerar el juego. No se presupone
una conexion en directo entre GeoGebra y un proceso Python durante la partida.

## Requisitos del juego

### Tres comodines por equipo

Cada equipo empieza con uno de cada tipo. Cada comodin se consume una sola
vez por equipo y por partida, no una vez por pregunta.

- [x] **Pasapalabra:** pasar el turno sin eliminar al equipo, con un reto nuevo para el siguiente. Mantener el comportamiento de la version anterior.
- [x] **Tiempo extra:** sumar 20 segundos por defecto a la cuenta restante del reto actual.
- [x] Permitir configurar los segundos del tiempo extra en la pantalla inicial, por separado del tiempo normal por reto.
- [x] **Eliminar una incorrecta:** desactivar exactamente una respuesta incorrecta del reto actual, elegida entre las disponibles, sin eliminar nunca la correcta.
- [x] Mantener separados el consumo de cada equipo y los efectos temporales sobre cada reto.
- [x] Mostrar los comodines disponibles y consumidos de cada equipo.
- [x] Usar iconos pequenos y reconocibles: flecha para pasar, reloj con mas para ampliar tiempo y una opcion tachada para descartar.
- [x] Incorporar nombres al pasar el raton y areas de pulsacion de 40 por 40 pixeles; comprobar su apariencia en Portable en la fase 4.
- [x] Comprobar que los PNG se incluyen en el `.ggb`, sin recursos remotos ni fuentes de emojis.
- [x] Impedir usos repetidos, clics de otros equipos o usos con el reto ya cerrado.
- [x] Si se juega sin limite de tiempo, desactivar el tiempo extra sin consumirlo.

### Puntuacion y eliminacion

- [x] Mostrar **un punto por cada respuesta acertada** en el marcador de cada equipo, manteniendo la regla del contador anterior.
- [x] Evitar sumar puntos mas de una vez con dobles clics o actualizaciones del reloj.
- [x] Conservar los puntos de los equipos eliminados y de los que revivan.
- [x] Al responder mal, eliminar al equipo y cerrar su respuesta al reto.
- [x] Corregir en la version nueva el comportamiento del reloj: al llegar a cero con una respuesta pendiente, eliminar automaticamente al equipo, detener el reloj y cerrar el intento.
- [x] Con tiempo inicial 0, mantener el modo sin limite y sin eliminacion por reloj.

En los juegos anteriores, agotar el tiempo solo muestra un aviso. Ese
comportamiento se conserva alli para no modificar las versiones ya existentes.

### Oportunidad de revivir

- [x] Dar a cada equipo una oportunidad extra de revivir, utilizable una sola vez por partida mientras este eliminado.
- [x] Tras el fallo de otro equipo, permitir que el profesor elija a un equipo eliminado que haya levantado la mano.
- [x] Incluir un boton pequeno de **anadir (+)** que abra la seleccion de equipos eliminados con oportunidad disponible.
- [x] No reincorporar al equipo solo por seleccionarlo: debe responder correctamente.
- [x] Consumir la oportunidad al comenzar el intento; un fallo lo mantiene eliminado y no devuelve el comodin.
- [x] Si acierta, devolverlo a los turnos activos y conservar su puntuacion.
- [x] Al revivir, dejar indisponibles los tres comodines iniciales, incluso los que no hubiera gastado.
- [x] No permitir comodines iniciales durante el propio intento de revivir.
- [x] Permitir al profesor continuar sin conceder un intento.
- [x] Evitar cerrar la partida antes de resolver la posible oportunidad de revivir, incluso si solo queda un equipo activo.
- [x] Restaurar correctamente el orden de turnos al finalizar el intento.

Regla confirmada y criterios para esta fase:

- [x] El intento usa la **misma pregunta fallada**, manteniendo desactivada la opcion incorrecta que se acaba de elegir y la que se hubiera descartado con el comodin. Quedaran al menos dos opciones al iniciar el intento. La solucion y la explicacion permanecen ocultas hasta que este termine o el profesor decida continuar sin intento.
- Un acierto al intentar revivir suma tambien un punto, aplicando la regla general.
- Agotar el tiempo cuenta como fallo y permite ofrecer una oportunidad de revivir.
- Como maximo se ofrece un intento de revivir por fallo de un turno normal; no se encadenan intentos por el fallo de otro intento de revivir.
- El equipo que acaba de fallar no puede revivir por su propio fallo: la oportunidad corresponde a los que ya estaban eliminados.

### Aviso suave al fallar

- [x] Dar una senal visual discreta al fallar o agotarse el tiempo.
- [x] Usar un tono rosado tenue en la zona de estado, sin sacudidas, destellos, sonidos ni movimientos bruscos.
- [x] Ocultar tambien la senal al pausar; el color se restablece con la siguiente accion de juego.

### Pausa con pantalla oculta

- [x] Incorporar un control pequeno de pausa y reanudacion accesible al profesor.
- [x] Al pausar, ocultar todo el contenido del juego: pregunta, opciones, solucion, grupos, puntos y comodines.
- [x] Mostrar una pantalla neutra con solo el control necesario para reanudar.
- [x] Congelar el tiempo restante y bloquear respuestas, turnos y consumo de comodines.
- [x] Al reanudar, recuperar exactamente el estado y tiempo anteriores, sin contar el tiempo pasado en pausa.
- [x] Permitir pausar tambien durante un intento de revivir.
- [x] Configurar el archivo para abrir solo la vista grafica, sin panel algebraico ni entrada.

## Fases de trabajo

### Fase 1: base nueva, reloj, puntos y pausa

- [x] Crear el script y archivo nuevos con el banco de naturales y generacion sin efectos sobre los anteriores.
- [x] Definir los estados de inicio, pregunta activa, respuesta cerrada, pausa y fin de partida, preparando el estado de intento de revivir.
- [x] Implementar eliminacion por tiempo, puntuacion y pausa real con ocultacion.
- [x] Probar automaticamente acierto, fallo, tiempo agotado y pausa; prueba interactiva en fase 4.

Resultado esperado: una primera version jugable y reproducible desde Python,
con el reloj y los cambios de estado comprobados.

### Fase 2: comodines e iconos

- [x] Incorporar los tres comodines con consumo independiente por equipo.
- [x] Anadir la configuracion inicial del tiempo extra y sus iconos compactos.
- [x] Verificar en las pruebas que ampliar el tiempo conserva lo transcurrido; la velocidad nativa tiene un intervalo fijo.
- [x] Probar automaticamente segundo uso, cambio de turno, pausa, tiempo sin limite y nuevo reto.

Resultado esperado: cada equipo puede gastar una vez cada ayuda y el marcador
refleja lo que le queda.

### Fase 3: revivir con control del profesor

- [x] Confirmar que se utiliza la misma pregunta y se conservan las opciones descartadas.
- [x] Concretar y documentar los demas criterios del intento de revivir.
- [x] Incorporar el boton de anadir, la seleccion del equipo y el intento.
- [x] Integrar puntuacion, reloj, pausa, turnos y retirada de comodines al revivir.
- [x] Probar automaticamente acierto, fallo, tiempo agotado, oportunidad ya consumida y continuacion sin intento.
- [x] Comprobar en las pruebas el final de partida con cero o un equipo activo y con posibles intentos de revivir.

Resultado esperado: el profesor puede conceder una oportunidad sin regalar
la respuesta ni alterar incorrectamente los turnos o puntos.

### Fase 4: comprobacion para el aula y documentacion

- [x] Ejecutar `python3 -m py_compile` sobre el nuevo script y regenerar su `.ggb`.
- [x] Comprobar ZIP/XML, referencias, scripts y recursos incorporados al archivo.
- [x] Verificar las transiciones importantes del juego y que generar la nueva version no modifica los archivos anteriores.
- [ ] Probar en GeoGebra Classic 5 Portable con wifi desconectado y pantalla completa.
- [ ] Revisar legibilidad y ausencia de solapamientos en el portatil y en la pizarra, con 2 y con 8 equipos.
- [x] Probar automaticamente reinicio de partida, agotamiento del banco de preguntas y restablecimiento de comodines y puntos.
- [x] Documentar como regenerar el juego y las reglas definitivas; actualizar este TODO con lo realmente comprobado.

Las comprobaciones automaticas del archivo no sustituyen las pruebas
interactivas de GeoGebra. Se anotaran por separado las que se hayan ejecutado
y las que queden pendientes en el portatil o la pizarra.
