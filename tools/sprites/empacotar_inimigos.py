"""Empacota os inimigos renderizados (arte/render/inimigos/, feito por tools/blender/inimigos.py) em folhas por inimigo.

uso: python3 tools/sprites/empacotar_inimigos.py [inimigos...]     (sem argumentos: todos)
     python3 tools/sprites/empacotar_inimigos.py --unidades [tipos...]   (aliados: arte/render/unidades ->
                                                                         sprites/un_<tipo>_<k>.png + js/unidades_meta.js)
     python3 tools/sprites/empacotar_inimigos.py --vitrine [tipos...]    (herois grandes da tela de herois e do inicio:
                                                                         arte/render/vitrine -> sprites/vi_* + js/vitrine_meta.js)

Reaproveita o empacotador das torres (tools/sprites/empacotar.py) como biblioteca: mesma limpeza de sombra, mesmo
formato de quadro [folha, x, y, largura, altura, ancoraX, ancoraY]. Cada inimigo vira sprites/in_<tipo>_<k>.png, para o
jogo carregar so os inimigos que aparecem na fase. Saida: js/inimigos_meta.js
  INIMIGOS_META = {scale, sheets: [arquivos], fams: {tipo: [indices das folhas]}, sets: {tipo: {r, u, d, a, x, boost}}}
"""
import json, os, sys, shutil, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import empacotar as emp

ROOT = emp.ROOT
SRC = os.path.join(ROOT, 'arte', 'render', 'inimigos')
META_JS = os.path.join(ROOT, 'js', 'inimigos_meta.js')
PREFIX, VAR = 'in_', 'INIMIGOS_META'
if '--unidades' in sys.argv:
    sys.argv.remove('--unidades')
    SRC = os.path.join(ROOT, 'arte', 'render', 'unidades')
    META_JS = os.path.join(ROOT, 'js', 'unidades_meta.js')
    PREFIX, VAR = 'un_', 'UNIDADES_META'
if '--vitrine' in sys.argv:
    sys.argv.remove('--vitrine')
    SRC = os.path.join(ROOT, 'arte', 'render', 'vitrine')
    META_JS = os.path.join(ROOT, 'js', 'vitrine_meta.js')
    PREFIX, VAR = 'vi_', 'VITRINE_META'


def main():
    meta = json.load(open(os.path.join(SRC, 'meta.json')))
    only = set(sys.argv[1:])
    tmp = tempfile.mkdtemp(prefix='inimigos_')
    emp.RENDER = tmp
    old_js = {}
    if only and os.path.exists(META_JS):
        txt = open(META_JS).read()
        old_js = json.loads(txt[txt.index('{'):txt.rindex('}') + 1])
    sheets, fams, sets = [], {}, {}
    report = {}
    try:
        for name, info in meta['sets'].items():
            fam = PREFIX + name
            if only and name not in only and old_js.get('fams', {}).get(name) is not None:
                # reaproveita o empacotamento anterior deste inimigo
                base = len(sheets)
                idx = old_js['fams'][name]
                sheets += [old_js['sheets'][i] for i in idx]
                remap = {o: base + j for j, o in enumerate(idx)}
                sets[name] = shift_sets(old_js['sets'][name], lambda v: remap[v])
                fams[name] = list(range(base, len(sheets)))
                report[name] = 'mantido'
                continue
            d = os.path.join(tmp, fam)
            os.makedirs(d)
            # na vitrine o heroi e ~4x maior que no jogo: contorno mais grosso para a mesma espessura na tela
            contorno(os.path.join(SRC, name), os.path.join(d, name), name, 4 if PREFIX == 'vi_' else 2)
            with open(os.path.join(d, 'meta.json'), 'w') as fh:
                json.dump({'family': fam, 'px_per_game': meta['px_per_game'], 'game_per_bu': meta['game_per_bu'], 'sets': {name: info}}, fh)
            res = emp.pack_family(fam)
            base = len(sheets)
            sheets += ['sprites/' + n for n in res['sheets']]
            fams[name] = list(range(base, len(sheets)))
            sets[name] = shift_sets(res['sets'][name], lambda v: base + v)
            if PREFIX == 'in_':
                # delator (o adversario derrotado correndo de volta): os mesmos quadros do andar, com as cores de sempre
                for m, lm in (('r', 'l'), ('q', 'lq'), ('u', 'lu'), ('e', 'le'), ('d', 'ld'), ('a', 'la')):
                    if m in sets[name] and lm not in sets[name]:
                        sets[name][lm] = sets[name][m]
            size = sum(os.path.getsize(os.path.join(emp.OUT, n)) for n in res['sheets'])
            report[name] = f"{len(res['sheets'])} folha(s), {size / 1e6:.2f} MB"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    sheets = [webp(n) for n in sheets]
    with open(META_JS, 'w') as fh:
        fh.write('\'use strict\';\n// Gerado por tools/sprites/empacotar_inimigos.py a partir de tools/blender/inimigos_glb.py ou unidades_glb.py. Nao editar a mao.\n')
        fh.write('const ' + VAR + ' = ' + json.dumps({'scale': meta['px_per_game'], 'sheets': sheets, 'fams': fams, 'sets': sets}, separators=(',', ':')) + ';\n')
    print(json.dumps(report, ensure_ascii=False, indent=1))


