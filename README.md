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

### Lista de espera (Netlify Forms)

Os dois formulários (`lista-espera` no topo e `lista-espera-final` no fim) já têm
`data-netlify="true"`. Depois de publicar no Netlify:

1. No painel do site, abra **Forms** e clique em **Enable form detection**.
2. Volte a publicar (arraste outra vez a pasta com o `index.html`).
3. Os registos aparecem em **Forms**, com email, perfil e origem (topo ou final).
   Em *Forms › Form notifications* pode receber um email a cada registo.

### Secções

1. **Hero** — título, formulário de lista de espera e módulo que ajusta a largura sozinho.
2. **Configurador** — o visitante altera largura, altura, profundidade, módulos, prateleiras,
   espessura, portas e rodapé. O site recalcula ao vivo:
   - o desenho do móvel em vista dimétrica com cotas;
   - a lista de corte (peça, quantidade, medidas, metros de orla);
   - o plano de corte em chapas de 2750 × 1830 mm (nesting MaxRects, serra de 4 mm,
     refilo de 10 mm, rotação livre) e a sobra reutilizável da última chapa;
   - as etiquetas de peça na secção "Na oficina".
3. **Como funciona** — Modelar → Parametrizar → Cortar.
4. **Biblioteca** — seis blocos pré-definidos que abrem no configurador.
5. **Para quem é** — marcenarias, designers de interiores, fábricas.
6. **Funcionalidades** — seis capacidades da extensão.
7. **Na oficina** — etiquetas de peça geradas a partir do configurador.
8. **Perguntas** — FAQ.
9. **CTA final** — segundo formulário de lista de espera.

### O que editar

| O quê | Onde |
|---|---|
| Textos | `site/src/index.html` e a lista `FEATS` em `site/src/app.js` |
| Cores e tipografia | bloco `:root` no topo de `site/src/styles.css` |
| Blocos da biblioteca | objeto `PRESETS` em `site/src/app.js` |
| Regras de construção das peças | função `compute()` em `site/src/app.js` |
| Chapa, serra e refilo | constante `SHEET` em `site/src/app.js` |
| Email de contacto | FAQ e rodapé em `site/src/index.html`; mensagem de erro em `app.js` |
| Perguntas frequentes | secção `#faq` em `site/src/index.html` |

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

## Lista de espera (Supabase)

As inscrições do formulário vão para a tabela `lista_espera` do projeto Supabase **optimob**
(região eu-west-2). A estrutura e a regra de segurança estão em `supabase/lista_espera.sql`.

- O site usa só a chave **publishable** (pública). Com a regra de segurança, essa chave apenas
  consegue **inserir** inscrições; não lê, não altera e não apaga.
- Para ver as inscrições: Supabase › projeto optimob › **Table Editor** › `lista_espera`.
  Também dá para exportar em CSV a partir daí.
- Nunca colocar a *secret key* nem a *service_role* no site ou no repositório.

### Email de confirmação (Resend + Supabase Edge Function)

Código em `supabase/functions/confirmar-inscricao/index.ts`. Fluxo: nova linha em `lista_espera`
→ Database Webhook → função `confirmar-inscricao` → Resend envia o email.

Configuração (uma vez):
1. **Resend**: criar conta, adicionar o domínio `optimobsystem.com` e colocar na Hostinger os
   registos DNS que o Resend indicar (SPF/DKIM). Criar uma API key com permissão *Sending access*.
2. **Supabase › Edge Functions**: criar a função `confirmar-inscricao` com o código acima e
   desligar *Verify JWT* (a autenticação é feita pelo cabeçalho `x-webhook-secret`).
3. **Supabase › Edge Functions › Secrets**: `RESEND_API_KEY` e `WEBHOOK_SECRET` (texto aleatório).
4. **Supabase › Database › Webhooks**: novo webhook na tabela `lista_espera`, evento *Insert*,
   tipo *Supabase Edge Functions* → `confirmar-inscricao`, com o cabeçalho
   `x-webhook-secret: <o mesmo WEBHOOK_SECRET>`.

Várias inscrições ao mesmo tempo: a função responde logo ao webhook (202) e envia em segundo
plano. Se a Resend devolver 429 (limite de pedidos) ou um erro 5xx, tenta outra vez até 5 vezes,
com esperas crescentes. Cada envio leva um `Idempotency-Key` com o id da inscrição, por isso uma
repetição nunca gera um email duplicado. As falhas definitivas ficam em
*Edge Functions › confirmar-inscricao › Logs* ("Falhou após 5 tentativas").

Língua do email: o site envia a língua em que a página estava na inscrição (coluna `idioma`,
também quando a pessoa usa o tradutor do navegador). A função tem o texto em 39 línguas; numa
língua sem tradução envia em inglês; inscrições sem idioma (antigas) recebem português + inglês.
Para acrescentar uma língua, copie um bloco do objeto `L` em `index.ts` e traduza-o.
