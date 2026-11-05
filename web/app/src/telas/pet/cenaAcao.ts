/* A cena de cada acao do pet e a reacao ao toque (docs/registro/2026-11.md, a seção "VIDA DO PET, a cena e o toque", o passo 2 da "Vida do pet"). SO VISTA: le a acao que o
   motor registrou (Motor.acao), a sujeira e, no toque, o corpo; nao escreve no motor, no log nem no save, e o replay e a paridade nao a veem.
   A regra (docs/futuro/vida_do_pet_referencias.md, 5.1): a cena desenha o verbo que o motor registrou e nada alem. Por isso:
     - comer: mastiga (o corpo achata e estica) e solta migalhas, com a carne sobre a cabeca;
     - brincar: pulinhos, com a nota; chamar_atencao: pulinhos mais curtos e rapidos, com o ponto de exclamacao;
     - explorar: balanca de um lado ao outro, olhando em volta, com o emote de surpresa; emburrar: treme de leve e encolhe, com a raiva;
     - dormir: o sono de sono.ts (achatado, respirando, o "zz"); ocioso: nada alem dos passinhos do Seguidor (vistaMundo.ts), porque e a
       acao que mais tenta a inventar vida na tela;
     - cocô: quando a sujeira do motor SOBE, o pet se agacha e treme por COCO_MS, com a gota do esforco (a vista so ve a sujeira subir).
   O toque no pet e o `acariciar` que ja existe (acoes.ts, o mesmo evento do botao); a reacao sai do que o corpo calculou: a queda da solidao
   e do estresse (relaxou) e o fator do medo da mao que o corpo aplicou, (C - medo_da_mao q_susto) / C (corpo.ts, carinho). Os tempos, as alturas
   e as contagens daqui sao da vista: PROPOSTO, SEM FONTE; nao mudam a vida. Sem DOM nas contas (testadas em node); o desenho recebe o contexto. */
import { S, desenharGrade, type Paleta } from "../../grades.ts";

/** o gesto do corpo do pet sobre o desenho: `frente` e `alto` em texels do sprite (frente = o lado para onde ele olha; negativo = recua), `estica` a
    fracao da altura (1 = sem mudanca; o pe fica no chao, e a largura cresce o que a altura perde) */
export interface Gesto { frente: number; alto: number; estica: number }
export const SEM_GESTO: Gesto = { frente: 0, alto: 0, estica: 1 };

/** os numeros da cena (PROPOSTO, SEM FONTE): periodos em ms, alturas e deslocamentos em texels */
export const CENA_ACAO = {
  comerMs: 420, comerEstica: 0.07,
  brincarMs: 560, brincarAlto: 5,
  chamarMs: 380, chamarAlto: 3,
  explorarMs: 2400, explorarFrente: 3,
  emburrarMs: 70, emburrarFrente: 1, emburrarEstica: 0.95,
  cocoMs: 1800, cocoEstica: 0.88, cocoTremorMs: 90, cocoTremor: 1,
  /** a reacao ao toque: quanto dura, o pulinho de quem relaxou e o recuo de quem teme a mao, em texels */
  reacaoMs: 1600, reacaoAlto: 4, reacaoRecuo: 4, reacaoPulinhoMs: 600, reacaoRecuoMs: 500,
  /** as migalhas do comer: quantas, o ciclo de queda (ms) e a queda (px de CSS) */
  migalhas: 3, migalhaMs: 700, migalhaQueda: 14,
  /** os coracoes da reacao: o ciclo de subida (ms) e a subida (px de CSS) */
  coracaoMs: 1100, coracaoSobe: 34,
} as const;

/** o emote de cada acao do motor (a chave do atlas ou da grade); null onde a cena nao inventa: o dormir tem o "zz" do sono.ts e o ocioso nada */
export const EMOTE_DA_ACAO: Readonly<Record<string, string | null>> = {
  ocioso: null, dormir: null, comer: "carne", brincar: "nota", chamar_atencao: "exclam", explorar: "surpreso", emburrar: "raiva",
};

/** o emote do atlas de cada icone (o UP tem estes; os outros, a grade de grades.ts) e, sem atlas, a grade que faz as vezes do emote que ela nao tem */
export const EMOTE_ATLAS: Readonly<Record<string, string>> = { carne: "emoji_carne", nota: "emoji_nota", exclam: "emoji_exclam", coracao: "emoji_coracao", surpreso: "emoji_surpreso" };
export const EMOTE_GRADE: Readonly<Record<string, string>> = { surpreso: "pergunta" };

/* ------------------------------------------------------------------ o cocô: a sujeira do motor sobe */
let cocoVisto: { chave: string; sujeira: number } | null = null, cocoDesde = -1e9;
/** a vista olha a sujeira do motor: se SUBIU desde a ultima olhada (do mesmo pet), o pet esta no cocô por COCO_MS. A primeira olhada de
    um pet e a troca de pet nao contam. Idempotente no mesmo quadro (as duas vistas a chamam) */
