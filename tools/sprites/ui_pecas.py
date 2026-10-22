"""Recorta as pecas da interface pintada (geradas no KIE sobre magenta) em PNG com transparencia para sprites/ui/.

uso: python3 tools/sprites/ui_pecas.py
Entrada: arte/conceitos/ui_pecas/<peca>/*.png (a ultima de cada pasta). Tira o magenta e a franja rosada
(desmistura contra o magenta), descarta o "fantasma" da folha de referencia que as vezes aparece no topo e separa as
pecas de uma mesma imagem (3 botoes, 2 estrelas) da esquerda para a direita.
"""
import glob, os
import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
SRC = os.path.join(ROOT, 'arte', 'conceitos', 'ui_pecas')
OUT = os.path.join(ROOT, 'sprites', 'ui')
BG = np.array([255.0, 0.0, 255.0])

# peca: (nomes de saida da esquerda para a direita, largura final em px)
PECAS = {
    'painel': (['painel'], 1200),
    'botoes': (['botao_verde', 'botao_vermelho', 'botao_dourado'], 256),
    'pilula': (['pilula'], 900),
    'estrelas': (['estrela', 'estrela_vazia'], 300),
    'barra': (['barra'], 1100),
    'medalhao': (['medalhao'], 320),
    'logo': (['logo'], 1100),
    'prancha': (['prancha'], 1100),
}

# variacoes de cor: so o miolo brilhante muda (madeira, folhas e flores ficam); (matiz 0-1 ou None, mult. saturacao, mult. valor)
CORES = {'dourada': (0.12, 1.25, 1.22), 'vermelha': (0.015, 0.95, 1.0), 'teal': (0.47, 0.85, 0.92),
         'creme': (0.1, 0.22, 1.08), 'cinza': (None, 0.08, 0.92)}


def recolor(nome, miolo, saida):
    """miolo(H, W) -> mascara da regiao do centro a recolorir (so pixels verdes brilhantes dentro dela mudam)."""
    im = Image.open(os.path.join(OUT, nome + '.png')).convert('RGBA')
    a = np.asarray(im).astype(np.float32) / 255
    H, W = a.shape[:2]
    hsv = np.asarray(im.convert('RGB').convert('HSV')).astype(np.float32) / 255
    verde = (hsv[..., 0] > 0.17) & (hsv[..., 0] < 0.45) & (hsv[..., 1] > 0.2) & (a[..., 3] > 0.5)
    # o miolo e o pedaco verde ligado ao centro da peca (cobre a borda escura da capsula e para no concreto; as fitas
    # verdes dos cantos ficam de fora quando nao encostam nele)
    lab, _ = ndimage.label(verde & miolo(H, W))
    cy, cx = H // 2, W // 2
    alvo = lab[cy, cx] or np.bincount(lab[H // 3: 2 * H // 3, W // 3: 2 * W // 3].ravel())[1:].argmax() + 1
    m = ndimage.binary_fill_holes(ndimage.binary_closing(lab == alvo, iterations=2))
    for cor, (h, ks, kv) in CORES.items():
        out = hsv.copy()
        if h is not None:
            out[..., 0] = np.where(m, h, out[..., 0])
        out[..., 1] = np.where(m, np.clip(out[..., 1] * ks, 0, 1), out[..., 1])
        out[..., 2] = np.where(m, np.clip(out[..., 2] * kv, 0, 1), out[..., 2])
        rgb = Image.fromarray((out * 255).astype(np.uint8), 'HSV').convert('RGB')
        o = rgb.convert('RGBA')
        o.putalpha(im.getchannel('A'))
        o.save(os.path.join(OUT, saida.format(cor) + '.png'))
        print(saida.format(cor), o.size)


# linhas do topo a descartar (o KIE as vezes repete a faixa de HUD da folha de referencia, apagada, no alto)
TOPO = {}


def recorta(path):
    a = np.asarray(Image.open(path).convert('RGB')).astype(np.float32)
    d = np.linalg.norm(a - BG, axis=-1)
    alfa = np.clip((d - 70) / (190 - 70), 0, 1)
    # sombra do objeto no fundo magenta (roxo escuro): tambem e fundo
    hsv = np.asarray(Image.fromarray(a.astype(np.uint8)).convert('HSV')).astype(np.float32) / 255
    roxo = (hsv[..., 0] > 0.76) & (hsv[..., 0] < 0.92) & (hsv[..., 1] > 0.45)
    alfa = np.where(roxo, 0, alfa)
    # desmistura a cor da borda contra o magenta (sem franja rosada)
    am = np.maximum(alfa, 1e-3)[..., None]
    cor = np.clip((a - (1 - alfa[..., None]) * BG) / am, 0, 255)
    rgba = np.dstack([cor, alfa * 255]).astype(np.uint8)
    return rgba, alfa > 0.5


def componentes(mask, n):
    lab, k = ndimage.label(mask)
    if not k:
        return []
    H = mask.shape[0]
    objs = ndimage.find_objects(lab)
    sizes = ndimage.sum(mask, lab, range(1, k + 1))
    cand = []
    for i, (sl, sz) in enumerate(zip(objs, sizes)):
        if sz < mask.size * 0.004:
            continue
        cand.append((sz, i + 1, sl))
    cand.sort(reverse=True)
    principais = sorted(cand[:n], key=lambda c: c[2][1].start)
    return lab, principais, cand


def main():
    os.makedirs(OUT, exist_ok=True)
    for peca, (nomes, largura) in PECAS.items():
        f = sorted(glob.glob(os.path.join(SRC, peca, '*.png')))[-1]
        rgba, mask = recorta(f)
        # fantasma da folha de referencia colado no topo (sempre na mesma faixa): corte fixo por peca
        topo = TOPO.get(peca, 0)
        if topo:
            mask[:topo] = False
            rgba[:topo, :, 3] = 0
        # junta folhas e flores soltas ao objeto mais proximo (dilata antes de separar)
        grosso = ndimage.binary_dilation(mask, iterations=12)
        if peca == 'estrelas':
            # as folhas grudam as duas estrelas: corta na coluna mais vazia do terco do meio
            W = mask.shape[1]
            col = mask[int(mask.shape[0] * 0.24):].sum(0)
            cut = W // 3 + int(np.argmin(col[W // 3: 2 * W // 3]))
            grosso[:, cut] = False
        lab, principais, cand = componentes(grosso, len(nomes))
        for nome, (_, idx, sl) in zip(nomes, principais):
            sub = rgba[sl].copy()
            sub[..., 3] = np.where(lab[sl] == idx, sub[..., 3], 0)
            im = Image.fromarray(sub)
            bb = im.getbbox()
            im = im.crop(bb)
            k = largura / im.width
            im = im.resize((largura, max(1, round(im.height * k))), Image.LANCZOS)
            im.save(os.path.join(OUT, nome + '.png'))
            print(nome, im.size)
    # pilula: miolo = retangulo interno da moldura de madeira; botao redondo: disco central
    recolor('pilula', lambda H, W: _ret(H, W, 0.05, 0.95, 0.15, 0.88), 'pilula_{}')
    recolor('botao_verde', lambda H, W: _disco(H, W, 0.5, 0.505, 0.36), 'botao_{}')


def _ret(H, W, x0, x1, y0, y1):
    m = np.zeros((H, W), bool)
    m[int(H * y0):int(H * y1), int(W * x0):int(W * x1)] = True
    return m


def _disco(H, W, cx, cy, r):
    yy, xx = np.mgrid[0:H, 0:W]
    return (xx - W * cx) ** 2 + (yy - H * cy) ** 2 < (W * r) ** 2


if __name__ == '__main__':
    main()
