# OptiMOB

Furniture Design System — extensão de blocos paramétricos de marcenaria para SketchUp.

Este repositório reúne a identidade da marca e o site do produto.

```
optimob/
├── brand/                     Identidade visual
│   ├── source/                Código que gera o logótipo e o brandbook
│   │   ├── logo.py            Logótipo em vetor (glifos Inter Display + régua paramétrica)
│   │   ├── brandbook.py       Monta o brandbook em HTML (23 páginas)
│   │   ├── brandbook.css      Estilos do brandbook
│   │   ├── render.py          Exporta o brandbook para PDF
│   │   └── logo-original.png  Proposta original, usada na página "Evolução"
│   ├── svg/                   Logótipos finais em SVG
│   ├── png/                   Logótipos finais em PNG (alta resolução, fundo transparente)
│   ├── fonts/                 JetBrains Mono (woff2) usada no brandbook
│   └── dist/                  Brandbook em PDF + pacote de logótipos (.zip)
└── site/                      Site do produto
    ├── src/
    │   ├── index.html         Estrutura da página
    │   ├── styles.css         Estilos (tokens da marca no topo)
    │   └── app.js             Configurador: desenho, lista de corte, nesting e etiquetas
    ├── assets/                SVGs da marca usados pelo site
    ├── build.py               Junta tudo num único ficheiro HTML
    └── dist/
        ├── index.html         Site final, pronto a publicar
        └── artifact.html      A mesma página sem o esqueleto <html>, para publicar como Artifact
```

## Site

```bash
python3 site/build.py          # gera site/dist/index.html
```

O resultado é um único ficheiro HTML sem dependências (as fontes vêm do Google Fonts).
Serve para qualquer alojamento estático: GitHub Pages, Netlify, Vercel ou o seu próprio servidor.

### Secções

1. **Configurador** — o visitante altera largura, altura, profundidade, módulos, prateleiras,
   espessura, portas e rodapé. O site recalcula ao vivo:
   - o desenho do móvel em vista dimétrica com cotas;
   - a lista de corte (peça, quantidade, medidas, metros de orla);
   - o plano de corte em chapas de 2750 × 1830 mm (nesting MaxRects, serra de 4 mm,
     refilo de 10 mm, rotação livre) e a sobra reutilizável da última chapa;
   - as etiquetas de peça na secção "Na oficina".
2. **Processo** — Modelar → Parametrizar → Cortar.
3. **Funcionalidades** — seis capacidades da extensão.
4. **Biblioteca** — seis blocos pré-definidos que abrem no configurador.
5. **Na oficina** — etiquetas de peça geradas a partir do configurador.
6. **Acesso antecipado** — contacto por email.

### O que editar

| O quê | Onde |
|---|---|
| Textos | `site/src/index.html` e a lista `FEATS` em `site/src/app.js` |
| Cores e tipografia | bloco `:root` no topo de `site/src/styles.css` |
| Blocos da biblioteca | objeto `PRESETS` em `site/src/app.js` |
| Regras de construção das peças | função `compute()` em `site/src/app.js` |
| Chapa, serra e refilo | constante `SHEET` em `site/src/app.js` |
| Email de contacto | `#mailAddr` em `site/src/index.html` |

Depois de editar, corra `python3 site/build.py` outra vez.

## Marca

```bash
pip install playwright fonttools brotli
python3 brand/source/logo.py brand/svg        # regenera os SVGs do logótipo
python3 brand/source/brandbook.py             # gera brand/brandbook.html
python3 brand/source/render.py                # exporta brand/dist/OptiMOB_Brand_Guidelines_v1.pdf
```

O logótipo usa os glifos da **Inter Display** convertidos em vetor. Por isso é preciso ter
a Inter Display instalada para o regenerar (`/usr/share/fonts/opentype/inter/`, ou ajuste o
caminho `INTER` em `logo.py`).

### Paleta

| Nome | HEX | Uso |
|---|---|---|
| Grafite | `#1B1E1E` | Fundo principal |
| Azul Parâmetro | `#3AA0FF` | Ação, valores, puxadores |
| Bone | `#EEF0EA` | Texto, "Opti" |
| Carbono | `#111313` | Fundos profundos |
| Aço | `#2A2F30` | Linhas e divisões |
| Cinza Técnico | `#8A918F` | Texto secundário |
| Azul Profundo | `#1F6FC2` | Azul sobre fundos claros |
