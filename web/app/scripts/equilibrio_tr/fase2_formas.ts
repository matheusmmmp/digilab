/* Rodada de equilibrio do combate em tempo real, fase 2: as formas (docs/PLANO_EQUILIBRIO_COMBATE_TR.md, metas F-1 a F-7). So o motor,
   sem tela, CPU contra CPU, com semente, em cima do relogio da fase 1 (RELOGIO_V14, o candidato). Os lutadores sao os bots canonicos
   (como na M-A1 de docs/PLANO_EQUILIBRIO_GERAL.md): a forma, o carater canonico, sem treino, a semente da forma (sementeDe) e as regras
   CV21E_TR com o relogio dado. Mede:
   - F-1 a F-3 na matriz 8 x 8 das formas adultas (sem o espelho: "contra as outras 7");
   - F-4 as linhas do Champion (os 4 adolescentes, com as tecnicas) e os ramos do Rookie (as 2 criancas), a mesma especie dos dois
     lados, em rodizio pelas sementes (a especie nao entra na conta da linha);
   - F-5 de longe (cacador; sentinela e emboscador) contra de perto (brigao e colosso; duelista, furioso, vigia e tita), no Champion e
     no Ultimate. O guardiao, o espelho e a muralha (o contra-golpe) nao entram em nenhum dos dois lados;
   - F-6 cada forma adulta com e sem a passiva, contra as outras 7 (com as delas);
   - F-7 cada sombria (o epsilon minimo dela) contra as 8 formas adultas normais.
   No limite, a luta fica com a fracao de vida (sem desafiado): sao lutas de forca, e os lados trocam.
   As sementes: as da fase 1 (a faixa reservada, 5 bases x 20, hashSemente("equilibrio-tr", base, k)); 200 lutas por celula.
   --listas v14: as listas candidatas da rodada (LISTAS_V14, LISTAS_V14_R1, bots.ts); --variante <nome>: uma variante da grade (VARIANTES, abaixo),
   aplicada por cima.
   --disparo X: o multiplicador do disparo do tempo real (RelogioTR.disparo) por cima do relogio.
   uso (em web/app): npx tsx scripts/equilibrio_tr/fase2_formas.ts --faixa calibracao [--listas v14] [--variante <nome>] [--disparo X] --saida <arquivo.json> */
import { mkdirSync, writeFileSync } from "node:fs";
import { dirname } from "node:path";
import { execSync } from "node:child_process";
import {
  CSO, CV, CV21E_TR, ESPECIES, FORMAS_AD, LINHAS, LISTAS_V14, RELOGIO_V13, RELOGIO_V14, RIVAL_ESPECIE, SOMBRIA, caraterCanonico, copiarGambits,
  hashSemente, jogarTR, lutadorBot, perfilDe, sementeDe, CAT,
  type Forma, type FormaAdultaNormal, type ListaGambits, type Lutador, type RegrasLuta,
} from "../../motor/index.ts";
import { VARIANTES } from "./variantes_fase2.ts";

const arg = (k: string): string | null => { const i = process.argv.indexOf("--" + k); return i < 0 ? null : process.argv[i + 1] ?? null; };
/* as faixas reservadas (experiments/bancada/faixas.py): a primeira rodada e a segunda (calibracao2, conferencia2; DR2-2) */
const FAIXAS: Record<string, number> = { calibracao: 68101, conferencia: 70101, calibracao2: 72101, conferencia2: 74101 };
const faixa = arg("faixa"), saida = arg("saida"), variante = arg("variante");
if (!faixa || !(faixa in FAIXAS)) throw new Error("--faixa calibracao | conferencia | calibracao2 | conferencia2");
if (!saida) throw new Error("--saida <arquivo.json>");
if (variante !== null && !VARIANTES[variante]) throw new Error("variante desconhecida: " + variante);
/* --relogio v13: so para o diagnostico (o relogio dos pets v13); a fase 2 mede em cima do candidato da fase 1 */
/* --relogio-diag '{"recuo":1}': so diagnostico, por cima do candidato (nao e alavanca da fase 2) */
/* --disparo X: o multiplicador do disparo do tempo real (a grade do passo do disparo, depois da fase 3) */
const disparo = arg("disparo") === null ? {} : { disparo: Number(arg("disparo")) };
if ("disparo" in disparo && !(disparo.disparo > 0)) throw new Error("--disparo precisa ser um numero > 0");
const R: RegrasLuta = { ...CV21E_TR, relogio: { ...(arg("relogio") === "v13" ? RELOGIO_V13 : RELOGIO_V14), ...JSON.parse(arg("relogio-diag") ?? "{}"), ...disparo } };
/* as listas da rodada: a semente de hoje, as candidatas (--listas v14) e a variante por cima */
const LISTAS: Record<string, ListaGambits> = { ...(arg("listas") === "v14" ? LISTAS_V14 : arg("listas") === "v14r1" ? LISTAS_V14_R1 : {}), ...(variante ? VARIANTES[variante]() : {}) };
const SEMENTES_POR_BASE = 20;
const bases = [0, 1, 2, 3, 4].map(i => FAIXAS[faixa] + 101 * i);
const sementes = bases.flatMap(b => Array.from({ length: SEMENTES_POR_BASE }, (_, k) => hashSemente("equilibrio-tr", b, k)));
const r3 = (x: number): number => Math.round(x * 1000) / 1000;
const media = (xs: number[]): number => xs.reduce((a, b) => a + b, 0) / xs.length;

