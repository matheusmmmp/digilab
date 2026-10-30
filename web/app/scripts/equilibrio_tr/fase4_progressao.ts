/* Bancada da fase 4 da rodada de equilibrio do tempo real (docs/PLANO_EQUILIBRIO_COMBATE_TR.md, secao 2.4 e 2.5: G-1 a G-6, I-1 a I-5).
   So o motor, sem tela, CPU contra CPU, com semente, em cima das fases 1 a 3 (o candidato v14: o RELOGIO_V14, com o disparo a 6x da DE-9,
   as LISTAS_V14 e a reserva fixa no fim da DE-10).
   - os pets: o pet tipico de cada forma do estagio (a forma, o carater canonico, o treino uniforme de CIT.tipico ou nenhum), nas 4 especies
     (a especie gira com a semente), com a lista candidata da forma (LISTAS_V14) ou a de hoje; a escala da campanha (CESC_V9);
   - os rivais de forma canonica (os Megas da Liga, das instalacoes e da Fabrica, os rivais do Salao) lutam com a lista candidata da forma
     deles; os lideres e os desafiantes, com a lista deles de hoje;
   - os fatores (a alavanca da fase): os candidatos (FATORES_V14) ou, com --fatores-hoje, os de hoje (FATOR_LIDER_V9, CESC_V9.fatorNpc,
     FATOR_LIGA_V9, FATOR_INSTALACAO, FATOR_RIVAL_FABRICA_V9, FATOR_SALAO_V9); os de --fatores por cima.
   As partes:
   - g1: os 6 lideres, a serie da arena (a Cidadela, 3 lutas sem cura), o pet sem treino e com o tipico;
   - g2: os desafiantes da campanha (os NPCs com fator proprio), uma luta;
   - g3: a Liga (as 6 lutas seguidas, a cura dos v9), o Mega tipico de cada forma, a taxa de titulos;
   - g4: a Torre de Batalha e o Palacio, a 1a luta do Mega tipico (o pet de referencia nao tem dono nem chip: a lista do Palacio e a mesma);
   - g5: a Fabrica, a 1a serie (3 lutas sem cura) com o melhor alugado dos 3 (o de maior forca F-1 do candidato, disparo/conferencia_d6), sem
     troca;
   - g6: o Salao, cada nivel com o pet tipico;
   - itens: I-1 (sai do g1: sem treino os itens nao valem, itens.itensValem), I-2 (P-1 com a melhor combinacao de chips do de baixo), I-3 (a
     forca de cada forma adulta com a melhor combinacao contra as outras 7, como o F-1), I-4 (cada carta contra o lider do nivel) e I-5 (cada
     chip de regra no confronto do alvo dele, quando nao esta coberto). Os chips de regra entram antes da reserva (DE-10).
   Cada luta tem o limite com o desafiado (o lider, o NPC, o rival). Sementes: 5 bases da faixa x 20, hashSemente("equilibrio-tr", base, k).
   uso (em web/app): npx tsx scripts/equilibrio_tr/fase4_progressao.ts --faixa calibracao --parte g1|g2|g3|g4|g5|g6|i2|i3|i4|i5
     [--fatores '{"lider":{"torre":1.2},"npc":{"npc_tier2_sentinela":1.3},"liga":{"lago":1.2},"instalacao":1,"fabrica":.6,"salao":{"mega":1}}']
     [--cartas '{"carta_folego":{"guts":40}}'] --saida <arquivo.json>
   --cartas: o efeito candidato de uma carta por cima do de hoje (o valor da carta, a alavanca do I-4; so a bancada) */
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname } from "node:path";
import { execSync } from "node:child_process";
import {
  ADOL_V21, ARENAS, CESC_V9, CIT, CRIANCA_V21, CTR, CURA_LIGA_V9, CV, CV21E_TR, ESPECIES, ESTAGIOS_SALAO, FATOR_INSTALACAO, FATOR_LIDER_V9,
  FATOR_LIGA_V9, FATOR_RIVAL_FABRICA_V9, FATOR_SALAO_V9, FATORES_V14, FORMAS_AD, ITENS, LIGA, LINHAS, LINHA_DA_FORMA, LISTAS_V14, LUGARES_V6, NPC, RELOGIO_V14,
  STATS, alugueisFabrica, arenaDaLuta, capacidadeLista, caraterCanonico, cartaDe, chaveRegra, chipServe, copiarGambits, formaRivalFabrica,
  formaRivalInstalacao, formaRivalSalao, gambitsAdulto, hashSemente, itensValem, jogarArena, jogarSerie, jogarTR, listaComChips, lutadorBot,
  lutadorLiga, perfilDe, pontosComChips, regraQueCobre, rivalInstalacao, rivalSalao,
  type Chip, type Estagio, type Forma, type FormaAdultaNormal, type ListaGambits, type Lutador, type RegrasLuta,
} from "../../motor/index.ts";
import { ligarEscala } from "../../motor/catalogo.ts";

