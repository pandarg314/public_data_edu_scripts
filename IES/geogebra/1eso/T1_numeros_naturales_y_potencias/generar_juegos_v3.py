#!/usr/bin/env python3
"""Genera las copias v3 de Potencias y Operaciones; no modifica los originales.

    python3 generar_juegos_v3.py --dry-run
    python3 generar_juegos_v3.py
    python3 generar_juegos_v3.py --juego operaciones
"""

import argparse
import hashlib
from pathlib import Path

import generar_naturales_v3 as base
from generar_juegos import OPERACIONES, POTENCIAS

AQUI = Path(__file__).resolve().parent
JUEGOS = {
    "potencias": {
        "archivo": "juego_potencias_1eso_v3.ggb",
        "titulo": "POTENCIAS  |  1 ESO",
        "retos": POTENCIAS,
        "niveles": (),
    },
    "operaciones": {
        "archivo": "juego_operaciones_niveles_1eso_v3.ggb",
        "titulo": "OPERACIONES  |  1 ESO",
        "retos": [dict(reto, nivel=index) for index, (_, retos) in enumerate(OPERACIONES, 1) for reto in retos],
        "niveles": tuple(nombre for nombre, _ in OPERACIONES),
    },
}


def construir(juego):
    config = JUEGOS[juego]
    return base.construir(config["retos"], config["titulo"], config["niveles"], expression_y=160)


def guardar(juego, path=None):
    return base.guardar(path if path is not None else AQUI / JUEGOS[juego]["archivo"], construir(juego))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--juego", choices=["todos", *JUEGOS], default="todos")
    parser.add_argument("--dry-run", action="store_true", help="validar sin escribir archivos")
    args = parser.parse_args()
    for juego in JUEGOS if args.juego == "todos" else [args.juego]:
        config = JUEGOS[juego]
        contents = construir(juego)
        if args.dry_run:
            print(f"Validado: {config['archivo']}, {len(config['retos'])} retos; no se escribe ningun archivo.")
        else:
            path = base.guardar(AQUI / config["archivo"], contents)
            print(f"{path.name}: {len(config['retos'])} retos, version 3.")
            print("SHA256:", hashlib.sha256(path.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
