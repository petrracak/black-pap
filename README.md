# Black PAP · página de vendas

Página da Black Friday do Método PAP (Fernanda Garnizet). HTML, CSS e JS puros, sem build: a pasta `site/` é a página inteira.

## Publicar na Vercel

Importe esta pasta como projeto e selecione **Other** em Framework Preset. O `vercel.json` já define `site/` como Output Directory e cache de 30 dias para os recursos em `assets/`. Não é necessário comando de build.

Antes de publicar com tráfego pago, preencha `CHECKOUT_URL` e `WHATSAPP_URL` em `site/assets/js/main.js` e os IDs dos vídeos marcados para troca em `site/index.html`.

## Ver localmente

```bash
cd site && python3 -m http.server 5520
```

Abre em http://localhost:5520.

## Onde mexer

| O quê | Onde |
|---|---|
| Link do checkout (todos os botões de compra) | `site/assets/js/main.js` → `CHECKOUT_URL` |
| Link do WhatsApp do time | `site/assets/js/main.js` → `WHATSAPP_URL` |
| Vídeos de depoimento (YouTube) | `site/index.html`, seção 9 → `data-youtube="ID"` em cada card |
| Foto da primeira dobra (a mesma arte serve desktop, tablet e mobile) | `site/index.html`, seção 1 → `<picture class="bp-hero__photo">` |
| Dobras 2 e 3 | sem fotos, só os cards do bento |
| Foto da Fernanda na seção Mentora | procure `TROCAR` no `index.html` |
| Cor dos botões (CTA) | `site/assets/css/style.css`, `:root` → `--bp-cta`, `--bp-cta-grad`, `--bp-cta-ink` |
| Cores e fontes | `site/assets/css/style.css`, topo (`:root`) |

Depois de editar CSS ou JS, aumente o `?v=` no `index.html` para o navegador não usar a versão antiga.
Ao substituir uma imagem, mude o nome do arquivo (ou versione a URL): o navegador pode guardar recursos de `assets/` por até 30 dias.

## Imagens

- Prints originais: guardados na pasta irmã `03 - LANDING PAGE - FERNANDA GARNIZET - arquivo local/_originais/depoimentos/`. Para regerar os recortes, restaure `_originais/` nesta pasta e rode `python3 scripts/depoimentos.py`.
- Michele e Fernanda Oliveira (montados de dois prints, com trechos em destaque e zoom): `python3 scripts/depoimentos_montados.py`.
- Ícones: Tabler Icons outline (MIT) em `site/assets/icons/` e marcas do Simple Icons (WhatsApp, Pix) em `site/assets/icons/marcas/`. Depois de adicionar um SVG: `python3 scripts/icones.py` (injeta o sprite no `index.html`).
- Fotos do "Imagine conseguir": Unsplash (licença livre), em `site/assets/img/imagine/`.
- Selo de garantia: texto e número exportados do Figma PackPages, recoloridos em dourado (`site/assets/img/garantia/`). Os traços em volta são gerados pelo `main.js`.

## Arquivos anteriores

As variantes antigas para Elementor, exportações ZIP e materiais originais foram movidos para a pasta irmã `03 - LANDING PAGE - FERNANDA GARNIZET - arquivo local/`. A versão para Vercel permanece em `site/`.