const arg = (k: string): string | null => { const i = process.argv.indexOf("--" + k); return i < 0 ? null : process.argv[i + 1] ?? null; };
/* as faixas reservadas (experiments/bancada/faixas.py): a primeira rodada e a segunda (calibracao2, conferencia2; DR2-2) */
const FAIXAS: Record<string, number> = { calibracao: 68101, conferencia: 70101, calibracao2: 72101, conferencia2: 74101 };
const PARTES = ["g1", "g2", "g3", "g4", "g5", "g6", "i2", "i3", "i4", "i5"];
const faixa = arg("faixa"), saida = arg("saida"), parte = arg("parte");
if (!faixa || !(faixa in FAIXAS)) throw new Error("--faixa calibracao | conferencia | calibracao2 | conferencia2");
if (!saida) throw new Error("--saida <arquivo.json>");
if (!parte || !PARTES.includes(parte)) throw new Error("--parte " + PARTES.join(" | "));
const R: RegrasLuta = { ...CV21E_TR, relogio: RELOGIO_V14 }, VERSAO = R.versaoPet;

/* os fatores: os de hoje, com os de --fatores por cima (so as chaves conhecidas) */
interface Fatores { lider: Record<string, number>; npc: Record<string, number>; liga: Record<string, number>; instalacao: number; fabrica: number; salao: Record<string, number> }
const HOJE: Fatores = { lider: { ...FATOR_LIDER_V9 }, npc: { ...CESC_V9.fatorNpc }, liga: { ...FATOR_LIGA_V9 }, instalacao: FATOR_INSTALACAO,
  fabrica: FATOR_RIVAL_FABRICA_V9, salao: { ...FATOR_SALAO_V9 } };
const BASE: Fatores = process.argv.includes("--fatores-hoje") ? HOJE : { lider: { ...FATORES_V14.lider }, npc: { ...FATORES_V14.npc },
  liga: { ...FATORES_V14.liga }, instalacao: FATORES_V14.instalacao, fabrica: FATORES_V14.fabrica, salao: { ...FATORES_V14.salao } };
const fArg = JSON.parse(arg("fatores") ?? "{}") as Partial<Fatores>;
for (const k of Object.keys(fArg)) if (!(k in HOJE)) throw new Error("--fatores: chave desconhecida " + k);
for (const k of ["lider", "npc", "liga", "salao"] as const) for (const x of Object.keys(fArg[k] ?? {}))
  if (!(x in HOJE[k])) throw new Error(`--fatores.${k}: ${x} nao tem fator hoje`);
const FAT: Fatores = { lider: { ...BASE.lider, ...fArg.lider }, npc: { ...BASE.npc, ...fArg.npc }, liga: { ...BASE.liga, ...fArg.liga },
  instalacao: fArg.instalacao ?? BASE.instalacao, fabrica: fArg.fabrica ?? BASE.fabrica, salao: { ...BASE.salao, ...fArg.salao } };

