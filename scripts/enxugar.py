"""Deixa a página no menor tamanho possível para o conversor de Elementor,
sem perder texto nem imagem.

Duas frentes:

1. ELEMENTOS. O conversor cria um widget para cada pedaço do HTML. Os ícones
   sozinhos eram 136 elementos (86 <img> mais 50 <span> em volta). Aqui todos
   viram desenho de fundo no CSS, com uma classe por ícone, e somem do HTML.
   Também saem os <span> de dentro dos botões, as <figure> dos prints, as
   <div> que embrulhavam as respostas do FAQ e as camadas do ícone de suporte.

2. IMAGENS. Toda imagem .webp vira .jpg. Nem todo servidor tem suporte a WebP
   no PHP, e um importador que tropeça nisso derruba o site inteiro. De quebra
   as fotos são reduzidas, o que diminui o trabalho de quem for importar.

Uso: python3 scripts/enxugar.py
Saída: site-convertivel/
"""
import re
import shutil
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
ENTRADA = ROOT / "site-elementor"
OUT = ROOT / "site-convertivel"

LARGURA_MAX = 1000
QUALIDADE = 72

icones_usados = {}


def classe(nome):
    """Registra o ícone e devolve a classe que o CSS vai usar."""
    icones_usados[nome] = True
    return "bp-ic--" + nome


def nome_do_icone(trecho):
    m = re.search(r'src="assets/icones/([a-z0-9-]+)\.svg"', trecho)
    return m.group(1) if m else None


IMG = r'<img class="bp-ico[^"]*" src="assets/icones/[a-z0-9-]+\.svg"[^>]*>'


def enxugar(html):
    # ---- ícones dentro de um <span> de embrulho ----
    def tira_wrapper(m, alvo):
        nome = nome_do_icone(m.group(0))
        return m.group(1) + " " + classe(nome) + m.group(2)

    # bp-tile: <div class="bp-tile ..."><span class="bp-tile__ico"><img></span>
    html = re.sub(
        r'(<div class="bp-tile[^"]*)("[^>]*>)\s*<span class="bp-tile__ico">' + IMG + r"</span>",
        lambda m: tira_wrapper(m, "tile"), html)
    # bp-mod
    html = re.sub(
        r'(<article class="bp-mod[^"]*)("[^>]*>)\s*<span class="bp-mod__ico">' + IMG + r"</span>",
        lambda m: tira_wrapper(m, "mod"), html)
    html = re.sub(
        r'(<div class="bp-mod bp-mod--devices)("[^>]*>)\s*<span class="bp-mod__ico">' + IMG + r"</span>",
        lambda m: tira_wrapper(m, "mod"), html)
    # bp-stack__row
    html = re.sub(
        r'(<div class="bp-stack__row[^"]*)("[^>]*>)\s*<span class="bp-stack__ico">' + IMG + r"</span>",
        lambda m: tira_wrapper(m, "stack"), html)

    # ---- cards do "Imagine": some a <figure> e a <div> do corpo ----
    def scard(m):
        foto, nome = m.group(1), nome_do_icone(m.group(2))
        return (f'<li class="bp-scard {classe(nome)}">{foto}'
                f"<p>{m.group(3)}</p></li>")

    html = re.sub(
        r'<li class="bp-scard"><figure>(<img[^>]*>)</figure>'
        r'<div class="bp-scard__body"><span class="bp-scard__ico">(' + IMG + r")</span>"
        r"<p>(.*?)</p></div></li>",
        scard, html, flags=re.S)

    # ---- botões: fica só o texto ----
    def botao(m):
        return f'{m.group(1)}{m.group(2)}</a>'

    html = re.sub(
        r'(<a class="bp-btn[^"]*"[^>]*>)\s*(?:' + IMG + r')?\s*<span class="bp-btn__label">(.*?)</span>'
        r'\s*<span class="bp-btn__chip">(?:' + IMG + r')?</span>\s*</a>',
        botao, html, flags=re.S)
    # o botão do WhatsApp tem outra estrutura; aqui só desembrulha o texto
    html = re.sub(r'<span class="bp-btn__label">(.*?)</span>', r"\1", html, flags=re.S)

    # ---- vídeos: fica só o texto ----
    html = re.sub(
        r'(<a class="bp-video"[^>]*>)<span class="bp-video__play">' + IMG + r"</span>"
        r'<span class="bp-video__name">(.*?)</span></a>',
        lambda m: m.group(1) + m.group(2) + "</a>", html, flags=re.S)

    # ---- legenda dos bônus ----
    html = re.sub(
        r"<figcaption>(" + IMG + r")(.*?)</figcaption>",
        lambda m: f'<figcaption class="{classe(nome_do_icone(m.group(1)))}">{m.group(2)}</figcaption>',
        html, flags=re.S)

    # ---- faixa do topo e formas de pagamento ----
    html = re.sub(
        r"<span>(" + IMG + r")(.*?)</span>",
        lambda m: f'<span class="{classe(nome_do_icone(m.group(1)))}">{m.group(2)}</span>',
        html, flags=re.S)
    html = re.sub(
        r"<li>(" + IMG + r")(.*?)</li>",
        lambda m: f'<li class="{classe(nome_do_icone(m.group(1)))}">{m.group(2)}</li>',
        html, flags=re.S)

    # ---- FAQ: sai o ícone de mais e a div que embrulhava a resposta ----
    html = re.sub(r'<span class="bp-acc__ico">' + IMG + r"</span>", "", html)
    html = re.sub(r'<div class="bp-acc__a">(.*?)</div>', r"\1", html, flags=re.S)

    # ---- arte do suporte: um elemento só ----
    html = re.sub(
        r'<div class="bp-support__art">.*?</div>',
        '<div class="bp-support__art"></div>', html, flags=re.S)
    icones_usados["headset"] = True
    icones_usados["whatsapp-branco"] = True
    for so_no_css in ("player-play-escuro", "whatsapp-escuro", "arrow-up-right-claro", "plus", "lock"):
        icones_usados[so_no_css] = True

    # ---- ilustração dos cards do método ----
    html = re.sub(
        r'<div class="bp-mcard__art">\s*(' + IMG + r")\s*</div>",
        lambda m: f'<div class="bp-mcard__art {classe(nome_do_icone(m.group(1)))}"></div>',
        html, flags=re.S)

    # ---- prints: a <figure> não fazia nada ----
    html = re.sub(
        r'<figure class="bp-print">(<img )', r'\1class="bp-print" ', html)
    html = html.replace('class="bp-print" src=', 'class="bp-print" src=')
    html = re.sub(r'(<img class="bp-print"[^>]*>)</figure>', r"\1", html)

    # ---- o que sobrou de ícone solto (cadeado da linha de compra segura) ----
    html = re.sub(IMG, "", html)

    # ---- o "+" da tabela estava escondido no CSS ----
    html = re.sub(r'<div class="bp-stack__plus">.*?</div>', "", html, flags=re.S)

    html = re.sub(r"\n{3,}", "\n\n", html)
    return html