export function vigiarCoco(chave: string, sujeira: number, agora: number): void {
  if (cocoVisto && cocoVisto.chave === chave && sujeira > cocoVisto.sujeira) cocoDesde = agora;
  cocoVisto = { chave, sujeira };
}
/** no cocô agora? */
export const noCoco = (agora: number): boolean => agora - cocoDesde < CENA_ACAO.cocoMs && agora >= cocoDesde;
/** so para os testes: esquece o cocô visto */
export function esquecerCoco(): void { cocoVisto = null; cocoDesde = -1e9; }

/* ------------------------------------------------------------------ a reacao ao toque */
/** o que o corpo diz do carinho, lido antes e depois do `acariciar`: as concentracoes em [0, C] (a FALTA de cada drive), a escala C e o
    medo da mao (0 ou 1: ConfigCorpo.medo_da_mao, valendo so com `gestos`) */
export interface LeituraCorpo { solidao: number; estresse: number; susto: number; C: number; medo: number }
/** a reacao: `relaxou` se a solidao e o estresse cairam, `calmo` se nao havia o que aliviar; `carinho` e a fracao do carinho que o corpo
    aplicou (1 = inteiro) e `medo` o que o medo da mao tirou (1 - carinho). Os dois saem do corpo, nao da tela */
export interface Reacao { desde: number; tipo: "relaxou" | "calmo"; carinho: number; medo: number }

/** a reacao do corpo ao carinho: `antes` e `depois` do `acariciar`. Falha alto se as leituras nao forem do mesmo corpo ou nao forem finitas */
export function reacaoDoCorpo(antes: LeituraCorpo, depois: LeituraCorpo, agora: number): Reacao {
  for (const l of [antes, depois]) {
    for (const k of ["solidao", "estresse", "susto", "C", "medo"] as const) {
      if (!Number.isFinite(l[k])) throw new Error(`leitura do corpo sem ${k}`);
    }
  }
  if (antes.C !== depois.C || antes.C <= 0) throw new Error("as leituras do corpo sao de escalas diferentes");
  const fator = (antes.C - antes.medo * antes.susto) / antes.C, queda = antes.solidao + antes.estresse - (depois.solidao + depois.estresse);
  return { desde: agora, tipo: queda > 0 ? "relaxou" : "calmo", carinho: fator, medo: 1 - fator };
}

let reacao: Reacao | null = null;
/** guarda a reacao que a vista vai mostrar */
export function mostrarReacao(r: Reacao): void { reacao = r; }
/** a reacao se ainda vale, senao null */
export function reacaoAtual(agora: number): Reacao | null { return reacao && agora - reacao.desde < CENA_ACAO.reacaoMs && agora >= reacao.desde ? reacao : null; }
/** so para os testes */
export function esquecerReacao(): void { reacao = null; }

/** o gesto da reacao: o pulinho de quem relaxou (a altura vai com o carinho que o corpo aplicou) e o recuo de quem teme a mao (vai com o medo) */
export function gestoDaReacao(r: Reacao, agora: number): Gesto {
  const t = agora - r.desde;
  if (t < 0 || t >= CENA_ACAO.reacaoMs) return SEM_GESTO;
  const sobe = r.tipo === "relaxou" ? CENA_ACAO.reacaoAlto * r.carinho * Math.sin(Math.PI * Math.min(1, t / CENA_ACAO.reacaoPulinhoMs)) : 0;
  const recua = -CENA_ACAO.reacaoRecuo * r.medo * Math.sin(Math.PI * Math.min(1, t / CENA_ACAO.reacaoRecuoMs));
  return { frente: recua, alto: sobe, estica: r.tipo === "calmo" ? 1 - 0.04 * Math.sin(Math.PI * Math.min(1, t / CENA_ACAO.reacaoPulinhoMs)) : 1 };
}

/* ------------------------------------------------------------------ o gesto e o emote de agora */
/** o que a vista le do pet para a cena */
export interface EntradaCena { acao: string; sujeira: number; chave: string }

