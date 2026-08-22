#!/usr/bin/env python3
import csv
import sys
import base64
import io
import traceback
from pathlib import Path

import qrcode
from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).parent
CERT_TEMPLATE = (BASE_DIR / "certificado_ai_productivity_experience.html").read_text(encoding="utf-8")
VERIFY_TEMPLATE = (BASE_DIR / "verificacion_template.html").read_text(encoding="utf-8")
LOGO_FILE = BASE_DIR / "logo_white.png"

VERIFY_DOMAIN = "verify.suytex.com"


def slugify_codigo(codigo):
    return codigo.strip().lower().replace(" ", "-")


def generar_qr_base64(url):
    img = qrcode.make(url, border=1)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    return f"data:image/png;base64,{b64}"


def cargar_logo_base64() -> str:
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

    logo_b64 = cargar_logo_base64()

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        count = 0
        for row in rows:
            nombre = row["nombre"].strip()
            codigo_raw = row["codigo"].strip()
            codigo_slug = slugify_codigo(codigo_raw)

            verify_url = f"https://{VERIFY_DOMAIN}/{codigo_slug}"
            qr_b64 = generar_qr_base64(verify_url)

            cert_html = (
                CERT_TEMPLATE
                .replace("{{NOMBRE}}", nombre)
                .replace("{{CODIGO}}", codigo_raw)
                .replace("{{QR_BASE64}}", qr_b64)
                .replace("{{LOGO_BASE64}}", logo_b64)
            )
            html_path = out_cert_dir / f"{codigo_slug}.html"
            html_path.write_text(cert_html, encoding="utf-8")

            pdf_path = out_cert_dir / f"{codigo_slug}.pdf"
            try:
                page.goto(f"file://{html_path.resolve()}")
                page.wait_for_timeout(300)
                page.pdf(
                    path=str(pdf_path),
                    format="A4",
                    landscape=True,
                    print_background=True,
                    margin={"top": "0", "bottom": "0", "left": "0", "right": "0"},
                )
            except Exception as e:
                print(f"❌ ERROR generando PDF de {codigo_slug}: {e}")
                traceback.print_exc()

            verify_html = (
                VERIFY_TEMPLATE
                .replace("{{NOMBRE}}", nombre)
                .replace("{{CODIGO}}", codigo_raw)
            )
            verify_page_dir = out_verify_dir / codigo_slug
            verify_page_dir.mkdir(parents=True, exist_ok=True)
            (verify_page_dir / "index.html").write_text(verify_html, encoding="utf-8")

            count += 1
            print(f"✅ {nombre} -> {codigo_slug}")

        browser.close()

    print(f"\n{count} certificado(s) generado(s).")


if __name__ == "__main__":
    main()
