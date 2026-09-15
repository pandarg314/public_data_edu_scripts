#!/usr/bin/env python3
"""Genera los juegos eliminatorios de GeoGebra de 1º ESO (T1).

    python3 generar_juegos.py

Crea, junto a este script:
    juego_numeros_naturales_1eso.ggb
    juego_potencias_1eso.ggb

Para añadir o cambiar preguntas, edita NATURALES o POTENCIAS y vuelve a
ejecutar el script. Cada reto es un diccionario con:
    tema      texto pequeño que indica el apartado del tema
    pregunta  texto normal (se parte en líneas automáticamente)
    expr      expresión grande en LaTeX ("" si no hace falta)
    ok        opción correcta (LaTeX)
    malas     tres distractores (LaTeX), mejor si son errores típicos
    expl      explicación en LaTeX que aparece al responder
Las opciones se barajan con semilla fija, así que la letra correcta cambia
de un reto a otro pero no entre ejecuciones. No uses comillas dobles.
"""

import random
import re
import textwrap
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

AQUI = Path(__file__).resolve().parent
MAX_GRUPOS = 8


def T(s):
    return r"\text{" + s + "}"


# --------------------------------------------------------------------------
# Banco de retos: NÚMEROS NATURALES
# --------------------------------------------------------------------------
NATURALES = [
    # Valor posicional
    dict(tema="Valor posicional", pregunta="¿Cuánto vale la cifra 7 en este número?",
         expr=r"3\,702\,150", ok=r"700\,000", malas=["7", r"70\,000", r"7\,000\,000"],
         expl=T("El 7 está en las centenas de millar: ") + r"700\,000"),
    dict(tema="Valor posicional", pregunta="¿Cómo se escribe «dos millones treinta mil cinco»?",
         expr="", ok=r"2\,030\,005", malas=[r"2\,300\,005", r"2\,030\,500", r"230\,005"],
         expl=T("2 millones + 30 mil + 5 unidades = ") + r"2\,030\,005"),
    dict(tema="Valor posicional", pregunta="¿Cuántas decenas completas tiene este número?",
         expr=r"4\,580", ok="458", malas=["8", "45", r"4\,580"],
         expl=r"4\,580 = 458 \cdot 10" + T(": tiene 458 decenas")),
    dict(tema="Valor posicional", pregunta="¿Qué número es?",
         expr=r"5\ \text{UM} + 3\ \text{D} + 8\ \text{U}", ok=r"5\,038",
         malas=[r"5\,308", "538", r"50\,038"],
         expl=r"5\,000 + 30 + 8 = 5\,038" + T(" (no hay centenas: se pone un 0)")),
    dict(tema="Valor posicional", pregunta="¿Cuál es la descomposición de este número?",
         expr=r"60\,407", ok=r"6\ \text{DM} + 4\ \text{C} + 7\ \text{U}",
         malas=[r"6\ \text{UM} + 4\ \text{C} + 7\ \text{U}",
                r"6\ \text{DM} + 4\ \text{D} + 7\ \text{U}",
                r"6\ \text{DM} + 4\ \text{UM} + 7\ \text{U}"],
         expl=r"60\,407 = 60\,000 + 400 + 7"),
    dict(tema="Valor posicional", pregunta="¿Cuál de estos números es el MAYOR?",
         expr="", ok=r"100\,010", malas=[r"99\,999", r"100\,001", r"98\,999"],
         expl=T("Los de 6 cifras ganan; entre ellos, ") + r"100\,010 > 100\,001"),
    dict(tema="Valor posicional", pregunta="¿Cuál es el menor número de 4 cifras, todas distintas?",
         expr="", ok=r"1\,023", malas=[r"1\,000", r"1\,234", "0123"],
         expl=T("No puede empezar por 0 ni repetir cifras: ") + r"1\,023"),
    dict(tema="Valor posicional", pregunta="¿Cuál es el mayor número de 5 cifras que acaba en 0?",
         expr="", ok=r"99\,990", malas=[r"99\,999", r"90\,000", r"100\,000"],
         expl=T("Cuatro nueves y un 0 al final: ") + r"99\,990"),
    # Aproximación
    dict(tema="Aproximación", pregunta="Redondea a los millares:",
         expr=r"45\,649", ok=r"46\,000", malas=[r"45\,000", r"45\,600", r"45\,700"],
         expl=T("La cifra de las centenas es 6 ") + r"(\geq 5)" + T(": se sube a ") + r"46\,000"),
    dict(tema="Aproximación", pregunta="Redondea a las centenas:",
         expr=r"1\,250", ok=r"1\,300", malas=[r"1\,200", r"1\,000", r"1\,250"],
         expl=T("La cifra de las decenas es 5: se redondea hacia arriba, ") + r"1\,300"),
    dict(tema="Aproximación", pregunta="Estima el resultado redondeando los números:",
         expr=r"398 \cdot 51", ok=r"\approx 20\,000",
         malas=[r"\approx 2\,000", r"\approx 200\,000", r"\approx 15\,000"],
         expl=r"398 \approx 400,\ \ 51 \approx 50,\ \ 400 \cdot 50 = 20\,000"),
    # Propiedades
    dict(tema="Propiedades de las operaciones", pregunta="¿Qué propiedad se usa?",
         expr=r"7 \cdot 8 = 8 \cdot 7", ok=T("Conmutativa"),
         malas=[T("Asociativa"), T("Distributiva"), T("Elemento neutro")],
         expl=T("Cambiar el orden de los factores no cambia el producto")),
    dict(tema="Propiedades de las operaciones", pregunta="¿Qué propiedad se usa?",
         expr=r"(2 \cdot 5) \cdot 9 = 2 \cdot (5 \cdot 9)", ok=T("Asociativa"),
         malas=[T("Conmutativa"), T("Distributiva"), T("Elemento neutro")],
         expl=T("Agrupar los factores de otra forma no cambia el producto")),
    dict(tema="Propiedades de las operaciones", pregunta="¿Qué propiedad se usa?",
         expr=r"6 \cdot (10 + 3) = 6 \cdot 10 + 6 \cdot 3", ok=T("Distributiva"),
         malas=[T("Asociativa"), T("Conmutativa"), T("Elemento neutro")],
         expl=T("El 6 multiplica a cada sumando del paréntesis")),
    dict(tema="Propiedades de las operaciones",
         pregunta="¿Cuál es el elemento neutro de la multiplicación?",
         expr="", ok="1", malas=["0", "10", T("No tiene")],
         expl=r"a \cdot 1 = a" + T(" para cualquier número")),
    dict(tema="Propiedades de las operaciones",
         pregunta="¿Cuál de estas operaciones NO es conmutativa?",
         expr="", ok=T("La resta"), malas=[T("La suma"), T("La multiplicación"), T("Todas lo son")],
         expl=r"9 - 4 \neq 4 - 9" + T(": el orden importa")),
    # Cálculo mental
    dict(tema="Cálculo mental", pregunta="Calcula mentalmente:",
         expr=r"25 \cdot 37 \cdot 4", ok=r"3\,700", malas=["370", r"37\,000", r"1\,000"],
         expl=r"25 \cdot 4 = 100" + T(", y ") + r"100 \cdot 37 = 3\,700"),
    dict(tema="Cálculo mental", pregunta="Calcula mentalmente:",
         expr=r"99 \cdot 6", ok="594", malas=["600", "606", "540"],
         expl=r"100 \cdot 6 - 6 = 600 - 6 = 594"),
    dict(tema="Cálculo mental", pregunta="Calcula mentalmente:",
         expr=r"36 \cdot 1\,000", ok=r"36\,000", malas=[r"3\,600", r"360\,000", r"1\,036"],
         expl=T("Multiplicar por 1000 es añadir tres ceros")),
    dict(tema="Cálculo mental", pregunta="Calcula mentalmente:",
         expr=r"5\,000 : 100", ok="50", malas=["500", "5", r"50\,000"],
         expl=T("Dividir entre 100 es quitar dos ceros")),
    # División
    dict(tema="División", pregunta="Divisor 7, cociente 12 y resto 5. ¿Cuál es el dividendo?",
         expr=r"D = d \cdot c + r", ok="89", malas=["84", "24", "79"],
         expl=r"7 \cdot 12 + 5 = 84 + 5 = 89"),
    dict(tema="División", pregunta="¿Qué número NO puede ser el resto de una división entre 6?",
         expr="", ok="6", malas=["0", "3", "5"],
         expl=T("El resto siempre es menor que el divisor")),
    dict(tema="División", pregunta="Calcula el cociente y el resto:",
         expr=r"250 : 8", ok=r"c = 31,\ \ r = 2",
         malas=[r"c = 30,\ \ r = 10", r"c = 32,\ \ r = 0", r"c = 31,\ \ r = 8"],
         expl=r"8 \cdot 31 = 248,\ \ 250 - 248 = 2"),
    dict(tema="División", pregunta="¿Qué división NO se puede hacer?",
         expr="", ok=r"5 : 0", malas=[r"0 : 5", r"5 : 1", r"5 : 5"],
         expl=T("No se puede dividir entre 0. En cambio, ") + r"0 : 5 = 0"),
    # Jerarquía de operaciones
    dict(tema="Jerarquía de operaciones", pregunta="Calcula:",
         expr=r"8 + 4 \cdot 3", ok="20", malas=["36", "15", "24"],
         expl=T("Primero la multiplicación: ") + r"8 + 12 = 20"),
    dict(tema="Jerarquía de operaciones", pregunta="Calcula:",
         expr=r"20 - 12 : 4", ok="17", malas=["2", "8", "16"],
         expl=T("Primero la división: ") + r"20 - 3 = 17"),
    dict(tema="Jerarquía de operaciones", pregunta="Calcula:",
         expr=r"(8 + 4) \cdot 3", ok="36", malas=["20", "15", "27"],
         expl=T("Primero el paréntesis: ") + r"12 \cdot 3 = 36"),
    dict(tema="Jerarquía de operaciones", pregunta="Calcula:",
         expr=r"18 : 3 \cdot 2", ok="12", malas=["3", "36", "9"],
         expl=T("Multiplicación y división, de izquierda a derecha: ") + r"6 \cdot 2 = 12"),
    dict(tema="Jerarquía de operaciones", pregunta="Calcula:",
         expr=r"5 \cdot (6 - 2) + 3", ok="23", malas=["35", "31", "20"],
         expl=r"5 \cdot 4 + 3 = 20 + 3 = 23"),
    dict(tema="Jerarquía de operaciones", pregunta="Calcula:",
         expr=r"30 - 2 \cdot (4 + 6)", ok="10", malas=["280", "28", "20"],
         expl=r"30 - 2 \cdot 10 = 30 - 20 = 10"),
    dict(tema="Jerarquía de operaciones", pregunta="Calcula:",
         expr=r"2 + 3 \cdot [10 - (4 + 2)]", ok="14", malas=["20", "26", "32"],
         expl=r"10 - 6 = 4,\ \ 3 \cdot 4 = 12,\ \ 2 + 12 = 14"),
    dict(tema="Jerarquía de operaciones", pregunta="Calcula:",
         expr=r"12 - 4 - 3", ok="5", malas=["11", "1", "9"],
         expl=T("De izquierda a derecha: ") + r"8 - 3 = 5"),
    dict(tema="Jerarquía de operaciones", pregunta="Calcula:",
         expr=r"7 \cdot 0 + 7", ok="7", malas=["0", "14", "49"],
         expl=r"7 \cdot 0 = 0,\ \ 0 + 7 = 7"),
    # Problemas
    dict(tema="Problemas",
         pregunta="Compro 3 cuadernos de 4 € y un bolígrafo de 2 €. Pago con un billete "
                  "de 20 €. ¿Cuánto me devuelven?",
         expr="", ok=r"6\ \text{euros}", malas=[r"14\ \text{euros}", r"2\ \text{euros}", r"8\ \text{euros}"],
         expl=r"3 \cdot 4 + 2 = 14,\ \ 20 - 14 = 6"),
    dict(tema="Problemas",
         pregunta="Un autobús lleva 48 pasajeros. En una parada bajan 15 y suben 9. "
                  "¿Cuántos pasajeros hay ahora?",
         expr="", ok="42", malas=["24", "72", "54"],
         expl=r"48 - 15 + 9 = 42"),
    dict(tema="Problemas",
         pregunta="Repartimos 125 caramelos entre 6 amigos, dando a cada uno lo máximo "
                  "posible. ¿Cuántos caramelos sobran?",
         expr="", ok="5", malas=["20", "1", "0"],
         expl=r"125 = 6 \cdot 20 + 5" + T(": tocan a 20 y sobran 5")),
    dict(tema="Problemas", pregunta="Un año tiene 365 días. ¿Cuántas semanas completas son?",
         expr="", ok="52", malas=["53", "50", "51"],
         expl=r"365 = 7 \cdot 52 + 1"),
    dict(tema="Problemas",
         pregunta="Van de excursión 150 alumnos en autobuses de 40 plazas. "
                  "¿Cuántos autobuses hacen falta?",
         expr="", ok="4", malas=["3", "5", "110"],
         expl=r"150 = 40 \cdot 3 + 30" + T(": los 30 que sobran necesitan otro autobús")),
    dict(tema="Problemas",
         pregunta="Una caja tiene 12 paquetes y cada paquete trae 25 cromos. "
                  "¿Cuántos cromos hay en 4 cajas?",
         expr="", ok=r"1\,200", malas=["300", "41", r"1\,000"],
         expl=r"4 \cdot 12 \cdot 25 = 4 \cdot 300 = 1\,200"),
    # Números romanos
    dict(tema="Números romanos", pregunta="¿Qué número es?",
         expr=T("XLIV"), ok="44", malas=["46", "64", "54"],
         expl=T("XL = 40 (10 antes de 50) y IV = 4")),
    dict(tema="Números romanos", pregunta="¿Cómo se escribe 2026 en números romanos?",
         expr="", ok=T("MMXXVI"), malas=[T("MMXVI"), T("MMXXIV"), T("MMXXXVI")],
         expl=T("MM = 2000, XX = 20, VI = 6")),
]

