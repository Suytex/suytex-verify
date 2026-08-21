#!/usr/bin/env python3
"""
Generador de certificados + páginas de verificación — AI Productivity Experience

Uso:
    python3 generar_certificados.py alumnos.csv

alumnos.csv debe tener columnas: nombre,codigo
Ejemplo:
    nombre,codigo
    Juan Pérez,APE-2026-0001
    María Gómez,APE-2026-0002

Salida:
    output/certificados/{codigo}.html   -> abrir en Chrome, Cmd+P a PDF
    output/verify/{codigo}/index.html   -> subir tal cual a verify.suytex.com/{codigo}/
"""

import csv
import sys
import base64
import io
from pathlib import Path

import qrcode

BASE_DIR = Path(__file__).parent
CERT_TEMPLATE = (BASE_DIR / "certificado_ai_productivity_experience.html").read_text(encoding="utf-8")
VERIFY_TEMPLATE = (BASE_DIR / "verificacion_template.html").read_text(encoding="utf-8")

VERIFY_DOMAIN = "verify.suytex.com"


def slugify_codigo(codigo: str) -> str:
    return codigo.strip().lower().replace(" ", "-")


def generar_qr_base64(url: str) -> str:
    img = qrcode.make(url, border=1)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    return f"data:image/png;base64,{b64}"


def main():
    if len(sys.argv) != 2:
        print("Uso: python3 generar_certificados.py alumnos.csv")
        sys.exit(1)

    csv_path = Path(sys.argv[1])
    if not csv_path.exists():
        print(f"No encontré el archivo: {csv_path}")
        sys.exit(1)

    out_cert_dir = BASE_DIR / "output" / "certificados"
    out_verify_dir = BASE_DIR / "output" / "verify"
    out_cert_dir.mkdir(parents=True, exist_ok=True)
    out_verify_dir.mkdir(parents=True, exist_ok=True)

    count = 0
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            nombre = row["nombre"].strip()
            codigo_raw = row["codigo"].strip()
            codigo_slug = slugify_codigo(codigo_raw)

            verify_url = f"https://{VERIFY_DOMAIN}/{codigo_slug}"
            qr_b64 = generar_qr_base64(verify_url)

            # Certificado
            cert_html = (
                CERT_TEMPLATE
                .replace("{{NOMBRE}}", nombre)
                .replace("{{CODIGO}}", codigo_raw)
                .replace("{{QR_BASE64}}", qr_b64)
            )
            (out_cert_dir / f"{codigo_slug}.html").write_text(cert_html, encoding="utf-8")

            # Página de verificación
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

    print(f"\n{count} certificado(s) generado(s).")
    print(f"Certificados: {out_cert_dir}")
    print(f"Páginas de verificación (subir a {VERIFY_DOMAIN}/): {out_verify_dir}")


if __name__ == "__main__":
    main()
