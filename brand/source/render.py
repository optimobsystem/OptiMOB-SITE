"""Renderiza brand/brandbook.html em PDF (brand/dist) e, opcionalmente, PNGs de páginas.
Uso: python3 brand/source/render.py          -> PDF completo
     python3 brand/source/render.py 1 5 9    -> só pré-visualizações dessas páginas (brand/prev)
"""
import sys, os, pathlib
BRAND = pathlib.Path(__file__).resolve().parent.parent
os.chdir(BRAND)
os.makedirs('prev', exist_ok=True)
os.makedirs('dist', exist_ok=True)
from playwright.sync_api import sync_playwright
only = [int(x) for x in sys.argv[1:]]
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': 1600, 'height': 900})
    pg.goto((BRAND / 'brandbook.html').as_uri())
    pg.wait_for_timeout(800)
    n = pg.locator('section.page').count()
    for i in range(n):
        if only and i + 1 not in only:
            continue
        pg.locator('section.page').nth(i).screenshot(path=f'prev/p{i+1:02d}.png')
    if not only:
        pg.pdf(path='dist/OptiMOB_Brand_Guidelines_v1.pdf', width='1600px', height='900px',
               print_background=True, prefer_css_page_size=True)
    b.close()
print('done', n)