/* o efeito das cartas: o de hoje (itens.ts) ou o de --cartas por cima */
const CARTAS_ARG = JSON.parse(arg("cartas") ?? "{}") as Record<string, Record<string, unknown>>;
for (const k of Object.keys(CARTAS_ARG)) cartaDe(k);
const efeitoCarta = (id: string) => ({ ...cartaDe(id).carta, ...CARTAS_ARG[id] });
const SEMENTES_POR_BASE = 20;
const bases = [0, 1, 2, 3, 4].map(i => FAIXAS[faixa] + 101 * i);
const sementes = bases.flatMap(b => Array.from({ length: SEMENTES_POR_BASE }, (_, k) => hashSemente("equilibrio-tr", b, k)));
const r4 = (x: number): number => Math.round(x * 10000) / 10000;
const media = (xs: number[]): number => xs.reduce((a, b) => a + b, 0) / xs.length;
const TIPICO = CIT.tipico as Record<string, number>;
/* a parte do treino tipico que ja encheu os estagios de antes (o espaco do chip de stat; como na rodada geral) */
const ANTERIOR: Record<string, number> = { crianca: 0, adolescente: CTR.tetoEstagio.crianca, adulto: CTR.tetoEstagio.crianca + CTR.tetoEstagio.adolescente,
  mega: CTR.tetoVida };

/* ------------------------------------------------ os pets de referencia */
interface Ref { id: string; forma: (esp: Forma["esp"]) => Forma; car: Record<string, number> | null; lista: ListaGambits }
const listaDe = (id: string, hoje: ListaGambits): ListaGambits => LISTAS_V14[id] ?? hoje;
function formasDe(est: Estagio): Ref[] {
  if (est === "crianca") return (["sereno", "arisco"] as const).map(r => ({ id: r, forma: esp => ({ esp, est, ramo: r }), car: null, lista: listaDe(r, CRIANCA_V21[r]) }));
  if (est === "adolescente") return LINHAS.map(l => ({ id: l, forma: esp => ({ esp, est, ramo: "sereno", linha: l }),
    car: caraterCanonico(FORMAS_AD.find(f => LINHA_DA_FORMA[f] === l)!), lista: listaDe(l, ADOL_V21[l]) }));
  return FORMAS_AD.map(f => ({ id: f, forma: esp => ({ esp, est, ramo: "sereno", linha: LINHA_DA_FORMA[f], adulta: f }), car: caraterCanonico(f),
    lista: listaDe(f, gambitsAdulto(f, R)) }));
}
/** a lista com os chips de regra (DE-10): os chips entram antes da reserva (a ultima regra), sem tirar nenhuma */
function comChipsDeRegra(g: ListaGambits, chips: readonly string[], est: Estagio): ListaGambits {
  if (!g.regras.length) return listaComChips(g, chips, capacidadeLista(est), VERSAO);
  const reserva = g.regras[g.regras.length - 1], todas = new Set(g.regras.map(chaveRegra));
  const novos = chips.filter(id => { const c = ITENS.find(x => x.id === id) as Chip; return c.tipo === "chip_regra" && !todas.has(chaveRegra(c.regra)); });
  const sem = listaComChips({ regras: g.regras.slice(0, -1), final: g.final }, novos, capacidadeLista(est), VERSAO);
  return { regras: [...sem.regras, reserva], final: g.final };
}
/** o pet: `nivel` = o treino uniforme; os chips pelo motor (itens.ts), com a trava do treino minimo (sem `trava`: o efeito do item em si) */
function pet(ref: Ref, esp: Forma["esp"], nivel: number, chips: readonly string[] = [], trava = true, escala = true): Lutador {
  const f = ref.forma(esp), est = f.est, tr = Object.fromEntries(STATS.map(k => [k, nivel / STATS.length])) as never;
  const ch = trava && !itensValem(VERSAO, est, nivel) ? [] : chips;
  const pontos = pontosComChips(ch, est, tr, Math.max(0, nivel - ANTERIOR[est]), nivel > 0, VERSAO);
  const cond = escala ? perfilDe(f, ref.car, 1, pontos, true, VERSAO) : perfilDe(f, ref.car, 1, pontos);
  return { nome: `${ref.id}+${nivel}@${esp}`, estilo: { nome: ref.id, gambits: copiarGambits(comChipsDeRegra(ref.lista, ch, est)), eps: CV.eps }, cond };
}
/** o rival de forma canonica com a lista candidata da forma dele */
const comListaV14 = (L: Lutador, f: Forma): Lutador => {
  const id = f.adulta ?? f.linha ?? f.ramo!, g = LISTAS_V14[id];
  return g ? { ...L, estilo: { ...L.estilo, gambits: copiarGambits(g) } } : L;
};
/** o fator por cima da escala de um lutador montado com o fator `de` */
const comFator = (L: Lutador, de: number, para: number): Lutador => ({ ...L, cond: { ...L.cond, escala: L.cond.escala! / de * para } });