# --------------------------------------------------------------------------
# Banco de retos: POTENCIAS (exponente natural, sin fracciones ni letras)
# --------------------------------------------------------------------------
POTENCIAS = [
    # Qué es una potencia
    dict(tema="Qué es una potencia", pregunta="Escribe como potencia:",
         expr=r"3 \cdot 3 \cdot 3 \cdot 3 \cdot 3", ok="3^{5}", malas=["5^{3}", r"3 \cdot 5", "15"],
         expl=T("El 3 se multiplica 5 veces: base 3, exponente 5")),
    dict(tema="Qué es una potencia", pregunta="¿Cuál es la base y cuál el exponente?",
         expr="7^{4}", ok=T("base 7, exponente 4"),
         malas=[T("base 4, exponente 7"), T("base 7, exponente 28"), T("base 28, exponente 4")],
         expl=r"7^{4} = 7 \cdot 7 \cdot 7 \cdot 7" + T(": el exponente cuenta las veces")),
    dict(tema="Qué es una potencia", pregunta="¿Cómo se lee?",
         expr="6^{3}", ok=T("seis al cubo"),
         malas=[T("seis al cuadrado"), T("tres elevado a seis"), T("seis por tres")],
         expl=T("Exponente 2: al cuadrado. Exponente 3: al cubo")),
    dict(tema="Qué es una potencia", pregunta="¿Cuánto vale?",
         expr="2^{5}", ok="32", malas=["10", "25", "16"],
         expl=r"2 \cdot 2 \cdot 2 \cdot 2 \cdot 2 = 32" + T(" (no es ") + r"2 \cdot 5" + T(")")),
    dict(tema="Qué es una potencia", pregunta="¿Cuánto vale?",
         expr="3^{4}", ok="81", malas=["12", "64", "27"],
         expl=r"3 \cdot 3 \cdot 3 \cdot 3 = 9 \cdot 9 = 81"),
    dict(tema="Qué es una potencia", pregunta="¿Cuánto vale?",
         expr="2^{10}", ok=r"1\,024", malas=["20", "100", "512"],
         expl=r"2^{10} = 2^{5} \cdot 2^{5} = 32 \cdot 32 = 1\,024"),
    dict(tema="Qué es una potencia", pregunta="¿Qué es mayor?",
         expr=r"2^{3} \quad \text{o} \quad 3^{2}", ok="3^{2}",
         malas=["2^{3}", T("Son iguales"), T("No se puede saber")],
         expl=r"2^{3} = 8" + T(" y ") + r"3^{2} = 9"),
    dict(tema="Qué es una potencia", pregunta="¿Cuánto vale?",
         expr="(3 + 4)^{2}", ok="49", malas=["25", "14", "24"],
         expl=T("Primero el paréntesis: ") + r"7^{2} = 49" + T(" (no es ") + r"3^{2} + 4^{2}" + T(")")),
    dict(tema="Qué es una potencia", pregunta="¿Cuánto vale?",
         expr=r"2 + 3^{2}", ok="11", malas=["25", "8", "18"],
         expl=T("Primero la potencia: ") + r"2 + 9 = 11"),
    dict(tema="Qué es una potencia", pregunta="¿Cuánto vale?",
         expr=r"2 \cdot 3^{2}", ok="18", malas=["36", "12", "11"],
         expl=T("Primero la potencia: ") + r"2 \cdot 9 = 18"),
    # Casos especiales
    dict(tema="Exponente 0 y exponente 1", pregunta="¿Cuánto vale?",
         expr="9^{1}", ok="9", malas=["1", "0", "10"],
         expl=T("Con exponente 1 el número se queda igual")),
    dict(tema="Exponente 0 y exponente 1", pregunta="¿Cuánto vale?",
         expr="7^{0}", ok="1", malas=["0", "7", "70"],
         expl=T("Cualquier número (distinto de 0) elevado a 0 vale 1")),
    dict(tema="Exponente 0 y exponente 1", pregunta="¿Cuánto vale?",
         expr="1^{50}", ok="1", malas=["50", "0", "51"],
         expl=r"1 \cdot 1 \cdot 1 \cdot \ldots \cdot 1 = 1"),
    dict(tema="Exponente 0 y exponente 1", pregunta="¿Cuánto vale?",
         expr="0^{7}", ok="0", malas=["1", "7", "70"],
         expl=r"0 \cdot 0 \cdot 0 \cdot \ldots \cdot 0 = 0"),
    dict(tema="Exponente 0 y exponente 1", pregunta="¿Cuánto vale?",
         expr=r"((4^{3})^{0})^{2}", ok="1", malas=["4^{5}", "0", "4^{6}"],
         expl=r"3 \cdot 0 \cdot 2 = 0" + T(", y ") + r"4^{0} = 1"),
    # Cuadrados y cubos
    dict(tema="Cuadrados y cubos", pregunta="¿Cuál de estos números es un cuadrado perfecto?",
         expr="", ok="49", malas=["50", "20", "27"],
         expl=r"49 = 7^{2}." + T(" Ojo: ") + r"27 = 3^{3}" + T(" es un cubo")),
    dict(tema="Cuadrados y cubos", pregunta="¿Cuál de estos números es un cubo perfecto?",
         expr="", ok="125", malas=["25", "100", "36"],
         expl=r"125 = 5 \cdot 5 \cdot 5 = 5^{3}"),
    dict(tema="Cuadrados y cubos", pregunta="Un cuadrado mide 9 cm de lado. ¿Cuál es su área?",
         expr="", ok=r"81\ \text{cm}^{2}",
         malas=[r"18\ \text{cm}^{2}", r"36\ \text{cm}^{2}", r"27\ \text{cm}^{2}"],
         expl=T("Área = ") + r"9^{2} = 9 \cdot 9 = 81\ \text{cm}^{2}"),
    # Potencias de 10
    dict(tema="Potencias de 10", pregunta="¿Qué número es?",
         expr=r"10^{6}", ok=r"1\,000\,000", malas=["60", r"100\,000", r"10\,000\,000"],
         expl=T("Un 1 seguido de 6 ceros")),
    dict(tema="Potencias de 10", pregunta="¿Qué número es?",
         expr=r"4 \cdot 10^{5}", ok=r"400\,000", malas=[r"4\,000\,000", r"40\,000", "20"],
         expl=r"10^{5} = 100\,000,\ \ 4 \cdot 100\,000 = 400\,000"),
    dict(tema="Potencias de 10", pregunta="Escríbelo con una potencia de 10:",
         expr=r"7\,000\,000", ok=r"7 \cdot 10^{6}", malas=[r"7 \cdot 10^{7}", "10^{7}", "7^{6}"],
         expl=T("Detrás del 7 hay 6 ceros")),
    dict(tema="Potencias de 10", pregunta="¿Qué número es?",
         expr=r"3 \cdot 10^{3} + 5 \cdot 10^{1} + 2", ok=r"3\,052",
         malas=[r"3\,502", "352", r"30\,052"],
         expl=r"3\,000 + 50 + 2 = 3\,052"),
    dict(tema="Potencias de 10", pregunta="¿Cuántos ceros tiene este número escrito con cifras?",
         expr="10^{8}", ok="8", malas=["9", "80", "7"],
         expl=r"10^{8} = 100\,000\,000"),
    # Problemas
    dict(tema="Problemas",
         pregunta="Una bacteria se divide en 2 cada hora. Empezamos con 1. "
                  "¿Cuántas bacterias habrá dentro de 6 horas?",
         expr="", ok="64", malas=["12", "36", "32"],
         expl=r"2 \cdot 2 \cdot 2 \cdot 2 \cdot 2 \cdot 2 = 2^{6} = 64"),
    dict(tema="Problemas",
         pregunta="Un edificio tiene 5 plantas, cada planta tiene 5 pisos y cada piso "
                  "tiene 5 ventanas. ¿Cuántas ventanas hay?",
         expr="", ok="125", malas=["15", "25", "53"],
         expl=r"5 \cdot 5 \cdot 5 = 5^{3} = 125"),
    # Producto de potencias de la misma base
    dict(tema="Producto de potencias de la misma base", pregunta="Exprésalo como una sola potencia:",
         expr=r"5^{3} \cdot 5^{4}", ok="5^{7}", malas=["5^{12}", "25^{7}", "10^{7}"],
         expl=T("Misma base: se suman los exponentes, ") + "3 + 4 = 7"),
    dict(tema="Producto de potencias de la misma base", pregunta="Exprésalo como una sola potencia:",
         expr=r"2^{3} \cdot 2 \cdot 2^{6}", ok="2^{10}", malas=["2^{9}", "2^{18}", "8^{10}"],
         expl=T("El 2 del medio es ") + "2^{1}" + T(": ") + "3 + 1 + 6 = 10"),
    dict(tema="Producto de potencias de la misma base", pregunta="Exprésalo como una sola potencia:",
         expr=r"10^{3} \cdot 10^{4}", ok="10^{7}", malas=["10^{12}", "100^{7}", "20^{7}"],
         expl=r"3 + 4 = 7,\ \ 10^{7} = 10\,000\,000"),
    # Cociente de potencias de la misma base
    dict(tema="Cociente de potencias de la misma base", pregunta="Exprésalo como una sola potencia:",
         expr=r"5^{8} : 5^{6}", ok="5^{2}", malas=["5^{14}", "1^{2}", "5^{48}"],
         expl=T("Misma base: se restan los exponentes, ") + "8 - 6 = 2"),
    dict(tema="Cociente de potencias de la misma base", pregunta="Exprésalo como una sola potencia:",
         expr=r"2^{3} : 2", ok="2^{2}", malas=["2^{3}", "1^{3}", "2^{4}"],
         expl=T("El 2 es ") + "2^{1}" + T(": ") + "3 - 1 = 2"),
    dict(tema="Cociente de potencias de la misma base", pregunta="¿Cuánto vale?",
         expr=r"7^{4} : 7^{4}", ok="1", malas=["0", "7", "7^{8}"],
         expl=r"7^{4-4} = 7^{0} = 1" + T(" (un número entre sí mismo da 1)")),
    dict(tema="Cociente de potencias de la misma base", pregunta="Exprésalo como una sola potencia:",
         expr=r"2^{4} \cdot 2^{2} : 2^{3}", ok="2^{3}", malas=["2^{9}", "2^{5}", "4^{3}"],
         expl="4 + 2 - 3 = 3"),
    # Potencia de una potencia
    dict(tema="Potencia de una potencia", pregunta="Exprésalo como una sola potencia:",
         expr=r"\left(5^{3}\right)^{4}", ok="5^{12}", malas=["5^{7}", "5^{81}", "20^{3}"],
         expl=T("Se multiplican los exponentes: ") + r"3 \cdot 4 = 12"),
    dict(tema="Potencia de una potencia", pregunta="¿Cuánto vale?",
         expr=r"\left(2^{2}\right)^{3}", ok="64", malas=["32", "12", "36"],
         expl=r"\left(2^{2}\right)^{3} = 2^{6} = 64" + T(" (no es ") + "2^{5}" + T(")")),
    # Mismo exponente
    dict(tema="Potencias con el mismo exponente", pregunta="Exprésalo como una sola potencia:",
         expr=r"5^{8} \cdot 3^{8}", ok="15^{8}", malas=["15^{16}", "8^{8}", "15^{64}"],
         expl=T("Mismo exponente: se multiplican las bases, ") + r"5 \cdot 3 = 15"),
    dict(tema="Potencias con el mismo exponente", pregunta="Exprésalo como una sola potencia:",
         expr=r"6^{5} : 3^{5}", ok="2^{5}", malas=["3^{5}", "2^{0}", "18^{5}"],
         expl=T("Mismo exponente: se dividen las bases, ") + "6 : 3 = 2"),
    dict(tema="Potencias con el mismo exponente", pregunta="¿Cuánto vale?",
         expr=r"(2 \cdot 5)^{3}", ok=r"1\,000", malas=["250", "30", "100"],
         expl=r"10^{3} = 1\,000" + T(" (el exponente afecta al 2 y al 5)")),
    dict(tema="Potencias con el mismo exponente", pregunta="¿Cuánto vale?",
         expr=r"(3 \cdot 4)^{2}", ok="144", malas=["48", "24", "36"],
         expl=r"12^{2} = 144 = 3^{2} \cdot 4^{2} = 9 \cdot 16"),
    # Suma y resta
    dict(tema="¡Cuidado con la suma y la resta!", pregunta="¿Cuánto vale?",
         expr=r"2^{5} + 2^{3}", ok="40", malas=["2^{8}", "4^{8}", "2^{15}"],
         expl=T("No hay propiedad para la suma: ") + "32 + 8 = 40"),
    dict(tema="¡Cuidado con la suma y la resta!", pregunta="¿Cuánto vale?",
         expr=r"5^{4} - 2^{4}", ok="609", malas=["3^{4}", "3^{0}", "109"],
         expl=T("No hay propiedad para la resta: ") + "625 - 16 = 609"),
    dict(tema="¡Cuidado con la suma y la resta!", pregunta="¿Qué igualdad es FALSA?",
         expr="", ok=r"2^{3} + 2^{4} = 2^{7}",
         malas=[r"2^{3} \cdot 2^{4} = 2^{7}", r"\left(2^{3}\right)^{4} = 2^{12}", r"2^{4} : 2^{3} = 2"],
         expl=r"2^{3} + 2^{4} = 8 + 16 = 24" + T(", pero ") + "2^{7} = 128"),
    dict(tema="Repaso de propiedades", pregunta="¿Qué igualdad es VERDADERA?",
         expr="", ok=r"4^{3} \cdot 5^{3} = 20^{3}",
         malas=[r"3^{2} \cdot 3^{2} = 9^{4}", r"3^{5} : 3^{5} = 0", r"\left(2^{2}\right)^{3} = 2^{5}"],
         expl=T("Mismo exponente: se multiplican las bases, ") + r"4 \cdot 5 = 20"),
    # Escribir como potencia
    dict(tema="Escribir como potencia", pregunta="Escribe 81 como potencia de base 3:",
         expr="", ok="3^{4}", malas=["3^{27}", "9^{3}", "3^{3}"],
         expl=r"3 \cdot 3 \cdot 3 \cdot 3 = 81"),
    dict(tema="Escribir como potencia", pregunta="Escribe 1000 como potencia de base 10:",
         expr="", ok="10^{3}", malas=["10^{4}", "3^{10}", "100^{10}"],
         expl=r"10 \cdot 10 \cdot 10 = 1\,000"),
]

