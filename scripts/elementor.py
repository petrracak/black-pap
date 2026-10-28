"""Gera a versão da página para colar num widget HTML do Elementor.

Pega o site/ (index.html + css + js) e produz um arquivo único:
  - o CSS entra num <style> e o JS num <script>, então não há arquivos soltos;
  - a fonte do Google vira @import no topo do CSS;
  - os caminhos das imagens e dos ícones apontam para BASE (veja abaixo);
  - sai só o miolo da página, sem <html>, <head> ou <body>, porque o
    widget do Elementor já fica dentro do documento do WordPress.

Uso: python3 scripts/elementor.py
Saída: export-elementor/
"""
import re
import shutil
from pathlib import Path

# Onde a pasta assets vai morar no WordPress. Precisa começar com barra.
BASE = "/wp-content/uploads/black-pap"

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
OUT = ROOT / "export-elementor"

html = (SITE / "index.html").read_text()
css = (SITE / "assets" / "css" / "style.css").read_text()
js = (SITE / "assets" / "js" / "main.js").read_text()

# fonte do Google: do <link> para @import, que funciona dentro do <style>
fonte = re.search(r'<link href="(https://fonts\.googleapis\.com[^"]+)" rel="stylesheet">', html)
css = f'@import url("{fonte.group(1)}");\n\n' + css

# só o miolo: do primeiro comentário dos ícones até o fim do modal
miolo = html[html.index("<!-- icones:inicio -->"):html.rindex("</div>\n\n<script")] + "</div>"

# caminhos: assets/… vira BASE/assets/…
miolo = re.sub(r'(src|href)="assets/', rf'\1="{BASE}/assets/', miolo)
miolo = re.sub(r'data-zoom="assets/', f'data-zoom="{BASE}/assets/', miolo)
css = css.replace('url("../img/', f'url("{BASE}/assets/img/')

fragmento = f"""<!--
  BLACK PAP · Método PAP (Fernanda Garnizet)
  Cole este arquivo inteiro num widget HTML do Elementor.
  Antes disso, suba a pasta assets para {BASE}/ no seu WordPress.
-->
<style>
{css}
</style>

<div class="bp">
{miolo}
</div>

<script>
{js}
</script>
"""

OUT.mkdir(exist_ok=True)
(OUT / "elementor-html-widget.html").write_text(fragmento)

destino = OUT / "assets"
if destino.exists():
    shutil.rmtree(destino)
shutil.copytree(SITE / "assets", destino, ignore=shutil.ignore_patterns("css", "js", "icons"))

print("gerado:", OUT / "elementor-html-widget.html", len(fragmento), "bytes")
print("assets copiados para:", destino)