/** o lutador de uma forma (o id e a chave da lista: a forma adulta, a sombria, a linha ou o ramo); k escolhe a especie das linhas e
    dos ramos (a mesma dos dois lados) */
type Mk = (k: number) => Lutador;
const comLista = (L: Lutador, id: string): Lutador => LISTAS[id] ? { ...L, estilo: { ...L.estilo, gambits: copiarGambits(LISTAS[id]) } } : L;
const adulto = (f: FormaAdultaNormal): Mk => { const L = comLista(lutadorBot(f, R), f); return () => L; };
const semPassiva = (mk: Mk): Mk => k => { const L = mk(k); return { ...L, cond: { ...L.cond, passiva: null } }; };
function jovem(forma: (esp: Forma["esp"]) => Forma, car: Record<string, number>, id: string): Mk {
  const porEsp = ESPECIES.map(esp => { const f = forma(esp);
    return comLista({ nome: id, estilo: { nome: id, gambits: copiarGambits(sementeDe(f, R)), eps: CV.eps }, cond: perfilDe(f, car) }, id); });
  return k => porEsp[k % ESPECIES.length];
}
const linha = (l: typeof LINHAS[number]): Mk => jovem(esp => ({ esp, est: "adolescente", linha: l }), { [CAT.adolescente[l].eixo]: .5 }, l);
const ramo = (r: "sereno" | "arisco"): Mk => jovem(esp => ({ esp, est: "crianca", ramo: r }), {}, r);
function sombria(nome: string): Mk {
  const s = SOMBRIA[nome]!, base = s.base as FormaAdultaNormal, f: Forma = { esp: RIVAL_ESPECIE[base], est: "adulto", linha: s.linha, adulta: nome as Forma["adulta"] };
  const L = comLista({ nome, sombra: true, estilo: { nome, gambits: copiarGambits(sementeDe(f, R)), eps: Math.max(CV.eps, CSO.epsMin) },
    cond: perfilDe(f, caraterCanonico(base)) }, nome);
  return () => L;
}

/** a taxa do lado `a` contra `b`: 200 lutas (as 100 sementes x os dois lados); o empate vale meio ponto */
function taxa(a: Mk, b: Mk): number {
  let p = 0, n = 0;
  sementes.forEach((s, k) => {
    const A = a(k), B = b(k);
    p += jogarTR(A, B, s, { R }).pontosA; p += 1 - jogarTR(B, A, s, { R }).pontosA; n += 2;
  });
  return p / n;
}

