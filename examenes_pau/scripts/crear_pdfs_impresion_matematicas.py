#!/usr/bin/env python3
"""Crea PDFs de impresion con todos los examenes PAU de matematicas.

Lee los manifiestos generados por ``descargar_matematicas.py`` y produce un
PDF por via. Cada pagina lleva una marca superior para distinguir modelos,
ordinaria, extraordinaria y coincidencias. Las paginas de criterios de
correccion, orientaciones, tablas de la normal y paginas en blanco se retiran
para reducir copias impresas.
"""

from __future__ import annotations

import argparse
import csv
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
from dataclasses import dataclass
from pathlib import Path


BASE_DIR = Path("examenes_pau/matematicas")
OUT_DIR = BASE_DIR / "impresion"
DEFAULT_SUBJECTS = ("matematicas_ii", "matematicas_aplicadas_ccss_ii")
SUBJECT_LABELS = {
    "matematicas_ii": "Matematicas II",
    "matematicas_aplicadas_ccss_ii": "Matematicas Aplicadas CCSS II",
}
SUBJECT_SHORT_LABELS = {
    "matematicas_ii": "MAT II",
    "matematicas_aplicadas_ccss_ii": "MA CCSS II",
}
TYPE_ORDER = {
    "MODELO": 0,
    "ORDINARIA": 1,
    "ORDINARIA - COINCIDENCIAS": 2,
    "EXTRAORDINARIA": 3,
    "EXTRAORDINARIA - COINCIDENCIAS": 4,
}
TYPE_COLORS = {
    "MODELO": (0.10, 0.27, 0.60),
    "ORDINARIA": (0.00, 0.43, 0.25),
    "ORDINARIA - COINCIDENCIAS": (0.78, 0.39, 0.00),
    "EXTRAORDINARIA": (0.68, 0.10, 0.10),
    "EXTRAORDINARIA - COINCIDENCIAS": (0.47, 0.16, 0.60),
}
SECTION_LABELS = {
    "modelos de examen": "MODELO",
    "convocatoria ordinaria": "ORDINARIA",
    "convocatoria extraordinaria": "EXTRAORDINARIA",
}


@dataclass(frozen=True)
class ExamItem:
    subject: str
    section: str
    title: str
    path: Path
    year_start: int
    year_end: int
    mark: str
    original_order: int


