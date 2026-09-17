#!/usr/bin/env python3
"""Genera solo la version 2 de naturales; biblioteca estandar, sin descargas.

    python3 generar_naturales_v2.py
    python3 generar_naturales_v2.py --dry-run

El banco parte de NATURALES en generar_juegos.py y sustituye los romanos por
retos nuevos en RETOS_V2. Las reglas e interaccion estan en naturales_v2.js
y se incorporan al .ggb junto con todos los iconos.
"""

import argparse
import hashlib
import json
import math
import random
import re
import struct
import textwrap
import xml.etree.ElementTree as ET
import zipfile
import zlib
from pathlib import Path

from generar_juegos import NATURALES, construir_xml

AQUI = Path(__file__).resolve().parent
SALIDA = AQUI / "juego_numeros_naturales_1eso_v2.ggb"
REGLAS = AQUI / "naturales_v2.js"
LICENCIA = AQUI / "recursos_naturales_v2" / "LICENSE-Lucide.txt"

RETOS_V2 = [reto for reto in NATURALES if "romanos" not in reto["tema"].casefold()] + [
    dict(tema="C\u00e1lculo mental", pregunta="Calcula mentalmente:",
         expr=r"125 \cdot 8", ok=r"1\,000", malas=["133", "900", r"10\,000"],
         expl=r"125 \cdot 8 = (125 \cdot 4) \cdot 2 = 500 \cdot 2 = 1\,000"),
    dict(tema="Problemas",
         pregunta="Repartimos 168 libros por igual en 7 estantes. "
                  "\u00bfCu\u00e1ntos libros van en cada estante?",
         expr="", ok="24", malas=["21", "23", "28"],
         expl=r"168 : 7 = 24,\qquad 7 \cdot 24 = 168"),
]

# Geometria de iconos Lucide (ISC/MIT), adaptada a un raster de trazo redondo.
# Cada secuencia es una polilinea; las circunferencias se muestrean al generar.
ICONOS = {
    "pass": [[(5, 4), (15, 12), (5, 20), (5, 4)], [(19, 4), (19, 20)]],
    "time": [[(12, 8), (12, 12), (15, 14)], [(17, 4), (20, 4)], [(18.5, 2.5), (18.5, 5.5)]],
    "remove": [[(3, 6), (10, 6)], [(3, 12), (10, 12)], [(3, 18), (17, 18)], [(16, 6), (22, 12)], [(22, 6), (16, 12)]],
    "plus": [[(12, 5), (12, 19)], [(5, 12), (19, 12)]],
    "minus": [[(5, 12), (19, 12)]],
    "pause": [[(8, 5), (8, 19)], [(16, 5), (16, 19)]],
    "play": [[(7, 4), (20, 12), (7, 20), (7, 4)]],
    "next": [[(5, 12), (19, 12)], [(12, 5), (19, 12), (12, 19)]],
    "reset": [[(3, 4), (3, 10), (9, 10)]],
    "revive": [[(12, 7), (12, 17)], [(7, 12), (17, 12)]],
}


def arco(cx, cy, radius, start=0, end=2 * math.pi):
    return [(cx + radius * math.cos(start + (end - start) * i / 64),
             cy + radius * math.sin(start + (end - start) * i / 64)) for i in range(65)]


