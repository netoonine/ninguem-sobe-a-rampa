"""Video-resumo das animacoes da Torre de Arqueiros, montado a partir do render do Blender.
Reproduz a mesma logica de js/sprites.js: lote, construcao, arqueiros (parado/mirando/disparo),
upgrades (nivel antigo afunda, novo sobe, brilho), balestra girando e disparando, e a noite com as lanternas.

uso: python3 tools/sprites/previa.py [pasta_render] [saida.mp4]
"""
import json, math, os, subprocess, sys, tempfile
from PIL import Image, ImageChops, ImageDraw

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'arte', 'render', 'arqueiros')
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, 'arte', 'previa-arqueiros.mp4')
meta = json.load(open(os.path.join(SRC, 'meta.json')))
SC = meta['px_per_game']
W, H = 560, 430
AX, AY = 280, 330         # ancora da torre na tela (px)
FPS = 30
CREW = {'n1': ['a1', 'a1'], 'n2': ['a2', 'a2'], 'n3': ['a3', 'a3b']}
_cache = {}


def clean_shadow(im, haze=16, edge=24):
    """Mesma limpeza do empacotador: tira a nevoa da sombra do chao e esmaece nas bordas."""
    w, h = im.size
    px = im.load()
    for y in range(h):
        ey = min(y, h - 1 - y)
        for x in range(w):
            R, G, B, A = px[x, y]
            if A == 0 or max(R, G, B) > 6 or A > 200:
                continue
            a = max(0, A - haze) * 255 // (255 - haze) * 4 // 5
            e = min(ey, x, w - 1 - x)
            if e < edge:
                a = a * e // edge
            px[x, y] = (0, 0, 0, a)
    return im


def img(set_, name):
    k = (set_, name)
    if k not in _cache:
        im = Image.open(os.path.join(SRC, set_, name)).convert('RGBA')
        _cache[k] = im if name == 'glow.png' else clean_shadow(im)
    return _cache[k]


def anchor(set_):
    return meta['sets'][set_]['anchor']


def paste(canvas, im, set_, x, y, flip=False, k=1.0, alpha=1.0, sy=1.0, add=False):
    """Desenha o quadro com a ancora do conjunto em (x, y) pixels da tela."""
    ax, ay = anchor(set_)
    if flip:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
        ax = im.size[0] - ax
    if k != 1.0 or sy != 1.0:
        nw, nh = max(1, int(im.size[0] * k)), max(1, int(im.size[1] * k * sy))
        im = im.resize((nw, nh), Image.LANCZOS)
        ax, ay = ax * k, ay * k * sy
    if alpha < 1.0:
        a = im.split()[3].point(lambda v: int(v * alpha))
        im = im.copy()
        im.putalpha(a)
    ox, oy = int(round(x - ax)), int(round(y - ay))
    im = im.crop((max(0, -ox), max(0, -oy), im.size[0], im.size[1]))
    ox, oy = max(0, ox), max(0, oy)
    if add:
        layer = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
        layer.alpha_composite(im, (ox, oy))
        rgb = ImageChops.multiply(layer.convert('RGB'), Image.merge('RGB', [layer.split()[3]] * 3))
        base = canvas.convert('RGB')
        canvas.paste(ImageChops.add(base, rgb), (0, 0))
        return
    canvas.alpha_composite(im, (ox, oy))


def background():
    bg = Image.new('RGBA', (W, H), (224, 191, 132, 255))
    d = ImageDraw.Draw(bg)
    # caminho dos inimigos
    d.ellipse((-200, 372, W + 200, 640), fill=(207, 165, 110, 255))
    d.ellipse((-200, 388, W + 200, 624), fill=(220, 183, 132, 255))
    for i in range(40):
        x = (i * 173) % W
        y = 40 + (i * 97) % 380
        d.ellipse((x, y, x + 6, y + 3), fill=(205, 170, 118, 255))
    return bg


BG = background()


def ease_back(x, k=1.7):
    x -= 1
    return 1 + (k + 1) * x ** 3 + k * x ** 2


