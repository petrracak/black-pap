"""Recorta os prints de depoimento (_originais/depoimentos) e gera os WebP do carrossel.

As caixas estão em coordenadas de uma tela de 2000px de largura (o print
original tem 3420px); o script converte. Tudo fora da caixa sai: barra do
Safari, dock, coluna "Mídia recente" e o campo "Comente como...".

Uso: python3 scripts/depoimentos.py
"""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "_originais" / "depoimentos"
OUT = ROOT / "site" / "assets" / "img" / "depoimentos"
SCALE = 3420 / 2000
MAX_W = 1100

# arquivo original -> (arquivo final, caixa x0, y0, x1, y1)
CROPS = {
    "Adriana costa.png": ("adriana-costa", (229, 165, 1848, 1158)),
    "adriana.png": ("adriana-puppin", (92, 600, 1978, 1030)),
    "aldaia.png": ("aldaila", (243, 158, 1820, 1158)),
    "amanda.png": ("amanda", (122, 171, 1626, 1158)),
    # Ana Paula: só o texto, sem a foto da paciente (pedido da cliente)
    "Ana Paula flores.png": ("ana-paula", (312, 199, 1239, 474)),
    "Andreia veihga.png": ("andreia", (244, 148, 1512, 1158)),
    "elinaira.png": ("elinaira", (155, 167, 1270, 1158)),
    "josi.png": ("josi", (27, 169, 1377, 1158)),
    "lurdes.png": ("lurdes", (200, 154, 1250, 1158)),
    "marluce.png": ("marluce", (187, 146, 1434, 1158)),
    "Marinalva 2.png": ("marinalva", (67, 297, 1728, 668)),
}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, (slug, box) in CROPS.items():
        im = Image.open(SRC / name).convert("RGB")
        x0, y0, x1, y1 = (round(v * SCALE) for v in box)
        im = im.crop((x0, y0, x1, y1))
        if im.width > MAX_W:
            im = im.resize((MAX_W, round(im.height * MAX_W / im.width)), Image.LANCZOS)
        im.save(OUT / f"{slug}.webp", "WEBP", quality=82, method=6)
        print(slug, im.size)


if __name__ == "__main__":
    main()
