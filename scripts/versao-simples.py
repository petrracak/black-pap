"""Gera uma versão simplificada da página, feita para o plugin que converte
HTML em Elementor.

O que sai de fora (é o que trava o conversor):
  - todo o JavaScript;
  - o sprite de SVG embutido (eram 289 nós de desenho dentro do HTML);
  - carrosséis, cards que empilham, faixa em loop, cena das letras P-A-P,
    barra de progresso, barra fixa e o modal de ampliar print.

O que continua: todo o texto, todas as imagens, os ícones (agora como arquivos
.svg separados, já coloridos) e o visual da página em CSS simples.

Uso: python3 scripts/versao-simples.py
Saída: site-elementor/
"""
import math
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
OUT = ROOT / "site-elementor"

OURO = "#e6c27a"
ROSA = "#e2787a"
VERDE = "#25d366"
ESCURO = "#1a1206"

# ---------------------------------------------------------------- ícones
def gerar_icones():
    """Cada ícone vira um .svg colorido, para entrar na página como <img>."""
    destino = OUT / "assets" / "icones"
    destino.mkdir(parents=True, exist_ok=True)
    for arquivo in sorted((SITE / "assets" / "icons").glob("*.svg")):
        svg = arquivo.read_text()
        svg = re.sub(r'\s+class="[^"]*"', "", svg)
        svg = re.sub(r"\s+", " ", svg).strip()
        for nome, cor in (("", OURO), ("-rosa", ROSA), ("-escuro", ESCURO), ("-claro", "#ffb26b")):
            (destino / f"{arquivo.stem}{nome}.svg").write_text(
                svg.replace('stroke="currentColor"', f'stroke="{cor}"')
            )
    wpp = (SITE / "assets" / "icons" / "marcas" / "whatsapp.svg").read_text()
    wpp = wpp.replace("<path ", f'<path fill="{VERDE}" ').replace("<title>WhatsApp</title>", "")
    (destino / "whatsapp.svg").write_text(wpp)
    (destino / "whatsapp-branco.svg").write_text(wpp.replace(VERDE, "#ffffff"))
    (destino / "whatsapp-escuro.svg").write_text(wpp.replace(VERDE, "#052e16"))
    pix = (SITE / "assets" / "icons" / "marcas" / "pix.svg").read_text()
    (destino / "pix.svg").write_text(
        pix.replace("<path ", '<path fill="#32bcad" ').replace("<title>Pix</title>", "")
    )


def gerar_selo():
    """O selo de 7 dias com os traços já desenhados (antes vinham do JS)."""
    tracos = []
    for lado in (0, 1):
        for i in range(44):
            ang = -70 + i * 3.2 + lado * 180
            op = min(1.0, abs(math.sin(math.radians(ang))) * 1.3) * 0.9
            if op <= 0.05:
                continue
            rad = math.radians(ang - 90)
            x1, y1 = 200 + 170 * math.cos(rad), 200 + 170 * math.sin(rad)
            x2, y2 = 200 + 186 * math.cos(rad), 200 + 186 * math.sin(rad)
            tracos.append(
                f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                f'stroke="{OURO}" stroke-width="2.2" stroke-linecap="round" stroke-opacity="{op:.2f}"/>'
            )
    for ang in range(0, 360, 9):
        rad = math.radians(ang - 90)
        x1, y1 = 200 + 56 * math.cos(rad), 200 + 56 * math.sin(rad)
        x2, y2 = 200 + 66 * math.cos(rad), 200 + 66 * math.sin(rad)
        tracos.append(
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{OURO}" stroke-width="2" stroke-linecap="round" stroke-opacity="0.75"/>'
        )

    texto = (SITE / "assets" / "img" / "garantia" / "text-dourado.svg").read_text()
    miolo = re.search(r"<svg[^>]*>(.*)</svg>", texto, re.S).group(1)

    selo = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" width="400" height="400">
