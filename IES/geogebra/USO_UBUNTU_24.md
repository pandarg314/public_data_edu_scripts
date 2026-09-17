# GeoGebra en Ubuntu 24.04: portatil y pizarra digital

Registro de la puesta en marcha del 16 de septiembre de 2026. El objetivo es
abrir los juegos `.ggb` guardados en el portatil y proyectarlos en la pizarra
digital, incluso si falla internet en el instituto.

## Version elegida

Se ha utilizado **GeoGebra Classic 5 Portable para Linux de 64 bits**, archivo
`GeoGebra-Linux-Portable-5-4-930-2.tar.bz2`. El
[manual oficial de instalacion](https://geogebra.github.io/docs/reference/en/GeoGebra_Installation/)
enlaza la [descarga de Linux Portable](https://download.geogebra.org/package/linux-port),
aunque marca esta distribucion Linux como **sin soporte**.

Tambien se consultaron estas alternativas:

- [Consulta sobre GeoGebra 6 en Ask Ubuntu](https://askubuntu.com/questions/1523589/install-geogebra-6-in-ubuntu-22-04): referencia de la conversacion; no se siguio esa via de instalacion.
- [GeoGebra Discovery en Snapcraft](https://snapcraft.io/install/geogebra-discovery/ubuntu): su editor lo describe como experimental y no destinado todavia al uso diario. Se descarto para este uso en clase.

## Carpeta real y primera ejecucion

El archivo descargado se localizo fuera del proyecto, en:

```text
/home/pandargdell/ferramentes/ies_ferramentes/GeoGebra-Linux-Portable-5-4-930-2.tar.bz2
```

Las primeras instrucciones suponian que estaba en `~/Downloads`; esta es la
ruta corregida y comprobada. Dentro del archivo se verificaron el lanzador
`geogebra-portable` y el entorno Java incluido. No hace falta instalar Java
por separado ni usar `sudo`.

Estos fueron los comandos para descomprimir y arrancar, ejecutados en una
terminal de Ubuntu:

```bash
cd ~/ferramentes/ies_ferramentes
tar -xjf GeoGebra-Linux-Portable-5-4-930-2.tar.bz2
cd GeoGebra-Linux-Portable-5-4-930-2
chmod +x geogebra-portable
./geogebra-portable
```

**El usuario confirmo que GeoGebra abre y funciona.** La aplicacion queda en
esa carpeta externa al proyecto. El `.tar.bz2` es un archivo comprimido: se
extrae y se ejecuta el lanzador; no se instala con `apt`.

Para abrirlo otro dia, basta con este comando desde cualquier carpeta:

```bash
~/ferramentes/ies_ferramentes/GeoGebra-Linux-Portable-5-4-930-2/geogebra-portable
```

## Pantalla completa y dock

El dock tapaba parte de la ventana. Ubuntu permite asignar un atajo para
alternar la pantalla completa de la ventana activa; por defecto esta sin
asignar. Vease la [documentacion de atajos de Ubuntu](https://help.ubuntu.com/stable/ubuntu-help/keyboard-shortcuts-set.html).

1. Abrir una terminal con **Ctrl + Alt + T**. Puede estar en cualquier carpeta.
2. Pegar el siguiente comando entero y pulsar **Intro** una vez. No usar `sudo`.

```bash
gsettings set org.gnome.desktop.wm.keybindings toggle-fullscreen "['<Super>F11']"
```

El comando ocupa **una sola linea real**. Si la terminal lo muestra repartido
en dos renglones por falta de ancho, no pasa nada. No se debe introducir un
salto de linea entre `toggle-fullscreen` y `"['<Super>F11']"`: son partes del
mismo comando. Si ya se ejecuto partido, volver a pegar la linea completa.

Volver a GeoGebra y pulsar **Super + F11**. Super es la tecla con el logo de
Windows. La misma combinacion permite salir de pantalla completa. El ajuste
se guarda para el usuario y no hay que repetir el comando en cada arranque.

**El usuario confirmo que la pantalla completa funciona.**

La alternativa grafica esta en **Configuracion > Teclado > Ver y personalizar
atajos > Ventanas > Alternar el modo de pantalla completa**.

Para consultar la asignacion actual:

```bash
gsettings get org.gnome.desktop.wm.keybindings toggle-fullscreen
```

Para volver al valor predeterminado:

```bash
gsettings reset org.gnome.desktop.wm.keybindings toggle-fullscreen
```

**Super + Flecha arriba** o **Alt + F10** maximizan la ventana, pero conservan
las barras del escritorio. Es distinto de la pantalla completa.
[Documentacion de maximizacion de Ubuntu](https://help.ubuntu.com/stable/ubuntu-help/shell-windows-maximize.html.en).

## Juegos locales y correccion del temporizador

Desde **Archivo > Abre** se pueden seleccionar los juegos de
[`1eso/T1_numeros_naturales_y_potencias/`](1eso/T1_numeros_naturales_y_potencias/),
carpeta relativa a este documento:

- `juego_numeros_naturales_1eso.ggb`.
- `juego_potencias_1eso.ggb`.
- `juego_operaciones_niveles_1eso.ggb`.

Se habia observado que la cuenta atras no avanzaba al probar un par de juegos
en la web. Se modifico `generar_juegos.py` y se regeneraron los tres `.ggb`
para sustituir el reloj JavaScript basado en `setInterval` por una animacion
nativa de GeoGebra. El deslizador oculto `transcurrido` determina el tiempo
`restante`; ya no se incluye JavaScript global en los archivos.

El reloj se reinicia al empezar, pasar palabra o cambiar de reto. Se detiene
al responder, volver al inicio o agotarse el tiempo. Con tiempo 0 se juega
sin limite. Al llegar a cero aparece el aviso de tiempo agotado; no elimina
automaticamente al grupo ni bloquea su respuesta. Es un reloj aproximado
para el aula.

La validacion anterior comprobo la sintaxis de Python y la estructura ZIP/XML
de los tres archivos. Eso no sustituye la prueba interactiva. Los detalles y
las instrucciones para regenerarlos estan en el
[README del tema](1eso/T1_numeros_naturales_y_potencias/README.md).

## Prueba pendiente antes de clase

El arranque de GeoGebra y el atajo de pantalla completa estan confirmados.
Queda comprobar los juegos sin wifi y en la pizarra. El usuario ha senalado
que agotar el tiempo debe eliminar al equipo: ese cambio y las nuevas reglas
se recogen en el [TODO de la version 2](TODO.md), en un script y juego nuevos.

1. Conectar el portatil a la pizarra digital y activar la pantalla completa.
2. Desconectar el wifi y abrir cada uno de los tres juegos locales.
3. Elegir 5 segundos, empezar y comprobar que la cuenta baja hasta cero.
4. Comprobar el reinicio con **Siguiente reto** y **PASAPALABRA**.
5. Responder antes de que acabe el tiempo y comprobar que el reloj se detiene.
6. Volver al inicio y probar una partida con tiempo 0, sin cuenta atras.
7. Comprobar en la pizarra que se ven completos los botones y el marcador.

La aplicacion portable y estos juegos locales permiten trabajar sin internet
una vez descargados; las funciones de servicios en linea quedan fuera de
esta prueba.