def icono_png(nombre, size=40, apagado=False, marco=False, width=None):
    """PNG RGBA antialias de iconos pequenos, sin Pillow ni fuentes externas."""
    width = width or size
    paths = list(ICONOS[nombre])
    if nombre == "time":
        paths.append(arco(11, 13, 8))
    elif nombre == "revive":
        paths.append(arco(12, 12, 10))
    elif nombre == "reset":
        paths.append(arco(12, 12, 8, -2.7, 2.2))
    segments = [(a, b) for path in paths for a, b in zip(path, path[1:])]
    color = (182, 188, 193) if apagado else (42, 91, 100)
    borde = (194, 202, 206) if apagado else (102, 133, 141)
    fondo = (242, 244, 245) if apagado else (245, 249, 250)

    def distance(x, y, a, b):
        dx, dy = b[0] - a[0], b[1] - a[1]
        t = max(0, min(1, ((x - a[0]) * dx + (y - a[1]) * dy) / (dx * dx + dy * dy)))
        return math.hypot(x - a[0] - t * dx, y - a[1] - t * dy)

    data = bytearray()
    # Los controles tienen 40 px de area y un dibujo de 24 px.
    drawing = 24 if size == 40 else size - 2
    margin = (size - drawing) / 2
    for y in range(size):
        data.append(0)
        for x in range(width):
            px, py = (x + 0.5 - margin) * 24 / drawing, (y + 0.5 - margin) * 24 / drawing
            d = min(distance(px, py, a, b) for a, b in segments)
            alpha = round(255 * max(0, min(1, (1.1 - d) * drawing / 24 + 0.5)))
            edge = min(x, y, width - 1 - x, size - 1 - y)
            if marco and edge >= 1:
                background = borde if edge == 1 else fondo
                pixel = tuple(round((c * alpha + bg * (255 - alpha)) / 255)
                              for c, bg in zip(color, background))
                data.extend((*pixel, 255))
            else:
                data.extend((*color, alpha))

    def chunk(kind, payload):
        return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", zlib.crc32(kind + payload))

    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, size, 8, 6, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(data)) + chunk(b"IEND", b""))


def explicacion_latex(value):
    """Parte las explicaciones sin cortar comandos ni grupos de LaTeX."""
    tokens = []
    for token in re.findall(r"\\text\{[^}]*\}|\\[,;! ]|[^ ]+", value):
        if token.startswith(r"\text{"):
            tokens.extend(r"\text{" + word + " }" for word in token[6:-1].split())
        else:
            tokens.append(token)
    lines, current, width = [], [], 0
    for token in tokens:
        length = len(re.sub(r"\\[a-zA-Z]+|[{}]", "", token)) + 1
        if current and width + length > 68:
            lines.append(" ".join(current))
            current, width = [], 0
        current.append(token)
        width += length
    if current:
        lines.append(" ".join(current))
    return r"\begin{array}{l}" + r" \\ ".join(lines) + r"\end{array}"


def banco():
    rng = random.Random(1)
    letters = [k % 4 for k in range(len(RETOS_V2))]
    rng.shuffle(letters)
    result = []
    for index, question in enumerate(RETOS_V2):
        options = list(question["malas"])
        if len(options) != 3 or len(set(options + [question["ok"]])) != 4:
            raise ValueError(f"Reto {index + 1}: opciones repetidas")
        rng.shuffle(options)
        options.insert(letters[index], question["ok"])
        result.append(dict(topic=question["tema"], question="\n".join(textwrap.wrap(question["pregunta"], 63)),
                           expression=question["expr"], options=options, correct=letters[index],
                           explanation=explicacion_latex(question["expl"])))
    return result


