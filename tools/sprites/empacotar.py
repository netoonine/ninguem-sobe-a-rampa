"""Empacota os quadros renderizados no Blender em folhas de sprites para o jogo, uma familia de torre por vez.

uso: python3 tools/sprites/empacotar.py [familias...]      (sem argumentos: todas as pastas de arte/render com meta.json)

Cada familia (arte/render/<familia>/) vira as folhas sprites/<familia>_<k>.png. O jogo so carrega as folhas das
torres levadas na fase. Tudo vai para js/sprites_meta.js:
  SPRITE_META = {scale, sheets: [arquivos], fams: {familia: [indices das folhas]}, sets: {conjunto: {...}}}
Cada quadro vira [folha, x, y, largura, altura, ancoraX, ancoraY] (pixels), onde a ancora e o ponto do chao no
centro da torre (ou os pes do personagem / o pivo da torreta). O jogo desenha o quadro em
(x - ancoraX / escala, y - ancoraY / escala), com escala = pixels por unidade do jogo.

Uma familia so e reempacotada quando o render dela muda (cache em arte/render/<familia>/pack.json).
"""
import json, os, sys
import numpy as np
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
# chapa (cores das torres): CHAPA=V (padrao) le arte/render e grava js/sprites_meta.js; CHAPA=R le arte/render_r e grava
# js/sprites_meta_r.js (so folhas e conjuntos; o que nao tem render_r vem do meta da V) com folhas <familia>_r_<k>.png
CHAPA = (os.environ.get('CHAPA', 'V').strip().upper() or 'V')[:1]
SUF = '_r' if CHAPA == 'R' else ''
RENDER = os.path.join(ROOT, 'arte', 'render' + SUF)
OUT = os.path.join(ROOT, 'sprites')
META_JS = os.path.join(ROOT, 'js', 'sprites_meta' + SUF + '.js')
META_V_JS = os.path.join(ROOT, 'js', 'sprites_meta.js')
SHEET = 2048
PAD = 2
ORDER = ['comum', 'icones', 'ambiente', 'arqueiros', 'zarabatana', 'magos', 'artilharia', 'quartel', 'cisterna', 'catavento', 'estandarte', 'mercado']