const t0 = performance.now();
ligarEscala(parte !== "i3");
const out: Record<string, unknown> = {
  gerado_por: "web/app/scripts/equilibrio_tr/fase4_progressao.ts", data: new Date().toISOString().slice(0, 10),
  commit: execSync("git rev-parse --short HEAD").toString().trim(), node: process.version,
  faixa, bases, sementes_por_base: SEMENTES_POR_BASE, relogio: R.relogio, listas: "v14", reserva_no_fim: true, fatores: FAT, cartas: CARTAS_ARG, parte, metas: {},
};
const metas = out.metas as Record<string, unknown>;

/* ------------------------------------------------ G-1: os lideres (e o I-1) */
function lider(id: string, fator = FAT.lider[id]): { B: Lutador; lutas: number; est: Estagio } {
  const a0 = ARENAS.find(a => a.id === id)!, a = { ...arenaDaLuta(a0.lider, VERSAO)!, fator };
  return { B: lutadorBot(a0.lider, R, a), lutas: a.lutas ?? 1, est: LUGARES_V6[a0.lugar].est };
}
/** a taxa de series vencidas inteiras do pet (lado A, o lider desafiado) */
function taxaLider(ref: Ref, nivel: number, id: string, chips: readonly string[] = [], carta: string | null = null, fator?: number): number {
  const { B, lutas, est } = lider(id, fator);
  const ef = carta && itensValem(VERSAO, est, nivel) ? efeitoCarta(carta) : null;
  let v = 0;
  sementes.forEach((s, k) => {
    const serie = jogarArena(pet(ref, ESPECIES[k % ESPECIES.length], nivel, chips), B, hashSemente("equilibrio-tr-lider", s, id), R, lutas, 1, ef);
    if (serie.length === lutas && serie[lutas - 1].pontosA === 1) v++;
  });
  return v / sementes.length;
}
if (parte === "g1") {
  const arenas: Record<string, unknown> = {};
  for (const a of ARENAS) {
    const est = LUGARES_V6[a.lugar].est, formas: Record<string, { sem: number; com: number }> = {};
    for (const ref of formasDe(est)) formas[ref.id] = { sem: r4(taxaLider(ref, 0, a.id)), com: r4(taxaLider(ref, TIPICO[est], a.id)) };
    const v = Object.values(formas), sem = media(v.map(x => x.sem)), com = media(v.map(x => x.com)), pior = Math.min(...v.map(x => x.com));
    arenas[a.id] = { lider: a.lider, estagio: est, fator: FAT.lider[a.id], sem: r4(sem), com: r4(com), pior: r4(pior),
      pior_forma: Object.entries(formas).find(([, x]) => x.com === pior)![0], passa: sem <= .05 && com >= .8 && pior >= .5, formas };
  }
  metas["G-1"] = { arenas, passa: Object.values(arenas).every(x => (x as { passa: boolean }).passa) };
  /* I-1: sem treino os itens nao valem (a trava do treino minimo), entao o pet sem treino com os melhores itens e o pet sem treino */
  const trava = (["crianca", "adolescente", "adulto", "mega"] as Estagio[]).every(est => !itensValem(VERSAO, est, 0));
  const pior = Math.max(...Object.values(arenas).map(x => (x as { sem: number }).sem));
  metas["I-1"] = { itens_valem_sem_treino: !trava, pior_lider_sem_treino: r4(pior), passa: trava && pior <= .05 };
}

