# Juegos GeoGebra por cursos

Este repositorio organiza juegos de GeoGebra para ESO. La idea principal no es usar GeoGebra solo para explicar, sino como arbitro de retos competitivos en clase.

## Contexto de aula

- La clase trabaja en grupos de 2 a 4 personas.
- Hay una pizarra digital: todos ven la misma pantalla.
- El profesor controla el GeoGebra o da turno a un grupo para responder.
- Cada ronda muestra un unico reto comun para todos.
- El grupo que responde debe elegir una opcion cerrada.
- Si acierta, sigue jugando. Si falla, queda eliminado.

## Formato comun de los juegos

Cada `.ggb` deberia seguir esta plantilla:

- Banco de retos del tema.
- Reto elegido al azar, no en orden fijo.
- Enunciado visual grande: grafica, figura, recta, region, expresion o tabla.
- Opciones de respuesta visibles con casillas.
- Una unica respuesta correcta.
- Correccion inmediata: correcto o incorrecto.
- Boton de nuevo reto que vuelva a sortear.
- Opcional: temporizador para limitar la decision del grupo.

## Reglas de diseno

- Todo debe leerse bien desde la pizarra digital.
- Pocas opciones, pero bien elegidas: normalmente 3 a 6.
- Distractores utiles: errores tipicos del alumnado.
- Nada debe depender de que cada alumno tenga su propio dispositivo.
- El juego debe poder jugarse oralmente por turnos.
- La aleatoriedad es importante para que no se memorice el orden.
- Tras responder, conviene bloquear o dejar clara la respuesta antes de pasar al siguiente reto.

## Estructura por cursos

- `1eso/`: juegos de 1 ESO (T1 números naturales y potencias).
- `2eso/`: juegos existentes de rectas y geometria.
- `3eso/`: juegos futuros de 3 ESO.
- `4eso/`: estructura por temas de 4 ESO.

## Estado actual

- En `1eso/T1_numeros_naturales_y_potencias/` hay tres juegos (naturales, potencias y operaciones combinadas en 3 niveles) generados con `generar_juegos.py`. Incluyen marcador por grupos, turnos, pasapalabra (una vez por grupo), retos sin repetir y cronómetro.
- En `2eso/` hay juegos de rectas/geometria con opciones por ejercicio. Sirven como referencia, aunque necesitan mejorar la aleatoriedad al pasar de reto.
- En `4eso/T7_y_T8_funciones/01_reconocer_por_la_grafica/` hay juegos de reconocimiento de funciones por la grafica. Son la referencia principal para la filosofia eliminatoria.

## Ideas base por tipo de contenido

- Graficas: identificar funcion, familia, pendiente, transformacion o parametros.
- Figuras: reconocer tipo, propiedad, longitud, angulo o razon.
- Rectas y regiones: elegir ecuacion, solucion, interseccion o desigualdad.
- Expresiones: elegir forma equivalente, factorizacion, dominio o raiz.
- Datos: elegir medida, grafico correcto o conclusion.

## Modo torneo

Una partida puede funcionar asi:

1. Se forman los grupos.
2. GeoGebra sortea un reto.
3. Un grupo responde eligiendo una casilla.
4. Si acierta, permanece.
5. Si falla, queda eliminado.
6. Se pulsa nuevo reto.
7. Gana el ultimo grupo vivo o el grupo con mas aciertos.