class Pantalla:
    def __init__(self, construction):
        self.construction = construction
        self.labels = []
        self.resources = {}

    def element(self, label, kind, x, y, action=None, tooltip=None):
        self.labels.append(label)
        element = ET.SubElement(self.construction, "element", type=kind, label=label)
        # En botones, label controla el texto; en imagenes, alpha es la opacidad.
        ET.SubElement(element, "show", object="false", label="true" if kind == "button" else "false")
        ET.SubElement(element, "objColor", r="36", g="43", b="48", alpha="1" if kind == "image" else "0")
        ET.SubElement(element, "layer", val="5")
        ET.SubElement(element, "fixed", val="true")
        ET.SubElement(element, "auxiliary", val="true")
        ET.SubElement(element, "selectionAllowed", val="true" if action else "false")
        ET.SubElement(element, "absoluteScreenLocation", x=str(x), y=str(y))
        if action:
            ET.SubElement(element, "javascript", val=action)
        if tooltip:
            ET.SubElement(element, "caption", val=tooltip)
            ET.SubElement(element, "tooltipMode", val="3")
        else:
            ET.SubElement(element, "tooltipMode", val="2")
        return element

    def text(self, label, x, y, value="", size=1, bold=False, latex=False, action=None):
        ET.SubElement(self.construction, "expression", label=label, exp=json.dumps(value, ensure_ascii=False))
        element = self.element(label, "text", x, y, action)
        ET.SubElement(element, "font", serif="false", sizeM=str(size), size="0", style="1" if bold else "0")
        if latex:
            ET.SubElement(element, "isLaTeX", val="true")

    def button(self, label, caption, x, y, action, width=180):
        element = self.element(label, "button", x, y, action)
        ET.SubElement(element, "caption", val=caption)
        ET.SubElement(element, "bgColor", r="225", g="238", b="236", alpha="255")
        ET.SubElement(element, "font", serif="false", sizeM="1.15", size="0", style="1")
        ET.SubElement(element, "dimensions", width=str(width), height="40")

    def icon(self, label, kind, x, y, tooltip, action=None, size=40, off=False, marco=False, width=None):
        variant = f"-marco{width or size}" if marco else ""
        resource = f"icons/{kind}-{size}-{'off' if off else 'on'}{variant}.png"
        if resource not in self.resources:
            self.resources[resource] = icono_png(kind, size, off, marco, width)
        # GeoGebra fija las imagenes por su esquina inferior izquierda.
        element = self.element(label, "image", x, y + size, action, tooltip)
        ET.SubElement(element, "file", name=resource)
        ET.SubElement(element, "inBackground", val="false")
        ET.SubElement(element, "interpolate", val="true")

    def help_icon(self, label, kind, x, y, tooltip, action=None, size=40, marco=False, width=None):
        self.icon(label, kind, x, y, tooltip, action, size, marco=marco, width=width)
        self.icon(label + "Off", kind, x, y, tooltip + " (no disponible)",
                  size=size, off=True, marco=marco, width=width)


