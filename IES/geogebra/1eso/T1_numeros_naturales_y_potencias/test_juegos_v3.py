#!/usr/bin/env python3
"""Pruebas de los nuevos juegos; --javascript JUEGO emite su bateria JS."""

import copy
import hashlib
import json
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zipfile
from collections import Counter
from pathlib import Path

import generar_juegos_v3 as gen
from generar_juegos import OPERACIONES, POTENCIAS


class JuegosV3Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contents = {key: gen.construir(key) for key in gen.JUEGOS}

    def test_bancos_originales_completos(self):
        for key, count in (("potencias", 44), ("operaciones", 45)):
            with self.subTest(juego=key):
                config = gen.JUEGOS[key]
                bank = gen.base.banco(config["retos"])
                self.assertEqual(len(bank), count)
                for original, question in zip(config["retos"], bank):
                    self.assertEqual(question["expression"], original["expr"])
                    self.assertEqual(question["question"].replace("\n", " "), original["pregunta"])
                    self.assertEqual(question["topic"], original["tema"])
                    self.assertEqual(question["options"][question["correct"]], original["ok"])
                    self.assertEqual(set(question["options"]), set([original["ok"]] + original["malas"]))
                    self.assertEqual(question["explanation"], gen.base.explicacion_latex(original["expl"]))
                distribution = Counter(q["correct"] for q in bank)
                self.assertLessEqual(max(distribution.values()) - min(distribution.values()), 1)

    def test_niveles_y_contenidos_no_se_filtran_como_naturales(self):
        bank = gen.base.banco(gen.JUEGOS["operaciones"]["retos"])
        self.assertEqual(Counter(q["level"] for q in bank), {1: 15, 2: 15, 3: 15})
        self.assertEqual(gen.JUEGOS["operaciones"]["niveles"], ("Nivel 1", "Nivel 2", "Nivel 3"))
        self.assertTrue(all("^" not in q["expression"] and r"\sqrt" not in q["expression"]
                            for q in bank if q["level"] == 1))
        for level in (2, 3):
            expressions = [q["expression"] for q in bank if q["level"] == level]
            self.assertTrue(any("^" in e for e in expressions))
            self.assertTrue(any(r"\sqrt" in e for e in expressions))
        self.assertTrue(any("[" in q["expression"] for q in bank if q["level"] == 3))
        powers = gen.base.banco(gen.JUEGOS["potencias"]["retos"])
        self.assertTrue(any("propiedades" in q["topic"].casefold() for q in powers))
        self.assertTrue(all("level" not in q for q in powers))
        before = copy.deepcopy((POTENCIAS, OPERACIONES))
        gen.base.banco(gen.JUEGOS["operaciones"]["retos"])
        self.assertEqual((POTENCIAS, OPERACIONES), before)
        self.assertTrue(all("nivel" not in reto for _, retos in OPERACIONES for reto in retos))

    def test_misma_interfaz_y_codigo_de_reglas(self):
        natural = gen.base.construir()
        natural_root = ET.fromstring(natural["geogebra.xml"])
        natural_labels = {e.get("label") for e in natural_root.findall("construction/element")}
        for key, contents in self.contents.items():
            root = ET.fromstring(contents["geogebra.xml"])
            labels = [e.get("label") for e in root.findall("construction/element")]
            self.assertEqual(len(labels), len(set(labels)))
            extra = {"level0", "level1", "level2", "level3"} if key == "operaciones" else set()
            self.assertEqual(set(labels), natural_labels | extra)
            title = root.find("construction/expression[@label='title']")
            self.assertEqual(json.loads(title.get("exp")), gen.JUEGOS[key]["titulo"])
            js = contents["geogebra_javascript.js"].decode()
            self.assertTrue(js.endswith(gen.base.REGLAS.read_text()))
            ui = json.loads(js.split("var NATURALES_UI = ", 1)[1].split(";\n", 1)[0])
            self.assertEqual(set(ui), set(labels) - {"reloj"})
            self.assertNotIn("setInterval(", js)
            self.assertNotIn("setTimeout(", js)
            for image in root.findall("construction/element[@type='image']"):
                name = image.find("file").get("name")
                self.assertEqual(contents[name], natural[name])
                self.assertEqual(image.find("objColor").get("alpha"), "1")
            for element in root.findall("construction/element"):
                self.assertEqual(element.find("show").get("object"), "false")
                script = element.find("javascript")
                if script is not None:
                    self.assertIn("NV3.dispatch(", script.get("val"))
            self.assertEqual(contents["LICENSE-Lucide.txt"], natural["LICENSE-Lucide.txt"])

    def test_selector_compacto_fuera_del_reloj_y_de_los_controles(self):
        root = ET.fromstring(self.contents["operaciones"]["geogebra.xml"])
        end = 710
        for level in (1, 2, 3, 0):
            button = root.find(f"construction/element[@label='level{level}']")
            self.assertEqual(button.find("show").get("label"), "true")
            self.assertIn(f'NV3.dispatch("level", {level})', button.find("javascript").get("val"))
            position, size = button.find("absoluteScreenLocation"), button.find("dimensions")
            x, y = int(position.get("x")), int(position.get("y"))
            width, height = int(size.get("width")), int(size.get("height"))
            self.assertGreaterEqual(x, end)
            self.assertLessEqual(y + height, 40)
            end = x + width
        self.assertLess(end, 1055)
        self.assertEqual(root.find("construction/element[@label='round']/absoluteScreenLocation").get("x"), "470")

    def test_espacio_para_expresiones_y_explicaciones(self):
        for key, config in gen.JUEGOS.items():
            root = ET.fromstring(self.contents[key]["geogebra.xml"])
            expression = root.find("construction/element[@label='expression']/absoluteScreenLocation")
            answer = root.find("construction/element[@label='answer0']/absoluteScreenLocation")
            self.assertGreaterEqual(int(answer.get("y")) - int(expression.get("y")), 65)
            for question in gen.base.banco(config["retos"]):
                self.assertLessEqual(question["explanation"].count(r" \\ ") + 1, 2)
                if question["expression"]:
                    self.assertNotIn("\n", question["question"])

    def test_generacion_reproducible_sin_modificar_anteriores(self):
        originals = [p for p in gen.AQUI.glob("*.ggb") if p.name not in
                     {c["archivo"] for c in gen.JUEGOS.values()}]
        before = {p: hashlib.sha256(p.read_bytes()).digest() for p in originals}
        with tempfile.TemporaryDirectory() as directory:
            for key in gen.JUEGOS:
                first = gen.guardar(key, Path(directory) / (key + "-a.ggb"))
                second = gen.guardar(key, Path(directory) / (key + "-b.ggb"))
                self.assertEqual(first.read_bytes(), second.read_bytes())
                with zipfile.ZipFile(first) as archive:
                    self.assertIsNone(archive.testzip())
                    self.assertEqual({n: archive.read(n) for n in archive.namelist()}, self.contents[key])
        self.assertEqual(before, {p: hashlib.sha256(p.read_bytes()).digest() for p in originals})


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--javascript" and sys.argv[2] in gen.JUEGOS:
        print('if (typeof print === "undefined") { var print = function(s) { console.log(s); }; }')
        print(gen.construir(sys.argv[2])["geogebra_javascript.js"].decode())
        print((gen.AQUI / "test_naturales_v3.js").read_text())
    else:
        unittest.main()
