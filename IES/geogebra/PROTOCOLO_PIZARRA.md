# Protocolo de diseno y prueba en pizarra digital

Registrado el 18 de septiembre de 2026. Criterios comunes para los juegos de
esta carpeta, tanto nuevos como actualizados. Este documento fija el protocolo;
no implica que los archivos existentes ya lo cumplan. El estado de cada
adaptacion se registra en [TODO.md](TODO.md).

## Zona segura

- Reservar una franja vacia en los cuatro bordes de la vista del juego, sin
  preguntas, respuestas, marcadores ni controles propios de la partida.
- Partir de un **5 % del ancho a izquierda y derecha y un 5 % del alto arriba
  y abajo**, con un minimo de 40 pixeles por lado. Es un criterio de este
  proyecto, ajustable tras la prueba real, no una garantia frente a cualquier
  recorte ni una especificacion de GeoGebra.
- Calcular el espacio sobre la vista grafica disponible, descontando menus,
  barras y paneles. La resolucion del escritorio no es el tamano de esa vista.
- Mantener dentro de la zona segura el elemento completo y su area de clic,
  no solo su punto de anclaje. Comprobar formulas, textos de varias lineas,
  reloj ampliado, cruces, copas y marcador de ocho equipos.
- La franja puede tener el mismo fondo que el juego. Dibujar un marco sin
  desplazar el contenido no proporciona proteccion.
- Reorganizar el conjunto para que quepa: sumar un desplazamiento a todas las
  coordenadas puede proteger un lado y recortar el contrario. Centralizar el
  margen y contemplar tambien las posiciones que actualiza JavaScript.
- Conservar textos legibles y controles principales con areas de clic de al
  menos 40 por 40 pixeles. No encoger indiscriminadamente el juego para hacerlo
  caber. Registrar la resolucion minima comprobada y las limitaciones.
- Aplicar el criterio a configuracion, partida, rescate, pausa, confirmaciones
  y resultados. Pausa, reanudar, siguiente ronda y fin de partida deben ser
  accesibles cuando corresponda, sin depender de controles de GeoGebra pegados
  al borde exterior.

## Dos pausas diferentes

GeoGebra puede mostrar un boton nativo de animacion en la esquina inferior
izquierda de la vista grafica. Detiene o reanuda animaciones; no es el control
de pausa del juego. Su ubicacion esta descrita en el
[manual de animacion de GeoGebra](https://geogebra.github.io/docs/manual/en/Animation/).

En los juegos v3, la **pausa propia esta arriba a la derecha**, junto al
reinicio: oculta el contenido, bloquea las acciones y congela el reloj. Es la
que se debe usar para interrumpir la clase. Mover los objetos de nuestro juego
no desplaza el boton nativo de la esquina. La pausa propia tambien debe quedar
dentro de la zona segura al adaptar la interfaz.

## Diagnostico de bordes recortados

La incidencia inicial es que en la pizarra no se veia el pequeno control
inferior izquierdo. La captura aportada es del portatil: permite identificar
el control, pero no confirmar como se ve la imagen en la pizarra.

1. Comparar portatil y pizarra mostrando el escritorio y otra aplicacion. Si
   tambien pierden bordes, revisar primero la salida de video y la pantalla.
   Si solo ocurre con GeoGebra, revisar su ventana, paneles y espacio de dibujo.
2. Anotar modelo de pizarra/proyector, conexion, modo duplicado o extendido,
   resolucion y escala. En Ubuntu se consultan las pantallas en Configuracion;
   duplicar usa la misma resolucion y orientacion en ambas, segun la
   [documentacion de Ubuntu](https://help.ubuntu.com/stable/ubuntu-help/display-dual-monitors.html.en).
3. Consultar el manual del modelo para comprobar recorte de bordes u
   **overscan** y relacion de aspecto/zoom. Overscan puede recortar una salida
   externa; es una posibilidad, no el diagnostico confirmado. La
   [explicacion de Intel](https://www.intel.com/content/www/us/en/support/articles/000057043/graphics.html)
   describe el problema; sus pasos de software para Windows no se aplican a
   nuestro Ubuntu. No cambiar ajustes ni controladores a ciegas.
4. Comprobar los cuatro extremos mirando la pizarra real. Una foto que incluya
   el marco fisico ayuda a mostrar lo que una captura del portatil no registra.
5. Usar el margen del juego como proteccion adicional. Si el recorte supera
   esa franja, corregir la proyeccion o revisar el margen medido.

## Pruebas antes de dar por terminada una version

- [ ] Abrir el `.ggb` local con GeoGebra Classic 5 Portable y wifi desconectado.
- [ ] Probar pantalla completa, usando el atajo registrado en
  [USO_UBUNTU_24.md](USO_UBUNTU_24.md), con la pizarra conectada.
- [ ] Revisar 1366 por 768 y 1280 por 720 como escenarios iniciales, ademas de
  la resolucion real del aula. No darlos por compatibles sin probarlos; anotar
  el tamano de la vista grafica y la escala en cada caso.
- [ ] Recorrer configuracion, partida con dos y ocho equipos, pausa/reanudacion,
  rescate, confirmaciones y resultados con empates.
- [ ] Revisar preguntas y explicaciones largas, todas las opciones, los ultimos
  diez segundos, comodines gastados y descartes. Nada debe solaparse ni entrar
  en la franja de seguridad.
- [ ] Comprobar que cada control visible responde al clic y que pausar oculta
  realmente la pregunta y conserva el tiempo.
- [ ] Comprobar legibilidad desde el fondo del aula y las cuatro esquinas en
  la pizarra, no solo en el portatil.
- [ ] Guardar fecha, archivos/versiones, equipo, resolucion, escala, resultado
  y pendientes. Distinguir pruebas automaticas, revision en Portable y prueba
  fisica en aula; ninguna sustituye a las otras.

## Estado inicial

Los tres juegos v3 comparten un diseno de coordenadas absolutas, con vista de
referencia de 1180 por 650 pixeles. Algunos objetos quedan muy cerca del borde,
por ejemplo la pausa a 12 pixeles del superior. **Todavia no incorporan el
margen de este protocolo.** Queda adaptar el generador y las posiciones
dinamicas, regenerar los tres juegos y comprobarlos en la pizarra. En este
registro no se han modificado los `.ggb` ni la configuracion de Ubuntu.
