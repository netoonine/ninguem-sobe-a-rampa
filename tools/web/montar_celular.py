#!/usr/bin/env python3
"""Versao para celular (artifact do claude.ai): folhas pela metade, toque, tela cheia e save na conta.

    python3 tools/web/montar_celular.py        ->  dist/celular/  (index.html + js/ + sprites/)

O jogo continua o mesmo: as folhas saem com metade do lado (1,5x a tela logica em vez de 3x, sobra no celular) e o
js/celular.js corrige o drawImage para as coordenadas das folhas originais, entao nenhum _meta precisa mudar alem do
caminho dos arquivos (png com alfa vira webp). Imagens ja convertidas e mais novas que a fonte nao sao refeitas.
"""
import json, math, os, re, shutil, sys
from PIL import Image

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SAI = os.path.join(RAIZ, 'dist', 'celular')
K = 0.5

# mesma ordem do index.html do jogo (lida dele); o debug.js fica de fora (le parametros da URL)
import re as _re
SCRIPTS = [m for m in _re.findall(r'src="js/([\w]+)\.js"', open(os.path.join(RAIZ, 'index.html'), encoding='utf-8').read()) if m != 'debug']


def novo(path):
    """caminho da folha na versao do celular"""
    base, ext = os.path.splitext(path)
    return base + ('.jpg' if ext.lower() in ('.jpg', '.jpeg') else '.webp')


def converte(src, dst):
    im = Image.open(src)
    w, h = im.size
    nw, nh = math.ceil(w * K), math.ceil(h * K)
    if dst.endswith('.jpg'):
        im.convert('RGB').resize((nw, nh), Image.LANCZOS).save(dst, quality=84, optimize=True, progressive=True)
    else:
        # alfa pre-multiplicado na reducao: sem franja escura nas bordas
        im = im.convert('RGBA').convert('RGBa').resize((nw, nh), Image.LANCZOS).convert('RGBA')
        im.save(dst, quality=86, method=6)
    return [w, h]


def imagens():
    os.makedirs(os.path.join(SAI, 'sprites'), exist_ok=True)
    cache_p = os.path.join(SAI, 'orig.json')
    orig = json.load(open(cache_p)) if os.path.exists(cache_p) else {}
    mapa = {}
    for nome in sorted(os.listdir(os.path.join(RAIZ, 'sprites'))):
        src = os.path.join(RAIZ, 'sprites', nome)
        if not os.path.isfile(src) or not re.search(r'\.(png|webp|jpe?g)$', nome, re.I):
            continue
        nn = novo(nome)
        assert nn not in mapa.values(), 'dois arquivos viram ' + nn
        mapa[nome] = nn
        dst = os.path.join(SAI, 'sprites', nn)
        if nn in orig and os.path.exists(dst) and os.path.getmtime(dst) >= os.path.getmtime(src):
            continue
        orig[nn] = converte(src, dst)
        print('  ', nome, '->', nn)
    # interface (9 fatias, retratos, logo): copia sem mexer
    ui_s, ui_d = os.path.join(RAIZ, 'sprites', 'ui'), os.path.join(SAI, 'sprites', 'ui')
    os.makedirs(ui_d, exist_ok=True)
    for nome in os.listdir(ui_s):
        if nome.lower().endswith('.png'):
            shutil.copy2(os.path.join(ui_s, nome), os.path.join(ui_d, nome))
    for nn in [n for n in orig if n not in mapa.values()]:
        del orig[nn]
    json.dump(orig, open(cache_p, 'w'))
    return mapa, orig


def troca(txt, velho, novo_, n=1, arq=''):
    achou = txt.count(velho)
    assert achou == n, f'{arq}: esperava {n}x e achei {achou}x: {velho[:70]!r}'
    return txt.replace(velho, novo_)