def construir():
    # Reutilizar la configuracion XML del generador previo sin ejecutar su main.
    root = ET.fromstring(construir_xml("Numeros naturales - version 2", RETOS_V2, 1))
    construction = root.find("construction")
    construction.clear()
    construction.set("title", "Numeros naturales - 1 ESO - v2")
    root.find("gui/window").attrib.update(width="1180", height="690")
    root.find("euclidianView/size").attrib.update(width="1180", height="650")
    root.find("euclidianView/bgColor").attrib.update(r="250", g="251", b="252")
    for node in root.findall("gui/perspectives/perspective/views/view"):
        if node.get("id") == "1":
            node.set("size", "1180")
    ET.SubElement(construction, "expression", label="reloj", exp="0")
    clock = ET.SubElement(construction, "element", type="numeric", label="reloj")
    ET.SubElement(clock, "value", val="0")
    ET.SubElement(clock, "show", object="false", label="false")
    ET.SubElement(clock, "auxiliary", val="true")
    ET.SubElement(clock, "slider", min="0", max="600", absoluteScreenLocation="true",
                  width="100", x="0", y="0", fixed="true", horizontal="true")
    ET.SubElement(clock, "animation", step="0.05", speed="10 / 600", type="3", playing="false")
    screen = Pantalla(construction)
    screen.text("title", 28, 40, "N\u00daMEROS NATURALES  |  1 ESO", 1.35, bold=True)
    screen.text("configGroups", 55, 170, size=1.5)
    screen.text("configTime", 55, 250, size=1.5)
    screen.text("configExtra", 55, 330, size=1.5)
    for name, action, y, step in [("groups", "groups", 137, 1), ("time", "seconds", 217, 5), ("extra", "extra", 297, 5)]:
        for suffix, kind, x, delta in [("Minus", "minus", 520, -step), ("Plus", "plus", 575, step)]:
            screen.icon(name + suffix, kind, x, y, "Reducir" if delta < 0 else "Aumentar",
                        f'NV2.dispatch("{action}", {delta});')
    screen.button("start", "Empezar", 55, 405, 'NV2.dispatch("start");')
    screen.icon("pause", "pause", 1110, 12, "Pausar y ocultar", 'NV2.dispatch("pause");')
    screen.icon("resume", "play", 550, 285, "Reanudar", 'NV2.dispatch("pause");')
    screen.icon("restart", "reset", 1055, 12, "Nueva partida", 'NV2.dispatch("requestReset");')
    screen.text("resetTitle", 390, 220, size=1.6, bold=True)
    screen.text("resetQuestion", 300, 270, size=1.1)
    screen.button("resetYes", "Reiniciar", 345, 310, 'NV2.dispatch("reset");')
    screen.button("resetNo", "Continuar", 555, 310, 'NV2.dispatch("cancelReset");')
    screen.text("round", 510, 38, size=0.95)
    screen.text("topic", 28, 80, size=1.05)
    screen.text("question", 28, 125, size=1.3, bold=True)
    screen.text("expression", 40, 182, size=2, latex=True)
    for option in range(4):
        screen.text("answer" + str(option), 40, 225 + option * 48, size=1.6, latex=True,
                    action=f'NV2.dispatch("answer", {option});')
    screen.text("status", 28, 437, size=1.15, bold=True)
    screen.text("explanation", 28, 477, size=1.05, latex=True)
    for label, kind, x, tooltip in [("helpPass", "pass", 28, "Pasapalabra"),
                                  ("helpTime", "time", 88, "Sumar tiempo"),
                                  ("helpRemove", "remove", 205, "Eliminar una incorrecta")]:
        screen.help_icon(label, kind, x, 570, tooltip, f'NV2.dispatch("help", "{kind}");',
                         marco=True, width=112 if kind == "time" else 40)
    screen.text("extraAmount", 134, 598, size=1, action='NV2.dispatch("help", "time");')
    construction.find("element[@label='extraAmount']/layer").set("val", "6")
    screen.icon("addTeam", "plus", 28, 570, "Elegir equipo para revivir", 'NV2.dispatch("choose");')
    screen.text("rescueTitle", 78, 598, size=1.1)
    screen.button("reveal", "Ver soluci\u00f3n", 560, 567, 'NV2.dispatch("reveal");')
    screen.button("next", "Siguiente reto", 560, 567, 'NV2.dispatch("next");')
    screen.text("turn", 850, 90, size=1.25, bold=True)
    screen.text("clock", 715, 80, size=1.25, bold=True)
    for team in range(8):
        y = 135 + team * 57
        screen.text("team" + str(team), 850, y, size=1.0, bold=True)
        for i, (kind, tooltip) in enumerate([("pass", "Pasapalabra"), ("time", "Tiempo extra"),
                                             ("remove", "Eliminar incorrecta"), ("revive", "Revivir")]):
            screen.help_icon(f"team{team}_{kind}", kind, 851 + 33 * i, y + 9, tooltip, size=18)
        screen.icon("choose" + str(team), "plus", 1095, y - 13,
                    f"Dar el intento al Grupo {team + 1}", f'NV2.dispatch("rescue", {team});')
    js = ("var NATURALES_BANK = " + json.dumps(banco(), ensure_ascii=True, separators=(",", ":")) + ";\n"
          + "var NATURALES_UI = " + json.dumps(screen.labels) + ";\n" + REGLAS.read_text(encoding="utf-8"))
    ET.indent(root, space="\t")
    contents = {"geogebra.xml": ET.tostring(root, encoding="utf-8", xml_declaration=True),
                "geogebra_javascript.js": js.encode("utf-8"),
                "LICENSE-Lucide.txt": LICENCIA.read_bytes(), **screen.resources}
    return contents


def guardar(path=SALIDA):
    contents = construir()
    # Marcas de tiempo estables para que regenerar sin cambios de fuentes sea reproducible.
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, data in contents.items():
            info = zipfile.ZipInfo(name, (2026, 9, 16, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, data)
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="validar fuentes sin escribir el .ggb")
    args = parser.parse_args()
    if args.dry_run:
        contents = construir()
        ET.fromstring(contents["geogebra.xml"])
        print(f"Validado: {len(RETOS_V2)} retos, {len(contents) - 3} iconos; no se ha escrito ningun archivo.")
    else:
        path = guardar()
        print(f"{path.name}: {len(RETOS_V2)} retos, version 2.")
        print("SHA256:", hashlib.sha256(path.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