/* ------------------------------------------------ G-2: os desafiantes */
if (parte === "g2") {
  const npcs: Record<string, unknown> = {};
  for (const k of Object.keys(FAT.npc)) {
    const est = NPC[k]!.est, B = comFator(lutadorBot(k, R), HOJE.npc[k], FAT.npc[k]), formas: Record<string, { sem: number; com: number }> = {};
    for (const ref of formasDe(est)) {
      const t = (nivel: number) => media(sementes.map((s, i) => jogarTR(pet(ref, ESPECIES[i % ESPECIES.length], nivel), B, hashSemente("equilibrio-tr-npc", s, k), { R, desafiado: 1 }).pontosA === 1 ? 1 : 0));
      formas[ref.id] = { sem: r4(t(0)), com: r4(t(TIPICO[est])) };
    }
    const v = Object.values(formas), sem = media(v.map(x => x.sem)), com = media(v.map(x => x.com)), pior = Math.min(...v.map(x => x.com));
    npcs[k] = { nome: NPC[k]!.nome, estagio: est, fator: FAT.npc[k], sem: r4(sem), com: r4(com), pior: r4(pior),
      pior_forma: Object.entries(formas).find(([, x]) => x.com === pior)![0], passa: sem <= .3 && com >= .8 && pior >= .5, formas };
  }
  metas["G-2"] = { desafiantes: npcs, passa: Object.values(npcs).every(x => (x as { passa: boolean }).passa) };
}

/* ------------------------------------------------ G-3: a Liga */
if (parte === "g3") {
  const lideres = LIGA.map((x, i) => comListaV14(lutadorLiga(i, R, FAT.liga[x.arena]), { esp: x.esp, est: "mega", ramo: "sereno", linha: LINHA_DA_FORMA[x.adulta], adulta: x.adulta }));
  const formas: Record<string, { titulos: number; por_luta: number[] }> = {};
  for (const ref of formasDe("mega")) {
    let tit = 0;
    const chegou = LIGA.map(() => 0);
    sementes.forEach((s, k) => {
      const serie = jogarSerie(pet(ref, ESPECIES[k % ESPECIES.length], TIPICO.mega), lideres, hashSemente("equilibrio-tr-liga", s), R, 1, null, CURA_LIGA_V9);
      serie.forEach((r, j) => { if (r.pontosA === 1) chegou[j]++; });
      if (serie.length === LIGA.length && serie.every(r => r.pontosA === 1)) tit++;
    });
    formas[ref.id] = { titulos: r4(tit / sementes.length), por_luta: chegou.map(x => r4(x / sementes.length)) };
  }
  const t = Object.values(formas).map(x => x.titulos);
  metas["G-3"] = { fatores: FAT.liga, cura: CURA_LIGA_V9, formas, min: r4(Math.min(...t)), max: r4(Math.max(...t)),
    fora: Object.entries(formas).filter(([, x]) => x.titulos < .25 || x.titulos > .85).map(([k]) => k), passa: t.every(x => x >= .25 && x <= .85) };
}

/* ------------------------------------------------ G-4: a Torre e o Palacio (a 1a luta) */
if (parte === "g4") {
  const formas: Record<string, number> = {};
  for (const ref of formasDe("mega")) formas[ref.id] = r4(media(sementes.map((s, k) => {
    const st = hashSemente("equilibrio-tr-torre", s), B = comListaV14(rivalInstalacao(st, 0, R, FAT.instalacao), formaRivalInstalacao(st, 0));
    return jogarTR(pet(ref, ESPECIES[k % ESPECIES.length], TIPICO.mega), B, hashSemente("equilibrio-tr-torre-luta", st), { R, desafiado: 1 }).pontosA === 1 ? 1 : 0;
  })));
  const v = Object.values(formas), melhor = Math.max(...v), pior = Math.min(...v);
  metas["G-4"] = { fator: FAT.instalacao, formas, melhor: r4(melhor), pior: r4(pior), palacio_igual_a_torre: true, passa: melhor >= .7 && pior >= .4 };
}

