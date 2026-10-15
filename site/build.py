"""Monta o site OptiMOB num único ficheiro HTML.

Uso:  python3 site/build.py
Gera: site/dist/index.html     -> documento completo, pronto para qualquer alojamento estático
      site/dist/artifact.html  -> mesmo conteúdo sem o esqueleto <html>, para publicar como Artifact
"""
import base64
import pathlib
import re

SITE = pathlib.Path(__file__).resolve().parent
SRC = SITE / 'src'
ASSETS = SITE / 'assets'
DIST = SITE / 'dist'


def svg(name):
    s = (ASSETS / f'{name}.svg').read_text()
    return re.sub(r'<svg ', '<svg role="img" aria-label="OptiMOB" ', s, count=1)


def main():
    tpl = (SRC / 'index.html').read_text()
    css = (SRC / 'styles.css').read_text()
    js = (SRC / 'app.js').read_text()
    favicon = 'data:image/svg+xml;base64,' + base64.b64encode((ASSETS / 'optimob-app-icon.svg').read_bytes()).decode()

    out = (tpl.replace('/*@css*/', css)
              .replace('/*@js*/', js)
              .replace('{{FAVICON}}', favicon)
              .replace('{{LOGO_SEM_REGUA}}', svg('optimob-sem-regua'))
              .replace('{{LOGO}}', svg('optimob-principal-transparente'))
              .replace('{{SIMBOLO}}', svg('optimob-simbolo')))
    head, body = out.split('<!--@body-->')

    DIST.mkdir(exist_ok=True)
    (DIST / 'artifact.html').write_text(head + body)
    full = ('<!doctype html>\n<html lang="pt">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            + head + '</head>\n<body>\n' + body + '</body>\n</html>\n')
    (DIST / 'index.html').write_text(full)
    print(f'site/dist/index.html  {len(full)/1024:.0f} KB')


if __name__ == '__main__':
    main()
