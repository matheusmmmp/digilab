/* A textura do pet de agora para as cenas 3D da tela Pet (a sala de cena3d.ts e a ilha de ilha/): o quadro do atlas do jogo, ou a grade
   de reserva sem ele (os e2e e as capturas). Respeita o que o sprite de sempre respeita: o ovo ao nascer, a forma sombria e o olho
   fechado ao dormir (na reserva; no atlas, o quadro parado). A chave diz quando a textura muda. Saiu de cena3d.ts sem mudar. */
import { OVO, chaveSprite, corDominante } from "../../../motor/index.ts";
import { atlasAtual, desenharSprite, dimSprite, quadroAgora } from "../../atlas.ts";
import { S, gradeDe, paleta } from "../../grades.ts";
import { jogoAtual } from "../../jogo.ts";

/** a textura do pet de agora: o quadro do atlas (local) ou a grade de reserva; a chave diz quando trocar */
export function fonteDoPet(quadro: number): { chave: string; canvas: HTMLCanvasElement } {
  const { motor: m, nascendo } = jogoAtual(), a = atlasAtual(), c = document.createElement("canvas"), g = c.getContext("2d");
  if (!g) throw new Error("canvas 2d indisponível");
  if (a.tipo === "ok") {
    const nome = nascendo > 0 ? OVO[m.especie] : chaveSprite(m.forma), [w, h] = dimSprite(a.dados, nome);
    const iq = nascendo > 0 ? 0 : quadroAgora(a, nome, m.acao === "dormir");
    /* o quadro do atlas na caixa fixa do idle, em 1x, com 1 px de folga para o contorno da forma sombria */
    c.width = w + 2; c.height = h + 2;
    desenharSprite(g, a, nome, 1, 1, 1, iq, { sombria: m.sombria });
    return { chave: `${nome}:${iq}:${m.sombria ? 1 : 0}`, canvas: c };
  }
  const grade = nascendo > 0 ? S.ovo : S[gradeDe(m.estagioAtual)], pal = paleta(corDominante(m.tracos));
  const fechado = m.acao === "dormir" || quadro % 17 === 0;
  c.width = Math.max(...grade.map(l => l.length)); c.height = grade.length;
  grade.forEach((l, y) => [...l].forEach((ch, x) => {
    if (ch === ".") return;
    g.fillStyle = pal[fechado && ch === "w" ? "b" : ch] || "#FF00FF"; g.fillRect(x, y, 1, 1);
  }));
  return { chave: `reserva:${nascendo > 0 ? "ovo" : m.estagioAtual}:${fechado ? 1 : 0}`, canvas: c };
}