def target_pos(t):
    return W / 2 + 230 * math.sin(t * 0.55), 418


def draw_target(canvas, x, y):
    d = ImageDraw.Draw(canvas)
    d.ellipse((x - 22, y - 6, x + 22, y + 8), fill=(120, 90, 60, 120))
    d.ellipse((x - 12, y - 40, x + 12, y - 4), fill=(150, 60, 50, 255), outline=(60, 30, 20, 255), width=3)
    d.ellipse((x - 9, y - 58, x + 9, y - 40), fill=(170, 80, 60, 255), outline=(60, 30, 20, 255), width=3)


def sparkle(canvas, age, n, seed):
    if age < 0 or age > 1.1:
        return
    d = ImageDraw.Draw(canvas)
    for i in range(n):
        h1 = (math.sin((seed + i) * 127.1) * 43758.5) % 1
        h2 = (math.sin((seed + i * 7.3) * 127.1) * 43758.5) % 1
        h3 = (math.sin((seed + i * 3.1) * 127.1) * 43758.5) % 1
        a = age - h3 * 0.3
        if a < 0 or a > 0.8:
            continue
        x = AX + (h1 - 0.5) * 60 * SC
        y = AY + (-8 - h2 * 40 - a * 55) * SC
        r = (1 - a / 0.8) * (2 + h3 * 2.5) * SC
        col = (255, 224, 138, int(255 * (1 - a / 0.8)))
        d.polygon([(x, y - r * 2), (x + r * 0.5, y - r * 0.5), (x + r * 2, y), (x + r * 0.5, y + r * 0.5),
                   (x, y + r * 2), (x - r * 0.5, y + r * 0.5), (x - r * 2, y), (x - r * 0.5, y - r * 0.5)], fill=col)


def tower_frame(key, t, st, night=False):
    """Uma tela: torre key no tempo t. st guarda tiros e construcao."""
    cv = BG.copy()
    tx, ty = target_pos(t)
    draw_target(cv, tx, ty)
    S = meta['sets'][key]
    bt = t - st['built']
    BUILD_T, UP = 0.6, (0.1 if st.get('prev') else 0.0)
    if key == 'lote':
        paste(cv, img('lote', f'loop_{int(t * 12) % 24:02d}.png'), 'lote', AX, AY)
        return cv
    if st.get('prev') and bt < 0.2:
        e = bt / 0.2
        paste(cv, img(st['prev'], 'loop_00.png'), st['prev'], AX, AY, k=1 + 0.12 * e, sy=(1 - 0.75 * e * e) / (1 + 0.12 * e), alpha=1 - e)
    p = (bt - UP) / BUILD_T
    if p < 1:
        if p >= 0:
            paste(cv, img(key, f'build_{min(11, int(p * 12)):02d}.png'), key, AX, AY)
        sparkle(cv, bt / 0.9, 16 if st.get('prev') else 10, 3)
        return cv
    paste(cv, img(key, f'loop_{int(t * 12) % 24:02d}.png'), key, AX, AY)
    since = t - st['shotT']
    if key == 'n4':
        B = meta['sets']['bal']
        sl = S['slots'][0]
        px, py = AX + (sl[0] - S['anchor'][0]), AY + (sl[1] - S['anchor'][1])
        ax = (tx - AX) / SC
        ay = ((ty - AY) / SC) / 0.72
        yaw = math.atan2(-ay, ax)
        dd = int(round(yaw / (2 * math.pi) * 16)) % 16
        f = min(7, int(since / 1.0 * 8)) if 0 <= since < 1.0 else 7
        paste(cv, img('bal', f'd{dd:02d}_{f:02d}.png'), 'bal', px, py)
    else:
        for i, sl in enumerate(S['slots']):
            v = CREW[key][i]
            pop = min(1.0, max(0.0, (bt - BUILD_T - i * 0.07) / 0.24))
            if pop <= 0:
                continue
            px, py = AX + (sl[0] - S['anchor'][0]), AY + (sl[1] - S['anchor'][1])
            flip = tx < px
            if st['who'] == i and 0 <= since < 0.42:
                fr = f'shoot_{min(7, int(since / 0.42 * 8)):02d}.png'
            elif since < 1.5:
                fr = f'aim_{int(t * 5 + i * 2) % 4:02d}.png'
            else:
                fr = f'idle_{int(t * 8 + i * 5) % 12:02d}.png'
            paste(cv, img(v, fr), v, px, py, flip=flip, k=ease_back(pop) if pop < 1 else 1.0)
    paste(cv, img(key, 'front.png'), key, AX, AY)
    fl = (bt - BUILD_T - UP) / 0.3
    if 0 <= fl < 1:
        paste(cv, img(key, f'loop_{int(t * 12) % 24:02d}.png'), key, AX, AY, alpha=0.45 * (1 - fl), add=True)
    if bt < 1.2:
        sparkle(cv, bt / 0.9, 16 if st.get('prev') else 10, 3)
    if night:
        dark = Image.new('RGB', (W, H), (70, 84, 140))
        rgb = ImageChops.multiply(cv.convert('RGB'), dark)
        cv = rgb.convert('RGBA')
        g = img(key, 'glow.png')
        paste(cv, g, key, AX, AY, add=True)
        paste(cv, g, key, AX, AY, add=True, alpha=0.6)
    return cv