/* ------------------------------------------------ G-5: a Fabrica (a 1a serie, o melhor alugado) */
if (parte === "g5") {
  const f1 = JSON.parse(readFileSync(new URL("../medicoes/equilibrio_tr/disparo/conferencia_d6/formas_calibracao.json", import.meta.url), "utf-8")) as { metas: { "F-1": { forca: Record<string, number> } } };
  const forca = f1.metas["F-1"].forca;
  for (const f of FORMAS_AD) if (typeof forca[f] !== "number") throw new Error("F-1 sem a forca de " + f);
  const mega = (f: Forma, fator: number): Lutador => {
    const adulta = f.adulta as FormaAdultaNormal, p = perfilDe(f, caraterCanonico(adulta), 1, null, true, VERSAO, true);
    return comListaV14({ nome: adulta, estilo: { nome: `fabrica:${adulta}`, gambits: copiarGambits(gambitsAdulto(adulta, R)), eps: CV.eps }, cond: { ...p, escala: p.escala! * fator } }, f);
  };
  let series = 0;
  const escolhidos: Record<string, number> = {};
  sementes.forEach(s0 => {
    const s = hashSemente("equilibrio-tr-fabrica", s0), al = alugueisFabrica(s);
    const melhor = al.reduce((a, b) => forca[b.adulta!] > forca[a.adulta!] ? b : a);
    escolhidos[melhor.adulta!] = (escolhidos[melhor.adulta!] ?? 0) + 1;
    const Bs = [0, 1, 2].map(k => mega(formaRivalFabrica(s, k), FAT.fabrica));
    const serie = jogarSerie(mega(melhor, 1), Bs, hashSemente("equilibrio-tr-fabrica-luta", s), R, 1, null, 0);
    if (serie.length === 3 && serie.every(r => r.pontosA === 1)) series++;
  });
  metas["G-5"] = { fator_rival: FAT.fabrica, uma_serie: r4(series / sementes.length), escolhidos, passa: series / sementes.length >= .25 };
}

/* ------------------------------------------------ G-6: o Salao */
if (parte === "g6") {
  const niveis: Record<string, unknown> = {};
  for (const est of ESTAGIOS_SALAO) {
    const formas: Record<string, number> = {};
    for (const ref of formasDe(est)) formas[ref.id] = r4(media(sementes.map((s, k) => {
      const ss = hashSemente("equilibrio-tr-salao", s, est), B = comListaV14(rivalSalao(ss, est, R, FAT.salao[est]), formaRivalSalao(ss, est));
      return jogarTR(pet(ref, ESPECIES[k % ESPECIES.length], TIPICO[est]), B, hashSemente("equilibrio-tr-salao-luta", ss), { R, desafiado: 1 }).pontosA === 1 ? 1 : 0;
    })));
    const m = media(Object.values(formas));
    niveis[est] = { fator: FAT.salao[est], taxa: r4(m), formas, passa: m >= .7 && m <= .95 };
  }
  metas["G-6"] = { niveis, passa: Object.values(niveis).every(x => (x as { passa: boolean }).passa) };
}

/* ------------------------------------------------ os itens */
const CHIPS = ITENS.filter(x => x.tipo !== "carta") as Chip[], CARTAS = ITENS.filter(x => x.tipo === "carta").map(x => x.id);
/** as combinacoes de ate 3 chips que servem no estagio (3 vagas, as 6 medalhas); os de regra entram no fim, entao a ordem nao conta */
function combinacoes(est: Estagio): string[][] {
  const ids = CHIPS.filter(c => chipServe(c, est)).map(c => c.id), out: string[][] = [[]];
  for (let i = 0; i < ids.length; i++) {
    out.push([ids[i]]);
    for (let j = i + 1; j < ids.length; j++) { out.push([ids[i], ids[j]]); for (let k = j + 1; k < ids.length; k++) out.push([ids[i], ids[j], ids[k]]); }
  }
  return out;
}
/* I-2: P-1 com a melhor combinacao do de baixo (a de mais pontos contra o de cima, por forma) */
if (parte === "i2") {
  const sBusca = bases.map(b => hashSemente("equilibrio-tr", b, 0)), sP1 = bases.flatMap(b => [0, 1].map(k => hashSemente("equilibrio-tr", b, k)));
  const pontos = (fb: Ref, chips: string[], baixo: Estagio, alto: Estagio, ss: number[], mesmaEsp: boolean) => {
    let p = 0, n = 0, vit = 0;
    for (const fa of formasDe(alto)) ESPECIES.forEach((eb, ib) => ESPECIES.forEach((ea, ia) => {
      if (mesmaEsp && ib !== ia) return;
      const A = pet(fb, eb, TIPICO[baixo], chips), B = pet(fa, ea, 0);
      for (const s of ss) for (const lado of [0, 1]) {
        const x = lado === 0 ? jogarTR(A, B, s, { R, desafiado: 1 }).pontosA : 1 - jogarTR(B, A, s, { R, desafiado: 0 }).pontosA;
        p += x; n++; if (x === 1) vit++;
      }
    }));
    return { p, n, vit };
  };
  const par = (baixo: Estagio, alto: Estagio) => {
    let p = 0, n = 0, vit = 0;
    const melhores: Record<string, string[]> = {};
    for (const fb of formasDe(baixo)) {
      const cs = combinacoes(baixo);
      const m = cs.reduce((a, c) => { const x = pontos(fb, c, baixo, alto, sBusca, true).p; return x > a.x ? { c, x } : a; }, { c: [] as string[], x: -1 });
      melhores[fb.id] = m.c;
      const r = pontos(fb, m.c, baixo, alto, sP1, false); p += r.p; n += r.n; vit += r.vit;
    }
    return { pontos: r4(p / n), vitorias: r4(vit / n), lutas: n, melhor_combinacao: melhores };
  };
  const viz = { rookie_champion: par("crianca", "adolescente"), champion_ultimate: par("adolescente", "adulto"), ultimate_mega: par("adulto", "mega") };
  const dois = { rookie_ultimate: par("crianca", "adulto"), champion_mega: par("adolescente", "mega") };
  metas["I-2"] = { vizinhos: viz, dois_estagios: dois, passa: Object.values(viz).every(x => x.pontos <= .1) && Object.values(dois).every(x => x.vitorias === 0) };
}
/* I-3: a forca de cada forma adulta com a melhor combinacao contra as outras 7 sem item (a matriz do F-1: sem escala, sem treino, sem a
   trava; o efeito do item em si). A melhor combinacao sai de 1 semente por base; a forca, das 100 */
