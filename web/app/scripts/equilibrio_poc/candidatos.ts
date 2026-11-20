/* LUTA_POC, LP5 (docs/PLANO_EQUILIBRIO_LUTA_POC.md, secao 4.3): os candidatos da rodada, so na bancada. Um candidato e o CANDIDATO_V21 com
   alguns numeros trocados (candidatoDe); um nome desconhecido, uma chave que o candidato nao tem ou um numero que nao e positivo falham alto.
   Os candidatos com nome ficam no CANDIDATOS; os da grade (grade.ts) vem de um JSON e so rodam com --grade. Os numeros novos sao
   PROPOSTOS, SEM FONTE, ate o Matheus decidir. */
import { readFileSync } from "node:fs";
import { conferirBordaRingue, conferirForcaAtr, conferirPuloMax, conferirApoio as conferirApoioPoc, conferirArenaPorEstagio as conferirArenaPoc, conferirEsquiva as conferirEsquivaPoc, conferirTiro as conferirTiroPoc } from "../../motor/arena/luta.ts";
import { CANDIDATO_V21, conferirDivisao, esquivaDe, extrasLp6, type Candidato } from "./comum.ts";

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
    if (k === "npcDivisao") {
      /* a divisao de um NPC (D-LP5-18) entra inteira: os 6 pesos, somando 6, e so de um NPC que o candidato tem */
      const div = out[k] as Record<string, unknown>;
      for (const [npcK, w] of Object.entries(v)) {
        if (!(npcK in base.npcTotal)) throw new Error(`candidato ${t.nome}: npcDivisao.${npcK} nao e um NPC`);
        if (typeof w !== "object" || w === null) throw new Error(`candidato ${t.nome}: npcDivisao.${npcK} precisa ser um objeto`);
        conferirDivisao(npcK, w as Record<string, unknown>);
        div[npcK] = { ...(w as Record<string, number>) };
      }
      continue;
    }
    const alvo = atual as Record<string, number>;
    for (const [s, x] of Object.entries(v)) {
      if (!(s in alvo)) throw new Error(`candidato ${t.nome}: ${k}.${s} nao existe`);
      /* o treino dos rivais, o tiro, a esquiva e as chaves da LP6 podem ser 0 (o nucleo confere as faixas); o resto e positivo */
      if (typeof x !== "number" || !Number.isFinite(x) || x < 0 || (x === 0 && k !== "treinoRival" && k !== "tiro" && k !== "esquiva" && k !== "apoio" && k !== "arena" && k !== "nucleo")) throw new Error(`candidato ${t.nome}: ${k}.${s} invalido (${x})`);
      alvo[s] = x;
    }
  }
  out.nome = t.nome;
  conferirTiroPoc(base.tiro);
  const esq = esquivaDe(base); if (esq) conferirEsquivaPoc(esq);
  const x = extrasLp6(base); if (x.apoio) conferirApoioPoc(x.apoio); if (x.arenaPorEstagio) conferirArenaPoc(x.arenaPorEstagio);
  /* as chaves da N3: o nucleo confere as faixas (falha alto fora delas) */
  const n = x.nucleo;
  if (n?.forcaAtr !== undefined) conferirForcaAtr(n.forcaAtr);
  if (n?.puloMax !== undefined) conferirPuloMax(n.puloMax);
  if (n?.bordaRingue !== undefined) conferirBordaRingue(n.bordaRingue);
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
/** LP5-2 (D-LP5-17): o lp5_1_esq com o total do Gazimon em 0,8 vez o de hoje (76,8), o ponto de maior folga da grade lp5_2/r3. Os outros
    9 NPCs ficam com o total de hoje: o MarinBullmon e o Tortomon ja passam com ele; os outros 7 nao passam em nenhum total. PROPOSTO, SEM FONTE */
export const LP5_2 = candidatoDe({
  nome: "lp5_2", pesoPonto: 15,
  gama: { vigor: .02, recuperacao: .02, guarda: .06, forca: .02, mira: .14, folego: .14 },
  mapa: { hp: 1300, vel: 60 }, multVida: E(.6, .9, 1.35, 2.025), multAtk: E(1, 1.5, 2.25, 3.375),
  tiro: { distMin: 110, esperaMax: 1500, recuo: 1.5, recuaNaPrep: 2, recuaAbaixo: .75, danoProj: .7, velProj: 1 },
  esquiva: { ligada: 1, gamaMira: .6, gamaFolego: .6, kAtento: .5, pertoChance: 0, pertoReacao: 200, contraMs: 0 },
  npcTotal: { npc_tier1_brutamontes: 76.8 },
});
/** LP5-3 (D-LP5-20): o lp5_2 com o fator dos rivais do Salao em 0,8, o ponto de maior folga do G4 na grade lp5_3/r2. A Liga, a Torre e a
    Fabrica ficam em 1: nenhum fator da grade (ate 0,1) fecha o G1, o G2 ou o G3. PROPOSTO, SEM FONTE */
