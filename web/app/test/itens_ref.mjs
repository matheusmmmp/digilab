// Pets de referencia e partidas da medicao dos itens (test/medir_itens.mjs): os pets e as sementes da parte 2
// (test/calibrar_arenas.mjs e test/calibrar_escala_v6.mjs), com os itens pelo motor (motor/itens.ts). Sem estado: cada funcao recebe
// a tarefa inteira (roda nos workers da medicao e nos scripts de exploracao).
//
// Pets v9 (rodada de equilibrio geral, fase 3; docs/EQUILIBRIO_GERAL.md): as funcoes recebem a versao. `R` (CV21D) e a versao 6 sao o
// padrao, a medicao de antes (pets v6: regras V21D, CESC_V6, os fatores de ARENAS); com `v6: false` na tarefa (ou R9 e a versao 9 nas
// funcoes), os pets v9: regras V21E (CV21E; as listas V21E nas formas de referencia), a escala da versao 9 (CESC_V9, a mesma vida e o
// mesmo beta) e os fatores dos lideres dos v9 (arenas.arenaDaLuta com a versao 9, FATOR_LIDER_V9).
import * as M from "../motor/index.ts";

const { ADOL_V21, ARENAS, CIT, CRIANCA_V21, CV, CV21D, CV21E, ESPECIES, FORMAS_AD, LINHAS, LINHA_DA_FORMA, LUGARES_V6, STATS } = M;
/** as regras das lutas dos pets v6 (a medicao de antes) e dos pets v9 */
export const R = CV21D, R9 = CV21E;
/** as regras e a versao do pet da medicao: v6 (V21D, versao 6) ou v9 (V21E, versao 9) */
export const regrasRef = v6 => v6 ? R : R9;
export const versaoRef = v6 => v6 ? M.VERSAO_ESCALA_V6 : M.VERSAO_ESCALA_V9;
export const N_LIDER = 10, N_ESTAGIO = 10, N_MATRIZ = 100;
const TIPICO = CIT.tipico;
/** a parte do treino tipico que ja encheu os estagios de antes (o tipico enche cada estagio ate o teto) */
const ANTERIOR = { crianca: 0, adolescente: M.CTR.tetoEstagio.crianca, adulto: M.CTR.tetoEstagio.crianca + M.CTR.tetoEstagio.adolescente,
  mega: M.CTR.tetoVida };

const primeiraForma = l => FORMAS_AD.find(f => LINHA_DA_FORMA[f] === l);
export function formasDe(est, Rr = R) {
  if (est === "crianca") return ["sereno", "arisco"].map(r => [r, e => ({ esp: e, est, ramo: r }), null, CRIANCA_V21[r]]);
  if (est === "adolescente") return LINHAS.map(l => [l, e => ({ esp: e, est, ramo: "sereno", linha: l }), M.caraterCanonico(primeiraForma(l)), ADOL_V21[l]]);
  return FORMAS_AD.map(f => [f, e => ({ esp: e, est, ramo: "sereno", linha: LINHA_DA_FORMA[f], adulta: f }), M.caraterCanonico(f), M.gambitsAdulto(f, Rr)]);
}
/** o lutador de referencia com os itens: `nivel` = treino uniforme (o tipico, ou 0); `pontosEst` = a parte do treino no estagio
    atual (o tipico enche os estagios de antes ate o teto); os chips pelo motor (itens.ts); escala: campanha e arenas (perfil
    absoluto na escala da versao: v6 ou v9) ou arena sem escala (a matriz). A carta fica fora: vai para jogarArena/jogarV2.
    `trava`: nos pets v9 os itens so fazem efeito com o treino minimo (itens.itensValem, como no motor); sem ela (a matriz de M-D3), o
    efeito do item em si, sem a trava. `vi`: a versao dos itens (a do pet; 6 = os itens de antes, para comparar nas regras dos v9) */
export function lutador([nome, forma, car, g], esp, nivel, chips0, escala, versao = M.VERSAO_ESCALA_V6, trava = true, vi = versao) {
  const f = forma(esp), est = f.est, tr = Object.fromEntries(STATS.map(k => [k, nivel / STATS.length]));
  const chips = trava && !M.itensValem(vi, est, nivel) ? [] : chips0;
  const pontos = M.pontosComChips(chips, est, tr, Math.max(0, nivel - ANTERIOR[est]), nivel > 0, vi);
  const cond = escala ? M.perfilDe(f, car, 1, pontos, true, versao) : M.perfilDe(f, car, 1, pontos);
  return { nome: `${nome}+${nivel}@${esp}`, estilo: { nome, gambits: M.copiarGambits(M.listaComChips(g, chips, M.capacidadeLista(est), vi)), eps: CV.eps }, cond };
}
/** o efeito da carta na luta (null: sem carta; nos pets v9, tambem sem o treino minimo) */
const efeitoDe = (carta, versao, est, nivel) => carta && M.itensValem(versao, est, nivel) ? M.cartaDe(carta).carta : null;