if (parte === "i3") {
  const refs = formasDe("adulto"), sBusca = bases.map(b => hashSemente("equilibrio-tr", b, 0));
  const forca = (fx: Ref, chips: string[], ss: number[]) => {
    let p = 0, n = 0;
    for (const fy of refs) if (fy !== fx) ss.forEach((s, k) => {
      const esp = ESPECIES[k % ESPECIES.length], X = pet(fx, esp, 0, chips, false, false), Y = pet(fy, esp, 0, [], false, false);
      p += jogarTR(X, Y, s, { R }).pontosA + 1 - jogarTR(Y, X, s, { R }).pontosA; n += 2;
    });
    return p / n;
  };
  const formas: Record<string, { sem_item: number; com_item: number; combinacao: string[] }> = {};
  for (const fx of refs) {
    const m = combinacoes("adulto").reduce((a, c) => { const x = forca(fx, c, sBusca); return x > a.x ? { c, x } : a; }, { c: [] as string[], x: -1 });
    formas[fx.id] = { sem_item: r4(forca(fx, [], sementes)), com_item: r4(forca(fx, m.c, sementes)), combinacao: m.c };
  }
  metas["I-3"] = { formas, max: r4(Math.max(...Object.values(formas).map(x => x.com_item))), passa: Object.values(formas).every(x => x.com_item <= .6) };
}
/* I-4: cada carta, o pet tipico contra o lider do nivel dele (os lideres do estagio; a carta so vale contra os NPCs da campanha) */
if (parte === "i4") {
  const cartas: Record<string, unknown> = {};
  for (const c of CARTAS) {
    const arenas: Record<string, { sem: number; com: number; efeito: number }> = {};
    for (const a of ARENAS) {
      const est = LUGARES_V6[a.lugar].est, refs = formasDe(est);
      const sem = media(refs.map(r => taxaLider(r, TIPICO[est], a.id))), com = media(refs.map(r => taxaLider(r, TIPICO[est], a.id, [], c)));
      arenas[a.id] = { sem: r4(sem), com: r4(com), efeito: r4(com - sem) };
    }
    const ef = Object.values(arenas).map(x => x.efeito);
    cartas[c] = { arenas, efeito_medio: r4(media(ef)), menor_efeito: r4(Math.min(...ef)), passa: media(ef) >= .03 };
  }
  metas["I-4"] = { cartas, passa: Object.values(cartas).every(x => (x as { passa: boolean }).passa) };
}
/* I-5: cada chip de regra no confronto do alvo dele (itens.ts), o pet tipico com o chip, quando nao esta coberto (regraQueCobre). Os
   confrontos, pela frase do alvo: Recuo, as formas do Champion e do Ultimate contra quem prepara o pesado (o colosso e a tita);
   Oportunista, o guardiao e o colosso contra os lideres do Champion; Perseguidor, o colosso e o guardiao do Champion e as formas deles no
   Ultimate (vigia, tita, espelho, muralha) contra os cacadores (o cacador, a sentinela e o emboscador); Aparo, o cacador e o colosso e as
   formas deles no Ultimate contra o furioso */
