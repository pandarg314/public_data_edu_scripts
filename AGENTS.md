# AGENTS.md

- Mantener el repositorio orientado a docencia de matematicas en instituto: datos publicos, visualizacion, pensamiento critico y preparacion PAU.
- Preferir scripts reproducibles en `scripts/` y salidas en `datos/`, con rutas relativas al repo.
- Evitar dependencias externas si la biblioteca estandar resuelve bien el caso; documentar cualquier dependencia nueva.
- Para la linea PAU, usar `examenes_pau/`: scripts en `examenes_pau/scripts/`, PDFs y manifiestos en subcarpetas claras por materia, via de matematicas y convocatoria.
- Validar cambios de Python con `python3 -m py_compile` y, cuando haya red disponible, con `--dry-run` antes de descargar.