# --------------------------------------------------------------------------
# Construcción del .ggb
# --------------------------------------------------------------------------
JS_CRONO = """\
// ===== Cronómetro de cuenta atrás =====
// En cada reto nuevo (cambia "ronda") vuelve a "segundos"; se para al responder.
// "segundos" se elige en la pantalla de inicio (0 = sin límite).
//
// Funciona en GeoGebra Classic 6 / web (setInterval nativo) y en
// GeoGebra Classic 5 de escritorio (Java/Rhino), donde se emula con java.util.Timer.

if (typeof setInterval === "undefined" && typeof JavaAdapter !== "undefined") {
    var _ggbTimer = new java.util.Timer();
    setInterval = function (fn, delay) {
        var task = new JavaAdapter(java.util.TimerTask, { run: fn });
        _ggbTimer.schedule(task, delay, delay);
        return task;
    };
}

var _arrancado = false;

function ggbOnInit() {
    ggbApplet.registerObjectUpdateListener("ronda", "reiniciarCrono");
    if (!_arrancado && typeof setInterval !== "undefined") {
        setInterval(tick, 1000);
        _arrancado = true;
    }
}

function reiniciarCrono() {
    ggbApplet.setValue("restante", ggbApplet.getValue("segundos"));
}

function tick() {
    if (ggbApplet.getValue("reto") < 1 || ggbApplet.getValue("resp") > 0) return;
    var r = ggbApplet.getValue("restante");
    if (r > 0.5) {
        ggbApplet.setValue("restante", r - 1);
    }
}
"""

