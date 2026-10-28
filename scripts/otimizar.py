"""Gera a página completa (com as animações) já aliviada para o conversor.

O que pesa num conversor de HTML para Elementor é a quantidade de elementos:
ele cria um widget para cada pedaço. O sprite de ícones sozinho eram 290
elementos dentro do index.html, 26% da página, só para desenhar os ícones.

Aqui o sprite sai do HTML e vira um arquivo (assets/icons/sprite.svg). O JS
carrega e injeta ele no começo, então os ícones continuam coloridos pelo CSS e
com a animação de traço, igual antes.

  index.html: 1.121 -> 831 elementos, 67 KB -> 44 KB

Nada mais muda: carrosséis, cards que empilham, cena do P-A-P, faixa em loop,
selo girando e a barra fixa continuam funcionando.

Uso: python3 scripts/otimizar.py
Saída: site-otimizado/
"""
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
OUT = ROOT / "site-otimizado"

CARREGADOR = '''  /* ---------- ícones ----------
     O sprite mora em assets/icons/sprite.svg para deixar o index.html leve.
     É injetado aqui no começo, então o <use href="#t-..."> acha os símbolos e
     o CSS continua colorindo e animando cada ícone. */
  (function () {
    var alvo = document.getElementById("bp-sprite");
    if (!alvo || alvo.firstChild) return;
    var pedido = new XMLHttpRequest();
    pedido.open("GET", "assets/icons/sprite.svg", true);
    pedido.onload = function () {
      if (pedido.status >= 200 && pedido.status < 300) alvo.innerHTML = pedido.responseText;
    };
    pedido.send();
  })();

'''


def main():
    html = (SITE / "index.html").read_text()
    sprite = re.search(r"<!-- icones:inicio -->(.*?)<!-- icones:fim -->", html, re.S).group(1)

    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(SITE / "assets", OUT / "assets")

    # o sprite vira arquivo; o <svg> de fora não vai junto, só os símbolos
    simbolos = re.search(r"<svg[^>]*>(.*)</svg>", sprite, re.S).group(1)
    (OUT / "assets" / "icons" / "sprite.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg">' + simbolos + "</svg>"
    )

    # os .svg soltos só serviam para montar o sprite; não vão para o site
    for solto in (OUT / "assets" / "icons").glob("*.svg"):
        if solto.name != "sprite.svg":
            solto.unlink()
    shutil.rmtree(OUT / "assets" / "icons" / "marcas", ignore_errors=True)

    # no HTML fica só um ponto de encaixe
    html = html.replace(
        "<!-- icones:inicio -->" + sprite + "<!-- icones:fim -->",
        '<svg id="bp-sprite" width="0" height="0" style="position:absolute" aria-hidden="true"></svg>',
    )

    # tira a indentação (mantém as quebras de linha, que o HTML usa como espaço)
    html = re.sub(r"\n[ \t]+", "\n", html)
    html = re.sub(r"\n{3,}", "\n\n", html)
    (OUT / "index.html").write_text(html)

    js = (SITE / "assets" / "js" / "main.js").read_text()
    marca = '  body.classList.add("bp-js");\n'
    js = js.replace(marca, marca + "\n" + CARREGADOR, 1)
    (OUT / "assets" / "js" / "main.js").write_text(js)

    tags = len(re.findall(r"<[a-zA-Z]", html))
    print(f"index.html: {tags} elementos, {len(html)} bytes")
    print("sprite:", (OUT / "assets" / "icons" / "sprite.svg").stat().st_size, "bytes")


if __name__ == "__main__":
    main()