/* ------------------------------------------------ o trabalho de cada tarefa (roda nos workers)
   t.v6: a medicao de antes (pets v6); sem ele (false), os pets v9. A arena da luta: a de ARENAS nos v6 e a dos pets v9
   (arenas.arenaDaLuta com a versao 9: a mesma regra, lista e lutas, o fator de FATOR_LIDER_V9) */
const v6De = t => t.v6 !== false;
export function taxaLider(t) {
  M.ligarEscala(true);
  const v6 = v6De(t), Rr = regrasRef(v6), versao = versaoRef(v6), vi = t.itensV6 ? M.VERSAO_ESCALA_V6 : versao;
  const a0 = ARENAS.find(x => x.id === t.arena), a = v6 ? a0 : M.arenaDaLuta(a0.lider, versao);
  const est = LUGARES_V6[a.lugar].est, fo = formasDe(est, Rr)[t.forma], B = M.lutadorBot(a.lider, Rr, a);
  const ef = efeitoDe(t.carta, vi, est, t.nivel), lutas = a.lutas ?? 1;
  let soma = 0, tot = 0;
  for (const e of ESPECIES) {
    const A = lutador(fo, e, t.nivel, t.chips, true, versao, true, vi);
    for (const s of t.sementes) for (let k = 0; k < N_LIDER; k++) {
      const serie = M.jogarArena(A, B, M.hashSemente("calib-arena", s, A.nome, B.nome, k), Rr, lutas, 1, ef);
      soma += serie.length === lutas ? serie[serie.length - 1].pontosA : 0; tot++;
    }
  }
  return soma / tot;
}
export function taxaEstagio(t) {
  M.ligarEscala(true);
  const v6 = v6De(t), R = regrasRef(v6), versao = versaoRef(v6), vi = t.itensV6 ? M.VERSAO_ESCALA_V6 : versao;
  const fb = formasDe(t.baixo, R)[t.forma], ef = efeitoDe(t.carta, vi, t.baixo, TIPICO[t.baixo]), cura = ef?.cura ?? null;
  let pontos = 0, vit = 0, tot = 0;
  for (const fa of formasDe(t.alto, R)) for (const eb of ESPECIES) for (const ea of ESPECIES) {
    const A0 = lutador(fb, eb, TIPICO[t.baixo], t.chips, true, versao, true, vi), A = M.comCarta(A0, ef), B = lutador(fa, ea, 0, [], true, versao);
    /* os nomes das sementes sao os de calibrar_escala_v6 (sem o item): numeros aleatorios comuns com a parte 2 */
    for (const s of t.sementes) for (let k = 0; k < N_ESTAGIO; k++) {
      const sp = M.hashSemente("escala-v6", s, A0.nome, B.nome, k);
      const p = k < N_ESTAGIO / 2 ? M.jogarV2(A, B, sp, R, null, 1, cura ? [cura, null] : null).pontosA
        : 1 - M.jogarV2(B, A, sp, R, null, 0, cura ? [null, cura] : null).pontosA;
      pontos += p; tot++; if (p === 1) vit++;
    }
  }
  return { pontos: pontos / tot, vitorias: vit / tot, partidas: tot };
}
/** forca da forma medida (com os itens) contra as outras 7 sem item; desafiado: null (fracao de vida) ou a regra do jogo */
export function forcaMatriz(t) {
  M.ligarEscala(false);
  const v6 = v6De(t), R = regrasRef(v6), versao = versaoRef(v6), vi = t.itensV6 ? M.VERSAO_ESCALA_V6 : versao;
  const fs = formasDe("adulto", R), fx = fs[t.forma], ef = t.carta ? M.cartaDe(t.carta).carta : null, cura = ef?.cura ?? null;
  let soma = 0, tot = 0;
  const porRival = {};
  for (const fy of fs) {
    if (fy === fx) continue;
    let sr = 0, tr = 0;
    for (const e of ESPECIES) {
      const X0 = lutador(fx, e, t.nivel ?? 0, t.chips, false, versao, false, vi), X = M.comCarta(X0, ef), Y = lutador(fy, e, t.nivel ?? 0, [], false, versao);
      for (const s of t.sementes) for (let k = 0; k < N_MATRIZ; k++) {
        const sp = M.hashSemente("itens-matriz", s, fx[0], fy[0], e, k);
        const p = k < N_MATRIZ / 2 ? M.jogarV2(X, Y, sp, R, null, t.desafiado ? 1 : null, cura ? [cura, null] : null).pontosA
          : 1 - M.jogarV2(Y, X, sp, R, null, t.desafiado ? 0 : null, cura ? [null, cura] : null).pontosA;
        sr += p; tr++;
      }
    }
    porRival[fy[0]] = +(sr / tr).toFixed(4); soma += sr; tot += tr;
  }
  return { forca: soma / tot, por_rival: porRival };
}
export const TRABALHOS = { lider: taxaLider, estagio: taxaEstagio, matriz: forcaMatriz };
