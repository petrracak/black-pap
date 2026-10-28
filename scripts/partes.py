"""Divide a versão simplificada em partes, para converter uma de cada vez.

Serve para quando o conversor cai de novo: em vez de mandar a página inteira,
você manda um pedaço por vez e depois junta tudo numa página só do Elementor.

Também gera um arquivo bem pequeno (teste.html) só para ver se o plugin
está funcionando, antes de subir qualquer coisa.

Uso: python3 scripts/partes.py
Saída: site-elementor/partes/
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site-elementor"
OUT = SITE / "partes"

# cada parte junta as seções que fazem sentido ficar perto
PARTES = [
    ("1-topo", ["__hero__", "dores"]),
    ("2-contraste-prints", ["contraste", "resultados"]),
    ("3-imagine", ["futuro"]),
    ("4-metodo-conteudo", ["metodo", "conteudo"]),
    ("5-bonus-videos", ["bonus", "videos"]),
    ("6-oferta-garantia", ["oferta", "garantia"]),
    ("7-mentora-contato-faq", ["mentora", "contato", "faq", "__footer__"]),
]

html = (SITE / "index.html").read_text()
cabeca = html[: html.index("</head>")] + "</head>\n<body class=\"bp\">\n"
rodape = "\n</body>\n</html>\n"

secoes = {
    m.group(1): m.group(0)
    for m in re.finditer(r'<section class="bp-sec[^"]*" id="([a-z]+)">.*?</section>', html, re.S)
}
secoes["__hero__"] = html[html.index('<header class="bp-hero"'): html.index("<main>")]
secoes["__footer__"] = html[html.index('<footer class="bp-footer">'): html.index("</footer>") + len("</footer>")]

OUT.mkdir(exist_ok=True)
for antigo in OUT.glob("*.html"):
    antigo.unlink()

# o CSS fica um nível acima, dentro de partes/
cabeca_parte = cabeca.replace('href="assets/css/style.css"', 'href="../assets/css/style.css"')

for nome, ids in PARTES:
    corpo = "\n".join(secoes[i] for i in ids)
    corpo = corpo.replace('src="assets/', 'src="../assets/')
    (OUT / f"{nome}.html").write_text(cabeca_parte + corpo + rodape)
    tags = len(re.findall(r"<[a-zA-Z]", corpo))
    print(f"{nome:24} {tags:4} elementos")

# arquivo mínimo, só para testar se o plugin responde
teste = secoes["garantia"].replace('src="assets/', 'src="../assets/')
(OUT / "teste.html").write_text(cabeca_parte + teste + rodape)
print(f"{'teste':24} {len(re.findall(r'<[a-zA-Z]', teste)):4} elementos")