if (parte === "i5") {
  const CH = formasDe("adolescente"), UL = formasDe("adulto"), so = (rs: Ref[], ids: string[]) => rs.filter(r => ids.includes(r.id));
  const ALVO: Record<string, { pets: Ref[]; rivais: (est: Estagio) => Ref[]; lideres?: string[] }> = {
    chip_recuo: { pets: [...CH, ...UL], rivais: est => est === "adolescente" ? so(CH, ["colosso"]) : so(UL, ["tita"]) },
    chip_oportunista: { pets: so(CH, ["guardiao", "colosso"]), rivais: () => [], lideres: ["torre", "floresta"] },
    chip_perseguidor: { pets: [...so(CH, ["colosso", "guardiao"]), ...so(UL, ["vigia", "tita", "espelho", "muralha"])],
      rivais: est => est === "adolescente" ? so(CH, ["cacador"]) : so(UL, ["sentinela", "emboscador"]) },
    chip_aparo: { pets: [...so(CH, ["cacador", "colosso"]), ...so(UL, ["sentinela", "emboscador", "vigia", "tita"])],
      rivais: est => est === "adolescente" ? so(CH, ["brigao"]) : so(UL, ["furioso"]) },
  };
  const chips: Record<string, unknown> = {};
  for (const [id, alvo] of Object.entries(ALVO)) {
    const c = ITENS.find(x => x.id === id) as Chip & { regra: never };
    const confrontos: Record<string, { lutas: number; disparou: number; fracao: number }> = {}, cobertos: string[] = [];
    for (const ref of alvo.pets) {
      const est = ref.forma("brasa").est;
      if (!chipServe(c, est)) continue;
      if (regraQueCobre(ref.lista.regras, c.regra)) { cobertos.push(ref.id); continue; }
      const rivais: [string, (k: number) => Lutador][] = alvo.lideres ? alvo.lideres.map(a => [a, () => lider(a).B])
        : alvo.rivais(est).map(rv => [rv.id, (k: number) => pet(rv, ESPECIES[k % ESPECIES.length], TIPICO[est])]);
      for (const [nome, B] of rivais) {
        let disparou = 0;
        sementes.forEach((s, k) => {
          const A = pet(ref, ESPECIES[k % ESPECIES.length], TIPICO[est], [id]), iChip = A.estilo.gambits!.regras.findIndex(r => chaveRegra(r) === chaveRegra(c.regra));
          if (iChip < 0) throw new Error(`${id} fora da lista de ${ref.id}`);
          const res = jogarTR(A, B(k), hashSemente("equilibrio-tr-chip", s, id), { R, desafiado: 1 });
          if (res.acoes.some(x => x.lado === 0 && x.motivo === iChip)) disparou++;
        });
        confrontos[`${ref.id} x ${nome}`] = { lutas: sementes.length, disparou, fracao: r4(disparou / sementes.length) };
      }
    }
    const fr = Object.values(confrontos).map(x => x.fracao);
    chips[id] = { confrontos, cobertos, media: fr.length ? r4(media(fr)) : null, pior: fr.length ? r4(Math.min(...fr)) : null,
      passa: fr.length > 0 && media(fr) >= .5 };
  }
  metas["I-5"] = { chips, passa: Object.values(chips).every(x => (x as { passa: boolean }).passa) };
}

out.custo_s = r4((performance.now() - t0) / 1000);
mkdirSync(dirname(saida), { recursive: true });
writeFileSync(saida, JSON.stringify(out, null, 1) + "\n");
console.log(JSON.stringify(Object.fromEntries(Object.entries(metas).map(([k, v]) => [k, (v as { passa: boolean }).passa]))));
