/* LUTA_POC, LP5 (docs/PLANO_EQUILIBRIO_LUTA_POC.md, secao 4.3): os candidatos da rodada, so na bancada. Um candidato e o CANDIDATO_V21 com
   alguns numeros trocados (candidatoDe); um nome desconhecido, uma chave que o candidato nao tem ou um numero que nao e positivo falham alto.
   Os candidatos com nome ficam no CANDIDATOS; os da grade (grade.ts) vem de um JSON e so rodam com --grade. Os numeros novos sao
   PROPOSTOS, SEM FONTE, ate o Matheus decidir. */
import { readFileSync } from "node:fs";
import { conferirEsquiva as conferirEsquivaPoc, conferirTiro as conferirTiroPoc } from "../../motor/arena/luta.ts";
import { CANDIDATO_V21, esquivaDe, type Candidato } from "./comum.ts";

/** as trocas de um candidato: cada chave do Candidato, com as sub-chaves que mudam */
export type Troca = { nome: string } & { [K in Exclude<keyof Candidato, "nome">]?: Partial<Candidato[K]> | number };
export function candidatoDe(t: Troca): Candidato {
  if (!/^[a-z0-9_]+$/.test(t.nome) || t.nome === CANDIDATO_V21.nome) throw new Error(`candidato: nome invalido ${JSON.stringify(t.nome)}`);
  const base = JSON.parse(JSON.stringify(CANDIDATO_V21)) as Candidato, out = base as unknown as Record<string, unknown>;
  for (const [k, v] of Object.entries(t)) {
    if (k === "nome") continue;
    if (!(k in base)) throw new Error(`candidato ${t.nome}: a chave ${k} nao existe`);
    const atual = out[k];
    if (typeof atual === "number") {
      if (typeof v !== "number" || !(v > 0)) throw new Error(`candidato ${t.nome}: ${k} precisa ser um numero positivo`);
      out[k] = v;
      continue;
    }
    if (typeof v !== "object" || v === null) throw new Error(`candidato ${t.nome}: ${k} precisa ser um objeto`);
    const alvo = atual as Record<string, number>;
    for (const [s, x] of Object.entries(v)) {
      if (!(s in alvo)) throw new Error(`candidato ${t.nome}: ${k}.${s} nao existe`);
      /* o treino dos rivais e o tiro podem ser 0 (o nucleo confere a faixa do tiro); o resto e positivo */
      if (typeof x !== "number" || !Number.isFinite(x) || x < 0 || (x === 0 && k !== "treinoRival" && k !== "tiro" && k !== "esquiva")) throw new Error(`candidato ${t.nome}: ${k}.${s} invalido (${x})`);
      alvo[s] = x;
    }
  }
  out.nome = t.nome;
  conferirTiroPoc(base.tiro);
  const esq = esquivaDe(base); if (esq) conferirEsquivaPoc(esq);
  return Object.freeze(base);
}

/** os candidatos com nome (os que entram nas medidas inteiras e no relato) */
const E = (cr: number, ad: number, ul: number, me: number) => ({ crianca: cr, adolescente: ad, adulto: ul, mega: me });
/** LP5-1, rodada 1: o w15_g02 da grade r1d (scripts/medicoes/equilibrio_poc/lp5_1/r1d), o de T1 mais perto da faixa entre os que passam
    T3, E1 e D1 (a regra de escolha da secao 4.2). PROPOSTO, SEM FONTE */
export const LP5_1_R1 = candidatoDe({
  nome: "lp5_1_r1", pesoPonto: 15,
  gama: { vigor: .02, recuperacao: .02, guarda: .06, forca: .02, mira: .14, folego: .14 },
  mapa: { hp: 1300, vel: 60 }, multVida: E(.6, .9, 1.35, 2.025), multAtk: E(1, 1.5, 2.25, 3.375),
});
/** LP5-1, rodada 2: o g02_d7_v1 da grade r2 (scripts/medicoes/equilibrio_poc/lp5_1/r2): o lp5_1_r1 com a distancia do tiro (o recuo na
    preparacao a 2 vezes o movimento) e o dano do projetil a 0,7 (D-LP5-12 e D-LP5-13). PROPOSTO, SEM FONTE */
export const LP5_1_R2 = candidatoDe({
  nome: "lp5_1_r2", pesoPonto: 15,
  gama: { vigor: .02, recuperacao: .02, guarda: .06, forca: .02, mira: .14, folego: .14 },
  mapa: { hp: 1300, vel: 60 }, multVida: E(.6, .9, 1.35, 2.025), multAtk: E(1, 1.5, 2.25, 3.375),
  tiro: { distMin: 110, esperaMax: 1500, recuo: 1.5, recuaNaPrep: 2, recuaAbaixo: .75, danoProj: .7, velProj: 1 },
});
/** o lp5_1_r2 com a esquiva ligada (D-LP5-16: o Matheus, "pode ligar esquiva nova"): o ponto m6_f6_p0 da grade lp5_1/r4e, o unico com 6 metas.
    A leitura do golpe de perto fica desligada (pertoChance 0): ligada (0,35), o E1 reprova e o A1 pende para quem atira. PROPOSTO, SEM FONTE */
export const LP5_1_ESQ = candidatoDe({
  nome: "lp5_1_esq", pesoPonto: 15,
  gama: { vigor: .02, recuperacao: .02, guarda: .06, forca: .02, mira: .14, folego: .14 },
  mapa: { hp: 1300, vel: 60 }, multVida: E(.6, .9, 1.35, 2.025), multAtk: E(1, 1.5, 2.25, 3.375),
  tiro: { distMin: 110, esperaMax: 1500, recuo: 1.5, recuaNaPrep: 2, recuaAbaixo: .75, danoProj: .7, velProj: 1 },
  esquiva: { ligada: 1, gamaMira: .6, gamaFolego: .6, kAtento: .5, pertoChance: 0, pertoReacao: 200, contraMs: 0 },
});
export const CANDIDATOS: Readonly<Record<string, Candidato>> = { v21: CANDIDATO_V21, lp5_1_r1: LP5_1_R1, lp5_1_r2: LP5_1_R2, lp5_1_esq: LP5_1_ESQ };
/** o candidato da linha de comando: --candidato <nome>, ou --candidato-json <arquivo> (so a grade) */
export function candidatoDaLinha(nome: string, json: string, grade: boolean): Candidato {
  if (json) {
    if (!grade) throw new Error("candidato: o --candidato-json so roda na grade (--grade)");
    return candidatoDe(JSON.parse(readFileSync(json, "utf-8")) as Troca);
  }
  const c = CANDIDATOS[nome];
  if (!c) throw new Error(`candidato desconhecido ${nome} (${Object.keys(CANDIDATOS).join(", ")})`);
  return c;
}
