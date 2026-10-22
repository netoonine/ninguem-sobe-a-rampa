'use strict';
// Provisorio enquanto os cenarios de Brasilia nao saem do Blender: os 12 fundos da mata, na ordem das 5 fases.
// Some sozinho quando o empacotador gravar os fundos novos (5 entradas em SPRITE_META.cenario).
if (typeof SPRITE_META !== 'undefined' && SPRITE_META.cenario && SPRITE_META.cenario.length === 12) {
  SPRITE_META.cenario = [0, 1, 3, 5, 11].map(i => SPRITE_META.cenario[i]);
}