<defs>
<linearGradient id="anel" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#f6dfa6"/><stop offset=".55" stop-color="#b5863a" stop-opacity=".25"/><stop offset="1" stop-color="#e6c27a"/></linearGradient>
<radialGradient id="miolo" cx=".5" cy=".42" r=".6"><stop offset="0" stop-color="#3a2a12"/><stop offset=".6" stop-color="#140f07"/><stop offset="1" stop-color="#050403"/></radialGradient>
<linearGradient id="sete" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fbe8bb"/><stop offset=".5" stop-color="#e6c27a"/><stop offset="1" stop-color="#b5863a"/></linearGradient>
</defs>
<circle cx="200" cy="200" r="128" fill="url(#miolo)"/>
<circle cx="200" cy="200" r="128" fill="none" stroke="url(#anel)" stroke-width="2.5"/>
{''.join(tracos)}
<g transform="translate(200 200) scale(0.68) translate(-153 -156)">{miolo}</g>
<g transform="translate(200 200) scale(0.55) translate(-36 -51.5)"><path d="M7.01461 103L49.5532 18.5078V17.8037H0V0H72V18.0552L29.4113 103H7.01461Z" fill="url(#sete)"/></g>
</svg>"""
    (OUT / "assets" / "img" / "garantia").mkdir(parents=True, exist_ok=True)
    (OUT / "assets" / "img" / "garantia" / "selo-7-dias.svg").write_text(selo)


# ---------------------------------------------------------------- HTML
def icone(nome, cor="", classe="bp-ico"):
    sufixo = "-rosa" if cor == "rosa" else ""
    if nome in ("whatsapp", "pix"):
        arquivo, sufixo = nome, ""
    else:
        arquivo = nome
    return (f'<img class="{classe}" src="assets/icones/{arquivo}{sufixo}.svg" '
            f'alt="" width="24" height="24" loading="lazy">')


def trocar_icones(trecho, cor=""):
    def sub(m):
        classes, nome = m.group(1), m.group(3)
        marca = nome if m.group(2) == "m" else nome
        extra = "bp-ico"
        if "bp-i--brand" in classes:
            extra = "bp-ico bp-ico--marca"
        return icone(marca, cor, extra)
    return re.sub(r'<svg class="([^"]*)"[^>]*><use href="#([tm])-([a-z0-9-]+)"\s*/></svg>', sub, trecho)


def construir_html():
    s = (SITE / "index.html").read_text()

    # fora o sprite, a barra de progresso, a barra fixa, o modal e o script
    s = re.sub(r"<!-- icones:inicio -->.*?<!-- icones:fim -->\n?", "", s, flags=re.S)
    s = re.sub(r'<div class="bp-progress".*?</div>\n\n', "", s, flags=re.S)
    s = re.sub(r"<!-- Barra fixa no celular -->.*?</div>\n\n", "", s, flags=re.S)
    s = re.sub(r"<!-- Ampliar print / vídeo -->.*?</div>\n\n", "", s, flags=re.S)
    s = re.sub(r'<script src="[^"]*"></script>\n', "", s)
    s = s.replace('<link rel="stylesheet" href="assets/css/style.css?v=21">',
                  '<link rel="stylesheet" href="assets/css/style.css">')

    # faixa: uma linha só, sem loop
    s = re.sub(
        r'<!-- Faixas cruzadas.*?<div class="bp-bands".*?</div>\n</div>\n',
        '''<div class="bp-faixa">
  <div class="bp-faixa__linha">
    <span>''' + icone("sparkles") + '''Black PAP</span>
    <span>''' + icone("rosette-discount") + '''mais de 60% de desconto</span>
    <span>''' + icone("broadcast") + '''12 aulas ao vivo</span>
    <span>''' + icone("users-group") + '''comunidade de alunas</span>
    <span>''' + icone("shield-check") + '''7 dias de garantia</span>
  </div>
</div>
''', s, flags=re.S)

    # cena das letras P-A-P: vira um bloco parado
    s = re.sub(
        r'<!-- Cena de rolagem.*?<div class="bp-pap" data-pap>.*?\n  </div>\n',
        '''<div class="bp-container">
    <div class="bp-pap">
      <p class="bp-pap__label">Método</p>
      <p class="bp-pap__sigla">PAP</p>
      <p class="bp-pap__nome">A <b>P</b>rática da <b>A</b>prendizagem e <b>P</b>otencialização Humana</p>
    </div>
  </div>
''', s, flags=re.S)

    # carrosséis viram grades
    s = re.sub(r'<div class="bp-rail bp-rail--flow"[^>]*>\s*<div class="bp-rail__track">',
               '<div class="bp-container"><div class="bp-grade bp-grade--prints">', s)
    s = re.sub(r'<div class="bp-rail bp-rail--metodo"[^>]*>\s*<div class="bp-rail__track">',
               '<div class="bp-container"><div class="bp-grade bp-grade--metodo">', s)
    s = re.sub(r'<div class="bp-rail bp-rail--shelf"[^>]*>\s*<div class="bp-rail__track">',
               '<div class="bp-container"><div class="bp-grade bp-grade--bonus">', s)
    s = re.sub(r'<div class="bp-rail bp-rail--videos"[^>]*>\s*<div class="bp-rail__track">',
               '<div class="bp-container"><div class="bp-grade bp-grade--videos">', s)
    s = re.sub(r'\s*<div class="bp-rail__nav">.*?</div>\s*</div>', "\n  </div></div>", s, flags=re.S)

    # fundo decorativo da seção de prints (tinha texto correndo)
    s = re.sub(r'<div class="bp-prints__bg".*?</div>\n', "", s, flags=re.S)

    # os grid-area serviam ao bento antigo; aqui a grade é simples
    s = re.sub(r'\sstyle="grid-area:[a-z]+"', "", s)

    # prints: sem botão de ampliar
    s = re.sub(r'<button type="button" data-zoom="[^"]*">(.*?)</button>', r"\1", s, flags=re.S)
    s = re.sub(r'<p class="bp-hint".*?</p>\n', "", s, flags=re.S)

    # vídeos: viram links
    s = re.sub(r'<button class="bp-video" type="button" data-youtube="">(.*?)</button>',
               r'<a class="bp-video" href="#" rel="noopener">\1</a>', s)

    # cards do "Imagine": grade normal
    s = s.replace('<ol class="bp-stack-cards" data-stack>', '<ul class="bp-grade bp-grade--imagine">')
    s = s.replace("</ol>\n  </div>", "</ul>\n  </div>")
    s = s.replace('<li class="bp-scard">', '<li class="bp-scard">')

    # marca d'água do card do Protocolo (era um SVG grande de fundo)
    s = re.sub(r'<svg class="bp-i bp-mod__mark"[^>]*>.*?</svg>\n\s*', "", s, flags=re.S)

    # enfeites que dependiam de animação
    s = re.sub(r'<span class="bp-orbit[^"]*"></span>', "", s)
    s = re.sub(r'<span class="bp-spark"[^>]*></span>', "", s)
    s = re.sub(r'<span class="bp-board"></span>', "", s)
    s = re.sub(r'<span class="bp-support__wave"></span>', "", s)
    s = re.sub(r'<span class="bp-support__bubble">.*?</span>', "", s, flags=re.S)
    s = s.replace(' bp-draw', '')

    # selo da garantia: um arquivo só
    s = re.sub(r'<div class="bp-seal".*?</div>\n',
               '<img class="bp-selo" src="assets/img/garantia/selo-7-dias.svg" alt="Garantia de 7 dias" width="400" height="400" loading="lazy">\n',
               s, flags=re.S)

    # preço sem contagem
    s = s.replace('<span data-count-from="2997" data-count-to="997">997</span>', "997")

    # ícones viram imagens (os da seção de dores em rosa)
    i, f = s.index('<section class="bp-sec bp-dores"'), s.index('<section class="bp-sec bp-contraste"')
    s = s[:i] + trocar_icones(s[i:f], "rosa") + trocar_icones(s[f:])
    s = trocar_icones(s)

    # onde o fundo é dourado ou verde, o ícone precisa ser escuro para aparecer
    def escurecer(bloco):
        return re.sub(r'/icones/([a-z0-9-]+)\.svg', r'/icones/\1-escuro.svg', bloco)

    s = re.sub(r'<div class="bp-faixa__linha">.*?</div>', lambda m: escurecer(m.group(0)), s, flags=re.S)
    s = re.sub(r'<span class="bp-scard__ico">.*?</span>', lambda m: escurecer(m.group(0)), s, flags=re.S)
    s = re.sub(r'<span class="bp-video__play">.*?</span>', lambda m: escurecer(m.group(0)), s, flags=re.S)
    s = re.sub(r'(<a class="bp-btn bp-btn--whats".*?)whatsapp\.svg', r'\1whatsapp-escuro.svg', s, flags=re.S)
    s = re.sub(r'(<span class="bp-support__badge">.*?)whatsapp\.svg', r'\1whatsapp-branco.svg', s, flags=re.S)

    # a seta dentro do botão fica sobre fundo escuro: sempre dourada
    s = re.sub(r'(class="bp-btn__chip"[^>]*><img class="bp-ico" src="assets/icones/arrow-up-right)-rosa',
               r'\1', s)

    # sem JavaScript, cada link precisa estar escrito no próprio href
    s = s.replace('<a class="bp-btn bp-btn--whats" href="#"', '<a class="bp-btn bp-btn--whats" href="COLE-AQUI-O-LINK-DO-WHATSAPP"')
    s = re.sub(r'(<a class="bp-btn[^"]*") href="#(oferta)?"', r'\1 href="COLE-AQUI-O-LINK-DA-HOTMART"', s)
    s = s.replace('<a class="bp-video" href="#"', '<a class="bp-video" href="COLE-AQUI-O-LINK-DO-VIDEO" target="_blank"')
    s = re.sub(r'<!--\s*VÍDEOS:.*?-->',
               '<!-- VÍDEOS: troque COLE-AQUI-O-LINK-DO-VIDEO pelo endereço de cada vídeo no YouTube. -->',
               s, flags=re.S)

    # sobra de atributos que só serviam para o JS
    s = re.sub(r'\s(data-reveal|data-stagger|data-spot|data-rail|data-stack|data-pap|data-checkout|data-whatsapp)(="[^"]*")?', "", s)
    s = re.sub(r'\s(aria-roledescription|aria-hidden)="[^"]*"', "", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "assets" / "css").mkdir(parents=True)
    gerar_icones()
    gerar_selo()
    shutil.copytree(SITE / "assets" / "img", OUT / "assets" / "img", dirs_exist_ok=True)
    for lixo in (OUT / "assets" / "img" / "garantia").glob("text*.svg"):
        lixo.unlink()
    (OUT / "assets" / "img" / "garantia" / "number.svg").unlink(missing_ok=True)
    shutil.copy(ROOT / "scripts" / "style-simples.css", OUT / "assets" / "css" / "style.css")
    shutil.copy(ROOT / "scripts" / "LEIA-ANTES.txt", OUT / "LEIA-ANTES.txt")
    (OUT / "index.html").write_text(construir_html())
    print("gerado:", OUT / "index.html")


if __name__ == "__main__":
    main()
