"""Monta os depoimentos da Michele e da Fernanda Oliveira, que vieram em dois prints
(perfil + texto), no mesmo formato dos outros: cabeçalho com foto e nome e o texto
embaixo, com os trechos pedidos pela cliente marcados e alguns em "zoom".

Coordenadas em tela de 2000px de largura (o print tem 3420px).
Uso: python3 scripts/depoimentos_montados.py
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "_originais" / "depoimentos"
OUT = ROOT / "site" / "assets" / "img" / "depoimentos"
K = 3420 / 2000
MAX_W = 1100
MARKER = (255, 236, 140)

POSTS = {
    "michele": {
        "nome": "Michelle Machado",
        "perfil": "michele-perfil.png",
        "avatar": (240, 827, 203),  # centro x, centro y, raio
        "texto": "michele-texto.png",
        "recorte": (500, 162, 1910, 1246),
        # trechos marcados: (x0, y0, x1, y1)
        "marcar": [
            (556, 337, 1698, 373),
            (1186, 505, 1764, 541),
            (556, 841, 1766, 877),
            (556, 878, 922, 914),
            (556, 1118, 1162, 1154),
        ],
        # trechos que "saltam" ampliados
        "zoom": [(556, 337, 1698, 373), (556, 1118, 1162, 1154)],
    },
    "fernanda-oliveira": {
        "nome": "Fernanda Oliveira",
        "perfil": "fernanda-perfil.png",
        "avatar": (483, 793, 282),
        "texto": "fernanda-texto.png",
        "recorte": (505, 157, 1690, 1228),
        "marcar": [
            (990, 652, 1618, 686),
            (528, 686, 1012, 720),
            (1526, 719, 1556, 752),
            (528, 752, 1636, 786),
            (528, 786, 1550, 819),
            (528, 819, 1182, 852),
            (884, 852, 1262, 885),
            (622, 1018, 1662, 1051),
            (528, 1051, 1492, 1084),
        ],
        "zoom": [(884, 852, 1262, 885), (922, 1051, 1440, 1084)],
    },
}


def font(size, bold=False):
    f = ImageFont.truetype("/System/Library/Fonts/SFNS.ttf", size)
    try:
        f.set_variation_by_name("Bold" if bold else "Regular")
    except Exception:
        pass
    return f


def px(box):
    return tuple(round(v * K) for v in box)


def avatar(perfil, cx, cy, r, d):
    im = Image.open(SRC / perfil).convert("RGB")
    cx, cy, r = cx * K, cy * K, r * K
    face = im.crop((round(cx - r), round(cy - r), round(cx + r), round(cy + r))).resize((d * 4, d * 4), Image.LANCZOS)
    mask = Image.new("L", face.size, 0)
    ImageDraw.Draw(mask).ellipse((0, 0, face.width - 1, face.height - 1), fill=255)
    face = face.resize((d, d), Image.LANCZOS)
    return face, mask.resize((d, d), Image.LANCZOS)


def tint(region):
    """Pinta o fundo branco de amarelo-marca-texto sem mexer na letra."""
    layer = Image.new("RGB", region.size, MARKER)
    return ImageChops.multiply(region, layer)


def build(slug, p):
    texto = Image.open(SRC / p["texto"]).convert("RGB")
    rx0, ry0, rx1, ry1 = px(p["recorte"])
    body = texto.crop((rx0, ry0, rx1, ry1))
    off = lambda b: (b[0] - rx0, b[1] - ry0, b[2] - rx0, b[3] - ry0)

    for b in p["marcar"]:
        x0, y0, x1, y1 = off(px(b))
        pad = 6
        box = (x0 - pad, y0 + 2, x1 + pad, y1 - 2)
        body.paste(tint(body.crop(box)), box)

    # zoom: o trecho é recortado já marcado, ampliado e colado por cima com sombra
    for b in p["zoom"]:
        x0, y0, x1, y1 = off(px(b))
        pad = 14
        seg = body.crop((x0 - pad, y0 - 4, x1 + pad, y1 + 4))
        z = 1.16
        seg = seg.resize((round(seg.width * z), round(seg.height * z)), Image.LANCZOS)
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        nx = round(cx - seg.width / 2)
        nx = max(8, min(nx, body.width - seg.width - 8))
        ny = round(cy - seg.height / 2)
        shadow = Image.new("L", (seg.width + 80, seg.height + 80), 0)
        ImageDraw.Draw(shadow).rounded_rectangle((40, 48, 40 + seg.width, 48 + seg.height), 18, fill=120)
        shadow = shadow.filter(ImageFilter.GaussianBlur(18))
        body.paste((60, 50, 20), (nx - 40, ny - 40), shadow)
        m = Image.new("L", seg.size, 0)
        ImageDraw.Draw(m).rounded_rectangle((0, 0, seg.width - 1, seg.height - 1), 14, fill=255)
        body.paste(seg, (nx, ny), m)

    # cabeçalho no padrão dos outros prints (escala do print original)
    pad_l = round(56 * K)
    head_h = round(150 * K)
    d = round(96 * K)
    card = Image.new("RGB", (body.width, head_h + body.height), "white")
    face, mask = avatar(p["perfil"], *p["avatar"], d)
    ay = round(28 * K)
    card.paste(face, (pad_l - round(28 * K), ay), mask)
    dr = ImageDraw.Draw(card)
    tx = pad_l - round(28 * K) + d + round(20 * K)
    dr.text((tx, ay + round(10 * K)), p["nome"], font=font(round(36 * K), True), fill=(5, 5, 5))
    dr.text((tx, ay + round(56 * K)), "Psicopedagogas na Prática", font=font(round(28 * K)), fill=(101, 103, 107))
    for i in range(3):
        cxd = body.width - round((60 - i * 16) * K)
        rr = round(4 * K)
        dr.ellipse((cxd - rr, ay + round(40 * K) - rr, cxd + rr, ay + round(40 * K) + rr), fill=(80, 80, 80))
    card.paste(body, (0, head_h))

    if card.width > MAX_W:
        card = card.resize((MAX_W, round(card.height * MAX_W / card.width)), Image.LANCZOS)
    card.save(OUT / f"{slug}.webp", "WEBP", quality=84, method=6)
    print(slug, card.size)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for slug, p in POSTS.items():
        build(slug, p)
