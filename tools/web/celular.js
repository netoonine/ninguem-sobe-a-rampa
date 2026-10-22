'use strict';
// Versao do celular (tools/web/montar_celular.py): as folhas vem com metade do lado. Este arquivo roda antes do jogo e
// faz o drawImage aceitar as coordenadas das folhas originais (as dos _meta), entao o resto do codigo nao muda.

(() => {
  const ORIG = window.MOB_ORIG || {};   // nome do arquivo reduzido -> [largura, altura] da folha original
  const proto = CanvasRenderingContext2D.prototype;
  const raw = proto.drawImage;

  // [kx, ky] = px da folha reduzida por px da original; null = imagem que nao foi reduzida
  const of = im => {
    if (im._sk !== undefined) return im._sk;
    if (typeof HTMLImageElement === 'undefined' || !(im instanceof HTMLImageElement)) return (im._sk = null);
    if (!im.complete || !im.naturalWidth) return null;   // ainda carregando: decide no proximo quadro
    const src = im.currentSrc || im.src || '';
    let nome = src.slice(src.lastIndexOf('/') + 1).split(/[?#]/)[0];
    try { nome = decodeURIComponent(nome); } catch (e) { /* nome sem escapes */ }
    const o = ORIG[nome];
    return (im._sk = o ? [im.naturalWidth / o[0], im.naturalHeight / o[1]] : null);
  };
  window.MOBK = { of };

  proto.drawImage = function (im, a, b, c, d, e, f, g, h) {
    const k = im && of(im);
    if (!k) return raw.apply(this, arguments);
    const n = arguments.length;
    const iw = im.naturalWidth || im.width, ih = im.naturalHeight || im.height;
    // (im, x, y): no tamanho da folha original
    if (n === 3) return raw.call(this, im, a, b, iw / k[0], ih / k[1]);
    if (n !== 9) return raw.apply(this, arguments);
    // recorte em px da original -> px da reduzida; corta o que passar da borda (o WebKit antigo nao desenha nada)
    let sx = a * k[0], sy = b * k[1], sw = c * k[0], sh = d * k[1];
    if (sx + sw > iw) { const nw = Math.max(0, iw - sx); g *= nw / sw; sw = nw; }
    if (sy + sh > ih) { const nh = Math.max(0, ih - sy); h *= nh / sh; sh = nh; }
    if (sw <= 0 || sh <= 0) return;
    return raw.call(this, im, sx, sy, sw, sh, e, f, g, h);
  };
})();