COL_TITULO = (20, 50, 110)
COL_GRIS = (110, 110, 110)
COL_OPCION = (222, 233, 250)
COL_OK_BG, COL_OK = (190, 236, 196), (0, 110, 30)
COL_MAL_BG, COL_MAL = (250, 205, 205), (170, 0, 0)
COL_TURNO_BG = (255, 234, 140)


def attr(s):
    return escape(str(s), {'"': "&quot;", "\n": "&#10;"})


def ggb_str(s):
    assert '"' not in s, f"No se pueden usar comillas dobles: {s}"
    return '"' + s + '"'


def opcion_larga(o):
    """True si la opción no cabe en media pantalla con letra grande."""
    if "\\ \\text{" in o or re.search(r"\\text\{[^}]{5,}\}", o):
        return True
    visible = re.sub(r"\\[a-zA-Z]+|\\.|[{}^]", "", o)
    return len(visible) > 11


def ggb_list(items):
    return "{" + ", ".join(items) + "}"


class Construccion:
    def __init__(self):
        self.partes = []

    def add(self, xml):
        self.partes.append(xml)

    def numero(self, label, valor):
        self.add(f'<expression label="{label}" exp="{valor}"/>\n'
                 f'<element type="numeric" label="{label}">\n'
                 f'\t<value val="{valor}"/>\n\t<show object="false" label="false"/>\n'
                 f'</element>')

    def oculto(self, label, exp, tipo):
        self.add(f'<expression label="{label}" exp="{attr(exp)}"/>\n'
                 f'<element type="{tipo}" label="{label}">\n'
                 f'\t<show object="false" label="false"/>\n'
                 f'</element>')

    def texto(self, label, exp, x, y, cond=None, color=(0, 0, 0), bg=None, size=1.0,
              bold=False, latex=False, script=None):
        xml = [f'<expression label="{label}" exp="{attr(exp)}"/>',
               f'<element type="text" label="{label}">',
               '\t<show object="true" label="false"/>']
        if cond:
            xml.append(f'\t<condition showObject="{attr(cond)}"/>')
        xml.append('\t<objColor r="%d" g="%d" b="%d" alpha="0"/>' % color)
        if bg:
            xml.append('\t<bgColor r="%d" g="%d" b="%d" alpha="255"/>' % bg)
        xml += ['\t<layer val="5"/>', '\t<labelMode val="0"/>', '\t<fixed val="true"/>']
        if latex:
            xml.append('\t<isLaTeX val="true"/>')
        xml.append(f'\t<font serif="false" sizeM="{size}" size="0" style="{1 if bold else 0}"/>')
        xml.append(f'\t<absoluteScreenLocation x="{x}" y="{y}"/>')
        if script:
            xml.append(f'\t<ggbscript val="{attr(script)}"/>')
        xml.append('</element>')
        self.add("\n".join(xml))

    def boton(self, label, caption, x, y, script, cond=None, bg=(40, 90, 200),
              color=(255, 255, 255), size=1.4, w=None, h=None):
        xml = [f'<element type="button" label="{label}">',
               '\t<show object="true" label="true"/>']
        if cond:
            xml.append(f'\t<condition showObject="{attr(cond)}"/>')
        xml.append('\t<objColor r="%d" g="%d" b="%d" alpha="0"/>' % color)
        xml.append('\t<bgColor r="%d" g="%d" b="%d" alpha="255"/>' % bg)
        xml += ['\t<layer val="6"/>', '\t<labelMode val="0"/>', '\t<fixed val="true"/>',
                '\t<auxiliary val="true"/>',
                f'\t<ggbscript val="{attr(script)}"/>',
                f'\t<font serif="false" sizeM="{size}" size="0" style="1"/>',
                f'\t<caption val="{attr(caption)}"/>',
                f'\t<absoluteScreenLocation x="{x}" y="{y}"/>']
        if w and h:
            xml.append(f'\t<dimensions width="{w}" height="{h}" angle="0" scaled="false"/>')
        xml.append('</element>')
        self.add("\n".join(xml))


