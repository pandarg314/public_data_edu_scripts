#!/usr/bin/env python3
"""Genera solo la version 3 de naturales; biblioteca estandar, sin descargas.

    python3 generar_naturales_v3.py
    python3 generar_naturales_v3.py --dry-run

El banco parte de NATURALES en generar_juegos.py y sustituye los romanos y las
propiedades por retos nuevos en RETOS_V3. No incluye potencias ni raices.
Las reglas e interaccion estan en naturales_v3.js
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

from generar_juegos import NATURALES, construir_xml, oper

AQUI = Path(__file__).resolve().parent
SALIDA = AQUI / "juego_numeros_naturales_1eso_v3.ggb"
REGLAS = AQUI / "naturales_v3.js"
LICENCIA = AQUI / "recursos_naturales_v2" / "LICENSE-Lucide.txt"

# La misma paleta se incorpora al JavaScript y a los recursos PNG.
PALETA = {
    "ink": [36, 43, 48], "muted": [101, 114, 123], "paper": [250, 251, 252],
    "teal": [42, 91, 100], "tealSoft": [225, 240, 242], "option": [238, 244, 246],
    "red": [164, 47, 59], "redSoft": [250, 226, 229], "failure": [248, 227, 226],
    "green": [25, 110, 79], "greenSoft": [218, 240, 225], "success": [222, 240, 228],
    "gold": [143, 97, 10], "goldSoft": [255, 242, 200],
}

RETOS_JERARQUIA_V3 = [
    oper("6+3*4", ["(6+3)*4", "6+3+4", "3*4"], "Jerarqu\u00eda de operaciones"),
    oper("24/3*2", ["24/(3*2)", "24/3", "24/2"], "Jerarqu\u00eda de operaciones",
         nota="Mismo nivel: de izquierda a derecha"),
    oper("18-6+2", ["18-(6+2)", "18-6", "18-2"], "Jerarqu\u00eda de operaciones",
         nota="Mismo nivel: de izquierda a derecha"),
    oper("3*(8-5)+4", ["3*8-5+4", "3*(8-5+4)", "3*(8-5)"], "Jerarqu\u00eda de operaciones"),
    oper("24/[2*(5-2)]", ["24/2*(5-2)", "2*(5-2)", "24/2"], "Jerarqu\u00eda de operaciones"),
]

RETOS_V3 = [reto for reto in NATURALES
            if not any(tema in reto["tema"].casefold() for tema in ("romanos", "propiedades"))] + RETOS_JERARQUIA_V3 + [
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
    "cross": [[(6, 6), (18, 18)], [(18, 6), (6, 18)]],
    "trophy": [[(8, 2), (16, 2), (16, 9), (15, 12), (12, 14), (9, 12), (8, 9), (8, 2)],
               [(8, 4), (3, 4), (3, 7), (4, 9), (8, 10)],
               [(16, 4), (21, 4), (21, 7), (20, 9), (16, 10)],
               [(12, 14), (12, 21)], [(8, 22), (16, 22)]],
}


def arco(cx, cy, radius, start=0, end=2 * math.pi):
    return [(cx + radius * math.cos(start + (end - start) * i / 64),
             cy + radius * math.sin(start + (end - start) * i / 64)) for i in range(65)]


def png_rgba(width, height, data):
    def chunk(kind, payload):
        return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", zlib.crc32(kind + payload))

    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(data)) + chunk(b"IEND", b""))


def cartel_png(width, height):
    data = bytearray()
    for y in range(height):
        data.append(0)
        for x in range(width):
            edge = min(x, y, width - 1 - x, height - 1 - y)
            color = PALETA["gold"] if edge <= 2 else PALETA["goldSoft"]
            data.extend((*color, 255 if edge else 0))
    return png_rgba(width, height, data)


def reloj_png(size=116, urgent=False):
    border = PALETA["red" if urgent else "teal"]
    background = PALETA["redSoft" if urgent else "tealSoft"]
    radius = size / 2 - 2
    data = bytearray()
    for y in range(size):
        data.append(0)
        for x in range(size):
            distance = math.hypot(x + .5 - size / 2, y + .5 - size / 2)
            alpha = round(255 * max(0, min(1, radius + .5 - distance)))
            ring = max(0, min(1, distance - (radius - 3) + .5))
            color = [round(fg * ring + bg * (1 - ring)) for fg, bg in zip(border, background)]
            data.extend((*color, alpha))
    return png_rgba(size, size, data)


def icono_png(nombre, size=40, apagado=False, marco=False, width=None, usado=False):
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
    color = (182, 188, 193) if apagado else PALETA["teal"]
    borde = (194, 202, 206) if apagado else (102, 133, 141)
    fondo = (242, 244, 245) if apagado else (245, 249, 250)
    if nombre == "trophy":
        color = PALETA["gold"]
    elif nombre == "cross":
        color = PALETA["red"]
    if usado:
        # En 18 px, una cruz clara sustituye al dibujo; en 40 px, lo tacha.
        if size <= 18:
            segments = []
        color, borde, fondo = (194, 145, 151), PALETA["red"], PALETA["redSoft"]
    cross = [((5, 5), (19, 19)), ((19, 5), (5, 19))]

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
            d = min((distance(px, py, a, b) for a, b in segments), default=100)
            alpha = round(255 * max(0, min(1, (1.1 - d) * drawing / 24 + 0.5)))
            foreground = color
            if usado:
                cross_distance = min(distance(px, py, a, b) for a, b in cross)
                cross_alpha = round(255 * max(0, min(1, (1.65 - cross_distance) * drawing / 24 + 0.5)))
                if cross_alpha:
                    total = cross_alpha + alpha * (255 - cross_alpha) / 255
                    foreground = tuple(round((c * cross_alpha + bg * alpha * (255 - cross_alpha) / 255) / total)
                                       for c, bg in zip(PALETA["red"], color))
                    alpha = round(total)
            edge = min(x, y, width - 1 - x, size - 1 - y)
            if marco and edge >= 1:
                background = borde if edge == 1 else fondo
                pixel = tuple(round((c * alpha + bg * (255 - alpha)) / 255)
                              for c, bg in zip(foreground, background))
                data.extend((*pixel, 255))
            else:
                data.extend((*foreground, alpha))
    return png_rgba(width, size, data)


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
        if token == r"\\":
            if current:
                lines.append(" ".join(current))
            current, width = [], 0
            continue
        length = len(re.sub(r"\\[a-zA-Z]+|[{}]", "", token)) + 1
        if current and width + length > 68:
            lines.append(" ".join(current))
            current, width = [], 0
        current.append(token)
        width += length
    if current:
        lines.append(" ".join(current))
    return r"\begin{array}{l}" + r" \\ ".join(lines) + r"\end{array}"


def banco(retos=RETOS_V3):
    rng = random.Random(1)
    letters = [k % 4 for k in range(len(retos))]
    rng.shuffle(letters)
    result = []
    for index, question in enumerate(retos):
        options = list(question["malas"])
        if len(options) != 3 or len(set(options + [question["ok"]])) != 4:
            raise ValueError(f"Reto {index + 1}: opciones repetidas")
        rng.shuffle(options)
        options.insert(letters[index], question["ok"])
        result.append(dict(topic=question["tema"], question="\n".join(textwrap.wrap(question["pregunta"], 63)),
                           expression=question["expr"], options=options, correct=letters[index],
                           explanation=explicacion_latex(question["expl"])))
        if "nivel" in question:
            result[-1]["level"] = question["nivel"]
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

    def icon(self, label, kind, x, y, tooltip, action=None, size=40, off=False, marco=False, width=None, used=False):
        variant = f"-marco{width or size}" if marco else ""
        state = "used" if used else "off" if off else "on"
        resource = f"icons/{kind}-{size}-{state}{variant}.png"
        if resource not in self.resources:
            self.resources[resource] = icono_png(kind, size, off, marco, width, used)
        # GeoGebra fija las imagenes por su esquina inferior izquierda.
        element = self.element(label, "image", x, y + size, action, tooltip)
        ET.SubElement(element, "file", name=resource)
        ET.SubElement(element, "inBackground", val="false")
        ET.SubElement(element, "interpolate", val="true")

    def help_icon(self, label, kind, x, y, tooltip, action=None, size=40, marco=False, width=None):
        self.icon(label, kind, x, y, tooltip, action, size, marco=marco, width=width)
        self.icon(label + "Off", kind, x, y, tooltip + " (no disponible)",
                  size=size, off=True, marco=marco, width=width)
        self.icon(label + "Used", kind, x, y, tooltip + " (gastado)",
                  size=size, used=True, marco=marco, width=width)

    def poster(self, label, x, y, width, height):
        resource = "icons/cartel-final.png"
        self.resources[resource] = cartel_png(width, height)
        element = self.element(label, "image", x, y + height)
        element.find("layer").set("val", "4")
        ET.SubElement(element, "file", name=resource)
        ET.SubElement(element, "inBackground", val="false")
        ET.SubElement(element, "interpolate", val="true")

    def clock_face(self, label, urgent=False):
        resource = "icons/clock-face-" + ("urgent" if urgent else "normal") + ".png"
        self.resources[resource] = reloj_png(urgent=urgent)
        element = self.element(label, "image", 714, 48 + 116)
        element.find("layer").set("val", "4")
        ET.SubElement(element, "file", name=resource)
        ET.SubElement(element, "inBackground", val="false")
        ET.SubElement(element, "interpolate", val="true")


def construir(retos=RETOS_V3, titulo=None, niveles=(), expression_y=182):
    # Reutilizar la configuracion XML del generador previo sin ejecutar su main.
    root = ET.fromstring(construir_xml(titulo or "Numeros naturales - version 3", retos, 1))
    construction = root.find("construction")
    construction.clear()
    construction.set("title", titulo + " - v3" if titulo else "Numeros naturales - 1 ESO - v3")
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
    screen.text("title", 28, 40, titulo or "N\u00daMEROS NATURALES  |  1 ESO", 1.35, bold=True)
    if niveles:
        choices = list(enumerate(niveles, 1)) + [(0, "Todos")]
        for slot, (index, caption) in enumerate(choices):
            screen.button("level" + str(index), caption, 710 + 82 * slot,
                          8, f'NV3.dispatch("level", {index});', width=80)
            element = construction.find(f"element[@label='level{index}']")
            element.find("dimensions").set("height", "32")
            element.find("font").set("sizeM", ".9")
    screen.text("configGroups", 55, 170, size=1.5)
    screen.text("configTime", 55, 250, size=1.5)
    screen.text("configExtra", 55, 330, size=1.5)
    for name, action, y, step in [("groups", "groups", 137, 1), ("time", "seconds", 217, 5), ("extra", "extra", 297, 5)]:
        for suffix, kind, x, delta in [("Minus", "minus", 520, -step), ("Plus", "plus", 575, step)]:
            screen.icon(name + suffix, kind, x, y, "Reducir" if delta < 0 else "Aumentar",
                        f'NV3.dispatch("{action}", {delta});')
    screen.button("start", "Empezar", 55, 405, 'NV3.dispatch("start");')
    screen.icon("pause", "pause", 1110, 12, "Pausar y ocultar", 'NV3.dispatch("pause");')
    screen.icon("resume", "play", 550, 285, "Reanudar", 'NV3.dispatch("pause");')
    screen.icon("restart", "reset", 1055, 12, "Nueva partida", 'NV3.dispatch("requestReset");')
    screen.text("resetTitle", 390, 220, size=1.6, bold=True)
    screen.text("resetQuestion", 300, 270, size=1.1)
    screen.button("resetYes", "Reiniciar", 345, 310, 'NV3.dispatch("reset");')
    screen.button("resetNo", "Continuar", 555, 310, 'NV3.dispatch("cancelReset");')
    screen.text("finishTitle", 390, 220, "Fin de partida", size=1.6, bold=True)
    screen.text("finishQuestion", 270, 270, "\u00bfTerminamos con los puntos actuales?", size=1.1)
    screen.button("finishYes", "Finalizar", 345, 310, 'NV3.dispatch("finish");')
    screen.button("finishNo", "Continuar", 555, 310, 'NV3.dispatch("cancelFinish");')
    screen.text("round", 470 if niveles else 510, 38, size=0.9 if niveles else 0.95)
    screen.text("topic", 28, 80, size=1.05)
    screen.text("question", 28, 125, size=1.3, bold=True)
    screen.text("expression", 40, expression_y, size=2, latex=True)
    for option in range(4):
        screen.text("answer" + str(option), 40, 225 + option * 48, size=1.6, latex=True,
                    action=f'NV3.dispatch("answer", {option});')
        screen.icon("discard" + str(option), "cross", 12, 232 + option * 48,
                    "Respuesta descartada", size=22)
    screen.text("status", 28, 437, size=1.15, bold=True)
    screen.text("explanation", 28, 477, size=1.05, latex=True)
    for label, kind, x, tooltip in [("helpPass", "pass", 28, "Pasapalabra"),
                                  ("helpTime", "time", 88, "Sumar tiempo"),
                                  ("helpRemove", "remove", 205, "Eliminar una incorrecta")]:
        screen.help_icon(label, kind, x, 570, tooltip, f'NV3.dispatch("help", "{kind}");',
                         marco=True, width=112 if kind == "time" else 40)
    screen.text("extraAmount", 134, 598, size=1, action='NV3.dispatch("help", "time");')
    construction.find("element[@label='extraAmount']/layer").set("val", "6")
    screen.icon("addTeam", "plus", 28, 570, "Elegir equipo para revivir", 'NV3.dispatch("choose");')
    screen.text("rescueTitle", 78, 598, size=1.1)
    screen.button("reveal", "Ver soluci\u00f3n", 360, 567, 'NV3.dispatch("reveal");')
    screen.button("next", "Siguiente ronda", 560, 567, 'NV3.dispatch("skip");')
    screen.button("finishGame", "Fin de partida", 850, 586, 'NV3.dispatch("requestFinish");', width=220)
    screen.text("turn", 850, 90, size=1.25, bold=True)
    screen.clock_face("clockFace")
    screen.clock_face("clockFaceUrgent", urgent=True)
    screen.text("clock", 753, 108, size=1.9, bold=True)
    screen.text("clockUrgent", 741, 114, size=3.1, bold=True)
    screen.text("clockUnit", 740, 134, "segundos", size=.8)
    screen.text("clockUnlimited", 747, 106, "Sin\nl\u00edmite", size=1.15, bold=True)
    screen.poster("winnerPoster", 28, 142, 730, 410)
    screen.icon("winnerCup", "trophy", 361, 166, "Ganadores", size=64)
    screen.text("winnerTitle", 305, 278, size=1.8, bold=True)
    screen.text("winnerScore", 345, 322, size=1.2, bold=True)
    screen.text("winnerSolo", 342, 390, size=1.4, bold=True)
    screen.icon("winnerSoloBadge", "trophy", 303, 367, "Equipo ganador", size=24)
    screen.text("winnerThanks", 280, 596, "\u00a1Bien jugado!", size=1.35, bold=True)
    for slot in range(8):
        x, y = 135 + (slot % 2) * 320, 362 + (slot // 2) * 46
        screen.text("winnerName" + str(slot), x, y, size=1.4, bold=True)
        screen.icon("winnerBadge" + str(slot), "trophy", x - 38, y - 23, "Equipo ganador", size=24)
    for team in range(8):
        y = 135 + team * 57
        screen.text("team" + str(team), 850, y, size=1.0, bold=True)
        screen.icon("teamCup" + str(team), "trophy", 1138, y - 23,
                    "Mayor puntuacion (incluye empates)", size=24)
        for i, (kind, tooltip) in enumerate([("pass", "Pasapalabra"), ("time", "Tiempo extra"),
                                             ("remove", "Eliminar incorrecta"), ("revive", "Revivir")]):
            screen.help_icon(f"team{team}_{kind}", kind, 851 + 33 * i, y + 9, tooltip, size=18)
        screen.icon("choose" + str(team), "plus", 1095, y - 13,
                    f"Dar el intento al Grupo {team + 1}", f'NV3.dispatch("rescue", {team});')
    js = ("var NATURALES_BANK = " + json.dumps(banco(retos), ensure_ascii=True, separators=(",", ":")) + ";\n"
          + "var NATURALES_COLORS = " + json.dumps(PALETA) + ";\n"
          + "var NATURALES_LEVELS = " + json.dumps(list(niveles)) + ";\n"
          + "var NATURALES_UI = " + json.dumps(screen.labels) + ";\n" + REGLAS.read_text(encoding="utf-8"))
    ET.indent(root, space="\t")
    contents = {"geogebra.xml": ET.tostring(root, encoding="utf-8", xml_declaration=True),
                "geogebra_javascript.js": js.encode("utf-8"),
                "LICENSE-Lucide.txt": LICENCIA.read_bytes(), **screen.resources}
    return contents


def guardar(path=SALIDA, contents=None):
    if contents is None:
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
        print(f"Validado: {len(RETOS_V3)} retos, {len(contents) - 3} iconos; no se ha escrito ningun archivo.")
    else:
        path = guardar()
        print(f"{path.name}: {len(RETOS_V3)} retos, version 3.")
        print("SHA256:", hashlib.sha256(path.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