const TROCA_LP5_3: Omit<Troca, "nome"> = {
  pesoPonto: 15,
  gama: { vigor: .02, recuperacao: .02, guarda: .06, forca: .02, mira: .14, folego: .14 },
  mapa: { hp: 1300, vel: 60 }, multVida: E(.6, .9, 1.35, 2.025), multAtk: E(1, 1.5, 2.25, 3.375),
  tiro: { distMin: 110, esperaMax: 1500, recuo: 1.5, recuaNaPrep: 2, recuaAbaixo: .75, danoProj: .7, velProj: 1 },
  esquiva: { ligada: 1, gamaMira: .6, gamaFolego: .6, kAtento: .5, pertoChance: 0, pertoReacao: 200, contraMs: 0 },
  npcTotal: { npc_tier1_brutamontes: 76.8 },
  fatorRival: { salao: .8 },
};
export const LP5_3 = candidatoDe({ nome: "lp5_3", ...TROCA_LP5_3 });
/** LP6-3 (docs/PLANO_LP6_SEGUNDO_GOLPE.md, secao 5; o adendo da LP6-3 no PLANO_EQUILIBRIO_LUTA_POC.md): o ponto de partida, o lp5_3 com as
    duas chaves da LP6-1 ligadas e os numeros da LP6-1 (o apoio a 0,6 do dano, recarga 2 vezes, clipe a 0,6; a elipse 1,15 e 1,3).
    PROPOSTO, SEM FONTE */
export const LP6_0 = candidatoDe({
  nome: "lp6_0", pesoPonto: 15,
  gama: { vigor: .02, recuperacao: .02, guarda: .06, forca: .02, mira: .14, folego: .14 },
  mapa: { hp: 1300, vel: 60 }, multVida: E(.6, .9, 1.35, 2.025), multAtk: E(1, 1.5, 2.25, 3.375),
  tiro: { distMin: 110, esperaMax: 1500, recuo: 1.5, recuaNaPrep: 2, recuaAbaixo: .75, danoProj: .7, velProj: 1 },
  esquiva: { ligada: 1, gamaMira: .6, gamaFolego: .6, kAtento: .5, pertoChance: 0, pertoReacao: 200, contraMs: 0 },
  npcTotal: { npc_tier1_brutamontes: 76.8 },
  fatorRival: { salao: .8 },
  apoio: { ligado: 1 }, arena: { ligada: 1 },
});
/** LP6-3, os 3 finalistas da R2 (lp6_3/r2; D-LP6-3-7 e D-LP6-3-8): o lp6_0 com o apoio so desde o Ultimate (sem o recuo), dano 0,6, recarga
    3 vezes, e a elipse do Ultimate e do Mega em 1,1/1,2, 1,15/1,3 ou 1,2/1,4. PROPOSTOS, SEM FONTE */
const finalista = (nome: string, Ultimate: number, Mega: number, nucleo?: Partial<Candidato["nucleo"]>) => candidatoDe({
  nome, pesoPonto: 15, ...(nucleo ? { nucleo } : {}),
  gama: { vigor: .02, recuperacao: .02, guarda: .06, forca: .02, mira: .14, folego: .14 },
  mapa: { hp: 1300, vel: 60 }, multVida: E(.6, .9, 1.35, 2.025), multAtk: E(1, 1.5, 2.25, 3.375),
  tiro: { distMin: 110, esperaMax: 1500, recuo: 1.5, recuaNaPrep: 2, recuaAbaixo: .75, danoProj: .7, velProj: 1 },
  esquiva: { ligada: 1, gamaMira: .6, gamaFolego: .6, kAtento: .5, pertoChance: 0, pertoReacao: 200, contraMs: 0 },
  npcTotal: { npc_tier1_brutamontes: 76.8 },
  fatorRival: { salao: .8 },
  apoio: { ligado: 1, dano: .6, recarga: 3, desde: 3 }, arena: { ligada: 1, Ultimate, Mega },
});
export const LP6_3_U110 = finalista("lp6_3_u110", 1.1, 1.2), LP6_3_U115 = finalista("lp6_3_u115", 1.15, 1.3), LP6_3_U120 = finalista("lp6_3_u120", 1.2, 1.4);
/** a N4 da investigacao do nucleo (docs/PLANO_LUTA_NUCLEO.md, secao 8): os contrafactuais, cada chave da N3 ligada sozinha no lp5_3 (a luta
    da v23) e as 4 juntas no lp5_3 e no lp6_3_u120 (a da v29). So na bancada: nenhuma versao de pet as liga (D-N-7). PROPOSTOS, SEM FONTE */
const n4 = (nome: string, nucleo: Partial<Candidato["nucleo"]>) => candidatoDe({ nome, ...TROCA_LP5_3, nucleo });
const JUNTAS = { forcaAtr: 1.15, tiroDoMorto: 1, puloMax: 75, bordaRingue: .9 };
export const N4: Readonly<Record<string, Candidato>> = {
  n4_atr100: n4("n4_atr100", { forcaAtr: 1 }), n4_atr115: n4("n4_atr115", { forcaAtr: 1.15 }), n4_atr125: n4("n4_atr125", { forcaAtr: 1.25 }),
  n4_morto: n4("n4_morto", { tiroDoMorto: 1 }), n4_pulo: n4("n4_pulo", { puloMax: 75 }), n4_borda: n4("n4_borda", { bordaRingue: .9 }),
  n4_juntas_v23: n4("n4_juntas_v23", JUNTAS), n4_juntas_v29: finalista("n4_juntas_v29", 1.2, 1.4, JUNTAS),
};
export const CANDIDATOS: Readonly<Record<string, Candidato>> = { v21: CANDIDATO_V21, lp5_1_r1: LP5_1_R1, lp5_1_r2: LP5_1_R2, lp5_1_esq: LP5_1_ESQ, lp5_2: LP5_2, lp5_3: LP5_3, lp6_0: LP6_0,
  lp6_3_u110: LP6_3_U110, lp6_3_u115: LP6_3_U115, lp6_3_u120: LP6_3_U120, ...N4 };
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
