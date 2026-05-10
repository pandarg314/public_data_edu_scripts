#!/usr/bin/env python3
"""Descarga examenes PAU/EvAU de Matematicas II desde la pagina UC3M.

El script no usa dependencias externas: parsea el HTML, localiza los enlaces
de la tabla de examenes y convierte los enlaces de Google Drive a URLs de
descarga directa. Escribe un manifiesto CSV para que el docente pueda auditar
fuente, destino y estado de cada archivo.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import re
import sys
import unicodedata
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, quote, urljoin, urlparse
from urllib.request import HTTPCookieProcessor, Request, build_opener


SOURCE_URL = (
    "https://www.uc3m.es/ss/Satellite/evau/es/TextoMixta/"
    "1371318154983/Examenes_de_Matematicas_II"
)
DEFAULT_OUT_DIR = Path("examenes_pau/matematicas/matematicas_ii")
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0 Safari/537.36"
)
EXAM_SECTIONS = {
    "modelos de examen",
    "convocatoria ordinaria",
    "convocatoria extraordinaria",
}


@dataclass(frozen=True)
class PageLink:
    text: str
    href: str
    section: str


@dataclass(frozen=True)
class DownloadItem:
    title: str
    section: str
    source_url: str
    download_url: str
    output_path: Path


@dataclass
class Result:
    item: DownloadItem
    status: str
    note: str = ""
    sha256: str = ""
    bytes_written: int = 0


class Uc3mExamParser(HTMLParser):
    """Parser minimo para conservar la seccion de cada enlace de la tabla."""

    def __init__(self, base_url: str) -> None:
        super().__init__(convert_charrefs=True)
        self.base_url = base_url
        self.links: list[PageLink] = []
        self.headers: list[str] = []
        self._in_th = False
        self._in_td = False
        self._in_a = False
        self._row_cell_index = 0
        self._current_section = ""
        self._th_text: list[str] = []
        self._a_text: list[str] = []
        self._a_href = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = {name.lower(): value or "" for name, value in attrs}

        if tag == "tr":
            self._row_cell_index = 0
        elif tag == "th":
            self._in_th = True
            self._th_text = []
        elif tag == "td":
            self._in_td = True
            if self._row_cell_index < len(self.headers):
                self._current_section = self.headers[self._row_cell_index]
            else:
                self._current_section = ""
            self._row_cell_index += 1
        elif tag == "a":
            self._in_a = True
            self._a_text = []
            self._a_href = attrs_dict.get("href", "")

    def handle_endtag(self, tag: str) -> None:
        if tag == "th":
            text = clean_text(" ".join(self._th_text))
            if text:
                self.headers.append(text)
            self._in_th = False
            self._th_text = []
        elif tag == "td":
            self._in_td = False
            self._current_section = ""
        elif tag == "a":
            text = clean_text(" ".join(self._a_text))
            href = self._a_href.strip()
            if text and href:
                self.links.append(
                    PageLink(
                        text=text,
                        href=urljoin(self.base_url, href),
                        section=clean_text(self._current_section),
                    )
                )
            self._in_a = False
            self._a_text = []
            self._a_href = ""

    def handle_data(self, data: str) -> None:
        if self._in_th:
            self._th_text.append(data)
        if self._in_a:
            self._a_text.append(data)


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.replace("\xa0", " ")).strip()


def fold(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    return "".join(ch for ch in normalized if not unicodedata.combining(ch)).lower()


def slugify(value: str) -> str:
    value = fold(clean_text(value))
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_") or "documento"


def request_bytes(opener, url: str, timeout: int) -> tuple[bytes, str, str, str]:
    req = Request(url, headers={"User-Agent": USER_AGENT})
    with opener.open(req, timeout=timeout) as response:
        data = response.read()
        final_url = response.geturl()
        content_type = response.headers.get("Content-Type", "")
        disposition = response.headers.get("Content-Disposition", "")
    return data, final_url, content_type, disposition


def fetch_page(url: str, timeout: int) -> str:
    opener = build_opener()
    data, _, content_type, _ = request_bytes(opener, url, timeout)
    charset = "utf-8"
    match = re.search(r"charset=([\w-]+)", content_type, flags=re.I)
    if match:
        charset = match.group(1)
    return data.decode(charset, errors="replace")


def parse_links(page_html: str, base_url: str) -> list[PageLink]:
    parser = Uc3mExamParser(base_url)
    parser.feed(page_html)
    return parser.links


def is_exam_link(link: PageLink) -> bool:
    return (
        fold(link.section) in EXAM_SECTIONS
        and "matematicas ii" in fold(link.text)
        and bool(extract_drive_file_id(link.href) or link.href.lower().endswith(".pdf"))
    )


def is_supporting_link(link: PageLink) -> bool:
    text = fold(link.text)
    return "criterios" in text or "calculadoras" in text


def extract_drive_file_id(url: str) -> str:
    parsed = urlparse(url)
    match = re.search(r"/file/d/([^/]+)", parsed.path)
    if match:
        return match.group(1)
    query_id = parse_qs(parsed.query).get("id", [""])[0]
    return query_id


def to_download_url(url: str) -> str:
    file_id = extract_drive_file_id(url)
    if file_id:
        return f"https://drive.google.com/uc?export=download&id={quote(file_id)}"
    return url


def build_items(links: Iterable[PageLink], out_dir: Path) -> list[DownloadItem]:
    items: list[DownloadItem] = []
    used_paths: set[Path] = set()

    for link in links:
        section_slug = slugify(link.section or "material_auxiliar")
        title_slug = slugify(link.text)
        rel_path = Path(section_slug) / f"{title_slug}.pdf"
        output_path = out_dir / rel_path

        suffix = 2
        while output_path in used_paths:
            output_path = out_dir / section_slug / f"{title_slug}_{suffix}.pdf"
            suffix += 1
        used_paths.add(output_path)

        items.append(
            DownloadItem(
                title=link.text,
                section=link.section or "Material auxiliar",
                source_url=link.href,
                download_url=to_download_url(link.href),
                output_path=output_path,
            )
        )
    return items


def looks_like_pdf(data: bytes) -> bool:
    return data[:5] == b"%PDF-"


def find_drive_confirm_url(page: bytes, final_url: str) -> str:
    text = page.decode("utf-8", errors="replace")
    text = html.unescape(text)
    for match in re.finditer(r'href="([^"]*?(?:confirm|download_warning)[^"]*)"', text):
        href = match.group(1).replace("&amp;", "&")
        if "export=download" in href or "/uc?" in href:
            return urljoin("https://drive.google.com", href)

    match = re.search(r"confirm=([0-9A-Za-z_]+)", text)
    file_id = extract_drive_file_id(final_url)
    if match and file_id:
        return (
            "https://drive.google.com/uc?"
            f"export=download&confirm={match.group(1)}&id={quote(file_id)}"
        )
    return ""


def download_one(item: DownloadItem, timeout: int, overwrite: bool) -> Result:
    if item.output_path.exists() and not overwrite:
        data = item.output_path.read_bytes()
        return Result(
            item=item,
            status="exists",
            note="already present; use --overwrite to replace",
            sha256=hashlib.sha256(data).hexdigest(),
            bytes_written=len(data),
        )

    opener = build_opener(HTTPCookieProcessor())
    data, final_url, content_type, _ = request_bytes(opener, item.download_url, timeout)

    if not looks_like_pdf(data) and "drive.google.com" in item.download_url:
        confirm_url = find_drive_confirm_url(data, final_url)
        if confirm_url:
            data, _, content_type, _ = request_bytes(opener, confirm_url, timeout)

    if not looks_like_pdf(data):
        note = f"response is not a PDF; content-type={content_type or 'unknown'}"
        return Result(item=item, status="error", note=note)

    item.output_path.parent.mkdir(parents=True, exist_ok=True)
    item.output_path.write_bytes(data)
    return Result(
        item=item,
        status="downloaded",
        sha256=hashlib.sha256(data).hexdigest(),
        bytes_written=len(data),
    )


def write_manifest(results: list[Result], manifest_path: Path) -> None:
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with manifest_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "section",
                "title",
                "source_url",
                "download_url",
                "output_path",
                "status",
                "note",
                "sha256",
                "bytes",
            ],
        )
        writer.writeheader()
        for result in results:
            writer.writerow(
                {
                    "section": result.item.section,
                    "title": result.item.title,
                    "source_url": result.item.source_url,
                    "download_url": result.item.download_url,
                    "output_path": result.item.output_path.as_posix(),
                    "status": result.status,
                    "note": result.note,
                    "sha256": result.sha256,
                    "bytes": result.bytes_written,
                }
            )


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Descarga examenes PAU/EvAU de Matematicas II desde UC3M."
    )
    parser.add_argument("--source-url", default=SOURCE_URL, help="Pagina UC3M origen.")
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=DEFAULT_OUT_DIR,
        help="Directorio de salida.",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=None,
        help="Ruta del CSV de manifiesto. Por defecto: OUT_DIR/manifest.csv.",
    )
    parser.add_argument(
        "--include-supporting",
        action="store_true",
        help="Incluye criterios generales y calculadoras permitidas si aparecen.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Lista lo que se descargaria sin escribir archivos.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Reemplaza PDFs ya existentes.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limita el numero de enlaces procesados; util para pruebas.",
    )
    parser.add_argument("--timeout", type=int, default=60, help="Timeout por peticion.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    manifest_path = args.manifest or args.out_dir / "manifest.csv"

    page_html = fetch_page(args.source_url, args.timeout)
    links = parse_links(page_html, args.source_url)
    selected_links = [link for link in links if is_exam_link(link)]
    if args.include_supporting:
        selected_links.extend(link for link in links if is_supporting_link(link))
    if args.limit is not None:
        selected_links = selected_links[: args.limit]

    items = build_items(selected_links, args.out_dir)
    if not items:
        print("No se han encontrado enlaces descargables.", file=sys.stderr)
        return 1

    if args.dry_run:
        for item in items:
            print(f"[dry-run] {item.section}: {item.title} -> {item.output_path}")
        print(f"Total enlaces: {len(items)}")
        return 0

    results: list[Result] = []
    for item in items:
        try:
            result = download_one(item, args.timeout, args.overwrite)
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            result = Result(item=item, status="error", note=str(exc))
        results.append(result)
        print(f"[{result.status}] {item.output_path}")

    write_manifest(results, manifest_path)
    errors = sum(1 for result in results if result.status == "error")
    print(f"Manifiesto: {manifest_path}")
    print(f"Total: {len(results)} | errores: {errors}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
