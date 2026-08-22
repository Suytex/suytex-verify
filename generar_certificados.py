#!/usr/bin/env python3
"""
Generador de certificados + páginas de verificación — Suytex Academy

Uso:
    python3 generar_certificados.py alumnos.csv

Entrada — alumnos.csv, con cabecera exactamente `nombre,codigo`:

    nombre,codigo
    Juan Pérez,APE-2026-0001
    María Gómez,APE-2026-0002

Salida — en output/ (ignorado por git), por cada alumno:

    output/certificados/{codigo}.html   HTML intermedio, todo embebido en base64
    output/certificados/{codigo}.pdf    el entregable (A4 horizontal)
    output/verify/{codigo}/index.html   página pública de verificación

El código se muestra tal cual en el CSV (APE-2026-0001), pero los nombres de
archivo y las URLs usan el slug en minúsculas (ape-2026-0001). Ver
slugify_codigo().

En CI este script no se corre a mano: lo invoca
.github/workflows/generar-certificados.yml, que adjunta los PDFs a un Release y
publica output/verify/* vía GitHub Pages.

Dependencias:
    pip install qrcode pillow playwright
    python -m playwright install --with-deps chromium

`pillow` es obligatoria aunque no se importe aquí: qrcode.make() devuelve una
imagen PIL y generar_qr_base64() la serializa con img.save().

Documentación: README.md · DISENO_CERTIFICADO.md
"""

import csv
import sys
import base64
import io
import traceback
from pathlib import Path

import qrcode
from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).parent

# Los templates se leen una sola vez al importar: son idénticos para todos los
# alumnos y solo cambian los placeholders.
CERT_TEMPLATE = (BASE_DIR / "certificado_ai_productivity_experience.html").read_text(encoding="utf-8")
VERIFY_TEMPLATE = (BASE_DIR / "verificacion_template.html").read_text(encoding="utf-8")
# El logo es a COLOR; el nombre "white" quedó de una versión anterior. No lo
# renombres: este nombre exacto es el contrato con el archivo en la raíz.
LOGO_FILE = BASE_DIR / "logo_white.png"

VERIFY_DOMAIN = "verify.suytex.com"


def slugify_codigo(codigo):
    """APE-2026-0001 -> ape-2026-0001 (nombres de archivo y URLs de Pages)."""
    return codigo.strip().lower().replace(" ", "-")


def generar_qr_base64(url):
    """QR de `url` como data URI PNG, para embeberlo en el HTML.

    border=1 es el mínimo del estándar: mantiene el QR compacto sin perder
    fiabilidad de lectura. Va embebido, no como archivo aparte, para que el
    PDF sea autocontenido.
    """
    img = qrcode.make(url, border=1)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    return f"data:image/png;base64,{b64}"


def cargar_logo_base64() -> str:
    """logo_white.png como data URI PNG, o "" si no está.

    Degrada en vez de fallar: sin el archivo, el certificado se emite sin logo
    y solo queda el aviso en el log. Es un fallo silencioso — si ves el ⚠️ en
    un run de CI, la tanda salió sin marca.
    """
    if not LOGO_FILE.exists():
        print(f"⚠️  No encontré {LOGO_FILE.name} — el certificado quedará sin logo.")
        return ""
    b64 = base64.b64encode(LOGO_FILE.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{b64}"


def main():
    if len(sys.argv) != 2:
        print("Uso: python3 generar_certificados.py alumnos.csv")
        sys.exit(1)

    csv_path = Path(sys.argv[1])
    out_cert_dir = BASE_DIR / "output" / "certificados"
    out_verify_dir = BASE_DIR / "output" / "verify"
    out_cert_dir.mkdir(parents=True, exist_ok=True)
    out_verify_dir.mkdir(parents=True, exist_ok=True)

    rows = list(csv.DictReader(open(csv_path, newline="", encoding="utf-8")))

    # Una sola vez para toda la tanda: el logo es el mismo en cada certificado.
    logo_b64 = cargar_logo_base64()

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        count = 0
        for row in rows:
            nombre = row["nombre"].strip()
            codigo_raw = row["codigo"].strip()
            codigo_slug = slugify_codigo(codigo_raw)

            # La URL del QR usa el slug, igual que la ruta que publica Pages.
            verify_url = f"https://{VERIFY_DOMAIN}/{codigo_slug}"
            qr_b64 = generar_qr_base64(verify_url)

            cert_html = (
                CERT_TEMPLATE
                .replace("{{NOMBRE}}", nombre)
                .replace("{{CODIGO}}", codigo_raw)
                .replace("{{QR_BASE64}}", qr_b64)
                .replace("{{LOGO_BASE64}}", logo_b64)
            )
            # El HTML se escribe a disco porque Playwright lo carga con file://
            # (no se imprime desde un string). Queda como artefacto de debug.
            html_path = out_cert_dir / f"{codigo_slug}.html"
            html_path.write_text(cert_html, encoding="utf-8")

            pdf_path = out_cert_dir / f"{codigo_slug}.pdf"
            try:
                page.goto(f"file://{html_path.resolve()}")
                # OBLIGATORIO: da tiempo a que carguen la fuente Inter (por red,
                # desde Google Fonts) y las imágenes base64 antes de imprimir.
                # Sin esta espera el PDF sale con tipografía de fallback y/o sin
                # logo, de forma intermitente. No la quites ni la bajes.
                page.wait_for_timeout(300)
                page.pdf(
                    path=str(pdf_path),
                    format="A4",
                    landscape=True,
                    print_background=True,
                    margin={"top": "0", "bottom": "0", "left": "0", "right": "0"},
                )
            # Un PDF que falle no aborta la tanda: se registra y se sigue con
            # el resto de alumnos. Revisa el log si el Release sale incompleto.
            except Exception as e:
                print(f"❌ ERROR generando PDF de {codigo_slug}: {e}")
                traceback.print_exc()

            verify_html = (
                VERIFY_TEMPLATE
                .replace("{{NOMBRE}}", nombre)
                .replace("{{CODIGO}}", codigo_raw)
            )
            # Un directorio por alumno con su index.html: es lo que permite que
            # Pages sirva verify.suytex.com/{codigo} como URL limpia.
            verify_page_dir = out_verify_dir / codigo_slug
            verify_page_dir.mkdir(parents=True, exist_ok=True)
            (verify_page_dir / "index.html").write_text(verify_html, encoding="utf-8")

            count += 1
            print(f"✅ {nombre} -> {codigo_slug}")

        browser.close()

    print(f"\n{count} certificado(s) generado(s).")


if __name__ == "__main__":
    main()
