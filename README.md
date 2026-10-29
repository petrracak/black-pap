# Black PAP · página de vendas

Página da Black Friday do Método PAP (Fernanda Garnizet). HTML, CSS e JS puros, sem build: a pasta `site/` é a página inteira.

## Publicar na Vercel

Importe esta pasta como projeto e selecione **Other** em Framework Preset. O `vercel.json` define `site/` como Output Directory. Não é necessário comando de build.

Antes de publicar com tráfego pago, preencha `CHECKOUT_URL` e `WHATSAPP_URL` em `site/assets/js/main.js` e os IDs dos vídeos marcados para troca em `site/index.html`.

## Ver localmente

```bash
cd site && python3 -m http.server 5520
```

Abre em http://localhost:5520.

## Preparar publicação no cPanel (FTPS)

O workflow `.github/workflows/deploy-cpanel-ftps.yml` envia apenas o conteúdo de `site/` para a raiz da conta FTP `deployblackpap@fernandagarnizet.com.br`, por FTPS explícito na porta 21, com verificação do certificado TLS. Não há comando de build nem dependências de servidor; o cPanel só precisa servir arquivos estáticos.

1. Em **cPanel → Domínios**, confirme que a raiz do subdomínio `blackpap.fernandagarnizet.com.br` é `/home/fernan41/blackpap.fernandagarnizet.com.br`. Em **Contas de FTP**, confirme que essa mesma pasta é o diretório da conta `deployblackpap@fernandagarnizet.com.br`. A raiz vista por essa conta no FTP corresponde a `server-dir: ./`.
2. Em **GitHub → Settings → Secrets and variables → Actions → Repository secrets**, cadastre `FTP_SERVER` (`br.brasil112-9575.com.br`, hostname do servidor Turbo Cloud confirmado por conexão FTPS sem login), `FTP_USERNAME` (`deployblackpap@fernandagarnizet.com.br`) e `FTP_PASSWORD`. Não coloque a senha no repositório. O nome sugerido pelo cPanel, `ftp.fernandagarnizet.com.br`, ainda não resolve no DNS; use o hostname do servidor enquanto isso.
3. Em **Actions**, execute **Publicar Black PAP no cPanel (FTPS)** manualmente, deixando **Publicar arquivos?** desmarcado. Essa execução usa `dry-run` para verificar conexão e listar as mudanças sem transferir arquivos.
4. Após conferir o resultado e autorizar a publicação, crie a variável de repositório `ENABLE_FTPS_DEPLOY` com valor `true` em **Settings → Secrets and variables → Actions → Variables**. A partir daí, mudanças em `site/` enviadas para `main` serão publicadas automaticamente. Também é possível executar manualmente com **Publicar arquivos?** marcado.

O arquivo `vercel.json` é usado apenas pela Vercel; ele não configura cache ou redirecionamentos no cPanel. A mudança de DNS é uma etapa separada.

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