def fold(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    return "".join(ch for ch in normalized if not unicodedata.combining(ch)).lower()


def ascii_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    return "".join(ch for ch in normalized if ord(ch) < 128)


def ps_string(value: str) -> str:
    value = ascii_text(value)
    return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def extract_years(value: str) -> tuple[int, int] | None:
    match = re.search(r"(20\d{2})\D+(20\d{2})", value)
    if not match:
        return None
    return int(match.group(1)), int(match.group(2))


def infer_years_from_pdf(path: Path) -> tuple[int, int] | None:
    if not shutil.which("pdftotext"):
        return None
    try:
        completed = subprocess.run(
            ["pdftotext", "-f", "1", "-l", "1", path.as_posix(), "-"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=20,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return extract_years(completed.stdout)


def mark_for(section: str, title: str, path: Path) -> str:
    base = SECTION_LABELS.get(fold(section), ascii_text(section).upper())
    if "coincidencia" in fold(title) or "coincidencias" in fold(path.as_posix()):
        base = f"{base} - COINCIDENCIAS"
    return base


def load_items(subject: str, base_dir: Path) -> list[ExamItem]:
    manifest_path = base_dir / subject / "manifest.csv"
    items: list[ExamItem] = []
    with manifest_path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for index, row in enumerate(reader):
            pdf_path = Path(row["output_path"])
            years = (
                extract_years(row["title"])
                or extract_years(pdf_path.name)
                or infer_years_from_pdf(pdf_path)
            )
            if years is None:
                raise ValueError(f"No se puede inferir el curso de {pdf_path}")
            items.append(
                ExamItem(
                    subject=subject,
                    section=row["section"],
                    title=row["title"],
                    path=pdf_path,
                    year_start=years[0],
                    year_end=years[1],
                    mark=mark_for(row["section"], row["title"], pdf_path),
                    original_order=index,
                )
            )
    return sorted(
        items,
        key=lambda item: (
            -item.year_start,
            -item.year_end,
            TYPE_ORDER.get(item.mark, 99),
            item.original_order,
        ),
    )


def check_tools() -> None:
    missing = [
        tool
        for tool in ("gs", "pdfinfo", "pdfseparate", "pdftotext", "pdfunite")
        if shutil.which(tool) is None
    ]
    if missing:
        raise RuntimeError(f"Faltan herramientas necesarias: {', '.join(missing)}")


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def page_count(pdf_path: Path) -> int:
    completed = subprocess.run(
        ["pdfinfo", pdf_path.as_posix()],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    match = re.search(r"^Pages:\s+(\d+)$", completed.stdout, flags=re.MULTILINE)
    if not match:
        raise ValueError(f"No se puede leer el numero de paginas de {pdf_path}")
    return int(match.group(1))


def extract_pages(input_pdf: Path, out_pattern: Path) -> None:
    run(["pdfseparate", input_pdf.as_posix(), out_pattern.as_posix()])


def page_text(page_pdf: Path) -> str:
    completed = subprocess.run(
        ["pdftotext", page_pdf.as_posix(), "-"],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
    )
    return completed.stdout


def is_normal_table_page(text: str) -> bool:
    text = fold(text)
    standard_table = (
        "normal estandar" in text
        and ("areas bajo la distribucion" in text or "area bajo la curva normal" in text)
        and "0,5000" in text
    )
    compact_table = (
        "distribucion normal" in text
        and "0,5000" in text
        and "0,5398" in text
        and "0,9987" in text
    )
    return standard_table or compact_table


def is_correction_criteria_page(text: str) -> bool:
    text = fold(text)
    return (
        "criterios especificos" in text
        and ("correccion" in text or "calificacion" in text)
    )


def is_orientation_page(text: str) -> bool:
    text = fold(text)
    return "documento de orientaciones para la pau" in text


def is_blank_page(text: str) -> bool:
    return not re.search(r"[0-9A-Za-z]", ascii_text(text))


def should_drop_page(text: str) -> bool:
    return (
        is_blank_page(text)
        or is_orientation_page(text)
        or is_normal_table_page(text)
        or is_correction_criteria_page(text)
    )


def write_stamp_ps(path: Path, label: str, color: tuple[float, float, float]) -> None:
    ps = f"""/PAUStampLabel ({ps_string(label)}) def
/PAUStamp {{
  gsave
    currentpagedevice /PageSize get aload pop /pageH exch def /pageW exch def
    {color[0]} {color[1]} {color[2]} setrgbcolor
    0 pageH 6 sub pageW 6 rectfill
    0 setgray
    /Helvetica-Bold findfont 8 scalefont setfont
    18 pageH 17 sub moveto PAUStampLabel show
  grestore
}} bind def
<< /EndPage {{
  exch pop 2 ne {{ PAUStamp true }} {{ false }} ifelse
}} bind >> setpagedevice
"""
    path.write_text(ps, encoding="ascii")


def write_exam_stamp_ps(path: Path, item: ExamItem) -> None:
    short = SUBJECT_SHORT_LABELS[item.subject]
    course = f"{item.year_start}-{item.year_end}"
    label = f"{short} | {course} | {item.mark}"
    color = TYPE_COLORS.get(item.mark, (0.20, 0.20, 0.20))
    write_stamp_ps(path, label, color)


def stamp_pdf(input_pdf: Path, stamp_ps: Path, output_pdf: Path) -> None:
    run(
        [
            "gs",
            "-q",
            "-dNOPAUSE",
            "-dBATCH",
            "-sDEVICE=pdfwrite",
            f"-sOutputFile={output_pdf.as_posix()}",
            stamp_ps.as_posix(),
            input_pdf.as_posix(),
        ]
    )


def filtered_exam_pdf(item: ExamItem, tmp_dir: Path, stem: str) -> tuple[Path | None, int]:
    pages_dir = tmp_dir / f"{stem}_paginas"
    pages_dir.mkdir()
    extract_pages(item.path, pages_dir / "page_%04d.pdf")

    kept_pages: list[Path] = []
    for page in sorted(pages_dir.glob("page_*.pdf")):
        if should_drop_page(page_text(page)):
            continue
        kept_pages.append(page)

    if not kept_pages:
        return None, 0

    filtered_pdf = tmp_dir / f"{stem}_sin_normal.pdf"
    stamped_pdf = tmp_dir / f"{stem}_marcado.pdf"
    stamp_ps_path = tmp_dir / f"{stem}_marca.ps"
    if len(kept_pages) == page_count(item.path):
        source_pdf = item.path
    else:
        run(["pdfunite", *[page.as_posix() for page in kept_pages], filtered_pdf.as_posix()])
        source_pdf = filtered_pdf

    write_exam_stamp_ps(stamp_ps_path, item)
    stamp_pdf(source_pdf, stamp_ps_path, stamped_pdf)
    return stamped_pdf, len(kept_pages)


def build_subject_pdf(subject: str, base_dir: Path, out_dir: Path) -> Path:
    items = load_items(subject, base_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    output_pdf = out_dir / f"{subject}_todos.pdf"

    with tempfile.TemporaryDirectory(prefix=f"{subject}_", dir="/tmp") as tmp_name:
        tmp_dir = Path(tmp_name)
        pieces: list[Path] = []
        for number, item in enumerate(items, start=1):
            stem = f"{number:03d}_{item.year_start}_{item.year_end}_{item.mark.lower().replace(' ', '_').replace('-', '')}"
            stamped_pdf, kept_count = filtered_exam_pdf(item, tmp_dir, stem)
            if stamped_pdf is not None and kept_count:
                pieces.append(stamped_pdf)

        run(["pdfunite", *[piece.as_posix() for piece in pieces], output_pdf.as_posix()])

    return output_pdf


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Crea PDFs de impresion compilados por via de matematicas."
    )
    parser.add_argument(
        "--base-dir",
        type=Path,
        default=BASE_DIR,
        help="Directorio base con las vias de matematicas.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=OUT_DIR,
        help="Directorio donde escribir los PDFs compilados.",
    )
    parser.add_argument(
        "--materia",
        choices=[*DEFAULT_SUBJECTS, "all"],
        default="all",
        help="Materia a compilar. Por defecto: all.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    check_tools()
    subjects = DEFAULT_SUBJECTS if args.materia == "all" else (args.materia,)
    for subject in subjects:
        output_pdf = build_subject_pdf(subject, args.base_dir, args.out_dir)
        print(output_pdf)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
