"""Genera los códigos QR del repositorio y de la app para el video pitch.

Uso:  python scripts/generar_qr.py https://github.com/usuario/repo https://su-app.streamlit.app
"""
import sys
from pathlib import Path

import qrcode

DESTINO = Path(__file__).resolve().parents[1] / "results" / "reports"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Indique al menos la URL del repositorio.")
    for nombre, url in zip(["qr_repositorio.png", "qr_app.png"], sys.argv[1:3]):
        qrcode.make(url).save(DESTINO / nombre)
        print("generado:", DESTINO / nombre, "->", url)