def scripts(mapa):
    d = os.path.join(SAI, 'js')
    os.makedirs(d, exist_ok=True)
    for s in SCRIPTS:
        txt = open(os.path.join(RAIZ, 'js', s + '.js'), encoding='utf-8').read()
        if s.endswith('_meta') or s == 'provisorio':
            for a, b in mapa.items():
                txt = txt.replace('"sprites/' + a + '"', '"sprites/' + b + '"')
            assert not re.search(r'"sprites/[^"/]+\.png"', txt), s + ': sobrou png nas folhas'
        elif s == 'main':
            # o jogo ocupa o palco (area segura do celular), nao a janela inteira
            txt = troca(txt, 'const w = window.innerWidth, h = window.innerHeight;',
                        "const st = document.getElementById('palco');\n"
                        '    const w = st ? st.clientWidth : window.innerWidth, h = st ? st.clientHeight : window.innerHeight;', arq=s)
            # ponteiro em vez de mouse: o mesmo caminho serve para dedo, caneta e mouse
            txt = troca(txt, "cv.addEventListener('mousemove', ev => {",
                        "cv.addEventListener('pointermove', ev => { if (ev.pointerType !== 'mouse') return;", arq=s)
            txt = troca(txt, "cv.addEventListener('mouseleave', () => { UI.mx = -1; UI.my = -1; });",
                        "cv.addEventListener('pointerleave', ev => { if (ev.pointerType === 'mouse') { UI.mx = -1; UI.my = -1; } });", arq=s)
            txt = troca(txt, "cv.addEventListener('mousedown', ev => {\n      Snd.init();",
                        "cv.addEventListener('pointerdown', ev => {\n"
                        "      UI.touch = ev.pointerType !== 'mouse';\n"
                        '      UI._prevArmed = UI.armed; UI.armed = null;\n'
                        '      Snd.init();', arq=s)
        elif s == 'sprites':
            # copia tingida da folha: no tamanho da folha reduzida, levando a escala junto
            txt = troca(txt, 'c.drawImage(im, 0, 0);', 'c.drawImage(im, 0, 0, cv.width, cv.height);', n=2, arq=s)
            txt = troca(txt, "c.drawImage(im, 0, 0, cv.width, cv.height);\n      return cv;",
                        "c.drawImage(im, 0, 0, cv.width, cv.height);\n      cv._sk = MOBK.of(im);\n      return cv;", arq=s)
        elif s == 'ui':
            # botoes do anel: no toque, o primeiro mostra o cartao e o segundo confirma
            txt = troca(txt, 'const hov = UI.circle(key, x, y, BR + 2, cb);',
                        'const hov = UI.circle(key, x, y, BR + 2, UI.twoTap(key, cb));', arq=s)
        open(os.path.join(d, s + '.js'), 'w', encoding='utf-8').write(txt)
    for s in ('celular', 'celular_fim'):
        shutil.copy2(os.path.join(RAIZ, 'tools', 'web', s + '.js'), os.path.join(d, s + '.js'))


def pagina(orig):
    tpl = open(os.path.join(RAIZ, 'tools', 'web', 'celular.html'), encoding='utf-8').read()
    tags = '\n'.join(f'<script src="js/{s}.js"></script>' for s in ['celular'] + SCRIPTS + ['celular_fim'])
    html = tpl.replace('<!--SCRIPTS-->', tags).replace('__ORIG__', json.dumps(orig, separators=(',', ':')))
    open(os.path.join(SAI, 'index.html'), 'w', encoding='utf-8').write(html)


def main():
    print('imagens...')
    mapa, orig = imagens()
    print('scripts...')
    scripts(mapa)
    pagina(orig)
    tot, n = 0, 0
    lista = {}
    for raiz, _, arqs in os.walk(SAI):
        for a in arqs:
            p = os.path.join(raiz, a)
            rel = os.path.relpath(p, SAI)
            if rel in ('index.html', 'orig.json', 'arquivos.json') or a.startswith('_'):
                continue
            lista[rel] = os.path.relpath(p, RAIZ)
            tot += os.path.getsize(p); n += 1
    json.dump(lista, open(os.path.join(SAI, 'arquivos.json'), 'w'), indent=0)
    print(f'{n} arquivos, {tot / 1e6:.1f} MB (fora o index.html)')


if __name__ == '__main__':
    main()