def arrow(cv, t, st, key):
    """Flecha voando do arqueiro ate o alvo (so para a previa)."""
    since = t - st['shotT']
    if key in ('lote', 'n4') or not (0 <= since < 0.35):
        return
    S = meta['sets'][key]
    sl = S['slots'][st['who']]
    x0, y0 = AX + (sl[0] - S['anchor'][0]), AY + (sl[1] - S['anchor'][1]) - 32
    tx, ty = target_pos(t)
    k = since / 0.35
    x = x0 + (tx - x0) * k
    y = y0 + (ty - 30 - y0) * k - math.sin(math.pi * k) * 80
    # direcao do voo (derivada da parabola) e a flecha do Blender girada
    k2 = min(1.0, k + 0.02)
    x2 = x0 + (tx - x0) * k2
    y2 = y0 + (ty - 30 - y0) * k2 - math.sin(math.pi * k2) * 80
    ang = math.degrees(math.atan2(y2 - y, x2 - x))
    fl = img('flecha', 'still.png')
    fl = fl.resize((fl.size[0] // 2, fl.size[1] // 2), Image.LANCZOS).rotate(-ang, expand=True, resample=Image.BICUBIC)
    cv.alpha_composite(fl, (int(x - fl.size[0] / 2), int(y - fl.size[1] / 2)))


# roteiro: (duracao, chave, combate?, noite?, cadencia)
STORY = [(1.2, 'lote', False, False, 0), (2.4, 'n1', False, False, 0), (3.2, 'n1', True, False, 0.8),
         (3.4, 'n2', True, False, 0.68), (3.4, 'n3', True, False, 0.58), (4.6, 'n4', True, False, 1.55),
         (3.4, 'n3', True, True, 0.58)]
tmp = tempfile.mkdtemp()
n = 0
t = 0.0
st = {'built': 0.0, 'shotT': -99, 'who': 0, 'prev': None, 'next': 99}
last = None
for dur, key, combat, night, rate in STORY:
    if key != last:
        st['prev'] = last if last not in (None, 'lote') and not night else None
        st['built'] = t if not night else t - 5
        st['next'] = t + (1.0 if last else 0) + 0.8
        last = key
    end = t + dur
    while t < end:
        if combat and t >= st['next']:
            st['shotT'] = t
            st['who'] = (st['who'] + 1) % 2
            st['next'] = t + rate
        cv = tower_frame(key, t, st, night)
        arrow(cv, t, st, key)
        cv.convert('RGB').save(os.path.join(tmp, f'{n:05d}.png'))
        n += 1
        t += 1 / FPS
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', os.path.join(tmp, '%05d.png'),
                '-vf', 'scale=1120:860:flags=lanczos', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', OUT], check=True)
print('OK', OUT, n, 'quadros')