def clean_shadow(a, haze=16, edge=24):
    """A sombra do chao (pixels pretos semitransparentes) vem com uma nevoa fraca no quadro todo:
    corta o que for mais fraco que `haze` e esmaece a sombra perto das bordas para nunca aparecer corte reto."""
    h, w = a.shape[:2]
    rgb = a[..., :3].astype(np.int32)
    al = a[..., 3].astype(np.int32)
    sh = (al > 0) & (rgb.max(axis=2) <= 6) & (al <= 200)
    na = np.maximum(0, al - haze) * 255 // (255 - haze) * 4 // 5   # sombra 20% mais clara, no tom das sombras do cenario
    yy, xx = np.mgrid[0:h, 0:w]
    e = np.minimum(np.minimum(yy, h - 1 - yy), np.minimum(xx, w - 1 - xx))
    na = np.where(e < edge, na * e // edge, na)
    out = a.copy()
    out[..., 3] = np.where(sh, na, al).astype(np.uint8)
    out[..., :3] = np.where(sh[..., None], 0, a[..., :3])
    return out


def glow_layer(a):
    """Camada de luz: alfa = canal mais forte, cor normalizada (somada com 'lighter' no jogo)."""
    rgb = a[..., :3].astype(np.int32) * a[..., 3:4].astype(np.int32) // 255
    m = rgb.max(axis=2)
    out = np.zeros_like(a)
    ok = m >= 4
    safe = np.maximum(m, 1)[..., None]
    out[..., :3] = np.where(ok[..., None], rgb * 255 // safe, 0).astype(np.uint8)
    out[..., 3] = np.where(ok, m, 0).astype(np.uint8)
    return out


def load(path, glow=False):
    a = np.array(Image.open(path).convert('RGBA'))
    a = glow_layer(a) if glow else clean_shadow(a)
    im = Image.fromarray(a)
    box = im.getbbox() or (0, 0, 1, 1)
    return im.crop(box), box


def newest(d):
    t = 0
    for f in os.listdir(d):
        p = os.path.join(d, f)
        if os.path.isdir(p):
            t = max(t, newest(p))
        elif f.endswith('.png') or f == 'meta.json':
            t = max(t, os.path.getmtime(p))
    return t


def pack_family(fam):
    """Empacota uma familia; devolve {'sheets': [arquivos], 'sets': {...} com quadros [folha_local, ...]}."""
    src = os.path.join(RENDER, fam)
    meta = json.load(open(os.path.join(src, 'meta.json')))
    scale = meta['px_per_game']
    frames = []

    def add(path, anchor, glow=False):
        im, box = load(path, glow)
        frames.append({'im': im, 'ax': anchor[0] - box[0], 'ay': anchor[1] - box[1], 'glow': glow})
        return len(frames) - 1

    def rel(p, anc):
        return [round((p[0] - anc[0]) / scale, 2), round((p[1] - anc[1]) / scale, 2)]

    sets = {}
    for name, info in meta['sets'].items():
        d = os.path.join(src, name)
        anc = info['anchor']
        s = {'fam': fam}
        seq = lambda prefix, n: [add(os.path.join(d, f'{prefix}_{f:02d}.png'), anc) for f in range(n)]
        if 'loop' in info:
            s['loop'] = seq('loop', info['loop'])
        if info.get('base'):
            s['base'] = add(os.path.join(d, 'base.png'), anc)
        if info.get('anim'):
            s['anim'] = seq('anim', info['anim'])
        if info.get('front'):
            s['front'] = add(os.path.join(d, 'front.png'), anc)
        if info.get('build'):
            s['build'] = seq('build', info['build'])
        if info.get('glow'):
            s['glow'] = add(os.path.join(d, 'glow.png'), anc, glow=True)
        for mode in ('idle', 'aim', 'shoot'):
            if mode in info and 'modes' not in info:
                s[mode] = seq(mode, info[mode])
        for mode, n in info.get('modes', {}).items():
            s[mode] = seq(mode, n)
        if info.get('still'):
            s['still'] = add(os.path.join(d, 'still.png'), anc)
        for k in ('pxk', 'boost'):
            if k in info:
                s[k] = info[k]
        if 'dirs' in info and 'frames' in info:
            s['dirs'] = [[add(os.path.join(d, f'd{i:02d}_{f:02d}.png'), anc) for f in range(info['frames'])] for i in range(info['dirs'])]
        elif 'dirs' in info:
            s['ndirs'] = info['dirs']
        if 'slots' in info:
            s['slots'] = [rel(p, anc) for p in info['slots']]
        if 'lanterns' in info:
            s['lanterns'] = [rel(p, anc) + list(p[2:]) for p in info['lanterns']]
        if 'points' in info:
            s['points'] = {k: rel(p, anc) for k, p in info['points'].items()}
        sets[name] = s

    # empacotamento em prateleiras, maiores primeiro; as camadas de luz vao em folhas separadas (nao recebem o tom do clima)
    order = sorted(range(len(frames)), key=lambda i: (frames[i]['glow'], -frames[i]['im'].size[1]))
    sheets, place, cur = [], {}, None
    glow_sheets = []
    for i in order:
        w, h = frames[i]['im'].size
        w += PAD
        h += PAD
        if frames[i]['glow'] and (cur is None or not cur.get('glow')):
            cur = {'img': Image.new('RGBA', (SHEET, SHEET)), 'x': 0, 'y': 0, 'rowh': 0, 'maxy': 0, 'glow': True}
            sheets.append(cur)
            glow_sheets.append(len(sheets) - 1)
        if cur is None or (cur['x'] + w > SHEET and cur['y'] + cur['rowh'] + h > SHEET):
            cur = {'img': Image.new('RGBA', (SHEET, SHEET)), 'x': 0, 'y': 0, 'rowh': 0, 'maxy': 0, 'glow': frames[i]['glow']}
            sheets.append(cur)
            if cur['glow']:
                glow_sheets.append(len(sheets) - 1)
        if cur['x'] + w > SHEET:
            cur['x'] = 0
            cur['y'] += cur['rowh']
            cur['rowh'] = 0
        if cur['y'] + h > SHEET:
            cur = {'img': Image.new('RGBA', (SHEET, SHEET)), 'x': 0, 'y': 0, 'rowh': 0, 'maxy': 0, 'glow': cur.get('glow')}
            sheets.append(cur)
            if cur['glow']:
                glow_sheets.append(len(sheets) - 1)
        cur['img'].paste(frames[i]['im'], (cur['x'], cur['y']))
        place[i] = (len(sheets) - 1, cur['x'], cur['y'])
        cur['x'] += w
        cur['rowh'] = max(cur['rowh'], h)
        cur['maxy'] = max(cur['maxy'], cur['y'] + h)

    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT):
        if f.startswith(fam + SUF + '_') and f.endswith('.png') and (SUF or not f.startswith(fam + '_r_')):
            os.remove(os.path.join(OUT, f))
    names = []
    for k, sh in enumerate(sheets):
        img = sh['img'].crop((0, 0, SHEET, min(SHEET, sh['maxy'])))
        fn = f'{fam}{SUF}_{k}.png'
        img.save(os.path.join(OUT, fn), optimize=True)
        names.append(fn)

    def fr(i):
        sh, x, y = place[i]
        f = frames[i]
        w, h = f['im'].size
        return [sh, x, y, w, h, round(f['ax'], 1), round(f['ay'], 1)]

    def conv(v):
        if isinstance(v, list):
            return [conv(x) for x in v]
        if isinstance(v, int):
            return fr(v)
        return v
    out_sets = {}
    for name, s in sets.items():
        out_sets[name] = {k: (v if k in ('slots', 'lanterns', 'points', 'pxk', 'boost', 'fam', 'ndirs') else conv(v)) for k, v in s.items()}
        # altura visivel (do chao ate o topo) em unidades do jogo, para medir a torre (A.towerH)
        tops = [f for k in ('base', 'anim', 'loop') if k in out_sets[name] for f in ([out_sets[name][k]] if k == 'base' else out_sets[name][k])]
        if tops:
            out_sets[name]['height'] = round(max(f[6] for f in tops) / scale, 1)
    return {'sheets': names, 'glow': glow_sheets, 'sets': out_sets, 'scale': scale, 'game_per_bu': meta['game_per_bu'], 'raw': meta}


def prev_meta():
    """SPRITE_META atual (js/sprites_meta.js), ou None. No fork as familias que ainda nao foram refeitas aqui (sem pasta
    em arte/render) continuam vindo das folhas herdadas do Guardioes: o empacotador carrega o que ja estava no meta."""
    try:
        s = open(META_V_JS).read()   # a chapa R herda da V o que nao tem render proprio
        return json.loads(s[s.index('{'):s.rindex('}') + 1])
    except Exception:
        return None


def n_fases():
    """Quantas fases o jogo tem (arte/render/cenario/fases.json, exportado por tools/fases_json.js); sem ele, 12."""
    try:
        return len(json.load(open(os.path.join(RENDER, 'cenario', 'fases.json'))))
    except Exception:
        return 12


def pack_cenario(prev=None):
    """Fundos das fases (arte/render/cenario/f<N>.png, 2x a tela do jogo) viram JPG; a luz (lava, braseiros) vai a parte.
    Uma entrada por fase de fases.json. Sem nenhum fundo renderizado ainda, fica o cenario que ja estava no meta."""
    src = os.path.join(RENDER, 'cenario')
    n = n_fases()
    if prev and prev.get('cenario') and not any(os.path.exists(os.path.join(src, f'f{i}.png')) for i in range(1, n + 1)):
        return prev['cenario']
    out = []
    for i in range(1, n + 1):
        png = os.path.join(src, f'f{i}.png')
        js = os.path.join(src, f'f{i}.json')
        if not (os.path.exists(png) and os.path.exists(js)):
            out.append(None)
            continue
        info = json.load(open(js))
        item = {'img': f'sprites/cenario_f{i}.jpg', 'palms': info.get('palms', []), 'env': info.get('env', [])}
        dst = os.path.join(OUT, f'cenario_f{i}.jpg')
        if not os.path.exists(dst) or os.path.getmtime(dst) < os.path.getmtime(png):
            Image.open(png).convert('RGB').save(dst, quality=87, optimize=True, progressive=True)
        glow = os.path.join(src, f'f{i}_glow.png')
        if info.get('glow') and os.path.exists(glow):
            gd = os.path.join(OUT, f'cenario_f{i}_luz.jpg')
            if not os.path.exists(gd) or os.path.getmtime(gd) < os.path.getmtime(glow):
                # brilho macio em volta da lava e das chamas (a luz e somada no jogo)
                from PIL import ImageFilter, ImageChops
                g0 = Image.open(glow).convert('RGB')
                bl = g0.filter(ImageFilter.GaussianBlur(10 * g0.width / 2560)).point(lambda v: min(255, int(v * 1.8)))  # raio na escala do render
                ImageChops.lighter(g0, bl).save(gd, quality=85, optimize=True)
            item['luz'] = f'sprites/cenario_f{i}_luz.jpg'
        # cheia da varzea: o mesmo fundo com a agua alta (o jogo mistura pelo g.flood)
        cheia = os.path.join(src, f'f{i}_cheia.png')
        if info.get('cheia') and os.path.exists(cheia):
            cd = os.path.join(OUT, f'cenario_f{i}_cheia.jpg')
            if not os.path.exists(cd) or os.path.getmtime(cd) < os.path.getmtime(cheia):
                Image.open(cheia).convert('RGB').save(cd, quality=87, optimize=True, progressive=True)
            item['cheia'] = f'sprites/cenario_f{i}_cheia.jpg'
        if info.get('fenda'):
            item['fenda'] = info['fenda']
        out.append(item)
    return out


def pack_mapa(nome='mapa'):
    """Fundo do mapa-mundi (tools/blender/mapa.py; mapa2 e a segunda regiao): JPG e a luz do vulcao."""
    src = os.path.join(RENDER, 'cenario')
    png = os.path.join(src, f'{nome}.png')
    if not os.path.exists(png):
        return None
    dst = os.path.join(OUT, f'cenario_{nome}.jpg')
    if not os.path.exists(dst) or os.path.getmtime(dst) < os.path.getmtime(png):
        Image.open(png).convert('RGB').save(dst, quality=87, optimize=True, progressive=True)
    item = {'img': f'sprites/cenario_{nome}.jpg'}
    glow = os.path.join(src, f'{nome}_glow.png')
    if os.path.exists(glow):
        gd = os.path.join(OUT, f'cenario_{nome}_luz.jpg')
        if not os.path.exists(gd) or os.path.getmtime(gd) < os.path.getmtime(glow):
            from PIL import ImageFilter, ImageChops
            g0 = Image.open(glow).convert('RGB')
            bl = g0.filter(ImageFilter.GaussianBlur(10 * g0.width / 2560)).point(lambda v: min(255, int(v * 1.8)))  # raio na escala do render
            ImageChops.lighter(g0, bl).save(gd, quality=85, optimize=True)
        item['luz'] = f'sprites/cenario_{nome}_luz.jpg'
    return item


def pack_titulo():
    """Tela de inicio (tools/blender/titulo.py): fundo em JPG, moldura de folhas em WEBP com alfa e a luz das brasas.
    So entra no meta quando as tres camadas existem (sem a chave o jogo usa o demo da fase 1)."""
    src = os.path.join(RENDER, 'titulo')
    layers = {'fundo': ('titulo_fundo.png', 'titulo_fundo.jpg'), 'frente': ('titulo_frente.png', 'titulo_frente.webp'),
              'luz': ('titulo_luz.png', 'titulo_luz.jpg')}
    if not all(os.path.exists(os.path.join(src, a)) for a, _ in layers.values()):
        return None
    item = {}
    for key, (a, b) in layers.items():
        png, dst = os.path.join(src, a), os.path.join(OUT, b)
        if not os.path.exists(dst) or os.path.getmtime(dst) < os.path.getmtime(png):
            im = Image.open(png)
            if key == 'frente':
                im.convert('RGBA').save(dst, 'WEBP', quality=90, method=6)
            elif key == 'luz':
                from PIL import ImageFilter, ImageChops
                g0 = im.convert('RGB').point(lambda v: max(0, v - 10) * 255 // 245)   # tira o resto de luz fraca (chao, tronco)
                bl = g0.filter(ImageFilter.GaussianBlur(10 * g0.width / 2560)).point(lambda v: min(255, int(v * 1.2)))
                ImageChops.lighter(g0, bl).save(dst, quality=85, optimize=True)
            else:
                im.convert('RGB').save(dst, quality=88, optimize=True, progressive=True)
        item[key] = 'sprites/' + b
    js = os.path.join(src, 'titulo.json')
    if os.path.exists(js):
        item['cam'] = json.load(open(js))
    return item


SKIP_SHIFT = ('slots', 'lanterns', 'points', 'pxk', 'boost', 'fam', 'height', 'ndirs')


def carried(prev, fam):
    """Familia sem render neste projeto: as folhas e os conjuntos dela que ja estavam no meta, com os indices das folhas
    voltando a ser locais (o main soma a base nova, como faz com as familias empacotadas agora)."""
    idx = prev['fams'][fam]
    base = idx[0] if idx else 0

    def unshift(v):
        if isinstance(v, list) and v and isinstance(v[0], list):
            return [unshift(x) for x in v]
        if isinstance(v, list) and len(v) == 7 and all(isinstance(x, (int, float)) for x in v):
            return [v[0] - base] + v[1:]
        return v
    sets = {name: {k: (unshift(v) if k not in SKIP_SHIFT else v) for k, v in s.items()}
            for name, s in prev['sets'].items() if s.get('fam') == fam}
    return {'sheets': [prev['sheets'][i][len('sprites/'):] for i in idx], 'glow': [i - base for i in prev.get('glowSheets', []) if i in idx],
            'sets': sets, 'scale': prev['scale']}


def main():
    fams = sys.argv[1:] or [f for f in ORDER if os.path.exists(os.path.join(RENDER, f, 'meta.json'))]
    prev = prev_meta()
    here = [f for f in ORDER if os.path.exists(os.path.join(RENDER, f, 'meta.json'))]
    every = [f for f in ORDER if f in here or (prev and f in prev.get('fams', {}))]
    sheets, fam_idx, sets, glow = [], {}, {}, []
    scale = None
    report = {}
    for fam in every:
        cache = os.path.join(RENDER, fam, 'pack.json')
        if fam not in here:
            res = carried(prev, fam)
            report[fam] = 'herdada do meta'
        elif fam in fams or not (os.path.exists(cache) and os.path.getmtime(cache) > newest(os.path.join(RENDER, fam))
                                 and all(os.path.exists(os.path.join(OUT, n)) for n in json.load(open(cache))['sheets'])):
            res = pack_family(fam)
            with open(cache, 'w') as fh:
                json.dump({k: v for k, v in res.items() if k != 'raw'}, fh)
            report[fam] = 'empacotada'
        else:
            res = json.load(open(cache))
            report[fam] = 'cache'
        scale = scale or res['scale']
        base = len(sheets)
        sheets += ['sprites/' + n for n in res['sheets']]
        fam_idx[fam] = list(range(base, len(sheets)))
        glow += [base + i for i in res.get('glow', [])]

        def shift(v):
            if isinstance(v, list) and v and isinstance(v[0], list):
                return [shift(x) for x in v]
            if isinstance(v, list) and len(v) == 7 and all(isinstance(x, (int, float)) for x in v):
                return [v[0] + base] + v[1:]
            return v
        for name, s in res['sets'].items():
            sets[name] = {k: (shift(v) if k not in SKIP_SHIFT else v) for k, v in s.items()}
        size = sum(os.path.getsize(os.path.join(OUT, n)) for n in res['sheets'])
        report[fam] += f" ({len(res['sheets'])} folhas, {size / 1e6:.1f} MB)"
    if SUF:
        with open(META_JS, 'w') as fh:
            fh.write('\'use strict\';\n// Gerado por tools/sprites/empacotar.py (CHAPA=R): torres na cor da Chapa Vermelha. Nao editar a mao.\n')
            fh.write('const SPRITE_META_R = ' + json.dumps({'scale': scale, 'sheets': sheets, 'fams': fam_idx, 'glowSheets': glow, 'sets': sets}, separators=(',', ':')) + ';\n')
        print(json.dumps({'chapa': CHAPA, 'familias': report}, ensure_ascii=False))
        return
    cenario = pack_cenario(prev)
    report['cenario'] = f"{sum(1 for c in cenario if c)} fundos"
    # mapa e tela de inicio ainda nao refeitos aqui: ficam os do meta
    keep = lambda k, v: v if v is not None else (prev or {}).get(k)
    with open(META_JS, 'w') as fh:
        fh.write('\'use strict\';\n// Gerado por tools/sprites/empacotar.py a partir dos renders do Blender (tools/blender/). Nao editar a mao.\n')
        fh.write('const SPRITE_META = ' + json.dumps({'scale': scale, 'sheets': sheets, 'fams': fam_idx, 'glowSheets': glow, 'sets': sets, 'cenario': cenario, 'mapa': keep('mapa', pack_mapa()), 'mapa2': keep('mapa2', pack_mapa('mapa2')), 'titulo': keep('titulo', pack_titulo())}, separators=(',', ':')) + ';\n')
    # origem dos projeteis sugerida (DATA.TOWER_TOP): ponto 'top' de cada torre, em unidades do jogo acima do chao
    tops = {k: round(-s['points']['top'][1]) for k, s in sets.items() if 'points' in s and 'top' in s['points']}
    print(json.dumps({'familias': report, 'tower_top': tops, 'alturas': {k: s['height'] for k, s in sets.items() if 'height' in s}}, ensure_ascii=False))


if __name__ == '__main__':
    main()
