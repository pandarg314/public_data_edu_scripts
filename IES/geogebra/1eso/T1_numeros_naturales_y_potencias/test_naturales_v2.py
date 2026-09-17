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

import generar_naturales_v2 as gen


class ArchivoV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contents = gen.construir()
        cls.root = ET.fromstring(cls.contents["geogebra.xml"])

    def test_banco_completo_y_respuestas_balanceadas(self):
        bank = gen.banco()
        self.assertEqual(len(bank), len(gen.RETOS_V2))
        counts = Counter(q["correct"] for q in bank)
        self.assertLessEqual(max(counts.values()) - min(counts.values()), 1)
        for original, question in zip(gen.RETOS_V2, bank):
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
                self.assertIn("NV2.dispatch(", script.get("val"))
                self.assertEqual(node.find("selectionAllowed").get("val"), "true")

    def test_iconos_png_incorporados_y_no_vacios(self):
        for node in self.root.findall("construction/element[@type='image']"):
            self.assertEqual(float(node.find("objColor").get("alpha")), 1,
                             f"{node.get('label')}: el PNG no debe quedar transparente en GeoGebra")
            data = self.contents[node.find("file").get("name")]
            self.assertEqual(data[:8], b"\x89PNG\r\n\x1a\n")
            width, height = struct.unpack(">II", data[16:24])
            self.assertIn((width, height), ((18, 18), (40, 40), (112, 40)))
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
            for suffix in ("", "Off"):
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
        self.assertIn('NV2.dispatch("help", "time")', seconds.find("javascript").get("val"))
        self.assertEqual(seconds.find("layer").get("val"), "6")

    def test_botones_con_texto_visible(self):
        buttons = self.root.findall("construction/element[@type='button']")
        self.assertTrue(buttons)
        for button in buttons:
            self.assertEqual(button.find("show").get("label"), "true", button.get("label"))
            self.assertTrue(button.find("caption").get("val").strip())

    def test_reloj_nativo_con_velocidad_constante(self):
        clock = self.root.find("construction/element[@label='reloj']")
        self.assertEqual(clock.find("slider").get("max"), "600")
        self.assertEqual(clock.find("animation").get("speed"), "10 / 600")
        self.assertEqual(clock.find("animation").get("playing"), "false")
        self.assertEqual(clock.find("animation").get("type"), "3")

    def test_generacion_reproducible_y_anteriores_intactos(self):
        originals = [gen.AQUI / name for name in ("generar_juegos.py", "juego_numeros_naturales_1eso.ggb",
                     "juego_potencias_1eso.ggb", "juego_operaciones_niveles_1eso.ggb")]
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
        print((gen.AQUI / "test_naturales_v2.js").read_text())
    else:
        unittest.main()
