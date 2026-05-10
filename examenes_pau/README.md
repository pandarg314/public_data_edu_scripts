# Examenes PAU

Carpeta para recopilar examenes oficiales PAU/EvAU y convertirlos en material de planificacion de clases.

## Matematicas

Fuentes iniciales: UC3M, paginas de examenes de Matematicas II y de Matematicas Aplicadas a las Ciencias Sociales II.

```bash
python3 examenes_pau/scripts/descargar_matematicas.py --dry-run
python3 examenes_pau/scripts/descargar_matematicas.py
```

Estructura de salida:

- `matematicas/matematicas_ii/`
- `matematicas/matematicas_aplicadas_ccss_ii/`

Cada materia contiene:

- `modelos_de_examen/`
- `convocatoria_ordinaria/`
- `convocatoria_extraordinaria/`
- `manifest.csv`

El manifiesto registra materia, titulo, seccion, URL original, URL de descarga, ruta local, estado, hash y tamano.

Para generar PDFs compilados listos para imprimir, con marca superior por tipo de examen y sin paginas de criterios de correccion, orientaciones, tablas de distribucion normal ni paginas en blanco:

```bash
python3 examenes_pau/scripts/crear_pdfs_impresion_matematicas.py
```

La salida se escribe en `matematicas/impresion/`, con un PDF por via.

## Nota rapida

- `modelos_de_examen/`: prototipos oficiales de formato; no son examenes celebrados. Pueden incluir criterios y soluciones orientativas.
- `convocatoria_ordinaria/` y `convocatoria_extraordinaria/`: examenes oficiales realizados.
- Archivos con `coincidencias`: versiones oficiales alternativas para alumnado con solapes horarios o incidencias.
- UC3M publica estos PDFs, pero el encabezado corresponde a las Universidades Publicas de la Comunidad de Madrid.
