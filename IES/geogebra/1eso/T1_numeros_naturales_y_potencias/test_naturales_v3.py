#!/usr/bin/env python3
"""Pruebas estructurales; --javascript emite las pruebas para Node o Rhino."""

import hashlib
import json
import struct
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zipfile
import zlib
from collections import Counter
from pathlib import Path

import generar_naturales_v3 as gen


class ArchivoV3Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contents = gen.construir()
        cls.root = ET.fromstring(cls.contents["geogebra.xml"])

    def test_banco_completo_y_respuestas_balanceadas(self):
        bank = gen.banco()
        self.assertEqual(len(bank), len(gen.RETOS_V3))
        counts = Counter(q["correct"] for q in bank)
        self.assertLessEqual(max(counts.values()) - min(counts.values()), 1)
        for original, question in zip(gen.RETOS_V3, bank):
            self.assertEqual(len(set(question["options"])), 4)
            self.assertEqual(question["options"][question["correct"]], original["ok"])
            self.assertTrue(question["explanation"].startswith(r"\begin{array}{l}"))

    def test_romanos_sustituidos_sin_modificar_el_banco_anterior(self):
        bank = gen.banco()
        self.assertEqual(len(bank), 41)
        self.assertTrue(all("romanos" not in q["topic"].casefold() for q in bank))
        self.assertEqual(sum("romanos" in q["tema"].casefold() for q in gen.NATURALES), 2)
        self.assertEqual(bank[-2]["options"][bank[-2]["correct"]], f"{125 * 8:,}".replace(",", r"\,"))
        self.assertEqual(bank[-1]["options"][bank[-1]["correct"]], str(168 // 7))
        self.assertEqual(168 % 7, 0)

    def test_propiedades_sustituidas_por_cinco_operaciones_cortas(self):
        self.assertEqual(sum("propiedades" in q["tema"].casefold() for q in gen.NATURALES), 5)
        replacements = gen.RETOS_JERARQUIA_V3
        self.assertEqual(len(replacements), 5)
        self.assertEqual(len(gen.banco()), 41)
        for question in gen.banco():
            contents = json.dumps(question, ensure_ascii=False).casefold()
            for excluded in ("propiedad", "conmutativa", "asociativa", "distributiva", "elemento neutro",
                             "potencia", "ra\u00edz", "ra\u00edces", "\\sqrt", "^"):
                self.assertNotIn(excluded, contents)
        retained = [q for q in gen.NATURALES if not any(t in q["tema"].casefold()
                    for t in ("romanos", "propiedades"))]
        self.assertEqual(gen.RETOS_V3[:len(retained)], retained)
        for question in replacements:
            expression = question["expr"].replace(r"\cdot", "*")
            self.assertLessEqual(len(expression), 24)
            self.assertTrue(2 <= sum(expression.count(op) for op in "+-*:") <= 3)

    def test_soluciones_y_distractores_de_las_operaciones_nuevas(self):
        expected = {
            r"6 + 3 \cdot 4": "18",
            r"24 : 3 \cdot 2": "16",
            "18 - 6 + 2": "14",
            r"3 \cdot (8 - 5) + 4": "13",
            r"24 : [2 \cdot (5 - 2)]": "4",
        }
        self.assertEqual({q["expr"]: q["ok"] for q in gen.RETOS_JERARQUIA_V3}, expected)
        for question in gen.RETOS_JERARQUIA_V3:
            self.assertEqual(len(set([question["ok"]] + question["malas"])), 4)
            self.assertTrue(all(value.isdigit() for value in [question["ok"]] + question["malas"]))
            self.assertTrue(question["expl"].endswith("= " + question["ok"]))

    def test_resoluciones_de_izquierda_a_derecha_y_agrupaciones(self):
        by_expression = {q["expr"]: q["expl"] for q in gen.RETOS_JERARQUIA_V3}
        for expression in (r"24 : 3 \cdot 2", "18 - 6 + 2"):
            self.assertIn("de izquierda a derecha", by_expression[expression])
        self.assertIn(r"8 \cdot 2 = 16", by_expression[r"24 : 3 \cdot 2"])
        self.assertIn("12 + 2 = 14", by_expression["18 - 6 + 2"])
        self.assertIn(r"3 \cdot 3 + 4 = 9 + 4 = 13", by_expression[r"3 \cdot (8 - 5) + 4"])
        self.assertIn(r"24 : [2 \cdot 3] = 24 : 6 = 4", by_expression[r"24 : [2 \cdot (5 - 2)]"])
        for expression, explanation in by_expression.items():
            formatted = gen.explicacion_latex(explanation)
            self.assertLessEqual(len(formatted.split(r" \\ ")), 2)
            self.assertNotIn(r"= \\ ", formatted)
            if expression in (r"24 : 3 \cdot 2", "18 - 6 + 2"):
                self.assertEqual(len(formatted.split(r" \\ ")), 2)

    def test_objetos_y_referencias(self):
        elements = self.root.findall("construction/element")
        labels = [node.get("label") for node in elements]
        self.assertEqual(len(labels), len(set(labels)))
        source = self.contents["geogebra_javascript.js"].decode()
        ui = json.loads(source.split("var NATURALES_UI = ", 1)[1].split(";\n", 1)[0])
        self.assertEqual(set(ui), set(labels) - {"reloj"})
        self.assertNotIn("setInterval(", source)
        self.assertNotIn("setTimeout(", source)
        for node in elements:
            self.assertEqual(node.find("show").get("object"), "false")
            script = node.find("javascript")
            if script is not None:
                self.assertIn("NV3.dispatch(", script.get("val"))
                self.assertEqual(node.find("selectionAllowed").get("val"), "true")

    def test_iconos_png_incorporados_y_no_vacios(self):
        for node in self.root.findall("construction/element[@type='image']"):
            self.assertEqual(float(node.find("objColor").get("alpha")), 1,
                             f"{node.get('label')}: el PNG no debe quedar transparente en GeoGebra")
            data = self.contents[node.find("file").get("name")]
            self.assertEqual(data[:8], b"\x89PNG\r\n\x1a\n")
            width, height = struct.unpack(">II", data[16:24])
            self.assertIn((width, height), ((18, 18), (22, 22), (24, 24), (40, 40),
                                          (64, 64), (112, 40), (116, 116), (730, 410)))
            position = node.find("absoluteScreenLocation")
            self.assertLessEqual(int(position.get("x")) + width, 1180)
            self.assertGreaterEqual(int(position.get("y")) - height, 0)
            self.assertLessEqual(int(position.get("y")), 650)
            offset, compressed = 8, b""
            while offset < len(data):
                size = struct.unpack(">I", data[offset:offset + 4])[0]
                kind, payload = data[offset + 4:offset + 8], data[offset + 8:offset + 8 + size]
                crc = struct.unpack(">I", data[offset + 8 + size:offset + 12 + size])[0]
                self.assertEqual(zlib.crc32(kind + payload), crc)
                if kind == b"IDAT":
                    compressed += payload
                offset += size + 12
            pixels = zlib.decompress(compressed)
            alphas = [pixels[y * (width * 4 + 1) + 4 + x * 4] for y in range(height) for x in range(width)]
            self.assertGreater(sum(alpha > 0 for alpha in alphas), 10)
            self.assertIn(0, alphas)

    def test_comodines_recuadrados_y_segundos_dentro_del_reloj(self):
        for label in ("helpPass", "helpTime", "helpRemove"):
            for suffix in ("", "Off", "Used"):
                element = self.root.find(f"construction/element[@label='{label}{suffix}']")
                resource = element.find("file").get("name")
                self.assertIn("-marco", resource)
                data = self.contents[resource]
                width, height = struct.unpack(">II", data[16:24])
                self.assertEqual((width, height), (112 if label == "helpTime" else 40, 40))
                length = struct.unpack(">I", data[33:37])[0]
                pixels = zlib.decompress(data[41:41 + length])
                def pixel(x, y):
                    pos = y * (width * 4 + 1) + 1 + x * 4
                    return pixels[pos:pos + 4]
                self.assertEqual(pixel(1, height // 2)[3], 255)
                self.assertNotEqual(pixel(1, height // 2), pixel(3, height // 2))
        seconds = self.root.find("construction/element[@label='extraAmount']")
        position = seconds.find("absoluteScreenLocation")
        self.assertGreater(int(position.get("x")), 88 + 40)
        self.assertLess(int(position.get("x")) + 56, 88 + 112)
        self.assertLessEqual(int(position.get("y")), 570 + 40)
        self.assertIn('NV3.dispatch("help", "time")', seconds.find("javascript").get("val"))
        self.assertEqual(seconds.find("layer").get("val"), "6")

    def test_botones_con_texto_visible(self):
        buttons = self.root.findall("construction/element[@type='button']")
        self.assertTrue(buttons)
        for button in buttons:
            self.assertEqual(button.find("show").get("label"), "true", button.get("label"))
            self.assertTrue(button.find("caption").get("val").strip())

    def test_estados_gastados_diferentes_e_inertes(self):
        labels = ["helpPass", "helpTime", "helpRemove"]
        labels += [f"team{i}_{kind}" for i in range(8) for kind in ("pass", "time", "remove", "revive")]
        for label in labels:
            resources = []
            for suffix in ("", "Off", "Used"):
                node = self.root.find(f"construction/element[@label='{label}{suffix}']")
                resources.append(self.contents[node.find("file").get("name")])
                if suffix:
                    self.assertIsNone(node.find("javascript"))
                    self.assertEqual(node.find("selectionAllowed").get("val"), "false")
                if suffix == "Used":
                    self.assertIn("gastado", node.find("caption").get("val"))
            self.assertEqual(len(set(resources)), 3)
        data = gen.icono_png("time", size=18, usado=True)
        length = struct.unpack(">I", data[33:37])[0]
        pixels = zlib.decompress(data[41:41 + length])
        offset = 9 * (18 * 4 + 1) + 1 + 9 * 4
        self.assertEqual(list(pixels[offset:offset + 4]), gen.PALETA["red"] + [255])

    def test_reloj_grande_y_cartel_con_espacio_para_ocho(self):
        def node(label):
            return self.root.find(f"construction/element[@label='{label}']")
        normal = node("clock")
        urgent = node("clockUrgent")
        self.assertGreater(float(urgent.find("font").get("sizeM")),
                           float(normal.find("font").get("sizeM")) * 1.5)
        self.assertGreaterEqual(float(normal.find("font").get("sizeM")), 1.9)
        for label in ("clock", "clockUrgent", "clockUnit", "clockUnlimited"):
            text = node(label)
            self.assertGreater(int(text.find("layer").get("val")),
                               int(node("clockFace").find("layer").get("val")))
            self.assertTrue(714 < int(text.find("absoluteScreenLocation").get("x")) < 830)
            self.assertTrue(48 < int(text.find("absoluteScreenLocation").get("y")) < 164)
        poster_layer = int(node("winnerPoster").find("layer").get("val"))
        positions = set()
        for i in range(8):
            winner = node(f"winnerName{i}")
            self.assertGreater(int(winner.find("layer").get("val")), poster_layer)
            x, y = (int(winner.find("absoluteScreenLocation").get(key)) for key in ("x", "y"))
            positions.add((x, y))
            self.assertTrue(28 + 40 <= x <= 758 - 180)
            self.assertTrue(342 <= y <= 552 - 20)
            self.assertIsNotNone(node(f"teamCup{i}"))
            self.assertIsNotNone(node(f"winnerBadge{i}"))
        self.assertEqual(len(positions), 8)
        for i in range(4):
            cross = node(f"discard{i}")
            self.assertEqual(int(cross.find("absoluteScreenLocation").get("x")) + 22, 34)
            self.assertIsNone(cross.find("javascript"))

    def test_circulo_del_reloj_y_estados(self):
        resources = []
        for label, tone in (("clockFace", "tealSoft"), ("clockFaceUrgent", "redSoft")):
            face = self.root.find(f"construction/element[@label='{label}']")
            self.assertEqual(face.find("absoluteScreenLocation").attrib, {"x": "714", "y": "164"})
            self.assertEqual(face.find("layer").get("val"), "4")
            data = self.contents[face.find("file").get("name")]
            resources.append(data)
            length = struct.unpack(">I", data[33:37])[0]
            pixels = zlib.decompress(data[41:41 + length])
            def pixel(x, y):
                offset = y * (116 * 4 + 1) + 1 + x * 4
                return list(pixels[offset:offset + 4])
            self.assertEqual(pixel(58, 58), gen.PALETA[tone] + [255])
            for x, y in ((0, 0), (115, 0), (0, 115), (115, 115)):
                self.assertEqual(pixel(x, y)[3], 0)
            for x, y in ((3, 58), (112, 58), (58, 3), (58, 112)):
                self.assertEqual(pixel(x, y)[3], 255)
        self.assertNotEqual(*resources)

    def test_controles_del_profesor_sin_solapamiento(self):
        boxes = []
        for label, action in (("reveal", "reveal"), ("next", "skip"), ("finishGame", "requestFinish")):
            node = self.root.find(f"construction/element[@label='{label}']")
            self.assertIn(f'NV3.dispatch("{action}")', node.find("javascript").get("val"))
            location, size = node.find("absoluteScreenLocation"), node.find("dimensions")
            x, y = int(location.get("x")), int(location.get("y"))
            w, h = int(size.get("width")), int(size.get("height"))
            self.assertTrue(x + w <= 1180 and y + h <= 650)
            boxes.append((x, y, x + w, y + h))
        for i, a in enumerate(boxes):
            for b in boxes[i + 1:]:
                self.assertTrue(a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1])
        self.assertGreaterEqual(boxes[2][1], 135 + 7 * 57 + 9 + 18 + 16)

    def test_paleta_compartida_y_contraste(self):
        source = self.contents["geogebra_javascript.js"].decode()
        palette = json.loads(source.split("var NATURALES_COLORS = ", 1)[1].split(";\n", 1)[0])
        self.assertEqual(palette, gen.PALETA)
        def luminance(rgb):
            linear = [v / 255 / 12.92 if v / 255 <= .04045 else ((v / 255 + .055) / 1.055) ** 2.4 for v in rgb]
            return sum(v * weight for v, weight in zip(linear, (.2126, .7152, .0722)))
        for foreground, background in (("red", "paper"), ("red", "redSoft"), ("green", "greenSoft"),
                                       ("gold", "goldSoft"), ("teal", "tealSoft"), ("muted", "paper")):
            ratio = (luminance(palette[background]) + .05) / (luminance(palette[foreground]) + .05)
            self.assertGreaterEqual(ratio, 4.5, foreground)

    def test_reloj_nativo_con_velocidad_constante(self):
        clock = self.root.find("construction/element[@label='reloj']")
        self.assertEqual(clock.find("slider").get("max"), "600")
        self.assertEqual(clock.find("animation").get("speed"), "10 / 600")
        self.assertEqual(clock.find("animation").get("playing"), "false")
        self.assertEqual(clock.find("animation").get("type"), "3")

    def test_generacion_reproducible_y_anteriores_intactos(self):
        originals = [gen.AQUI / name for name in ("generar_juegos.py", "juego_numeros_naturales_1eso.ggb",
                     "juego_potencias_1eso.ggb", "juego_operaciones_niveles_1eso.ggb",
                     "generar_naturales_v2.py", "naturales_v2.js", "juego_numeros_naturales_1eso_v2.ggb",
                     "test_naturales_v2.py", "test_naturales_v2.js", "README_naturales_v2.md")]
        before = {p: hashlib.sha256(p.read_bytes()).digest() for p in originals}
        with tempfile.TemporaryDirectory() as directory:
            first = gen.guardar(Path(directory) / "primero.ggb")
            second = gen.guardar(Path(directory) / "segundo.ggb")
            self.assertEqual(first.read_bytes(), second.read_bytes())
            with zipfile.ZipFile(first) as archive:
                self.assertIsNone(archive.testzip())
                self.assertEqual(set(archive.namelist()), set(self.contents))
        after = {p: hashlib.sha256(p.read_bytes()).digest() for p in originals}
        self.assertEqual(before, after)


if __name__ == "__main__":
    if sys.argv[1:] == ["--javascript"]:
        source = gen.construir()["geogebra_javascript.js"].decode()
        print('if (typeof print === "undefined") { var print = function(s) { console.log(s); }; }')
        print(source)
        print((gen.AQUI / "test_naturales_v3.js").read_text())
    else:
        unittest.main()