const t0 = performance.now();
/* F-1 a F-3: a matriz das formas adultas */
const mkAd = Object.fromEntries(FORMAS_AD.map(f => [f, adulto(f)])) as Record<FormaAdultaNormal, Mk>;
const M: Record<string, Record<string, number>> = Object.fromEntries(FORMAS_AD.map(f => [f, {}]));
for (let i = 0; i < FORMAS_AD.length; i++) for (let j = i + 1; j < FORMAS_AD.length; j++) {
  const a = FORMAS_AD[i], b = FORMAS_AD[j], t = taxa(mkAd[a], mkAd[b]);
  M[a][b] = r3(t); M[b][a] = r3(1 - t);
}
const forca = Object.fromEntries(FORMAS_AD.map(f => [f, r3(media(Object.values(M[f])))]));
const vence = Object.fromEntries(FORMAS_AD.map(f => [f, Object.values(M[f]).filter(x => x > .5).length]));
const fs = Object.values(forca);
/* F-4: as linhas do Champion e os ramos do Rookie */
const mkLi = Object.fromEntries(LINHAS.map(l => [l, linha(l)]));
const ML: Record<string, Record<string, number>> = Object.fromEntries(LINHAS.map(l => [l, {}]));
for (let i = 0; i < LINHAS.length; i++) for (let j = i + 1; j < LINHAS.length; j++) {
  const a = LINHAS[i], b = LINHAS[j], t = taxa(mkLi[a], mkLi[b]);
  ML[a][b] = r3(t); ML[b][a] = r3(1 - t);
}
const forcaLinha = Object.fromEntries(LINHAS.map(l => [l, r3(media(Object.values(ML[l])))]));
const serenoArisco = r3(taxa(ramo("sereno"), ramo("arisco")));
/* F-5: de longe contra de perto, por estagio */
const LONGE_AD: FormaAdultaNormal[] = ["sentinela", "emboscador"], PERTO_AD: FormaAdultaNormal[] = ["duelista", "furioso", "vigia", "tita"];
const longeAd = r3(media(LONGE_AD.flatMap(a => PERTO_AD.map(b => M[a][b]))));
const longeCh = r3(media(["brigao", "colosso"].map(b => ML.cacador[b])));
/* F-6: as passivas (a forma com e sem a dela, contra as outras 7 com as delas) */
const passivas = Object.fromEntries(FORMAS_AD.map(f => {
  const sem = media(FORMAS_AD.filter(g => g !== f).map(g => taxa(semPassiva(mkAd[f]), mkAd[g])));
  return [f, { com: forca[f], sem: r3(sem), efeito: r3(forca[f] - sem) }];
}));
/* F-7: as sombrias contra as normais */
const sombrias = Object.fromEntries(Object.keys(SOMBRIA).map(nome => {
  const mk = sombria(nome), por = Object.fromEntries(FORMAS_AD.map(g => [g, r3(taxa(mk, mkAd[g]))]));
  return [nome, { forca: r3(media(Object.values(por))), contra: por }];
}));

const entre = (x: number, a: number, b: number): boolean => x >= a && x <= b;
const out = {
  gerado_por: "web/app/scripts/equilibrio_tr/fase2_formas.ts", data: new Date().toISOString().slice(0, 10),
  commit: execSync("git rev-parse --short HEAD").toString().trim(), node: process.version,
  faixa, bases, sementes_por_base: SEMENTES_POR_BASE, relogio: R.relogio, listas: arg("listas") ?? "v13", variante,
  listas_trocadas: Object.keys(LISTAS),
  metas: {
    "F-1": { forca, fora: FORMAS_AD.filter(f => !entre(forca[f], .4, .6)), passa: fs.every(x => entre(x, .4, .6)) },
    "F-2": { distancia: r3(Math.max(...fs) - Math.min(...fs)), passa: Math.max(...fs) - Math.min(...fs) <= .2 },
    "F-3": { vence, passa: Object.values(vence).every(v => v >= 2) },
    "F-4": { champion: forcaLinha, rookie_sereno_x_arisco: serenoArisco,
      passa: Object.values(forcaLinha).every(x => entre(x, .4, .6)) && entre(serenoArisco, .4, .6) },
    "F-5": { champion_cacador_x_perto: longeCh, ultimate_longe_x_perto: longeAd, passa: entre(longeCh, .45, .55) && entre(longeAd, .45, .55) },
    "F-6": { passivas, passa: Object.values(passivas).every(p => Math.abs(p.efeito) <= .1) },
    "F-7": { forca: Object.fromEntries(Object.entries(sombrias).map(([k, v]) => [k, v.forca])),
      passa: Object.values(sombrias).every(s => entre(s.forca, .45, .65)) },
  },
  matriz_adultos: M, matriz_champion: ML, sombrias, custo_s: r3((performance.now() - t0) / 1000),
};
mkdirSync(dirname(saida), { recursive: true });
writeFileSync(saida, JSON.stringify(out, null, 1) + "\n");
console.log(JSON.stringify(out.metas, null, 1));
