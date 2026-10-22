"""Acessorios dos guardioes da mata (tripulacao das torres): coroa de flores, chapeu de palha, capa de folhas e
folhinhas na barra. Tudo se prende aos pivos que o lib.build_person devolve (cabeca e corpo).
"""
import math, random
from mathutils import Vector
from lib import TAU, mat, torus, sphere, lathe, cyl, blob


def flower_crown(root, parts, tag, cols, r=0.076, z=0.052, n=7, leaf=None):
    """Coroa de flores: aro de cipo com folhinhas e flores redondas alternando as cores."""
    head = parts['head']
    hc = Vector((0.006, 0, 0.055))
    leaf = leaf or mat('folha_coroa', '#5e9e3e', rough=0.7, var=0.1, bump=0.05, sheen=0.3)
    ring = torus(root, f'{tag}_coroaAro', (0, 0, 0), r, 0.009, leaf, n=24, segs=5)
    ring.parent = head
    ring.location = hc + Vector((-0.006, 0, z))
    ring.rotation_euler = (0, math.radians(-12), 0)
    for k in range(n):
        a = TAU * k / n + 0.2
        p = hc + Vector((-0.006 + r * math.cos(a) * math.cos(math.radians(12)), r * math.sin(a), z + r * math.cos(a) * math.sin(math.radians(12))))
        f = sphere(root, f'{tag}_coroaFlor{k}', 0.019, (0, 0, 0), scale=(1.0, 1.0, 0.7), m=cols[k % len(cols)], seg=10)
        f.parent = head
        f.location = p
        c = sphere(root, f'{tag}_coroaMiolo{k}', 0.007, (0, 0, 0), m=mat('miolo_flor', '#f6d24a', rough=0.5, var=0.0, bump=0.0), seg=6)
        c.parent = head
        c.location = p + Vector((0.004 * math.cos(a), 0.004 * math.sin(a), 0.011))
        lf = sphere(root, f'{tag}_coroaFolha{k}', 0.016, (0, 0, 0), scale=(1.6, 0.6, 0.35), m=leaf, seg=8, rot=(0, 0, a + 1.2))
        lf.parent = head
        lf.location = hc + Vector((-0.006 + (r + 0.008) * math.cos(a + 0.45), (r + 0.008) * math.sin(a + 0.45), z - 0.004))
    return ring


def straw_hat(root, parts, tag, brim=0.13, band=None):
    """Chapeu de palha de ribeirinho: copa arredondada, aba larga e fita."""
    head = parts['head']
    hc = Vector((0.006, 0, 0.055))
    straw = mat('palha_chapeu', '#e0bf72', rough=0.95, var=0.06, bump=0.45)
    cap = lathe(root, f'{tag}_chapeuCopa', [(0.03, 0.074, 0.074), (0.06, 0.07, 0.07), (0.085, 0.055, 0.055), (0.098, 0.0, 0.0)], straw, segs=18, lv=2, caps=False, solid=0.008)
    cap.parent = head
    cap.location = hc
    aba = cyl(root, f'{tag}_chapeuAba', brim, 0.012, (0, 0, 0), r2=brim * 0.92, m=straw, v=28, bev=0.004)
    aba.parent = head
    aba.location = hc + Vector((0, 0, 0.036))
    fita = torus(root, f'{tag}_chapeuFita', (0, 0, 0), 0.073, 0.009, band or mat('fita_chapeu', '#26a69a', rough=0.7, var=0.0, bump=0.05), n=20, segs=5)
    fita.parent = head
    fita.location = hc + Vector((0, 0, 0.046))
    return cap


def leaf_hem(root, parts, tag, m, z=0.42, r=0.11, n=9, seed=1):
    """Folhinhas pendendo na barra da capa (sobre o mantelete), so atras e dos lados."""
    rr = random.Random(seed)
    body = parts['body']
    for k in range(n):
        a = math.pi * 0.35 + math.pi * 1.3 * k / (n - 1)
        lf = sphere(root, f'{tag}_folhaBarra{k}', 0.03, (0, 0, 0), scale=(0.6, 1.0, 1.7), m=m, seg=8, rot=(0, rr.uniform(-0.2, 0.2), a))
        lf.parent = body
        lf.location = (r * math.cos(a), r * math.sin(a) * 1.1, z + rr.uniform(-0.01, 0.01))