def construir_xml(titulo, retos, semilla):
    n = len(retos)
    rng = random.Random(semilla)
    temas, preguntas, exprs, sols, expls, largos = [], [], [], [], [], []
    ops = {L: [] for L in "ABCD"}
    # La letra correcta se reparte a partes iguales entre A, B, C y D.
    letras = [k % 4 for k in range(n)]
    rng.shuffle(letras)
    for k, r in enumerate(retos, 1):
        assert len(r["malas"]) == 3 and len({r["ok"], *r["malas"]}) == 4, f"Reto {k}: opciones repetidas"
        opciones = list(r["malas"])
        rng.shuffle(opciones)
        opciones.insert(letras[k - 1], r["ok"])
        for L, o in zip("ABCD", opciones):
            ops[L].append(ggb_str(o))
        sols.append(str(opciones.index(r["ok"]) + 1))
        largos.append("1" if any(opcion_larga(o) for o in opciones) else "0")
        temas.append(ggb_str(r["tema"]))
        preguntas.append(ggb_str("\n".join(textwrap.wrap(r["pregunta"], 60))))
        exprs.append(ggb_str(r["expr"]))
        expls.append(ggb_str(r["expl"]))

    c = Construccion()
    # --- estado del juego ---
    for label, val in [("N", n), ("reto", 0), ("resp", 0), ("ronda", 0), ("G", 5),
                       ("turno", 1), ("segundos", 30), ("restante", 30)]:
        c.numero(label, val)
    c.oculto("pend", ggb_list(str(k) for k in range(1, n + 1)), "list")
    c.oculto("elim", ggb_list(["0"] * MAX_GRUPOS), "list")
    c.oculto("comodin", ggb_list(["1"] * MAX_GRUPOS), "list")
    c.oculto("aciertos", ggb_list(["0"] * MAX_GRUPOS), "list")
    # --- banco de retos ---
    c.oculto("tema", ggb_list(temas), "list")
    c.oculto("pregunta", ggb_list(preguntas), "list")
    c.oculto("expr", ggb_list(exprs), "list")
    for L in "ABCD":
        c.oculto("op" + L, ggb_list(ops[L]), "list")
    c.oculto("sol", ggb_list(sols), "list")
    c.oculto("expl", ggb_list(expls), "list")
    c.oculto("largo", ggb_list(largos), "list")
    # --- valores derivados ---
    c.oculto("solActual", "If(reto > 0, Element(sol, reto), 0)", "numeric")
    c.oculto("unaCol", "If(reto > 0, Element(largo, reto), 0)", "numeric")
    c.oculto("vivos", f"Sum(Sequence(If(k ≤ G ∧ Element(elim, k) ≟ 0, 1, 0), k, 1, {MAX_GRUPOS}))",
             "numeric")
    c.oculto("ganador", f"Sum(Sequence(If(k ≤ G ∧ Element(elim, k) ≟ 0, k, 0), k, 1, {MAX_GRUPOS}))",
             "numeric")
    c.oculto("orden", "Sequence(Mod(turno + j - 1, G) + 1, j, 1, G)", "list")
    c.oculto("candidatos",
             "Sequence(If(Element(elim, Element(orden, j)) ≟ 0, Element(orden, j), 0), j, 1, G)", "list")
    c.oculto("sigTurno", "Element(KeepIf(x > 0, candidatos), 1)", "numeric")

    # --- guiones ---
    sortear = "\n".join([
        "If(Length(pend) ≟ 0, SetValue(pend, Sequence(N)))",
        "SetValue(reto, RandomElement(pend))",
        "SetValue(pend, KeepIf(x ≠ reto, pend))",
        "SetValue(resp, 0)",
        "SetValue(ronda, ronda + 1)",
    ])
    empezar = "\n".join([
        f"SetValue(elim, {ggb_list(['0'] * MAX_GRUPOS)})",
        f"SetValue(comodin, {ggb_list(['1'] * MAX_GRUPOS)})",
        f"SetValue(aciertos, {ggb_list(['0'] * MAX_GRUPOS)})",
        "SetValue(turno, 1)",
        "SetValue(pend, Sequence(N))",
        "SetValue(ronda, 0)",
        sortear,
    ])
    siguiente = "If(vivos > 1, SetValue(turno, sigTurno))\n" + sortear
    pasapalabra = "SetValue(comodin, turno, 0)\nSetValue(turno, sigTurno)\n" + sortear

    inicio, juego = "reto ≟ 0", "reto > 0"

    # --- cabecera ---
    c.texto("tTitulo", ggb_str(titulo), 30, 50, color=COL_TITULO, size=1.7, bold=True)

    # --- pantalla de inicio ---
    reglas = ("Cómo se juega\n"
              "1. Cada grupo, en su turno, recibe un reto al azar.\n"
              "2. Si responde bien, sigue en juego. Si falla, queda eliminado.\n"
              "3. Una vez por partida, un grupo puede decir PASAPALABRA:\n"
              "    no responde, no le eliminan y el turno pasa al siguiente grupo.\n"
              "4. Gana el último grupo que quede en juego.")
    c.texto("tReglas", ggb_str(reglas), 30, 120, cond=inicio, size=1.4)
    c.texto("tGrupos", '"Número de grupos: " + G', 30, 430, cond=inicio, size=1.6, bold=True)
    c.boton("bGmenos", "  −  ", 380, 390, "SetValue(G, Max(2, G - 1))", cond=inicio, size=2.2)
    c.boton("bGmas", "  +  ", 470, 390, f"SetValue(G, Min({MAX_GRUPOS}, G + 1))", cond=inicio, size=2.2)
    c.texto("tSegundos",
            'If(segundos ≟ 0, "Tiempo por reto: sin límite", "Tiempo por reto: " + segundos + " s")',
            30, 510, cond=inicio, size=1.6, bold=True)
    c.boton("bTmenos", "  −  ", 380, 470, "SetValue(segundos, Max(0, segundos - 5))", cond=inicio, size=2.2)
    c.boton("bTmas", "  +  ", 470, 470, "SetValue(segundos, Min(120, segundos + 5))", cond=inicio, size=2.2)
    c.boton("bEmpezar", "   EMPEZAR   ", 30, 570, empezar, cond=inicio, bg=(30, 140, 60), size=2.6)

    # --- reto ---
    c.texto("tTema", "Element(tema, reto)", 30, 88, cond=juego, color=COL_GRIS, size=1.1)
    c.texto("tRonda", '"Reto " + ronda + "   (quedan " + Length(pend) + " sin salir)"', 520, 50,
            cond=juego, color=COL_GRIS, size=1.1)
    c.texto("tPregunta", "Element(pregunta, reto)", 30, 135, cond=juego, size=1.5, bold=True)
    # Con Element(...) a secas GeoGebra no aplica LaTeX; concatenado con "" sí.
    c.texto("tExpr", '"" + Element(expr, reto)', 50, 170, cond=juego, size=3.2, latex=True)

    # Opciones cortas: rejilla 2x2. Opciones largas: una columna.
    disposiciones = [
        ("", "unaCol ≟ 0", 2.2, {"A": (30, 285), "B": (440, 285), "C": (30, 380), "D": (440, 380)}),
        ("_1col", "unaCol ≟ 1", 2.0, {"A": (30, 272), "B": (30, 334), "C": (30, 396), "D": (30, 458)}),
    ]
    for (suf, cond_disp, tam, posiciones), (k, L) in (
            (d, kl) for d in disposiciones for kl in enumerate("ABCD", 1)):
        x, y = posiciones[L]
        exp = f'"\\;\\text{{{L})}}\\quad " + Element(op{L}, reto) + "\\;\\;"'
        responder = "\n".join([
            f"If(reto > 0 ∧ resp ≟ 0 ∧ vivos > 1 ∧ solActual ≟ {k}, "
            f"SetValue(aciertos, turno, Element(aciertos, turno) + 1))",
            f"If(reto > 0 ∧ resp ≟ 0 ∧ vivos > 1 ∧ solActual ≠ {k}, SetValue(elim, turno, 1))",
            f"If(reto > 0 ∧ resp ≟ 0, SetValue(resp, {k}))",
        ])
        c.texto(f"op{L}_normal{suf}", exp, x, y, size=tam, latex=True, bg=COL_OPCION, script=responder,
                cond=f"reto > 0 ∧ {cond_disp} ∧ ¬(resp > 0 ∧ (solActual ≟ {k} ∨ resp ≟ {k}))")
        c.texto(f"op{L}_bien{suf}", exp, x, y, size=tam, latex=True, bg=COL_OK_BG, color=COL_OK,
                cond=f"reto > 0 ∧ {cond_disp} ∧ resp > 0 ∧ solActual ≟ {k}")
        c.texto(f"op{L}_mal{suf}", exp, x, y, size=tam, latex=True, bg=COL_MAL_BG, color=COL_MAL,
                cond=f"reto > 0 ∧ {cond_disp} ∧ resp ≟ {k} ∧ solActual ≠ {k}")

    c.texto("tBien", '"¡CORRECTO!  El Grupo " + turno + " sigue en juego."', 30, 568,
            cond="reto > 0 ∧ resp > 0 ∧ resp ≟ solActual", color=COL_OK, size=1.6, bold=True)
    c.texto("tMal", '"INCORRECTO.  El Grupo " + turno + " queda eliminado."', 30, 568,
            cond="reto > 0 ∧ resp > 0 ∧ resp ≠ solActual ∧ Element(elim, turno) ≟ 1",
            color=COL_MAL, size=1.6, bold=True)
    c.texto("tMalSinElim", '"INCORRECTO."', 30, 568,
            cond="reto > 0 ∧ resp > 0 ∧ resp ≠ solActual ∧ Element(elim, turno) ≟ 0",
            color=COL_MAL, size=1.6, bold=True)
    c.texto("tExpl", '"" + Element(expl, reto)', 30, 588, cond="reto > 0 ∧ resp > 0", size=1.5, latex=True)

    c.texto("tCrono", '"Tiempo: " + restante + " s"', 1080, 50,
            cond="reto > 0 ∧ resp ≟ 0 ∧ segundos > 0 ∧ restante > 0", color=(0, 90, 0), size=1.5,
            bold=True)
    c.texto("tCrono0", '"¡TIEMPO!"', 1080, 50,
            cond="reto > 0 ∧ resp ≟ 0 ∧ segundos > 0 ∧ restante ≤ 0", color=COL_MAL, size=1.7,
            bold=True)

    c.boton("bPasa", "  PASAPALABRA  ", 30, 655, pasapalabra, bg=(235, 130, 0), size=2.0,
            cond="reto > 0 ∧ resp ≟ 0 ∧ vivos > 1 ∧ Element(comodin, turno) ≟ 1")
    c.boton("bSiguiente", "  Siguiente reto ►  ", 400, 655, siguiente, bg=(40, 90, 200), size=2.0,
            cond="reto > 0 ∧ vivos > 1")
    c.boton("bNueva", "Nueva partida", 1110, 690, "SetValue(reto, 0)\nSetValue(resp, 0)",
            bg=(130, 130, 130), size=1.0, cond=juego)

    # --- marcador ---
    c.texto("tTurno", '"Turno: Grupo " + turno', 850, 110, cond="reto > 0 ∧ vivos > 1",
            color=COL_TITULO, size=1.8, bold=True)
    for k in range(1, MAX_GRUPOS + 1):
        y = 170 + 48 * (k - 1)
        ac = f"Element(aciertos, {k})"
        cuenta = f'{ac} + If({ac} ≟ 1, " acierto", " aciertos")'
        comodin = f'If(Element(comodin, {k}) ≟ 1, "  ·  pasapalabra", "")'
        vivo = f"reto > 0 ∧ {k} ≤ G ∧ Element(elim, {k}) ≟ 0"
        c.texto(f"g{k}_vivo", f'"Grupo {k}  ·  " + {cuenta} + {comodin}', 850, y,
                cond=f"{vivo} ∧ turno ≠ {k}", size=1.2)
        c.texto(f"g{k}_turno", f'"► Grupo {k}  ·  " + {cuenta} + {comodin} + " "', 850, y,
                cond=f"{vivo} ∧ turno ≟ {k}", size=1.2, bold=True, bg=COL_TURNO_BG)
        c.texto(f"g{k}_elim", f'"Grupo {k}  ·  eliminado  (" + {cuenta} + ")"', 850, y,
                cond=f"reto > 0 ∧ {k} ≤ G ∧ Element(elim, {k}) ≟ 1", color=(160, 160, 160), size=1.2)
    c.texto("tGanador", '" ¡GANA EL GRUPO " + ganador + "! "', 850, 600,
            cond="reto > 0 ∧ vivos ≟ 1", color=(120, 60, 0), bg=(255, 215, 90), size=2.2, bold=True)

    cons = "\n".join(c.partes)
    return f"""<?xml version="1.0" encoding="utf-8"?>
<geogebra format="5.0" version="5.0.0.0" app="classic" xsi:noNamespaceSchemaLocation="http://www.geogebra.org/apps/xsd/ggb.xsd" xmlns="" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<gui>
\t<window width="1300" height="760"/>
\t<perspectives>
<perspective id="tmp">
\t<panes>
\t<pane location="" divider="1.0" orientation="1"/>
</panes>
\t<views>
\t<view id="1" visible="true" inframe="false" stylebar="false" location="1" size="1300" window="100,100,600,400"/>
\t<view id="2" visible="false" inframe="false" stylebar="false" location="3" size="300" window="100,100,250,400"/>
</views>
\t<toolbar show="false" items="0" position="1" help="false"/>
\t<input show="false" cmd="true" top="algebra"/>
\t<dockBar show="false" east="false"/>
</perspective>
</perspectives>
\t<labelingStyle val="0"/>
\t<font size="16"/>
</gui>
<euclidianView>
\t<size width="1300" height="760"/>
\t<coordSystem xZero="650" yZero="380" scale="50" yscale="50"/>
\t<evSettings axes="false" grid="false" gridIsBold="false" pointCapturing="0" rightAngleStyle="1" checkboxSize="26" gridType="3"/>
\t<bgColor r="250" g="250" b="247"/>
\t<axesColor r="0" g="0" b="0"/>
\t<gridColor r="220" g="220" b="220"/>
\t<lineStyle axes="1" grid="0"/>
\t<axis id="0" show="false" label="" unitLabel="" tickStyle="1" showNumbers="true"/>
\t<axis id="1" show="false" label="" unitLabel="" tickStyle="1" showNumbers="true"/>
</euclidianView>
<kernel>
\t<continuous val="false"/>
\t<usePathAndRegionParameters val="true"/>
\t<decimals val="2"/>
\t<angleUnit val="degree"/>
\t<algebraStyle val="0"/>
\t<coordStyle val="0"/>
</kernel>
<scripting blocked="false" disabled="false"/>
<construction title="{attr(titulo)}" author="" date="">
{cons}
</construction>
</geogebra>
"""


def guardar(nombre, titulo, retos, semilla):
    ruta = AQUI / nombre
    with zipfile.ZipFile(ruta, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("geogebra.xml", construir_xml(titulo, retos, semilla))
        z.writestr("geogebra_javascript.js", JS_CRONO)
    print(f"{ruta.name}: {len(retos)} retos")


if __name__ == "__main__":
    guardar("juego_numeros_naturales_1eso.ggb", "NÚMEROS NATURALES · 1º ESO", NATURALES, 1)
    guardar("juego_potencias_1eso.ggb", "POTENCIAS · 1º ESO", POTENCIAS, 2)