def ss(x, a, b):
    import numpy as np
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def possuido(a, tipo):
    """Bicho possuido pela Fumaca Negra: a cor do corpo e drenada (cinza puxado para o roxo, mais escuro) e so as
    brasas (pintas, veias e olhos laranja vivos) ficam acesas. Devolve (quadro, mascara de brasa 0..1). O liberto (l)
    nao passa por aqui: volta com as cores vivas, e a diferenca entre os dois e o que diz que ele estava possuido."""
    import numpy as np
    rgb = a[..., :3] / 255.0
    mx, mn = rgb.max(-1), rgb.min(-1)
    d = mx - mn
    dd = np.maximum(d, 1e-6)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    h = np.where(r == mx, (g - b) / dd, np.where(g == mx, 2 + (b - r) / dd, 4 + (r - g) / dd))
    h = np.where(d > 1e-6, (h / 6) % 1, 0)
    sat = np.where(mx > 1e-6, d / np.maximum(mx, 1e-6), 0)
    if tipo in ('ifrit',):
        # o Boitata e de fogo: a chama amarela-palida tambem e brasa
        brasa = ss(h, 0.0, 0.03) * (1 - ss(h, 0.18, 0.22)) * ss(sat, 0.18, 0.35) * ss(mx, 0.7, 0.85)
    else:
        brasa = ss(h, 0.02, 0.05) * (1 - ss(h, 0.15, 0.19)) * ss(sat, 0.42, 0.62) * ss(mx, 0.74, 0.9)
    lum = r * 0.3 + g * 0.55 + b * 0.15
    cinza = 0.35 * rgb + 0.65 * lum[..., None]
    cinza = cinza * 0.74 * np.array([0.95, 0.86, 1.06])
    out = rgb * brasa[..., None] + cinza * (1 - brasa[..., None])
    res = a.copy()
    corpo = (a[..., 3] > 0) & (mx > 0.03)
    res[..., :3] = np.where(corpo[..., None], out * 255, a[..., :3])
    return res, brasa * (a[..., 3] > 170)


def contorno(src, dst, tipo='', raio=2):
    """Copia os quadros com um contorno escuro fino em volta do corpo (a sombra no chao fica de fora): o bicho
    descola do chao escuro (fase 8) sem parecer recortado. raio em px do render (~0,5 unidade do jogo).
    Inimigos: os quadros possuidos (tudo menos l) ganham a cor drenada, contorno roxo-escuro e a camada de brasa
    G<modo>_NN; o liberto (l, lq, lu, le, ld, la) fica com as cores do render e o contorno marrom."""
    from PIL import Image, ImageFilter
    import numpy as np
    os.makedirs(dst)
    for fn in os.listdir(src):
        if not fn.endswith('.png') or fn.startswith('G'):
            continue
        im = Image.open(os.path.join(src, fn)).convert('RGBA')
        a = np.asarray(im).astype(np.float32)
        mal = False   # na satira ninguem esta possuido: cores do render e contorno marrom
        cor, alfa = ((34, 18, 42), 0.8) if mal else ((40, 24, 16), 0.62)
        if mal:
            a, brasa = possuido(a, tipo)
            gl = np.zeros_like(a)
            gl[..., :3] = a[..., :3]
            gl[..., 3] = brasa * 255
            Image.fromarray(gl.clip(0, 255).astype(np.uint8)).save(os.path.join(dst, 'G' + fn))
        corpo = (a[..., 3] > 170) & (a[..., :3].max(-1) > 22)
        m = Image.fromarray((corpo * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(raio * 2 + 1))
        borda = (np.asarray(m) > 0) & ~corpo
        k = alfa * borda
        out = a.copy()
        # contorno por cima da sombra/fundo transparente: "over" com a cor do contorno
        ao = a[..., 3] / 255.0
        an = k + ao * (1 - k)
        for i in range(3):
            num = cor[i] * k + a[..., i] * ao * (1 - k)
            out[..., i] = np.where(borda, num / np.maximum(an, 1e-6), a[..., i])
        out[..., 3] = np.where(borda, an * 255, a[..., 3])
        Image.fromarray(out.clip(0, 255).astype(np.uint8)).save(os.path.join(dst, fn))


def webp(rel):
    """Converte uma folha PNG do sprites/ para WebP com alfa (q90) e apaga o PNG; devolve o caminho novo."""
    from PIL import Image
    if rel.endswith('.webp'):
        return rel
    src = os.path.join(ROOT, rel)
    dst = src[:-4] + '.webp'
    if os.path.exists(src):
        Image.open(src).save(dst, 'WEBP', quality=90, alpha_quality=100, method=6)
        os.remove(src)
    return rel[:-4] + '.webp'


def shift_sets(s, f):
    out = {}
    for k, v in s.items():
        if k in ('fam', 'boost', 'pxk', 'height'):
            out[k] = v
        elif isinstance(v, list) and v and isinstance(v[0], list):
            out[k] = [[f(q[0])] + q[1:] for q in v]
        elif isinstance(v, list) and len(v) == 7:
            out[k] = [f(v[0])] + v[1:]
        else:
            out[k] = v
    return out


if __name__ == '__main__':
    main()