def css_dos_icones():
    regras = [
        "/* ---------- ícones como desenho de fundo ----------",
        "   Cada ícone virou uma classe. Isto tirou 136 elementos do HTML. */",
        "[class*=\"bp-ic--\"]::before { content: \"\"; display: inline-block; flex: none;"
        " width: 1.5em; height: 1.5em; background-position: center; background-repeat: no-repeat;"
        " background-size: contain; vertical-align: -.35em; }",
    ]
    for nome in sorted(icones_usados):
        regras.append(f'.bp-ic--{nome}::before {{ background-image: url("../icones/{nome}.svg"); }}')
    return "\n".join(regras) + "\n"


def converter_imagens():
    trocas = {}
    for origem in sorted((OUT / "assets" / "img").rglob("*.webp")):
        im = Image.open(origem).convert("RGB")
        if im.width > LARGURA_MAX:
            im = im.resize((LARGURA_MAX, round(im.height * LARGURA_MAX / im.width)), Image.LANCZOS)
        destino = origem.with_suffix(".jpg")
        im.save(destino, "JPEG", quality=QUALIDADE, optimize=True, progressive=True)
        origem.unlink()
        rel = str(origem.relative_to(OUT))
        trocas[rel] = str(destino.relative_to(OUT))
    return trocas


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(ENTRADA, OUT, ignore=shutil.ignore_patterns("partes", "LEIA-ANTES.txt"))

    html = enxugar((ENTRADA / "index.html").read_text())

    trocas = converter_imagens()
    for antigo, novo in trocas.items():
        html = html.replace(antigo.replace("\\", "/"), novo.replace("\\", "/"))

    css = (ENTRADA / "assets" / "css" / "style.css").read_text()
    css += "\n" + css_dos_icones()
    css += (ROOT / "scripts" / "style-enxuto.css").read_text()
    (OUT / "assets" / "css" / "style.css").write_text(css)
    (OUT / "index.html").write_text(html)

    # ícones que não são mais usados saem da pasta
    usados = {n + ".svg" for n in icones_usados}
    for svg in (OUT / "assets" / "icones").glob("*.svg"):
        if svg.name not in usados:
            svg.unlink()

    corpo = html[html.index("<body"):]
    print("elementos no corpo:", len(re.findall(r"<[a-zA-Z]", corpo)))
    print("index.html:", len(html), "bytes")
    print("ícones usados:", len(icones_usados))
    total = sum(f.stat().st_size for f in (OUT / "assets").rglob("*") if f.is_file())
    print("assets:", total // 1024, "KB")


if __name__ == "__main__":
    main()
