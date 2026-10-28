"""Junta os ícones de assets/icons num sprite e injeta no index.html
entre os comentários <!-- icones:inicio --> e <!-- icones:fim -->.

- assets/icons/*.svg ........ Tabler Icons outline (MIT), traço animável
- assets/icons/marcas/*.svg .. Simple Icons (CC0): WhatsApp e Pix

Cada traço recebe pathLength="1" para a animação de desenho funcionar.
Uso: python3 scripts/icones.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "site"
ICONS = ROOT / "assets" / "icons"
html_path = ROOT / "index.html"

symbols = []
for f in sorted(ICONS.glob("*.svg")):
    svg = f.read_text()
    inner = re.search(r"<svg[^>]*>(.*)</svg>", svg, re.S).group(1)
    inner = re.sub(r'<path stroke="none" d="M0 0h24v24H0z" fill="none"\s*/>', "", inner)
    inner = re.sub(r"<(path|circle|line|rect|polyline|polygon|ellipse)\b", r'<\1 pathLength="1"', inner)
    inner = re.sub(r"\s+", " ", inner).strip()
    symbols.append(f'<symbol id="t-{f.stem}" viewBox="0 0 24 24">{inner}</symbol>')

for f in sorted((ICONS / "marcas").glob("*.svg")):
    svg = f.read_text()
    inner = re.search(r"<svg[^>]*>(.*)</svg>", svg, re.S).group(1)
    inner = re.sub(r"<title>.*?</title>", "", inner)
    inner = inner.replace("<path ", '<path fill="currentColor" stroke="none" ')
    symbols.append(f'<symbol id="m-{f.stem}" viewBox="0 0 24 24">{inner}</symbol>')

sprite = '<svg width="0" height="0" style="position:absolute" aria-hidden="true">' + "".join(symbols) + "</svg>"
html = html_path.read_text()
html = re.sub(r"(<!-- icones:inicio -->).*?(<!-- icones:fim -->)", lambda m: m.group(1) + sprite + m.group(2), html, flags=re.S)
html_path.write_text(html)
print(len(symbols), "ícones injetados")