/** o gesto do corpo para a acao do motor (so quando o pet esta parado no lugar: andando, quem se mexe e o passo) */
export function gestoDaAcao(acao: string, agora: number): Gesto {
  const C = CENA_ACAO, tau = 2 * Math.PI;
  switch (acao) {
    case "comer": return { frente: 0, alto: 0, estica: 1 - C.comerEstica * Math.abs(Math.sin((agora / C.comerMs) * Math.PI)) };
    case "brincar": return { frente: 0, alto: C.brincarAlto * Math.abs(Math.sin((agora / C.brincarMs) * Math.PI)), estica: 1 };
    case "chamar_atencao": return { frente: 0, alto: C.chamarAlto * Math.abs(Math.sin((agora / C.chamarMs) * Math.PI)), estica: 1 };
    case "explorar": return { frente: C.explorarFrente * Math.sin((agora / C.explorarMs) * tau), alto: 0, estica: 1 };
    case "emburrar": return { frente: C.emburrarFrente * Math.sign(Math.sin((agora / C.emburrarMs) * Math.PI)), alto: 0, estica: C.emburrarEstica };
    default: return SEM_GESTO;                    /* ocioso e dormir: nada novo aqui */
  }
}
/** o gesto do cocô */
function gestoDoCoco(agora: number): Gesto {
  const C = CENA_ACAO;
  return { frente: C.cocoTremor * Math.sign(Math.sin((agora / C.cocoTremorMs) * Math.PI)), alto: 0, estica: C.cocoEstica };
}

/** o gesto de agora: a reacao ao toque, o cocô e, com o pet parado e acordado, o da acao. Com movimento reduzido, nenhum; em Pausa (como o
    Seguidor, vistaMundo.ts) so a reacao ao toque, que e resposta a uma mao do dono, e nao a vida que anda */
export function gestoAgora(e: EntradaCena, agora: number, reduzido: boolean, parado: boolean, pausa = false): Gesto {
  vigiarCoco(e.chave, e.sujeira, agora);
  if (reduzido) return SEM_GESTO;
  const r = reacaoAtual(agora);
  if (r) return gestoDaReacao(r, agora);
  if (pausa) return SEM_GESTO;
  if (noCoco(agora)) return gestoDoCoco(agora);
  return parado ? gestoDaAcao(e.acao, agora) : SEM_GESTO;
}

/** o emote de agora: a reacao ao toque (o coracao de quem relaxou; a gota de quem temeu a mao), o cocô (a gota do esforco) ou o da acao */
export function emoteAgora(e: EntradaCena, agora: number): string | null {
  vigiarCoco(e.chave, e.sujeira, agora);
  const r = reacaoAtual(agora);
  if (r) return r.medo > 0 ? "gota" : r.tipo === "relaxou" ? "coracao" : null;
  if (noCoco(agora)) return "gota";
  return EMOTE_DA_ACAO[e.acao] ?? null;
}

/* ------------------------------------------------------------------ o desenho dos efeitos (canvas 2D, por cima do pet) */
/** os efeitos soltos do pet: as migalhas de quem come e os coracoes de quem relaxou. (x, y, w, h) e o retangulo do sprite em px de CSS, K = px
    do canvas por px de CSS. Com movimento reduzido, so um coracao parado */
export function desenharEfeitos(cx: CanvasRenderingContext2D, K: number, x: number, y: number, w: number, h: number, e: EntradaCena, agora: number,
    reduzido: boolean, pal: Paleta, pausa = false): void {
  const C = CENA_ACAO, r = reacaoAtual(agora);
  if (r && r.tipo === "relaxou") {
    /* um coracao a mais por inteiro do carinho que o corpo aplicou: de 1 (sem carinho nenhum) a 3 */
    const n = 1 + Math.round(2 * r.carinho), esc = Math.max(1, Math.round(2 * K));
    for (let i = 0; i < n; i++) {
      const f = reduzido ? 0.4 : (((agora - r.desde) / C.coracaoMs) + i / n) % 1;
      if (!reduzido && agora - r.desde < (i / n) * C.coracaoMs) continue;
      cx.save(); cx.globalAlpha = reduzido ? 0.9 : Math.min(1, (1 - f) * 1.8);
      cx.setTransform(esc, 0, 0, esc, Math.round((x + w * (0.25 + 0.25 * i) - (S.coracao[0].length * esc) / (2 * K)) * K), Math.round((y + 4 - f * C.coracaoSobe) * K));
      desenharGrade(cx, S.coracao, 0, 0, pal);
      cx.restore();
    }
  }
  if (reduzido || pausa || e.acao !== "comer" || r) return;
  /* as migalhas: pedacinhos que caem da boca, defasados */
  cx.save(); cx.fillStyle = pal.d ?? "#C9533A"; cx.strokeStyle = "#1D2233"; cx.lineWidth = Math.max(1, K * 0.5);
  for (let i = 0; i < C.migalhas; i++) {
    const f = ((agora / C.migalhaMs) + i / C.migalhas) % 1, lado = (i - (C.migalhas - 1) / 2) * 0.16;
    const px = Math.round((x + w * (0.78 + lado) + Math.sin(i * 2.3) * 3) * K), py = Math.round((y + h * 0.62 + f * C.migalhaQueda) * K), t = Math.max(2, Math.round(2.5 * K));
    cx.globalAlpha = Math.min(1, (1 - f) * 2);
    cx.fillRect(px, py, t, t); cx.strokeRect(px, py, t, t);
  }
  cx.restore();
}
